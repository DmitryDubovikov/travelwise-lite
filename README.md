# travelwise-lite

> A Google ADK travel demo: a `SequentialAgent` planner delegating to an
> independent parallel-fan-out supplier over A2A, runnable in `adk web` at $0 on
> Gemini Flash. Adds a vendor-native framework and a distributed multi-agent
> topology alongside the LangGraph/CrewAI siblings.

**Status: iteration 1 of 5** (supplier standalone: `ParallelAgent` fan-out +
deterministic merge; see `ROADMAP.md`). The full showcase README lands at
iteration 5 — until then, `DECISIONS.md` explains why ADK, and
`docs/iterations/` walks each closed iteration.

## Quickstart (as of iteration 01 — supplier agent, local only)

Needs [uv](https://docs.astral.sh/uv/) and a free AI Studio key
(https://aistudio.google.com/apikey — no card, no billing):

```bash
uv sync
cp .env.example .env    # then put your key into GOOGLE_API_KEY=
```

Talk to the supplier agent (parallel flight + hotel fan-out, merged into one
validated offer):

```bash
set -a; . ./.env; set +a; echo "Lisbon in May, 4 nights" | uv run adk run supplier
```

## Make targets

| Target | What it does |
|---|---|
| `make check` | pytest smoke — pure Python, never calls the model or network |
| `make spike-remote` | spike hello agent as an A2A service on `:8001` (card at `/.well-known/agent-card.json`) |
| `make web` | `adk web` on `:8000` over the spike agents; the A2A hop is visible here |

The live walkthroughs are in `docs/iterations/`: `00/demo.md` (card curl,
protocol hop, log proof) and `01/demo.md` (supplier fan-out + merge).
