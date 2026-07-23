# Demo 01 — supplier standalone: фан-аут + детерминированный merge

Весь прогон доказывает одно утверждение: **внутри одного агента работает
задекларированная иерархия ADK** — `SequentialAgent(ParallelAgent(flight, hotel),
merge)`: две LLM-ветки одновременно заполняют свои ключи state, а
детерминированный merge-шаг превращает их в валидный `SupplierOffer`. За
пределами демо это дифференциатор №2 проекта (in-agent иерархия): то, что в
LangGraph собиралось бы из нод, рёбер и reducer-а, здесь — одна декларация
дерева, и она реально исполняется, а не только конструируется в тестах.

Все команды выполняются из корня репо: `/Users/dd/projects/pet/travelwise-lite`.
Нужен `.env` (одноразово): `cp .env.example .env`, для шага 3 в нём должен быть
настоящий бесплатный ключ — получить на https://aistudio.google.com/apikey и
заменить им значение `GOOGLE_API_KEY=`.

## 1. Смок-тесты без модели

**Что этим доказываем:** вся чистая логика итерации — схемы, детерминизм стабов,
merge (happy-path и мусорные входы) и дерево агентов — закрыта тестами, которые
не зовут ни Gemini, ни сеть; «зелёно» не стоит ни одного RPM.

```bash
make check
```

Ожидаемо: `12 passed` (5 смоков итерации 00 + 7 новых из
`tests/test_supplier.py`; предупреждения `DeprecationWarning` про
`SequentialAgent`/`ParallelAgent` → `Workflow` — норма, см. learnings).

## 2. Стабы — фикстуры с фолбэком (вспомогательная проверка)

**Что этим доказываем:** тулы — это hardcoded-фикстуры без I/O ($0-контракт
CLAUDE.md): незнакомый город не ломает поиск, а падает на дефолтный набор.
Проверка white-box (импорт внутренностей), поэтому — только дополнение к живому
шагу 3.

```bash
uv run python -c "
from supplier.tools import search_flights
import json
print(json.dumps(search_flights('Osaka', 'May', 4), indent=2))"
```

Ожидаемо — дефолтный набор (Осаки в фикстурах нет):

```json
[
  {
    "carrier": "AirDemo",
    "price_usd": 350,
    "depart": "2026-05-04 08:00",
    "return_": "2026-05-08 20:00"
  },
  {
    "carrier": "BudgetWings",
    "price_usd": 210,
    "depart": "2026-05-04 05:45",
    "return_": "2026-05-08 23:15"
  }
]
```

## 3. Живой прогон иерархии ⚠️ live, жжёт free-tier RPM (2 вызова Flash-Lite)

**Что этим доказываем:** дерево исполняется по-настоящему: обе ветки развилки
зовут свои тулы и пишут в state, merge собирает из state проверенный оффер. Сам
факт появления строки `[merge]` — доказательство Pydantic-валидации: при
невалидных данных `build_offer` бросает исключение, и строки бы не было.

```bash
set -a; . ./.env; set +a; echo "Lisbon in May, 4 nights" | uv run adk run supplier
```

Ожидаемо — три ответа подряд (сам артефакт, не только код возврата): эхо обеих
веток и финальный оффер от merge:

```
[flight_agent]: [{"carrier": "TAP Air Portugal", ...}, {"carrier": "Ryanair", ...}, {"carrier": "Lufthansa", ...}]
[hotel_agent]: [{"name": "Alfama Boutique", ...}, {"name": "Baixa Central", ...}, {"name": "Belém Riverside", ...}]
[merge]: {"flights":[{"carrier":"TAP Air Portugal","price_usd":420,"depart":"2026-05-04 09:15","return_":"2026-05-08 18:40"},{"carrier":"Ryanair","price_usd":180,...}],"hotels":[{"name":"Alfama Boutique","price_usd_per_night":140,"area":"Alfama","rating":4.6},...]}
```

(Живой Flash-Lite может переставить ключи или чуть иначе оформить эхо веток, а
сами ветки — прийти в любом порядке: `flight_agent` и `hotel_agent` исполняются
конкурентно, и между прогонами первым успевает то один, то другой — это мягкое
живое свидетельство фан-аута. Строка `[merge]` при этом нормализована
Pydantic-ом и содержит ровно три лиссабонских рейса и три отеля из фикстур.
Выйти из чата — `exit` или Ctrl+C.)

## Идемпотентность

Повторный `make check` — тот же `12 passed`. Повторный шаг 3 — тот же состав
`[merge]`-оффера (стабы детерминированы, merge — код): ещё 2 live-вызова, зато
проверяет, что накопившаяся сессионная база `supplier/.adk/session.db` (создаётся
`adk run`, в git не попадает — закрыта `.gitignore` паттерном `.adk/`) не влияет
на результат.
