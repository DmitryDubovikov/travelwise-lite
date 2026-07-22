# CLAUDE.md — travelwise-lite

Coding-agent constitution. Read this first, then `SPEC.md` for what to build,
`DECISIONS.md` for why, and `ROADMAP.md` for order and status. Keep this file
short; details live in the other three.

## What this is

The fifth `-lite` project. A minimal **Google ADK** multi-agent demo: a travel
**planner** agent that delegates to an independent **supplier** agent over the
**A2A protocol**. Its only job is to show working familiarity with ADK — it is a
"plus one framework" project, not a new résumé pillar.

The four siblings (policywise, dossier, triagewise, authwise) are LangGraph/CrewAI.
This one adds a vendor-native framework and a distributed multi-agent topology.

## The one rule that governs everything

**The topology is the product; the application is a fixture.**

All value is in the *shape* — A2A boundary, in-agent hierarchy, adk web/eval — not
in what the agents actually do. The travel domain is a backdrop. Tools return
hardcoded plausible data. Do not build real integrations, real search, real
parsing, or a custom UI. If a change makes the domain richer but the topology no
clearer, do not make it.

## What must be demonstrated (all three, see SPEC.md)

1. **A2A** — planner and supplier are two separate services, each with its own
   agent card. Planner calls supplier by protocol, never by import.
2. **In-agent hierarchy** — supplier uses a built-in ADK orchestrator
   (`ParallelAgent`) internally. Planner uses `SequentialAgent`.
3. **Built-in tooling** — both agents run and debug via `adk web`. No hand-written
   UI. Optionally one eval file.

## Hard constraints

- **$0 by default.** Model is Gemini Flash on the AI Studio free tier. Dev traffic
  is tens of calls/day — well inside free limits. No billing setup. No credit card.
- **Free tier only** — Flash / Flash-Lite. Never a Pro model (paid-only).
- **Tools are stubs.** `search_flights` / `search_hotels` return 2–3 fixed
  dictionaries. No HTTP, no live APIs, no scraping.
- **No custom frontend.** `adk web` is the interface. Building UI is out of scope.
- **Keep the domain tiny.** Two agents, a handful of sub-agents, stub tools. If you
  feel the urge to add a third domain concept, stop — that urge is the failure mode
  of the four sibling projects and is explicitly out of scope here.
- **Python + `uv`**, matching the sibling projects' tooling.
- **Pin everything that can drift — and pin the *newest stable*.** At the iter-0
  spike, take the latest stable `google-adk` / `a2a-sdk` / pydantic and pin them in
  `pyproject.toml`; exact concrete model ids (never a `-latest` alias) in one place
  (`.env`). This project is a *current*-framework-fluency signal — don't build on a
  stale ADK, and don't follow tutorials written for older versions. After the spike:
  no mid-project upgrades unless a real blocker forces one (record it in
  DECISIONS.md). Record the actual working versions in `DECISIONS.md`.
- **Tests never call the model.** pytest/CI covers pure Python only: schemas, stub
  tools, the deterministic merge, card resolution. The LLM end-to-end run is a
  manual demo, not a CI gate. No cassettes here — that's the siblings' territory.
- **ADK conventions beat the file tree.** `adk web` discovery layout (agent package
  with `__init__.py` exposing `root_agent`) wins over any tree sketched in SPEC.md.
- **Planner discovers supplier only via `SUPPLIER_CARD_URL` (env).** No hardcoded
  host/port in code; ports live in `.env.example` and the Makefile.

## Definition of done

- `planner-agent` and `supplier-agent` start as separate A2A services.
- Planner resolves a natural-language trip request, calls supplier over A2A, and
  returns an assembled plan.
- Supplier internally fans out (`ParallelAgent`) over stub flight/hotel sub-agents.
- Both agents load in `adk web`; the A2A call is visible end to end. Proof of the
  hop = the incoming request in the **supplier process log** plus the trace in
  `adk web` — verify in the log, not only in the UI.
- README states, in a few honest sentences, why ADK over LangGraph/LangChain here.
- Everything runs locally at $0 with a free Gemini key.

## Non-goals

Real bookings. Persistence. Auth. Observability/eval control planes (that's the
siblings' territory — do NOT rebuild it here). Deployment to GCP/Vertex. Anything
that turns a 2–3 evening demo into a platform.
