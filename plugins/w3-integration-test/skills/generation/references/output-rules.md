# Output Format & Structural Rules

> Format/structure rules for the CSV cells and files. Cell *wording* (non-tech, passive,
> screen_id, button labels, modals) → `writing-rules.md`. What sections exist → `test-categories.md`.

---

## 1. CSV format (the only CSV — bilingual, 11 columns)

```
№, 大分類, 中分類, 小分類, 正常/異常, PRE-CONDITION, 前提条件, STEPS, 実施内容, EXPECTED RESULT, 確認事項
```
- A **section-marker row** precedes each group: col A (№) = marker text (e.g. `1. 共通確認`), all
  other cols empty — exactly the shape of `references/example-589.csv`. `build_xlsx.py` detects
  these (col A not an integer) and renders them as section header rows; TC rows get the
  auto-number formula. Markers + when 7 vs 9 → `test-categories.md` §2.
- TC numbering is continuous 1..N (marker rows are not numbered).
- Modal codes (E001/I001/…) and screen names stay JP. Written by `scripts/build_csv.py`.

## 2. From CSV to Excel

`build_csv.py` emits the bilingual CSV from the Python tuples. The Excel deliverable is produced
separately by `build_xlsx.py` from that CSV, **only on request**, into its own IT-delivery
sub-folder `<alias> (screen_id=<X>)_QAテスト/` next to the CSV (created automatically). Working
files (CSV / build_csv.py / screen-analysis.md / sql) stay directly in the screen folder; the
Excel is isolated in the QAテスト sub-folder. Change the tuples → re-run build_csv → (re-run build_xlsx).
Full layout → `project-config.md` §2.

## 3. Column rules (hard checks)

- **1 action = 1 step — in PRE-CONDITION *and* STEPS.** Never bundle several actions in one
  numbered line. STEPS: "Click OK and wait for reload" → "Click OK." / "Observe the grid.".
  PRE-CONDITION: "On the [A] screen, without checking any row, click 「…」 to open [B]" →
  "1. On the [A] screen." / "2. Don't select any row." / "3. Click the 「…」 button." (drop the
  resulting screen/mode — that is an outcome, not a PRE action). Mirror EN/JP line-for-line.
  Wording detail → `writing-rules.md` §precondition. (generic Output Rule §1).
- **中分類 (col C) must not be blank when 小分類 (col D) is filled** (Output Rule §8). If 小分類
  has a value, 中分類 must carry the button/function name (Japanese).
- **No user actions in EXPECTED / 確認事項** (Output Rule §7). Actions (click/press/select)
  belong in STEPS. EXPECTED describes only what the tester *sees*.
  ❌ "After clicking ×, the modal closes." → ✅ "The modal is closed."
- **大分類 = feature name**, not 操作/表示 — see `test-categories.md` §3. (Drop any "Cat 1-8 only"
  self-check copied from old scripts.)

## 4. Forbidden literal terms in EXPECTED / 確認事項 (Output Rule §6)

These source-code tokens must never appear in an EXPECTED cell:
```
stopLoading()  startLoading()  .error()  $scope  $http  API call  handler  callback
createIModal   createEModal    createEModalByServerData   setLoading   dataBound
<any function/method name from source>
```
Replace with the visible UI state:
❌ "The indicator disappears (stopLoading() in the .error() handler)."
✅ "The loading indicator disappears."
(General technical→user-facing paraphrasing → `writing-rules.md` §non-tech.)

## 5. EXPECTED step numbering (map 1-to-1 with STEPS)

- **Every step has a matching result.** N steps → results numbered `1.`, `2.`, … `N.`
  (never skip a number, not even the first/middle).
- **One step, many results** → `1.1`, `1.2`, `1.3` (each sub-result on its own physical line — §6).
  **One step, one result** → flat `1.`.
- **Pure preparation step** (no observable result, e.g. "Wait for data to load") → `N. -`.
  A step with no outcome still gets `N. -`; do NOT jump straight to the next number.
```
STEPS:  1. Check 1+ rows.   2. Click the 「明細」 button.
EXPECTED: 1. -              2. The screen navigates to … (screen_id=Y).
```
- `build_csv.py`'s `verify()` enforces this via `_steps()`: STEPS and EXPECTED must share the
  **same set of top-level step numbers** — a `1.1`/`1.2` pair counts as its top-level step `1`, so a
  one-step-many-results TC passes (e.g. STEPS `1.` ↔ EXPECTED `1.1`,`1.2`). It does **not**
  auto-renumber; fix the tuples by hand until `verify()` prints `OK`.

## 6. Multiline cells & wrapping

- Multiline cells (PRE-CONDITION/前提条件/STEPS/実施内容/EXPECTED RESULT/確認事項): **every numbered
  AND sub-numbered item (`1.`, `2.`, `1.1`, `1.2`, …) sits on its OWN physical line**, `\n`-separated
  — never run `1.1 … 1.2 … 1.3 …` together on one line. **No double line breaks, no blank lines**
  inside a cell.
  - ❌ `1.1 An empty input form is displayed. 1.2 The 基本情報 section is expanded. 1.3 The dropdowns are blank.`
  - ✅ `1.1 An empty input form is displayed.\n1.2 The 基本情報 section is expanded.\n1.3 The dropdowns are blank.`
  - `build_csv.py`'s `verify()` warns when a physical line carries 2+ sub-numbers (`\d+\.\d+`).
- CSV written **UTF-8 with BOM** so Japanese opens cleanly in Excel (BOM bytes `EF BB BF`).

## 7. Code / comment language

Any code or file comment (in `build_csv.py`/`build_xlsx.py`, SQL files, etc.) is **English or
Japanese only — never Vietnamese.**

## 8. Pre-save self-check (must pass before saying "CSV ready")

- [ ] Bilingual CSV = 11 cols; a section-marker row precedes each group; numbering continuous 1..N.
- [ ] 大分類 = feature name (not 操作/表示, except the S1/S2-config/S5 exceptions).
- [ ] Every PRE-CONDITION (EN + JP) contains `(screen_id=X)` / `（screen_id=X）`.
- [ ] PRE-CONDITION & STEPS: one action per numbered line — no line cramming open+select+click; EN/JP mirror.
- [ ] Each numbered/sub-numbered item (`1.`/`2.`/`1.1`/`1.2`…) on its own physical line — no run-on `1.1 … 1.2 …`.
- [ ] Multi-field lists comma-separated, every field spelled out — no `送状備考1〜3` range, no `・` jam (`writing-rules.md` §enumerate).
- [ ] EXPECTED count = STEPS count, no skipped numbers; prep steps `N. -`.
- [ ] No forbidden literal terms (§4); no user actions in EXPECTED (§3).
- [ ] 中分類 not blank when 小分類 filled.
- [ ] S3 (バリデーション) holds 異常 cases only — every 正常 / boundary-PASS case is in S4.1 (`mimosa-rules.md` §s3-abnormal-only).
- [ ] Form/edit/create screen: register/update/delete success TC has a DB-persistence verify step in S4.1 (`mimosa-rules.md` §verify-db).
- [ ] Form/edit/create screen: a 2-browser concurrent-conflict TC in S4.1, EXPECTED derived from the real BE mechanism (`mimosa-rules.md` §concurrent-conflict).
- [ ] Form loaded by an id from a parent: direct-URL-access TCs (IDなし / 有効なID / 存在しないID), EXPECTED code-derived (`mimosa-rules.md` §direct-url-access).
- [ ] Form with collapsible sections: section-toggle TCs (全て開く / 全て閉じる / per-section ≫), not confused with grid 全画面表示/展開行 (`mimosa-rules.md` §form-accordion).
- [ ] CSV is UTF-8 BOM.
