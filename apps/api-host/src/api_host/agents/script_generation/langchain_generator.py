import os
from typing import Any, Protocol

from api_host.agents.script_generation.errors import (
    ScriptGenerationConfigurationError,
    ScriptGenerationError,
    ScriptGenerationServiceError,
)
from api_host.agents.script_generation.provider import ScriptGenerationRequest
from api_host.schemas.podcast_schemas import (
    PodcastScript,
    PodcastStyle,
)
from podcraft_contracts import LANGUAGE_NAMES, PODCAST_DURATION_MINUTES


DEFAULT_SCRIPT_MODEL = "gpt-4.1-mini"
STYLE_DESCRIPTIONS = {
    PodcastStyle.EDUCATIONAL: "educational, clear, and step-by-step",
    PodcastStyle.CONVERSATIONAL: "conversational, natural, and engaging",
    PodcastStyle.EXECUTIVE_SUMMARY: "concise, executive, and decision-focused",
}

class StructuredScriptModel(Protocol):
    def invoke(self, input: Any) -> PodcastScript: ...


class PromptTemplate(Protocol):
    def __or__(self, other: StructuredScriptModel) -> StructuredScriptModel: ...


class LangChainScriptGenerator:
    def __init__(
        self,
        structured_model: StructuredScriptModel | None = None,
        prompt: PromptTemplate | None = None,
        model: str | None = None,
    ) -> None:
        self._structured_model = structured_model
        self._prompt = prompt
        self._model = model or os.getenv("OPENAI_SCRIPT_MODEL", DEFAULT_SCRIPT_MODEL)

    def generate(self, request: ScriptGenerationRequest) -> PodcastScript:
        try:
            chain = self._build_chain()
            result = chain.invoke(
                {
                    "source_text": request.text,
                    "style": STYLE_DESCRIPTIONS[request.style],
                    "language": LANGUAGE_NAMES[request.language.value],
                    "target_minutes": PODCAST_DURATION_MINUTES[request.target_duration.value],
                }
            )
        except ScriptGenerationError:
            raise
        except Exception as exc:
            raise ScriptGenerationServiceError("OpenAI script generation failed.") from exc

        if isinstance(result, PodcastScript):
            return result
        if isinstance(result, dict):
            return PodcastScript.model_validate(result)

        raise ScriptGenerationServiceError("OpenAI script generation returned an invalid payload.")

    def _build_chain(self) -> StructuredScriptModel:
        if self._structured_model is not None and self._prompt is not None:
            return self._prompt | self._structured_model
        if self._structured_model is not None:
            return self._structured_model

        if not os.getenv("OPENAI_API_KEY"):
            raise ScriptGenerationConfigurationError(
                "OPENAI_API_KEY is required when SCRIPT_PROVIDER=openai."
            )

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise ScriptGenerationConfigurationError(
                "langchain-openai is required when SCRIPT_PROVIDER=openai."
            ) from exc

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are PodCraft AI's internal script agent. Return only structured output. "
                    "Create podcast scripts that are factual, clear, and ready for text-to-speech.",
                ),
                (
                    "human",
                    "Convert the source material into a podcast script.\n"
                    "Language: {language}\n"
                    "Style: {style}\n"
                    "Target duration: about {target_minutes} minutes\n\n"
                    "Requirements:\n"
                    "- Write the title and full script in {language}.\n"
                    "- Preserve the source meaning without inventing unsupported facts.\n"
                    "- Make the script natural for spoken audio.\n"
                    "- Set estimated_duration_minutes to {target_minutes}.\n\n"
                    "Source material:\n{source_text}",
                ),
            ]
        )
        structured_model = ChatOpenAI(model=self._model, temperature=0.4).with_structured_output(
            PodcastScript
        )
        return prompt | structured_model
