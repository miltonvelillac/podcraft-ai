import os
from typing import Any, Protocol

from podcraft_contracts import EnvVar, LANGUAGE_NAMES
from translation_mcp_server.translation.errors import (
    TranslationAuthenticationError,
    TranslationConfigurationError,
    TranslationProviderError,
    TranslationRateLimitError,
    TranslationServiceError,
)
from translation_mcp_server.translation.provider import TranslationRequest, TranslationResult


DEFAULT_OPENAI_TRANSLATION_MODEL = "gpt-4.1-nano"


class TextTranslationModel(Protocol):
    def invoke(self, input: dict[str, str]) -> Any: ...


class PromptTemplate(Protocol):
    def __or__(self, other: TextTranslationModel) -> TextTranslationModel: ...


class OpenAiTranslationProvider:
    def __init__(
        self,
        model: TextTranslationModel | None = None,
        prompt: PromptTemplate | None = None,
        model_name: str | None = None,
    ) -> None:
        self._model = model
        self._prompt = prompt
        self._model_name = model_name or os.getenv(
            EnvVar.OPENAI_TRANSLATION_MODEL,
            DEFAULT_OPENAI_TRANSLATION_MODEL,
        )

    def translate(self, request: TranslationRequest) -> TranslationResult:
        target_language_name = _language_name(request.target_language)
        try:
            chain = self._build_translation_chain()
            result = chain.invoke(
                {
                    "target_language": target_language_name,
                    "source_text": request.source_text,
                }
            )
        except TranslationProviderError:
            raise
        except Exception as exc:
            raise _to_translation_error(exc) from exc

        translated_text = _extract_text_result(result)
        if not translated_text:
            raise TranslationServiceError("OpenAI translation returned empty text.")

        return TranslationResult(translated_text=translated_text)

    def _build_translation_chain(self) -> TextTranslationModel:
        if self._model is not None and self._prompt is not None:
            return self._prompt | self._model
        if self._model is not None:
            return self._model

        if not os.getenv(EnvVar.OPENAI_API_KEY):
            raise TranslationConfigurationError(
                f"{EnvVar.OPENAI_API_KEY} is required when "
                f"{EnvVar.TRANSLATION_PROVIDER}=openai."
            )

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise TranslationConfigurationError(
                "langchain-openai is required when translation uses OpenAI."
            ) from exc

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You prepare text for direct text-to-speech narration. "
                    "Translate faithfully and return only the narration text.",
                ),
                (
                    "human",
                    "Translate this source text into {target_language}. "
                    "Preserve meaning, names, numbers, and paragraph intent. "
                    "Do not add commentary.\n\n"
                    "Source text:\n{source_text}",
                ),
            ]
        )
        return prompt | ChatOpenAI(model=self._model_name, temperature=0)


def _language_name(language: str) -> str:
    language_name = LANGUAGE_NAMES.get(language)
    if language_name is None:
        raise TranslationConfigurationError(f"Unsupported translation language: {language}.")
    return language_name


def _extract_text_result(result: Any) -> str:
    if isinstance(result, str):
        return result.strip()

    content = getattr(result, "content", None)
    if isinstance(content, str):
        return content.strip()

    return ""


def _to_translation_error(exc: Exception) -> Exception:
    status_code = getattr(exc, "status_code", None)

    if status_code == 401:
        return TranslationAuthenticationError(
            f"OpenAI translation authentication failed. Check {EnvVar.OPENAI_API_KEY}."
        )
    if status_code == 429:
        return TranslationRateLimitError(
            "OpenAI translation rate limit exceeded. Wait a moment and try again."
        )
    if isinstance(status_code, int) and status_code >= 500:
        return TranslationServiceError(
            "OpenAI translation is temporarily unavailable. Try again later."
        )
    if isinstance(status_code, int) and 400 <= status_code < 500:
        return TranslationConfigurationError(
            "OpenAI translation rejected the request. Check model and translation settings."
        )

    return TranslationServiceError("OpenAI translation failed.")
