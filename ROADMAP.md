# travelwise-lite — ROADMAP

> 🎯 **Цель:** минимальная демонстрация Google ADK — A2A-граница между двумя
> независимыми сервисами + встроенные оркестраторы + `adk web`. «Plus one
> framework», не новый столп резюме. Топология — продукт, приложение — фикстура.

Источник истины по **порядку и составу**. Правила — `CLAUDE.md`, что строим —
`SPEC.md`, почему — `DECISIONS.md`. Тонких спек и итерационных skills нет
(решение в DECISIONS: проект меньше одной итерации authwise).

Статусы: ⬜ todo · 🟦 in progress · ✅ done · ❌ отменено.

> Бюджет: **каркас (iter 0) + 4 содержательные + витрина = 6** — самый низкий
> потолок в семье (authwise 7, dossier 8, triagewise 9, policywise ~15). Это
> осознанно: новых «техник» ровно четыре (`ParallelAgent`, A2A-сервер,
> `RemoteA2aAgent` + `SequentialAgent`, `adk web`/`eval`) — по одной на итерацию,
> нарезать мельче нечего, укрупнять — терять границу A2A как отдельный шаг.
> Existence-gate, не accuracy-gate: качество планов путешествий — НЕ ворота.

| # | Ст. | Новое | 🧵 Красная нить | Скоуп | Verify |
|---|---|---|---|---|---|
| **0** | ⬜ | — *(каркас + спайк)* | Пины зафиксированы, ADK-API подтверждён до домена | uv-скелет, пины `google-adk`/`a2a-sdk`/`pydantic`, `.env.example` (ключ, model ids, порты, `SUPPLIER_CARD_URL`), Makefile; **спайк**: hello-агент → `to_a2a()` → `RemoteA2aAgent` → хоп в `adk web` на пиннутых версиях; фактические версии записаны в DECISIONS (снять `TBD`) | спайк-хоп виден; `make check` (pytest-смок, без LLM) зелёный |
| **1** | ⬜ | **ADK-агенты + `ParallelAgent`** | In-agent иерархия (диффер. №2) | supplier standalone: `supplier/schemas.py`, stub-tools, `SequentialAgent(ParallelAgent(flight, hotel), merge-код)`; state-ключи `flights`/`hotels`; тесты на стабы+merge (чистый Python) | локальный прогон возвращает валидный `SupplierOffer`; тесты зелёные без сети |
| **2** | ⬜ | **A2A-сервер + agent card** | Половина A2A-границы: supplier — отдельный сервис (диффер. №1) | `make run-supplier` (`:8001`); карта генерится фреймворком и отдаётся на well-known-пути; skill `get_offer` дёргается по протоколу | `curl` карты отдаёт JSON; протокольный вызов виден в **логе supplier-процесса** |
| **3** | ⬜ | **`RemoteA2aAgent` + `SequentialAgent`** | Вторая половина A2A: два процесса, вызов по карте, без импорта (диффер. №1) | planner: `parse` (`output_schema=TripRequest`, без tools) → `RemoteA2aAgent` (по `SUPPLIER_CARD_URL` из env) → `assemble`; `planner/schemas.py` (осознанный дубль) | e2e из двух процессов: «4 days in Lisbon in May» → собранный план; входящий запрос в логе supplier |
| **4** | ⬜ | **`adk web` (+ опц. `adk eval`)** | Встроенный тулинг вместо своего UI (диффер. №3) | оба агента дискаверятся в `adk web` (пакеты с `root_agent`); e2e-хоп из UI; опц. `trip.evalset.json` на 1–2 кейса | хоп: трейс в web **и** лог supplier; eval проходит (если делаем) |
| **5** | ⬜ | — *(витрина)* | Проект легибелен ревьюеру за 5 минут | README из DECISIONS: why ADK + honest counter-note (LangGraph/LangSmith), one-liner, run surface; чек-лист SPEC закрыт | все галки чек-листа SPEC стоят; свежий клон запускается по README при наличии free-ключа |

## Заметки

- **Rate-limit бюджет:** ≈4 LLM-вызова на запрос (Flash ~15 RPM, Flash-Lite ~30
  RPM на free tier) — живое демо ок; eval не гонять в цикле.
- **Правило среза:** сознательный потолок помечать `# tw-lite: <потолок> → <апгрейд>`.
- Итерации 0 и 5 — маленькие (~пол-вечера); 1–4 — по вечеру максимум. Итого 2–3
  вечера, как в DECISIONS.
