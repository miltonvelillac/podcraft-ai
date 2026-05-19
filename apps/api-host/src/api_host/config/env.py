from pathlib import Path

from dotenv import load_dotenv


def load_project_env(start: Path | None = None) -> None:
    project_root = _find_project_root(start or Path.cwd())
    load_dotenv(project_root / ".env")


def _find_project_root(start: Path) -> Path:
    for path in (start.resolve(), *start.resolve().parents):
        if (path / "pyproject.toml").exists():
            return path

    raise RuntimeError("Could not locate project root.")
