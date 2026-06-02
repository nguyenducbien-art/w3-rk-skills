# 3-Gate Workflow (A → B → C)

> Three STOP points that prevent the two classic failures: missing a button, or testing the
> wrong controller. Each gate is a contract: output the table, then continue. Gates A/B are
> output during analysis; Gate C just before saving the CSV.
>
> Why gates exist (lessons): confused two sibling controllers → inserted wrong DB rows
> (Gate A); button in func-mapping had no handler (Gate B); discovered missing patterns only
> after generating (Gate C).

---

## Gate A — UI Element Inventory (after reading controller + view)

Output one row per testable element:

```
## [GATE A] UI Element Inventory — <SCREEN_NAME> (screen_id=<X>)

| # | Type          | Name (JP)      | func / $scope fn | Modal codes | Requires selection | Max selection | .error() handler | Notes |
|---|---------------|----------------|------------------|-------------|--------------------|---------------|------------------|-------|
| 1 | button        | 〇〇ボタン     | $scope.someAction| Q003, I001  | yes                | 500 (<)       | createEModalByServerData | — |
| 2 | row-click     | 行クリック遷移 | $scope.toDetail  | —           | no                 | —             | — | navigates to /path |
| 3 | modal-display | エクスポート   | printModalExports| —           | —                  | —             | — | helper in template |
| 4 | counter       | {{ num_x }}    | dataBound        | —           | —                  | —             | — | updates on dataBound |
```

**Type values:** `button` / `row-click` / `modal-display` / `counter`.

**List ALL of:** every `$scope.xxx = function()` in the controller (incl. inherited from
BaseController), every PHP modal helper in the template, every `ng-click` row handler, every
`{{ num_* }}` counter. Mark filter-only buttons `filter-only — excluded`.

→ **STOP.** Confirm no `$scope` function is missing before continuing.

## Gate B — Func-Mapping Cross-Check

```
## [GATE B] Func-Mapping Cross-Check — <SCREEN_NAME> (screen_id=<X>)

### B-1 Matched (controller AND func-mapping)
| func (mapping) | $scope fn | is_display | Action |
### B-2 In func-mapping (is_display=1) but NOT in controller
| func | is_display | Risk → search parent controller / service |
### B-3 In controller but NOT in func-mapping
| $scope fn | Notes (filter-only / helper / should be added?) |
```

- Resolve every B-2 (search BaseController / shared service) before generating.
- B-3 filter-only is fine; others need a TC or an explicit exclusion reason.

→ **STOP.** Resolve all B-2 gaps before writing the CSV.

## Gate C — Coverage Audit (before save)

Cross-check the Gate A inventory against the CSV rows:

```
## [GATE C] Coverage Audit — <SCREEN_NAME> (screen_id=<X>)

| # | Gate A element | Type   | Expected patterns                | CSV №(s) | Status |
|---|----------------|--------|----------------------------------|----------|--------|
| 1 | 〇〇ボタン      | button | 選択なし, 成功, APIエラー, 確認 | 9,14,15  | ✅ |
| 2 | 行クリック遷移  | row-click | 成功（遷移）                  | 23       | ✅ |
```

- Each `button` must have all applicable patterns from `per-button-patterns.md`.
- Each `row-click` ≥ 1 navigation TC; each `modal-display` 1 "modal opens" TC; each `counter`
  1 display TC.
- Excluded buttons → `N/A — excluded`.

**🔴 Branch coverage (the #1 list-screen miss).** Output a SECOND table mapping **every row of the
analysis `Branches` table → its CSV TC №(s)**, or `DROPPED`:

```
| Branch | Condition → Outcome           | CSV №(s) | Status      |
|--------|-------------------------------|----------|-------------|
| B7     | update NG → server error      | 22       | ✅          |
| B11    | delete → in-use, can't delete | 24       | ✅          |
| B13    | taking no-IF → E030           | —        | ❌ DROPPED  |
```

Every `DROPPED` row must be generated before saving. **Only exception:** the `getCsv` / `doPrint`
**E022** (帳票タイプ未選択) and the cosmetic `読み込み中` / `Q015キャンセル` / `ダウンロード失敗`
branches — dropped per `mimosa-rules.md` §csv-report. The CSV/帳票 **E017 / E001** guard branches are
**now REQUIRED** (S3), as are all other branches (mutation NG, import/export no-interface → E030,
external-API errors, in-use-can't-delete) — each must become a TC.

→ **STOP.** No ❌ in either Gate C table before saving.

## §assume-all-enabled — W3 override: "assume all buttons enabled"

The func-mapping `is_display` column and the local DB seed are **NOT** the button ground-truth
for W3 (local seed ≠ stg; funcs may be inherited from BaseController). Generate TCs for **every
real button** of the screen — including ones currently `is_display=0` or not yet seeded locally.

- "Real" = the `func` exists in the screen controller **or** BaseController, and/or shows on stg.
- Determine the button set by: (a) stg UI → (b) `printToolButtons` + master `button_apis` (all
  rolls) → (c) grep BOTH the screen controller AND BaseController. Never trust the local
  `unit_button_apis` seed alone.
- Still never invent a button with no real `func`.
- For buttons hidden by default, the PRE-CONDITION adds `Run SQL:` to enable them — see
  `mimosa-rules.md` §setup-sql (JOIN via `screen_id`, never a hard-coded local id).

→ So in Gate A/C, treat hidden/un-seeded-but-real buttons as in-scope (not `excluded`).
