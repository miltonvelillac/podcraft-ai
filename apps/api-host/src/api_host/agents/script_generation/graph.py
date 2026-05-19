import os
from dataclasses import replace
from enum import StrEnum
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from api_host.config import load_project_env
from api_host.agents.script_generation.errors import (
    ScriptGenerationConfigurationError,
    ScriptGenerationServiceError,
)
from api_host.agents.script_generation.provider import ScriptGenerationRequest, ScriptGenerator
from api_host.schemas.podcast_schemas import PodcastScript
from podcraft_contracts import EnvVar


MAX_SOURCE_CHARS = 12_000
MAX_GENERATION_ATTEMPTS = 2


class ScriptGenerationGraphNode(StrEnum):
    PREPARE_SOURCE_TEXT = "prepare_source_text"
    GENERATE_SCRIPT = "generate_script"
    FAIL_GENERATION = "fail_generation"


class ScriptGenerationGraphRoute(StrEnum):
    DONE = "done"
    RETRY = "retry"
    FAIL = "fail"


class ScriptGenerationStateField(StrEnum):
    REQUEST = "request"
    NORMALIZED_TEXT = "normalized_text"
    SCRIPT = "script"
    ATTEMPTS = "attempts"
    LAST_ERROR = "last_error"


class ScriptGenerationState(TypedDict):
    request: ScriptGenerationRequest
    attempts: int
    normalized_text: NotRequired[str]
    script: NotRequired[PodcastScript]
    last_error: NotRequired[ScriptGenerationServiceError]


class ScriptGenerationGraph:
    """LangGraph workflow for podcast script generation inside the MCP host."""

    def __init__(
        self,
        generator: ScriptGenerator,
        max_source_chars: int | None = None,
        max_attempts: int | None = None,
    ) -> None:
        load_project_env()
        self._generator = generator
        self._max_source_chars = (
            max_source_chars
            if max_source_chars is not None
            else _read_positive_int_env(
                EnvVar.SCRIPT_GRAPH_MAX_SOURCE_CHARS,
                default=MAX_SOURCE_CHARS,
            )
        )
        self._max_attempts = (
            max_attempts
            if max_attempts is not None
            else _read_positive_int_env(
                EnvVar.SCRIPT_GRAPH_MAX_GENERATION_ATTEMPTS,
                default=MAX_GENERATION_ATTEMPTS,
            )
        )
        self._graph = self._build_graph()

    def generate(self, request: ScriptGenerationRequest) -> PodcastScript:
        state = self._graph.invoke(
            {
                ScriptGenerationStateField.REQUEST: request,
                ScriptGenerationStateField.ATTEMPTS: 0,
            }
        )
        script = state.get(ScriptGenerationStateField.SCRIPT)
        if script is None:
            raise ScriptGenerationServiceError("Script generation graph returned no script.")
        return script

    def _build_graph(self):
        graph = StateGraph(ScriptGenerationState)
        graph.add_node(ScriptGenerationGraphNode.PREPARE_SOURCE_TEXT, self._prepare_source_text)
        graph.add_node(ScriptGenerationGraphNode.GENERATE_SCRIPT, self._generate_script)
        graph.add_node(ScriptGenerationGraphNode.FAIL_GENERATION, self._fail_generation)

        graph.add_edge(START, ScriptGenerationGraphNode.PREPARE_SOURCE_TEXT)
        graph.add_edge(
            ScriptGenerationGraphNode.PREPARE_SOURCE_TEXT,
            ScriptGenerationGraphNode.GENERATE_SCRIPT,
        )
        graph.add_conditional_edges(
            ScriptGenerationGraphNode.GENERATE_SCRIPT,
            self._route_after_generation,
            {
                ScriptGenerationGraphRoute.DONE: END,
                ScriptGenerationGraphRoute.RETRY: ScriptGenerationGraphNode.GENERATE_SCRIPT,
                ScriptGenerationGraphRoute.FAIL: ScriptGenerationGraphNode.FAIL_GENERATION,
            },
        )

        return graph.compile()

    def _prepare_source_text(self, state: ScriptGenerationState) -> ScriptGenerationState:
        request = state[ScriptGenerationStateField.REQUEST]
        normalized_text = " ".join(request.text.split())
        if len(normalized_text) > self._max_source_chars:
            normalized_text = _truncate_at_word_boundary(normalized_text, self._max_source_chars)

        return {
            ScriptGenerationStateField.NORMALIZED_TEXT: normalized_text,
        }

    def _generate_script(self, state: ScriptGenerationState) -> ScriptGenerationState:
        request = state[ScriptGenerationStateField.REQUEST]
        normalized_text = state[ScriptGenerationStateField.NORMALIZED_TEXT]
        attempts = state.get(ScriptGenerationStateField.ATTEMPTS, 0) + 1

        try:
            script = self._generator.generate(replace(request, text=normalized_text))
        except ScriptGenerationConfigurationError:
            raise
        except ScriptGenerationServiceError as exc:
            return {
                ScriptGenerationStateField.ATTEMPTS: attempts,
                ScriptGenerationStateField.LAST_ERROR: exc,
            }

        return {
            ScriptGenerationStateField.ATTEMPTS: attempts,
            ScriptGenerationStateField.SCRIPT: script,
        }

    def _route_after_generation(
        self,
        state: ScriptGenerationState,
    ) -> ScriptGenerationGraphRoute:
        script = state.get(ScriptGenerationStateField.SCRIPT)
        if _is_valid_script(script):
            return ScriptGenerationGraphRoute.DONE
        if state.get(ScriptGenerationStateField.ATTEMPTS, 0) < self._max_attempts:
            return ScriptGenerationGraphRoute.RETRY
        return ScriptGenerationGraphRoute.FAIL

    def _fail_generation(self, state: ScriptGenerationState) -> ScriptGenerationState:
        if last_error := state.get(ScriptGenerationStateField.LAST_ERROR):
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


def _read_positive_int_env(env_var: EnvVar, default: int) -> int:
    raw_value = os.getenv(env_var)
    if raw_value is None or not raw_value.strip():
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ScriptGenerationConfigurationError(f"{env_var} must be a positive integer.") from exc

    if value <= 0:
        raise ScriptGenerationConfigurationError(f"{env_var} must be greater than zero.")

    return value
