# AI Fleet Commander — Repository Audit Report

**Date:** 2026-07-17
**Branch:** `backend-development`
**Scope:** Read-only audit. No code was changed.

---

## 1. Repository Overview

```
AI-Fleet-Commander/
├── backend/        17 Python files (engines, guards, main)
├── bots/
│   └── bots/       4 bot files  ← nested duplicate folder (see §2)
├── config/         settings.py (EMPTY)
├── deployment/     README only (empty)
├── docs/           17 numbered docs + README
├── examples/       2 examples + README
├── knowledge/      10 rule files
├── memory/         README only (empty)
├── prompts/        11 prompt files
├── schemas/        9 JSON schemas
├── strategies/     README only (empty)
└── tests/          README only (empty — no tests exist)
```

23 Python files total. All 23 pass syntax check (`py_compile`).

---

## 2. Duplicate Folders

### 🔴 `bots/bots/` — nested duplicate (main structural issue)

Bots live in `bots/bots/` instead of `bots/`. This forces awkward imports like:

```python
from bots.bots.trend_bot import TrendBot   # backend/main.py:1
```

Also, `bots/` itself has **no `__init__.py`** — only `bots/bots/__init__.py` exists. It works today only because of Python 3 namespace packages, but it is fragile and confusing.

**Recommendation (for later):** move the 4 bot files up one level to `bots/` and update the 4 imports in `backend/main.py`.

### Other duplicates
- **Duplicate commits:** `5d86ddd` and `f9cfdf4` are both titled "backend: Build Strategy Engine v1" (harmless, history only).
- **Duplicated logic:** `MarketEngine.is_safe_market()` and `MarketGuard.should_pause()` contain the **same hardcoded list** of dangerous regimes (`FLASH_CRASH`, `BLACK_SWAN`, `EXTREME_VOLATILITY`) in two places. Should live in one config.

---

## 3. Import Check

Import test results (actually executed, read-only):

| Module | Result |
|---|---|
| `backend.main` | ⚠️ Imports succeed, **but the whole demo runs at import time** (module-level code, no `main()` function, no `if __name__` guard) |
| `backend.capital_rotation_engine` | 🔴 **CRASHES on import** — `NameError: name 'OpportunityEngine' is not defined` |
| All other backend modules | ✅ OK |
| All 4 bots | ✅ OK |

### 🔴 Critical: `backend/capital_rotation_engine.py` is broken

The file structure is corrupted — it looks like a demo script was pasted onto the end of the file:

- **Line 59:** `from backend.opportunity_engine import ...` sits *inside* the `if __name__ == "__main__":` block (so it's skipped on import).
- **Line 60:** `from backend.capital_rotation_engine import CapitalRotationEngine` — the file **imports itself** (circular self-import).
- **Lines 63–114:** module-level demo code (`print`, engine calls) runs on every import, and references `OpportunityEngine` which was never imported at module level → **NameError whenever any other file imports this module.**

This is the single most serious bug in the repo. Fix: delete lines 59–114 or move them into a proper `if __name__ == "__main__":` block with correct imports at the top.

### Orphan modules (written but never imported/wired anywhere)
`commander.py`, `bot_ranking_engine.py`, `capital_rotation_engine.py`, `opportunity_engine.py`, `event_guard.py`, `kill_switch.py`, `market_guard.py`, `scheduler.py` — none are used by `main.py`. The "fleet command" layer exists as isolated demos only.

---

## 4. Backend Architecture Assessment

**Current state:** collection of small, independent demo classes. Each file has a class + `if __name__` demo block. There is **no integration layer** — `main.py` is a hardcoded demo script, not an application entry point.

Key observations:

1. **No orchestration.** `Commander` (the decision maker) is never connected to `MarketGuard`, `EventGuard`, `KillSwitch`, or the bots. The architecture described in `docs/01_System_Architecture.md` is not yet reflected in code.
2. **`main.py` has module-level side effects** — importing it runs the entire demo. Needs a `main()` function.
3. **Naming inconsistency:** `OpportunityEngine` uses `BOT_1`…`BOT_11` hardcoded weight keys, while `main.py`/bots use `TrendBot`, `ScalperBot`, etc. The two naming schemes never connect — `calculate_opportunity("TrendBot", ...)` would raise `KeyError`.
4. **Hardcoded values everywhere** (risk %, capital, regime lists, bot weights) while `config/settings.py` exists but is **empty** — nothing reads from it.
5. **No persistence:** `MemoryEngine` is an in-memory list; the `memory/` folder is unused. Everything is lost on restart.
6. **No error handling, no logging, no type hints, no docstrings** anywhere in backend.
7. **Formatting:** excessive blank lines between every statement (roughly doubles file length); inconsistent style across files.
8. **`datetime.utcnow()`** in `market_engine.py` is deprecated in Python 3.12+ — should be `datetime.now(timezone.utc)`.

---

## 5. Missing Files

| Missing | Impact |
|---|---|
| 🔴 `.gitignore` | `__pycache__/` folders are showing as untracked and can get committed |
| 🔴 `requirements.txt` | No dependency declaration (currently stdlib-only, but needed before any real feature) |
| 🟡 `bots/__init__.py` | Package is implicit/namespace-only; fragile imports |
| 🟡 Tests — `tests/` has only a README | Zero test coverage |
| 🟡 `config/settings.py` is empty | Config layer exists in name only |
| 🟡 `backend/bot_manager.py` is empty (0 bytes) | Placeholder committed with no content |
| 🟡 `backend/data_feed.py` is empty (0 bytes) | No market data source exists — `MarketEngine` values are manual inputs |
| 🟢 `docs/14_...` missing from docs/ | Not a bug — `14_Master_Claude_Prompt.md` lives in `prompts/`, but numbering split across folders is confusing |
| 🟢 `LICENSE` | Optional |

Also uncommitted work: 5 modified + 18 untracked files sitting on `backend-development` — worth committing in logical chunks once the above is decided.

---

## 6. Priority Summary

| # | Issue | Severity |
|---|---|---|
| 1 | `capital_rotation_engine.py` crashes on import (self-import + pasted demo code) | 🔴 Critical |
| 2 | `bots/bots/` nested duplicate folder + missing `bots/__init__.py` | 🔴 High |
| 3 | No `.gitignore` (`__pycache__` at risk of being committed) | 🔴 High |
| 4 | `main.py` runs everything at import; no `main()` entry point | 🟡 Medium |
| 5 | Bot-naming mismatch (`BOT_8` vs `TrendBot`) breaks OpportunityEngine integration | 🟡 Medium |
| 6 | 8 orphan modules not wired into anything | 🟡 Medium |
| 7 | Empty placeholders: `settings.py`, `bot_manager.py`, `data_feed.py` | 🟡 Medium |
| 8 | Duplicated dangerous-regime list; hardcoded values vs empty config | 🟢 Low |
| 9 | No tests, no logging, no docstrings, deprecated `utcnow()` | 🟢 Low |

**No code was modified during this audit.** Only this report file was created.
