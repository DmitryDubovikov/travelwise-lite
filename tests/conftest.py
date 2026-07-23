"""Shared test scaffold: repo root + the example env (same parser ADK uses)."""

from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
ENV = dotenv_values(ROOT / ".env.example")
