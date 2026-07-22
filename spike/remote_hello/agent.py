"""Spike: hello agent to be served over A2A. Throwaway — dies once the real
supplier lands (iters 1-2). Exists only to confirm the pinned ADK's A2A channel."""

import os

from google.adk.agents import Agent


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set (see .env.example)")
    return value


root_agent = Agent(
    name="hello_supplier",
    model=_env("MODEL_FLASH"),
    description="Spike hello agent, reachable over A2A.",
    instruction="Reply with one short friendly greeting and nothing else.",
)
