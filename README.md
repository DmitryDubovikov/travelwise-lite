# travelwise-lite

> A Google ADK travel demo: a `SequentialAgent` planner delegating to an
> independent parallel-fan-out supplier over A2A, runnable in `adk web` at $0 on
> Gemini Flash. Adds a vendor-native framework and a distributed multi-agent
> topology alongside the LangGraph/CrewAI siblings.

**Status: iteration 0 of 5** (skeleton + A2A spike; see `ROADMAP.md`). The full
showcase README lands at iteration 5 — until then, `DECISIONS.md` explains why
ADK, and `docs/iterations/` walks each closed iteration.

## Quickstart (as of iteration 00 — spike, not the travel domain yet)

Needs [uv](https://docs.astral.sh/uv/) and a free AI Studio key
(https://aistudio.google.com/apikey — no card, no billing):

```bash
uv sync
cp .env.example .env    # then put your key into GOOGLE_API_KEY=
```

## Make targets

| Target | What it does |
|---|---|
| `make check` | pytest smoke — pure Python, never calls the model or network |
| `make spike-remote` | spike hello agent as an A2A service on `:8001` (card at `/.well-known/agent-card.json`) |
| `make web` | `adk web` on `:8000` over the spike agents; the A2A hop is visible here |

The live walkthrough (card curl, protocol hop, log proof) is in
`docs/iterations/00/demo.md`.
