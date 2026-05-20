from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TranslationRequest:
    source_text: str
    target_language: str
    source_language: str | None = None


@dataclass(frozen=True)
class TranslationResult:
    translated_text: str


class TranslationProvider(Protocol):
    def translate(self, request: TranslationRequest) -> TranslationResult: ...
