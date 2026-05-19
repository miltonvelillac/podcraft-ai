from api_host.agents.script_generation.provider import ScriptGenerationRequest
from api_host.schemas.podcast_schemas import (
    PodcastLanguage,
    PodcastScript,
    PodcastStyle,
    PodcastTargetDuration,
)


class MockScriptGenerator:
    def generate(self, request: ScriptGenerationRequest) -> PodcastScript:
        normalized_text = " ".join(request.text.split())
        summary = self._truncate(normalized_text, max_chars=280)
        title = self._build_title(summary)
        intro = self._build_intro(request.style, request.language)
        duration_minutes = self._duration_minutes(request.target_duration)
        bridge = self._build_bridge(summary, request.language)

        return PodcastScript(
            title=title,
            script=f"{intro}\n\n{bridge}",
            estimated_duration_minutes=duration_minutes,
        )

    def _build_intro(self, style: PodcastStyle, language: PodcastLanguage) -> str:
        intros = {
            PodcastLanguage.ENGLISH: {
                PodcastStyle.EDUCATIONAL: "Welcome to PodCraft AI. In this episode, we will learn from the material step by step.",
                PodcastStyle.CONVERSATIONAL: "Welcome back. Let's talk through this topic in a simple, conversational way.",
                PodcastStyle.EXECUTIVE_SUMMARY: "Welcome to this executive briefing. Here are the key points you need to know.",
            },
            PodcastLanguage.SPANISH: {
                PodcastStyle.EDUCATIONAL: "Bienvenido a PodCraft AI. En este episodio, aprenderemos del material paso a paso.",
                PodcastStyle.CONVERSATIONAL: "Bienvenido de nuevo. Hablemos de este tema de forma simple y conversacional.",
                PodcastStyle.EXECUTIVE_SUMMARY: "Bienvenido a este resumen ejecutivo. Estos son los puntos clave que necesitas conocer.",
            },
            PodcastLanguage.PORTUGUESE: {
                PodcastStyle.EDUCATIONAL: "Bem-vindo ao PodCraft AI. Neste episodio, vamos aprender com o material passo a passo.",
                PodcastStyle.CONVERSATIONAL: "Bem-vindo de volta. Vamos conversar sobre este tema de forma simples.",
                PodcastStyle.EXECUTIVE_SUMMARY: "Bem-vindo a este resumo executivo. Estes sao os pontos principais que voce precisa saber.",
            },
        }
        return intros[language][style]

    def _build_bridge(self, summary: str, language: PodcastLanguage) -> str:
        bridges = {
            PodcastLanguage.ENGLISH: (
                "Today we are turning this source material into a clear podcast segment. "
                f"The main idea is: {summary}\n\n"
                "Let's break that down into practical takeaways, explain why it matters, "
                "and close with the key point listeners should remember."
            ),
            PodcastLanguage.SPANISH: (
                "Hoy convertiremos este material en un segmento claro de podcast. "
                f"La idea principal es: {summary}\n\n"
                "Vamos a desglosarlo en aprendizajes practicos, explicar por que importa "
                "y cerrar con el punto clave que la audiencia debe recordar."
            ),
            PodcastLanguage.PORTUGUESE: (
                "Hoje vamos transformar este material em um segmento claro de podcast. "
                f"A ideia principal e: {summary}\n\n"
                "Vamos dividir isso em aprendizados praticos, explicar por que importa "
                "e fechar com o ponto principal que a audiencia deve lembrar."
            ),
        }
        return bridges[language]

    def _duration_minutes(self, target_duration: PodcastTargetDuration) -> int:
        durations = {
            PodcastTargetDuration.SHORT: 2,
            PodcastTargetDuration.MEDIUM: 4,
            PodcastTargetDuration.LONG: 6,
        }
        return durations[target_duration]

    def _build_title(self, text: str) -> str:
        words = text.split()[:8]
        if not words:
            return "Generated Podcast"
        return " ".join(words).strip(".,:;!?").title()

    def _truncate(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return f"{text[:max_chars].rstrip()}..."
