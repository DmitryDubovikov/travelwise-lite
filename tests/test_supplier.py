"""Iter-1: supplier standalone — schemas, stub tools, deterministic merge, wiring.
No LLM, no network — ever."""

import json

import pytest
from pydantic import ValidationError

from supplier.merge import build_offer
from supplier.schemas import FlightOption, HotelOption, SupplierOffer, TripRequest
from supplier.tools import search_flights, search_hotels
from tests.conftest import ENV


def test_trip_request_defaults():
    request = TripRequest.model_validate({"destination": "Lisbon", "month": "May", "nights": 4})
    assert request.travelers == 1


def test_stub_tools_return_valid_options():
    flights = search_flights("Lisbon", "May", 4)
    hotels = search_hotels("Lisbon", "May", 4)
    assert 2 <= len(flights) <= 3
    assert 2 <= len(hotels) <= 3
    for option in flights:
        FlightOption.model_validate(option)
    for option in hotels:
        HotelOption.model_validate(option)


def test_stub_tools_are_deterministic_and_fall_back():
    # Same destination (any casing/spacing) -> same fixture; unknown -> default.
    assert search_flights("Lisbon", "May", 4) == search_flights("  lisbon ", "June", 2)
    assert search_hotels("Lisbon", "May", 4) == search_hotels("LISBON", "May", 4)
    assert search_flights("Osaka", "May", 4) == search_flights("Reykjavik", "July", 7)
    for option in search_hotels("Osaka", "May", 4):
        HotelOption.model_validate(option)


def test_merge_builds_offer_from_state_texts():
    offer = build_offer(
        json.dumps(search_flights("Lisbon", "May", 4)),
        json.dumps(search_hotels("Lisbon", "May", 4)),
    )
    assert isinstance(offer, SupplierOffer)
    assert offer.flights[0].carrier
    assert offer.hotels[0].rating > 0


def test_merge_strips_markdown_fence():
    fenced = "```json\n" + json.dumps(search_flights("Lisbon", "May", 4)) + "\n```"
    offer = build_offer(fenced, json.dumps(search_hotels("Lisbon", "May", 4)))
    assert len(offer.flights) == 3


def test_merge_rejects_garbage():
    hotels_ok = json.dumps(search_hotels("Lisbon", "May", 4))
    with pytest.raises(ValueError):  # missing state key — fan-out did not run
        build_offer(None, hotels_ok)
    with pytest.raises(ValueError):  # not JSON at all (JSONDecodeError is a ValueError)
        build_offer("here are your flights!", hotels_ok)
    with pytest.raises(ValueError):  # JSON but not an array
        build_offer('{"flights": []}', hotels_ok)
    with pytest.raises(ValidationError):  # array of wrong shape
        build_offer('[{"wrong": "shape"}]', hotels_ok)


def test_supplier_agent_wiring(monkeypatch):
    model_id = ENV.get("MODEL_FLASH_LITE")
    assert model_id, ".env.example must define MODEL_FLASH_LITE"
    monkeypatch.setenv("MODEL_FLASH_LITE", model_id)
    # Deferred: agent.py reads MODEL_FLASH_LITE at import time (adk discovery needs
    # a module-level root_agent).
    from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

    from supplier.agent import root_agent
    from supplier.merge import MergeAgent

    assert isinstance(root_agent, SequentialAgent)
    fan_out, merge = root_agent.sub_agents
    assert isinstance(fan_out, ParallelAgent)
    assert isinstance(merge, MergeAgent)
    by_key = {agent.output_key: agent for agent in fan_out.sub_agents}
    # The tool ↔ output_key pairing is the fan-out wiring being demonstrated.
    assert by_key["flights"].tools == [search_flights]
    assert by_key["hotels"].tools == [search_hotels]
    for agent in by_key.values():
        assert isinstance(agent, LlmAgent)
        assert agent.model == model_id
