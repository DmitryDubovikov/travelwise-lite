"""Stub search tools: hardcoded plausible fixtures, zero I/O (CLAUDE.md).

The (destination, month, nights) signature is the tool contract the LLM fills in
from the trip request; only `destination` varies the data — a dict lookup, not
logic. Docstrings double as the tool descriptions the model sees.
"""

_DEFAULT = "_default"

_FLIGHTS: dict[str, list[dict]] = {
    "lisbon": [
        {"carrier": "TAP Air Portugal", "price_usd": 420, "depart": "2026-05-04 09:15", "return_": "2026-05-08 18:40"},
        {"carrier": "Ryanair", "price_usd": 180, "depart": "2026-05-04 06:05", "return_": "2026-05-08 22:10"},
        {"carrier": "Lufthansa", "price_usd": 510, "depart": "2026-05-04 11:30", "return_": "2026-05-08 15:25"},
    ],
    _DEFAULT: [
        {"carrier": "AirDemo", "price_usd": 350, "depart": "2026-05-04 08:00", "return_": "2026-05-08 20:00"},
        {"carrier": "BudgetWings", "price_usd": 210, "depart": "2026-05-04 05:45", "return_": "2026-05-08 23:15"},
    ],
}

_HOTELS: dict[str, list[dict]] = {
    "lisbon": [
        {"name": "Alfama Boutique", "price_usd_per_night": 140, "area": "Alfama", "rating": 4.6},
        {"name": "Baixa Central", "price_usd_per_night": 95, "area": "Baixa", "rating": 4.2},
        {"name": "Belém Riverside", "price_usd_per_night": 175, "area": "Belém", "rating": 4.8},
    ],
    _DEFAULT: [
        {"name": "City Center Inn", "price_usd_per_night": 110, "area": "Center", "rating": 4.1},
        {"name": "Old Town Suites", "price_usd_per_night": 150, "area": "Old Town", "rating": 4.5},
    ],
}


def search_flights(destination: str, month: str, nights: int) -> list[dict]:
    """Search round-trip flight options to the destination for the given month and
    number of nights. Returns a list of flight option objects."""
    # Shallow copies: callers must not be able to mutate the module fixtures.
    return [dict(o) for o in _FLIGHTS.get(destination.strip().lower(), _FLIGHTS[_DEFAULT])]


def search_hotels(destination: str, month: str, nights: int) -> list[dict]:
    """Search hotel options at the destination for the given month and number of
    nights. Returns a list of hotel option objects."""
    return [dict(o) for o in _HOTELS.get(destination.strip().lower(), _HOTELS[_DEFAULT])]
