# DECISIONS.md — travelwise-lite

Why the project is shaped this way. This is also the seed for the public README.

## Purpose

Add **Google ADK** to a portfolio that already has LangGraph and CrewAI projects
(policywise, dossier, triagewise, authwise). Scope is deliberately small: this is a
"plus one framework" signal, not another control-plane pillar. The bar is *credible
working familiarity with ADK*, shown in 2–3 evenings, at $0.

## Why ADK over LangGraph / LangChain here

The project is built around what ADK does **natively and LangGraph does by hand**,
so the framework choice is justified by the task, not by novelty-seeking:

- **A2A between independent agents.** The planner and supplier are separate services
  with different owners, talking over a protocol. LangGraph models a system as one
  graph in one process — there are no independent agents, only nodes sharing state.
  To get a real cross-owner boundary on LangGraph you'd hand-roll the transport that
  A2A is meant to provide natively. A cross-organization boundary is exactly the
  scenario ADK was designed for.
- **Hierarchy from built-in orchestrators.** The supplier's internal fan-out is a
  `ParallelAgent`; the planner is a `SequentialAgent`. These are declared, not wired
  as a graph of nodes/edges/state. Less boilerplate for standard agentic shapes.
- **Full-stack tooling out of the box.** `adk web` and `adk eval` come with the
  framework — no custom UI or harness to write for a demo.

Honest counter-note (kept in the README): where you need surgical state control,
human-in-the-loop pauses, or mature observability, LangGraph + LangSmith still win.
This project doesn't need those, which is *why* ADK is the right call **here**.

## Why the travel domain

A2A must be natural, not contrived. Travel makes the boundary obvious: a planner and
an airline/hotel supplier are self-evidently different owners — nobody imports an
airline's code; you call its service. That kills the "this is just a networked
function call" objection with zero explanation needed. It's a canonical A2A example,
which is a small negative (slightly familiar) but a large positive (instantly legible
to a reviewer).

## Why all three differentiators, not one

They nest instead of stacking, so the cost is ~1.5× one differentiator, not 3×:
one agent's *internals* are the hierarchy, *two* such agents talking are A2A, and
running them is the built-in tooling — for free. The result reads as "can build a
distributed multi-agent system on ADK" rather than "knows one ADK primitive."

The only real added cost over a single-agent demo is A2A: a second process, two agent
cards, and the protocol call between them. That's the ~1 extra day.

## Why $0 / stubs

- Model is Gemini Flash on the AI Studio free tier (no card, no billing). Dev traffic
  is tens of calls/day, far under free limits.
- Tools are hardcoded fixtures — most runs exercise the topology without even needing
  the model. The spend ceiling is effectively zero, by construction.
- Note (not used here): ADK's Gemini **Live** (voice/video) API is the one path that
  would leave the free tier — audio tokens bill separately and stream by duration.
  Deliberately excluded; this project is text-only on Flash.

## Architecture decisions (2026-07-22)

- **Name: `travelwise-lite`** (matches the repo directory; early drafts said
  "tripwise-lite").
- **A2A client = `RemoteA2aAgent`, not a hand-written client.** The supplier is
  declared as a sub-agent of the planner's `SequentialAgent` by card URL; the
  framework does the handshake, serialization and JSON-RPC. A hand-rolled client
  would fight the framework and weaken the very signal this project exists to
  send (ADK fluency). Same logic for agent cards: generated and served by
  `to_a2a()` / `adk api_server --a2a` at the well-known path — no `card.py`.
- **Schemas duplicated deliberately, no `shared/` module.** The story is two
  owners; two owners don't import each other's code. A shared Pydantic module
  would quietly re-couple the sides A2A decouples. At four tiny models the
  duplication cost is ~zero; drift is caught by validation at the boundary.
- **Merge is deterministic code, not an LLM step.** One fewer call against the
  free-tier RPM budget, a reproducible offer, and it sidesteps the ADK
  constraint that an `LlmAgent` can't combine tools with `output_schema`.
- **Model map:** Flash for parse/assemble, Flash-Lite for the fan-out sub-agents
  (separate, higher free-tier RPM pool). ≈4 LLM calls per request against
  ~15/~30 RPM free limits — comfortable for a demo, tight for aggressive eval
  loops, which we don't run.
- **Process: the siblings' iteration machinery, ported and adapted** (revised
  2026-07-22; the initial call was "ROADMAP only"). `/iterationStart N` /
  `/iterationClose N` skills plus the three review agents (general-reviewer,
  constitution-reviewer, review-auditor) are ported from deskwise/authwise and
  adapted to the ADK stack: reviewer rubrics enforce the A2A-boundary seams and
  the $0/free-tier contract; deskwise's "питоний аналог" learning device becomes
  a **sibling analog** (ADK concepts explained via LangGraph/CrewAI); explainers
  must carry an explicit "ADK vs LangGraph/CrewAI" contrast section — the
  project's whole value is framework fluency, so the contrast is the product of
  the docs. The RPM/RPD free-tier budget plays the role money played in the
  siblings' AI discipline.
- **Pinned working versions** (filled after the iter-0 spike):
  `google-adk == TBD`, `a2a-sdk == TBD`, `pydantic == TBD`, python `TBD`,
  models: `TBD` (concrete ids, never `-latest` aliases).

## Relation to the sibling -lite projects

Same spirit as the four before it — *the application is a fixture; the interesting
thing is the shape* — but a fraction of the size, on purpose. The siblings each build
a control plane over one abstraction (trajectory, orchestration, LLMOps, RAG). This
one has no control plane and makes no such claim: it's a compact ADK topology demo
that widens framework coverage. That smallness is the point, not a shortfall.

## README one-liner (draft)

> **travelwise-lite** — a Google ADK travel demo: a `SequentialAgent` planner
> delegating to an independent parallel-fan-out supplier over A2A, runnable in
> `adk web` at $0 on Gemini Flash. Adds a vendor-native framework and a distributed
> multi-agent topology alongside the LangGraph/CrewAI siblings.
