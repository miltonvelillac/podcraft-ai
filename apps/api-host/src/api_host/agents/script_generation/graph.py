from dataclasses import replace
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from api_host.agents.script_generation.errors import (
    ScriptGenerationConfigurationError,
    ScriptGenerationServiceError,
)
from api_host.agents.script_generation.provider import ScriptGenerationRequest, ScriptGenerator
from api_host.schemas.podcast_schemas import PodcastScript


MAX_SOURCE_CHARS = 12_000
MAX_GENERATION_ATTEMPTS = 2


class ScriptGenerationState(TypedDict, total=False):
    request: ScriptGenerationRequest
    normalized_text: str
    script: PodcastScript
    attempts: int
    last_error: ScriptGenerationServiceError


class ScriptGenerationGraph:
    """LangGraph workflow for podcast script generation inside the MCP host."""

    def __init__(
        self,
        generator: ScriptGenerator,
        max_source_chars: int = MAX_SOURCE_CHARS,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> None:
        self._generator = generator
        self._max_source_chars = max_source_chars
        self._max_attempts = max_attempts
        self._graph = self._build_graph()

    def generate(self, request: ScriptGenerationRequest) -> PodcastScript:
        state = self._graph.invoke(
            {
                "request": request,
                "attempts": 0,
            }
        )
        script = state.get("script")
        if script is None:
            raise ScriptGenerationServiceError("Script generation graph returned no script.")
        return script

    def _build_graph(self):
        graph = StateGraph(ScriptGenerationState)
        graph.add_node("prepare_source_text", self._prepare_source_text)
        graph.add_node("generate_script", self._generate_script)
        graph.add_node("fail_generation", self._fail_generation)

        graph.add_edge(START, "prepare_source_text")
        graph.add_edge("prepare_source_text", "generate_script")
        graph.add_conditional_edges(
            "generate_script",
            self._route_after_generation,
            {
                "done": END,
                "retry": "generate_script",
                "fail": "fail_generation",
            },
        )

        return graph.compile()

    def _prepare_source_text(self, state: ScriptGenerationState) -> ScriptGenerationState:
        request = state["request"]
        normalized_text = " ".join(request.text.split())
        if len(normalized_text) > self._max_source_chars:
            normalized_text = _truncate_at_word_boundary(normalized_text, self._max_source_chars)

        return {
            "normalized_text": normalized_text,
        }

    def _generate_script(self, state: ScriptGenerationState) -> ScriptGenerationState:
        request = state["request"]
        normalized_text = state["normalized_text"]
        attempts = state.get("attempts", 0) + 1

        try:
            script = self._generator.generate(replace(request, text=normalized_text))
        except ScriptGenerationConfigurationError:
            raise
        except ScriptGenerationServiceError as exc:
            return {
                "attempts": attempts,
                "last_error": exc,
            }

        return {
            "attempts": attempts,
            "script": script,
        }

    def _route_after_generation(
        self,
        state: ScriptGenerationState,
    ) -> Literal["done", "retry", "fail"]:
        script = state.get("script")
        if _is_valid_script(script):
            return "done"
        if state.get("attempts", 0) < self._max_attempts:
            return "retry"
        return "fail"

    def _fail_generation(self, state: ScriptGenerationState) -> ScriptGenerationState:
        if last_error := state.get("last_error"):
            raise last_error
        raise ScriptGenerationServiceError("Script generation returned an invalid script.")


def _is_valid_script(script: PodcastScript | None) -> bool:
    if script is None:
        return False
    return bool(script.title.strip()) and bool(script.script.strip()) and script.estimated_duration_minutes > 0


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    truncated = text[:max_chars].rstrip()
    head, separator, _tail = truncated.rpartition(" ")
    if separator and head:
        return head
    return truncated
