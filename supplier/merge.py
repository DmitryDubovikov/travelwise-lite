"""Deterministic merge: state {flights, hotels} -> one validated SupplierOffer.

Code, not an LLM step (DECISIONS.md): saves an RPM call, keeps the offer
reproducible, and sidesteps ADK's tools-vs-`output_schema` limit. The fan-out
sub-agents can't use `output_schema` (they hold tools), so structure is enforced
here by Pydantic validation instead. Pure parse logic is env-free and testable
without the ADK runtime.
"""

import json
import re
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from supplier.schemas import SupplierOffer

# tw-lite: tolerance closed at this one fence regex → the deeper fix is writing
# state from tool_context instead of parsing the LLM echo, but SPEC deliberately
# demonstrates the `output_key` channel; do not grow this tic-by-tic.
_MD_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$")


def _parse_options(raw: object, key: str) -> list:
    """LLM text from a state key -> list of option dicts.

    Tolerates a markdown code fence around the JSON array (a common LLM tic);
    anything else non-conforming raises — validation is this step's job.
    """
    if raw is None:
        raise ValueError(f"state key {key!r} is missing — fan-out did not run")
    if isinstance(raw, str):
        raw = json.loads(_MD_FENCE.sub("", raw.strip()))
    if not isinstance(raw, list):
        raise ValueError(f"state key {key!r} must hold a JSON array, got {type(raw).__name__}")
    return raw


def build_offer(flights_raw: object, hotels_raw: object) -> SupplierOffer:
    """Validate both fan-out results into one SupplierOffer (raises on bad input)."""
    return SupplierOffer(
        flights=_parse_options(flights_raw, "flights"),
        hotels=_parse_options(hotels_raw, "hotels"),
    )


class MergeAgent(BaseAgent):
    """Non-LLM sequential step: reads the fan-out's state keys, emits the offer JSON."""

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        offer = build_offer(ctx.session.state.get("flights"), ctx.session.state.get("hotels"))
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(role="model", parts=[types.Part(text=offer.model_dump_json())]),
        )
