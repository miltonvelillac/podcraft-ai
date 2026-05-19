import os

from api_host.agents.script_generation.errors import ScriptGenerationConfigurationError
from api_host.agents.script_generation.langchain_generator import LangChainScriptGenerator
from api_host.agents.script_generation.mock_generator import MockScriptGenerator
from api_host.agents.script_generation.provider import ScriptGenerator
from api_host.config import load_project_env


def build_script_generator() -> ScriptGenerator:
    load_project_env()
    provider_name = os.getenv("SCRIPT_PROVIDER", "mock").strip().lower()

    if provider_name == "mock":
        return MockScriptGenerator()
    if provider_name == "openai":
        return LangChainScriptGenerator()

    raise ScriptGenerationConfigurationError(f"Unsupported SCRIPT_PROVIDER: {provider_name}.")
