# SPEC.md — travelwise-lite

What to build. Read `CLAUDE.md` for the governing rules first.

## Story

User: *"4 days in Lisbon in May."*

1. **planner-agent** parses the request into structured trip params.
2. Planner calls **supplier-agent** over **A2A**, passing those params.
3. Supplier fans out internally (parallel flight + hotel lookup), merges results,
   returns a structured offer.
4. Planner assembles a final human-readable plan from the offer.

Two owners, one boundary: the planner is "us"; the supplier is a stand-in for a
third-party provider we only know through its agent card. That asymmetry is why A2A
is real here and not a networked function call.

## Agents

### planner-agent (orchestrator, our side)
- Type: `SequentialAgent` wrapping three sub-agents:
  1. `parse` — `LlmAgent`, free text → `TripRequest` via `output_schema`
     (no tools on this agent — ADK forbids tools + `output_schema` together;
     here that's fine, parse has no tools).
  2. `delegate` — **`RemoteA2aAgent`** pointed at the supplier's agent card URL.
     This is the native ADK idiom: the framework does card handshake,
     serialization and the protocol call. **No hand-written A2A client.**
  3. `assemble` — `LlmAgent`: `SupplierOffer` → final plan text.
- Runs inside `adk web` (it needs no standalone service of its own).
- Knows the supplier only by `SUPPLIER_CARD_URL` from env. No import of supplier
  code, no hardcoded host/port.

### supplier-agent (specialist, "their" side)
- Honest shape (a bare `ParallelAgent` has no merge step):
  `SequentialAgent( ParallelAgent(flight-agent, hotel-agent), merge )`
  - `flight-agent` → tool `search_flights(destination, month, nights)`,
    writes to state key `flights`
  - `hotel-agent`  → tool `search_hotels(destination, month, nights)`,
    writes to state key `hotels`
  - `merge` — **deterministic code, not an LLM step**: reads `flights` + `hotels`
    from state, validates, emits one `SupplierOffer`. (Saves an LLM call, keeps
    the offer reproducible, and sidesteps the tools-vs-`output_schema` limit.)
- State-key contract is fixed: `flights`, `hotels` (via `output_key`). Parallel
  sub-agents share session state — distinct keys are what makes the fan-out safe.
- flight/hotel agents call tools, so they cannot use `output_schema`; structure is
  enforced by the merge step's validation instead.
- Exposes an agent card declaring one skill: `get_offer(TripRequest) -> SupplierOffer`.
  The card is generated and served by the framework (`to_a2a()` /
  `adk api_server --a2a`) at the well-known path — no hand-written card module.
- Runs as a **separate process / service** from the planner. This separation is the
  A2A demonstration — do not collapse them into one runner.

## Model map (rate-limit budget)

| Step | Model | Why |
|---|---|---|
| parse | Gemini Flash | one call, needs decent parsing |
| flight-agent, hotel-agent | Gemini Flash-Lite | fan-out; Flash-Lite has its own (higher) free-tier RPM pool |
| merge | — (no LLM) | deterministic code |
| assemble | Gemini Flash | one call, user-facing text |

≈ 4 LLM calls per user request. Free tier: Flash ~15 RPM, Flash-Lite ~30 RPM —
fine for a live demo; don't loop `adk eval` aggressively. Exact concrete model ids
are pinned in `.env` (never a `-latest` alias).

## A2A boundary (the thing that must stay honest)

- Planner ↔ supplier communicate **only** through the A2A protocol + agent cards.
- The supplier's internals (that it fans out in parallel, what tools it calls) are
  invisible to the planner. The planner sees a card and a typed skill.
- Contract between them = the `TripRequest` / `SupplierOffer` schemas (Pydantic),
  **duplicated deliberately** on each side (`planner/schemas.py`,
  `supplier/schemas.py`) — no `shared/` module. A shared import would quietly
  couple the two sides the protocol exists to decouple; two owners don't share a
  codebase. Drift is caught by Pydantic validation at the boundary. (Decision
  recorded in DECISIONS.md.)

## Data contracts (Pydantic, keep minimal, duplicated per side)

```
TripRequest:   destination: str, month: str, nights: int, travelers: int = 1
FlightOption:  carrier: str, price_usd: int, depart: str, return_: str
HotelOption:   name: str, price_usd_per_night: int, area: str, rating: float
SupplierOffer: flights: list[FlightOption], hotels: list[HotelOption]
```

## Stub tools (no I/O — hardcoded)

- `search_flights(...)` → 2–3 `FlightOption` dicts, fixed values.
- `search_hotels(...)`  → 2–3 `HotelOption` dicts, fixed values.
- Values can vary trivially by destination via a small dict lookup, but no network,
  no randomness that breaks reproducibility. These are fixtures, not logic.

## File tree (orientation, not law — ADK's `adk web` discovery convention wins)

`adk web` discovers agents as packages: each agent dir needs `__init__.py`
exposing `root_agent`, and `adk web` is pointed at the parent directory.

```
travelwise-lite/
  CLAUDE.md
  SPEC.md
  DECISIONS.md
  ROADMAP.md
  README.md                 # written last; DECISIONS.md is its seed
  pyproject.toml            # uv; pinned google-adk, a2a-sdk, pydantic
  .python-version
  .env.example              # GEMINI_API_KEY, model ids, ports, SUPPLIER_CARD_URL
  Makefile                  # run-supplier / web / eval
  planner/
    __init__.py             # exposes root_agent (adk web convention)
    agent.py                # SequentialAgent: parse -> RemoteA2aAgent -> assemble
    schemas.py              # planner's copy of the contract
  supplier/
    __init__.py             # exposes root_agent
    agent.py                # SequentialAgent(ParallelAgent(flight, hotel), merge)
    tools.py                # search_flights / search_hotels (stubs)
    schemas.py              # supplier's copy of the contract
  eval/
    trip.evalset.json       # optional: 1–2 cases for `adk eval`
```

No `a2a_client.py` (that's `RemoteA2aAgent`'s job), no `card.py` (cards are
generated and served by the framework), no `shared/` (contracts duplicated).

## Run surface (all $0, local)

```
make run-supplier     # supplier-agent as an A2A service on :8001 (card at /.well-known/…)
make web              # adk web on :8000 — the planner runs here; watch the A2A hop
make eval             # optional: adk eval against trip.evalset.json
```

Two processes total: the supplier service and `adk web` (which hosts the planner).
Ports and `SUPPLIER_CARD_URL` come from `.env` — nothing hardcoded.

One end-to-end demo: send "4 days in Lisbon in May" to the planner in `adk web`,
watch it parse → call supplier over A2A → supplier fans out in parallel → planner
returns the assembled plan. **Proof of the hop = the incoming request in the
supplier process log** (plus the trace in `adk web`) — verify in the log, not only
the UI.

## Where each differentiator shows up (checklist)

- [ ] A2A — two processes, supplier card served at the well-known path, protocol
      call between them; hop proven in the supplier log
- [ ] Sequential orchestrator — planner/agent.py
- [ ] Parallel orchestrator — supplier/agent.py (inside its SequentialAgent shell)
- [ ] Built-in tooling — `adk web` runs both; optional `adk eval`
- [ ] $0 — Flash/Flash-Lite + free key; stubs mean most runs barely need the model

## Build order (suggested, ~2–3 evenings; detail in ROADMAP.md)

0. **Spike first**: hello-agent → `to_a2a()` → `RemoteA2aAgent` → hop visible in
   `adk web`, on the pinned versions, *before any domain code*. ADK moves fast;
   if the API drifted from these docs, find out in the first hour. Record the
   working versions in DECISIONS.md.
1. Supplier schemas + stub tools. No LLM yet — pure Python, tested.
2. supplier-agent (`SequentialAgent(ParallelAgent, merge)`), callable locally.
3. Stand supplier up as an A2A service; card resolves at the well-known path.
4. planner-agent `SequentialAgent` with `RemoteA2aAgent`; end-to-end over two
   processes.
5. `adk web` for both; confirm the hop in the supplier log. Optional eval file.
6. README from DECISIONS.md.
