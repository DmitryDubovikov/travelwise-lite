"""Iter-0 smoke: pins hold and the spike constructs. No LLM, no network — ever."""

import importlib.metadata
import tomllib
from pathlib import Path

import google.adk
import pydantic
from dotenv import dotenv_values
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from starlette.applications import Starlette

ROOT = Path(__file__).resolve().parents[1]
# Same parser ADK itself uses to load .env at runtime.
ENV = dotenv_values(ROOT / ".env.example")


def _pinned(package: str) -> str:
    deps = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]
    for dep in deps:
        name, _, version = dep.partition("==")
        if name.split("[")[0].strip() == package:
            return version
    raise AssertionError(f"{package} is not pinned in pyproject.toml")


def test_installed_versions_match_pyproject_pins():
    assert google.adk.__version__ == _pinned("google-adk")
    assert importlib.metadata.version("a2a-sdk") == _pinned("a2a-sdk")
    assert pydantic.VERSION == _pinned("pydantic")


def test_card_url_uses_adk_well_known_path():
    url = ENV["SUPPLIER_CARD_URL"]
    assert url.endswith(AGENT_CARD_WELL_KNOWN_PATH)
    assert f":{ENV['SUPPLIER_PORT']}/" in url


def test_model_ids_are_concrete_free_tier():
    for key in ("MODEL_FLASH", "MODEL_FLASH_LITE"):
        model = ENV[key]
        assert "latest" not in model, f"{key} must be a concrete id, not an alias"
        assert "pro" not in model, f"{key} must stay on the free tier (never Pro)"
        assert "flash" in model


def test_spike_remote_builds_a2a_app(monkeypatch):
    monkeypatch.setenv("MODEL_FLASH", ENV["MODEL_FLASH"])
    # Deferred: the agent module reads MODEL_FLASH at import time.
    from spike.remote_hello.agent import root_agent

    app = to_a2a(root_agent, port=int(ENV["SUPPLIER_PORT"]))
    assert isinstance(app, Starlette)


def test_spike_caller_constructs_from_card_url(monkeypatch):
    monkeypatch.setenv("SUPPLIER_CARD_URL", ENV["SUPPLIER_CARD_URL"])
    # Deferred: the agent module reads SUPPLIER_CARD_URL at import time.
    from spike.caller.agent import root_agent

    assert root_agent.name == "hello_remote"
