"""Supplier agent: SequentialAgent(ParallelAgent(flight, hotel), merge).

The in-agent hierarchy differentiator: fan-out is a declared `ParallelAgent`
(isolation via distinct state keys `flights`/`hotels`), the "reducer" is a
deterministic merge step in the `SequentialAgent` shell. Env (model ids) is read
here at import time only because `adk run`/`adk web` discovery needs a
module-level `root_agent`; pure logic (schemas/tools/merge) imports without env.
"""

import os

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from supplier.merge import MergeAgent
from supplier.tools import search_flights, search_hotels


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set (see .env.example)")
    return value


def _lookup_agent(kind: str, tool, output_key: str) -> LlmAgent:
    """One fan-out branch: Flash-Lite + one stub tool + one state key."""
    return LlmAgent(
        name=f"{kind}_agent",
        model=_env("MODEL_FLASH_LITE"),
        description=f"Finds {kind} options for a trip request.",
        # Behavioral only: the parameter contract lives in the tool's signature
        # and docstring (what ADK sends the model) — don't restate it here.
        instruction=(
            f"Call {tool.__name__} exactly once with values from the trip request, "
            "then reply with ONLY the JSON array it returned — no prose, no markdown."
        ),
        tools=[tool],
        output_key=output_key,
    )


root_agent = SequentialAgent(
    name="supplier",
    description="Travel supplier: parallel flight + hotel lookup merged into one offer.",
    sub_agents=[
        ParallelAgent(
            name="fan_out",
            sub_agents=[
                _lookup_agent("flight", search_flights, "flights"),
                _lookup_agent("hotel", search_hotels, "hotels"),
            ],
        ),
        MergeAgent(name="merge"),
    ],
)
