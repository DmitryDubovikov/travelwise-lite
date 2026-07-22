# Итерация 00 — каркас + спайк A2A-канала

> 🎯 Топология — продукт, приложение — фикстура. Existence-gate, не accuracy-gate.

## Цель
Зафиксировать пины (свежайшие stable `google-adk` / `a2a-sdk` / `pydantic`) и
подтвердить весь A2A-канал ADK на этих пинах **до любого доменного кода**:
`to_a2a()` → карта на well-known-пути → `RemoteA2aAgent` → хоп виден в логе
remote-процесса. Если API разошёлся со SPEC — узнать в первый час, а не в iter 2–3.

## 🧵 Красная нить
Из ROADMAP #0: «Пины зафиксированы, ADK-API подтверждён до домена». Де-рискинг
дифференциатора №1 (A2A): спайк прогоняет ровно тот канал, на котором держатся
итерации 2–3.

## Сиблинг-аналог
Спайк ≈ iter-0-каркасы сиблингов (uv-скелет + smoke до содержательного кода).
Сам хоп: `to_a2a()` ≈ FastAPI-обвязка, которую в LangGraph-мире пришлось бы
писать руками, чтобы выставить граф как сервис; `RemoteA2aAgent` ≈ ручной
HTTP-клиент + сериализация состояния, которые там же пришлось бы катать поверх
этой обвязки. Здесь обе стороны границы — по одной строчке фреймворка.

## Новая техника (и минимальный объём)
- **Пины стека** — `pyproject.toml` под `uv`: `google-adk==2.5.0` (+extra `a2a`),
  `a2a-sdk==1.1.2`, `pydantic==2.13.4`, python 3.13. После спайка — апгрейды
  только через DECISIONS.
- **Спайк-хоп** — `spike/` (throwaway, сносится когда реальные агенты займут
  место в iter 1–3): `remote_hello` (LlmAgent) → `to_a2a()` на `:8001`;
  `caller` — `root_agent = RemoteA2aAgent(SUPPLIER_CARD_URL)`. Никакого домена.
- **Каркас** — `.env.example` (ключ, конкретные model ids, порты,
  `SUPPLIER_CARD_URL`), `Makefile` (`check`, `spike-remote`, `web`),
  pytest-смок (импорты/версии/конструирование агентов — без LLM и сети).

## Done-gate (по факту существования)
- `make check` зелёный: pytest-смок без LLM/сети (пины импортируются, версии
  совпадают, spike-агенты конструируются, `to_a2a()` отдаёт ASGI-app).
- Карта remote-агента отдаётся `curl`-ом на well-known-пути.
- Хоп `RemoteA2aAgent` → remote виден в **логе remote-процесса** (запрос дошёл
  по протоколу; полный round-trip — при наличии `GEMINI_API_KEY`).
- `DECISIONS.md`: `TBD` сняты — фактические версии + конкретные model ids.
- Ревью-пайплайн чист (CRITICAL/BUG = 0).

## Шаги
1. `pyproject.toml` + `.python-version` + `uv sync`; пины как выше.
2. `.env.example`, `.gitignore` (+`.env`), `Makefile` (`check` / `spike-remote` / `web`).
3. `spike/`: `remote_hello` + `to_a2a()`-сервер, `caller` с `RemoteA2aAgent`;
   поднять remote, `curl` карты, прогнать хоп, проверить лог.
4. Снять `TBD` в DECISIONS.md (версии, python, model ids).
5. Ревью-пайплайн (general + constitution → аудитор → фиксы → `/simplify`).

## Вне scope
Домен целиком: никаких schemas/tools/planner/supplier — это iter 1–3. Никакого
eval. Никакой доводки промптов hello-агента — он умрёт после спайка.
