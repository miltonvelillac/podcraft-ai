from api_host.schemas.podcast_schemas import PodcastScript, PodcastStyle, PodcastTargetDuration


class ScriptAgent:
    """Internal script-generation agent used by the MCP host."""

    def generate_script(
        self,
        text: str,
        style: PodcastStyle,
        target_duration: PodcastTargetDuration,
    ) -> PodcastScript:
        normalized_text = " ".join(text.split())
        summary = self._truncate(normalized_text, max_chars=280)
        title = self._build_title(summary)
        intro = self._build_intro(style)
        duration_minutes = self._duration_minutes(target_duration)

        script = (
            f"{intro}\n\n"
            f"Today we are turning this source material into a clear podcast segment. "
            f"The main idea is: {summary}\n\n"
            "Let's break that down into practical takeaways, explain why it matters, "
            "and close with the key point listeners should remember."
        )

        return PodcastScript(
            title=title,
            script=script,
            estimated_duration_minutes=duration_minutes,
        )

    def _build_intro(self, style: PodcastStyle) -> str:
        intros = {
            PodcastStyle.EDUCATIONAL: "Welcome to PodCraft AI. In this episode, we will learn from the material step by step.",
            PodcastStyle.CONVERSATIONAL: "Welcome back. Let's talk through this topic in a simple, conversational way.",
            PodcastStyle.EXECUTIVE_SUMMARY: "Welcome to this executive briefing. Here are the key points you need to know.",
        }
        return intros[style]

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
