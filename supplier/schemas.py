"""Supplier's copy of the boundary contract (TripRequest in, SupplierOffer out).

Deliberately duplicated with the planner's copy — no `shared/` module: two owners
don't share a codebase; drift is caught by validation at the A2A boundary
(DECISIONS.md).
"""

from pydantic import BaseModel


class TripRequest(BaseModel):
    destination: str
    month: str
    nights: int
    travelers: int = 1


class FlightOption(BaseModel):
    carrier: str
    price_usd: int
    depart: str
    return_: str


class HotelOption(BaseModel):
    name: str
    price_usd_per_night: int
    area: str
    rating: float


class SupplierOffer(BaseModel):
    flights: list[FlightOption]
    hotels: list[HotelOption]
