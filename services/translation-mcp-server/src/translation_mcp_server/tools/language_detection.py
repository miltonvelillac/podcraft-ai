from podcraft_contracts import LanguageCode


LANGUAGE_MARKERS = {
    LanguageCode.ENGLISH.value: (
        " the ",
        " and ",
        " is ",
        " are ",
        " with ",
        " for ",
        " this ",
        " that ",
        " to ",
    ),
    LanguageCode.SPANISH.value: (
        " el ",
        " la ",
        " los ",
        " las ",
        " de ",
        " que ",
        " para ",
        " con ",
        " este ",
        " una ",
    ),
    LanguageCode.PORTUGUESE.value: (
        " o ",
        " a ",
        " os ",
        " as ",
        " de ",
        " que ",
        " para ",
        " com ",
        " este ",
        " uma ",
    ),
}

LANGUAGE_CHAR_MARKERS = {
    LanguageCode.SPANISH.value: ("á", "é", "í", "ó", "ú", "ñ", "¿", "¡"),
    LanguageCode.PORTUGUESE.value: ("ã", "õ", "ç", "â", "ê", "ô"),
}


def detect_language(text: str) -> str | None:
    normalized_text = f" {text.lower()} "
    scores = {
        language: sum(marker in normalized_text for marker in markers)
        for language, markers in LANGUAGE_MARKERS.items()
    }

    for language, markers in LANGUAGE_CHAR_MARKERS.items():
        scores[language] += sum(text.lower().count(marker) for marker in markers)

    best_language, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score < 2:
        return None

    tied_languages = [
        language for language, score in scores.items() if score == best_score
    ]
    if len(tied_languages) > 1:
        return None

    return best_language
