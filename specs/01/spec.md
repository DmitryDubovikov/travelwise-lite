# Итерация 01 — supplier standalone: `ParallelAgent` + детерминированный merge

> 🎯 Топология — продукт, приложение — фикстура. Existence-gate, не accuracy-gate.

## Цель
Ввести встроенные оркестраторы ADK на стороне supplier: `SequentialAgent(ParallelAgent(flight, hotel), merge)`.
Агент работает standalone (без A2A — это iter 2), фан-аут и слияние видны и протестированы.

## 🧵 Красная нить
Из ROADMAP #1: **In-agent иерархия (дифференциатор №2)** — supplier внутри себя
использует встроенный оркестратор `ParallelAgent`, обёрнутый в `SequentialAgent`.

## Сиблинг-аналог
`ParallelAgent` ≈ fan-out-ребро в LangGraph: там мы бы объявили две ноды, провели
рёбра из одной точки и вручную описали reducer для конкурирующих записей в state.
Здесь фан-аут — декларация: изоляция шагов через **разные state-ключи**
(`flights`/`hotels`), а «reducer» — наш merge-шаг в `SequentialAgent`-оболочке.
`SequentialAgent` ≈ линейный LangGraph-граф без ручных edges.

## Новая техника (и минимальный объём)
- **`ParallelAgent`** — ровно два суб-агента (`flight`, `hotel`), каждый:
  `LlmAgent` (Flash-Lite из `MODEL_FLASH_LITE`) + один stub-tool + `output_key`.
- **merge как кастомный `BaseAgent`** — детерминированный код (не LLM): читает
  `flights`/`hotels` из state, парсит/валидирует Pydantic-схемами, эмитит один
  `SupplierOffer` JSON. Парс-логика — чистая функция, тестируемая без ADK-рантайма.
- Переиспользуем: идиому пакета `__init__.py → root_agent` и `_env()` из спайка
  (env — лениво/внутри `agent.py`, чистые модули `schemas.py`/`tools.py` env не трогают).

## Done-gate (по факту существования)
- `uv run adk run supplier` на «Lisbon, May, 4 nights» возвращает валидный
  `SupplierOffer` (один live-прогон, ≈2 LLM-вызова).
- `make check` зелёный: тесты схем, стабов, merge и сборки агента — чистый Python,
  без LLM и сети.
- Ревью-пайплайн чист (CRITICAL/BUG = 0).

## Шаги
1. `supplier/schemas.py` — `TripRequest`, `FlightOption`, `HotelOption`, `SupplierOffer` (по SPEC, без расширений).
2. `supplier/tools.py` — `search_flights` / `search_hotels`: 2–3 фиксированных dict'а, вариация по destination через маленький lookup, ноль I/O.
3. `supplier/agent.py` + `supplier/__init__.py` — flight/hotel `LlmAgent`'ы (`output_key="flights"/"hotels"`), `ParallelAgent`, merge-`BaseAgent`, `root_agent = SequentialAgent(...)`.
4. `tests/test_supplier.py` — схемы, детерминизм стабов, merge (happy + мусорный вход), конструкция агента (monkeypatch env, без сети).
5. Ревью-пайплайн (general + constitution → аудитор → фиксы → `/simplify`).

## Вне scope
A2A-сервер и карта (iter 2), planner целиком (iter 3), `adk web`-дискавери обоих (iter 4).
Никакого третьего доменного концепта: никаких новых полей схем, суб-агентов, «умных» цен.
