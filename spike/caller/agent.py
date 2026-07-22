"""Spike: caller side of the A2A hop. Knows the remote agent ONLY through its
card URL from env — no import of remote code, no hardcoded host/port."""

import os

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set (see .env.example)")
    return value


root_agent = RemoteA2aAgent(
    name="hello_remote",
    agent_card=_env("SUPPLIER_CARD_URL"),
    description="Spike: calls the hello agent over A2A by card URL.",
)
