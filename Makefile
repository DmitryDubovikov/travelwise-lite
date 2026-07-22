# Loads .env (if present) and exports everything to child processes.
-include .env
export

# Port defaults live here and in .env.example — never in code.
SUPPLIER_PORT ?= 8001
ADK_WEB_PORT ?= 8000

.PHONY: check spike-remote web

check:
	uv run pytest -q

# Spike: hello agent served as an A2A service (card at /.well-known/agent-card.json)
spike-remote:
	uv run python -m spike.server

# adk web over the spike agents (the caller's A2A hop is visible here)
web:
	uv run adk web spike --port $(ADK_WEB_PORT)
