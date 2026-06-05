# Review Checklist (audit dimensions)

> Each dimension maps to the shared rule it enforces (in
> `../generation/references/`). Audit the dumped TCs against the screen
> ground-truth + these rules. Flag findings as **Add / Modify / Delete**.

---

## 0. Suitability
- `screen_id` in the file (1.概要 N32) matches the requested screen; the file has TC rows under the
  5 sections. If not → stop, ask (see `review-workflow.md`).

## 1. Structure  (→ `test-categories.md`)
- 5 sections present with the right markers (default 7: 1/2/3/4/4.1/4.2/5; or 9 if S2 split).
- 大分類 (col B) = **feature name**, not abstract `操作`/`表示`/`検索` (except S1 / S2-config / S5).
- S1 = exactly the 4 verbatim TCs (page title / header / footer / menu).
- 中分類 not blank when 小分類 is filled.

## 2. Button coverage  (→ `gates-workflow.md` §assume-all-enabled + `per-button-patterns.md`)
- Every **real** button (from controller + BaseController + stg, assume-all-enabled) has TC(s).
  Flag any missing button. Flag any **invented** button (not on the screen / no real `func`).
- **「ご利用ガイド」 header button** (→ `mimosa-rules.md` §guide-button): if the screen has a
  `how_to_url` (button shown — check `SELECT how_to_url FROM screens WHERE id=X` / stg), expect ONE
  TC in S4.1: click 「ご利用ガイド」 → the screen's guide opens in a new browser tab. Flag **[Add]** if
  missing. If `how_to_url` is empty the button isn't rendered → there must be NO such TC (flag
  **[Delete]** if invented).

## 3. 🌟 Branch coverage — the #1 check  (→ `gates-workflow.md` Gate C)
- Build the screen's branch list (step 2). **Every branch must map to ≥1 TC** — list each DROPPED
  branch (e.g. mutation NG / server-validation, in-use-can't-delete, import/export no-interface →
  E030, external-API error / missing-token / not-installed).
- **Exception:** only the CSV/帳票 **E022** (帳票タイプ未選択) + cosmetic (`読み込み中`/`Q015キャンセル`/
  `ダウンロード失敗`) branches are dropped. The CSV/帳票 **E017 / E001** guards are **REQUIRED** now —
  flag them **[Add]** if missing (see §5).

## 4. Validation / BVA  (→ `mimosa-rules.md` §s3-abnormal-only, §BVA, §form-field-validation, §row-guards)
- **S3 = 異常 cases + the BVA boundary cluster** (§s3-abnormal-only). Flag a **non-boundary 正常 TC
  sitting in S3** → **[Modify]** move it to S4.1. But the **boundary triple (N-1/N/N+1) belongs
  together in S3** — flag **[Modify]** if boundary-PASS (N-1/N) cases were scattered to S4.1; pull
  them back to S3 next to the N+1 異常.
- Row-count limits: `MAX_SELECTION=200`→E024, `MAX_TRANSIT_SELECTION=500`→E028, operator `<`
  (n=limit PASS, n+1 FAIL). Boundary cluster **TOGETHER in S3**: N-1·N (正常) + N+1 FAIL (異常).
- Date-range filter (適用): the whole cluster in **S3** — N-1·N-day happy reloads (正常) + N+1-day FAIL
  + start>end + **3 partial/empty-input cases** (only-from / only-to / both-empty) (異常).
- Row guards: `選択なし → E001` only where the controller actually checks 0 rows (not blanket).
- **Form/edit screen**: per-field **異常** depth (→ §form-field-validation) — for each field by type:
  required-empty (**one TC per required field**) + all-required-empty + maxlength N+1 + numeric
  (**negative / zero** / out-of-range / non-numeric) + **invalid email** (if any) + **register-duplicate
  (既存コードと重複)** / edit-duplicate (unique key). Flag if S3 is shallow (only "required", missing
  maxlength / numeric / negative-zero / duplicate / email). The **boundary-PASS (上限ちょうど /
  下限ちょうど) cases stay in S3** with their 異常 counterpart (§BVA); only non-boundary accepted cases
  (valid email, **only-required-filled success**) belong in **S4.1**.
- **Date / numeric type depth** (§form-field-validation): a date field → wrong type (letters/special)
  + wrong format (not YYYY-MM-DD) → `E040「有効な日付を年月日（YYYY-MM-DD）形式で…」` (異常→S3); a numeric
  field also → `e` / exponent + special chars → `「…は半角数値で…」`. Flag **[Add]** if a date field has
  no type/format TC, or a numeric field no `e` / non-numeric TC.
- **S3 order** (§form-field-validation): single-field validation on top, cross-field / 全必須 / section
  validation at the bottom → flag **[Modify]** if mixed/confusing.
- **All-fields success** (§form-field-validation): a `全項目入力（必須＋任意）→ success` TC exists, not
  only the `only-required` one → flag **[Add]** if missing.

## 4b. Form/edit/create extras  (→ `mimosa-rules.md` §verify-db, §concurrent-conflict)
Only for form/edit/create screens (screen_type Edit-Form):
- **DB-persistence verify** — the register/update/delete **success** TC has a step verifying the
  record was created/updated/deleted in the DB (`[verify DB] Run SQL: SELECT … WHERE <natural key>`).
  Flag **[Add]** if the success TC has no DB-verify step. Flag **[Modify]** if the verify-SELECT step
  is missing the `[verify DB]` / `[DB確認]` prefix (§verify-db — it tags the step as a DB check, not a
  user action). (Display/list screens must NOT — see §7.)
- **Concurrent-conflict (2-tab / 2-browser)** — a TC interleaving two sessions ("1st tab / 2nd tab"
  = `1つ目/2つ目のタブ`, or two browsers) that edit the same record / register the same key at once
  (canonical shape in §concurrent-conflict). Flag **[Add]** if missing — don't mistake the tab-based
  TC for absent. Verify its EXPECTED matches the **real BE mechanism** (read Model/Observer/Controller):
  optimistic lock → exclusive-control error; no lock → last-write-wins; unique key → duplicate error.
  Flag **[Modify]** if it asserts a conflict error the BE doesn't produce, or claims overwrite when a
  lock exists, or blindly copies the no-lock "both succeed" outcome onto a screen that actually locks.
- **Direct URL access (deep-link)** — if the form **loads a record by an id from a parent screen**:
  3 TCs entering the URL directly — **no id** / **valid id** / **invalid id (not in DB)** (§direct-url-access).
  Flag **[Add]** if missing; verify each EXPECTED is code-derived (new-mode / redirect / error / record
  loads), not guessed. (The happy-path data flow still uses the nav flow, not a raw URL — §ids.)
- **Collapsible sections** — if the form has accordion sections (全て開く / 全て閉じる / per-section ≫,
  e.g. 469): toggle TCs in S4.1 (§form-accordion). Flag **[Add]** if missing. NOT the same as the
  list `展開ボタン→全画面表示` or grid `展開行` — flag **[Modify]** if mislabeled as those.
- **Master-select 「キャンセル」** (§nav-button-modal) — a 検索/選択 modal has **ONE** representative
  cancel TC (open → 「キャンセル」 → no selection applied, field unchanged). Flag **[Add]** if missing;
  but do NOT expect one per modal, and the `×` icon stays excluded.
- **Form S4.1 order** (§S4.1-order form override) — the field sub-flows (master-select / add-row /
  accordion) come **before** the 登録/更新 success group. Flag **[Modify]** if 登録 success sits above
  the field sub-flows.

## 5. CSV / 帳票  (→ `mimosa-rules.md` §csv-report)
- CSV (`getCsv`) + 帳票 (`doPrint`) each = **1 happy-path (S4.1) + the symmetric guard errors in S3**:
  CSV→E017 (権限なし) + CSV→E001 (選択なし); 帳票→E017 (利用可能帳票なし) + 帳票→E001 (選択なし).
  Flag **[Add]** if any of these 4 guard TCs is missing.
- Flag **[Delete]** only the cosmetic / deep ones if present: `読み込み中` / `Q015キャンセル` /
  `ダウンロード失敗` / `E022` (帳票タイプ未選択).
- 🔴 Do NOT confuse with interface import/export (`商品マスタ取込`/`出力`): those keep their own
  branches (modal + 実行 + no-interface→E030).

## 6. is_display vs available  (→ `mimosa-rules.md` §is_display-vs-available)
- グリッド列 `available=0` TC → wrong (no-op) → Delete.
- screen `available=0` TC → valid only if `screens.is_top=1`; else Delete.
- An `is_display=0` TC and an `available=0` TC with **identical EXPECTED** → the available=0 one is wrong.
- **List screen** S2 = `画面表示` + `グリッド列表示`; **form/edit screen** S2 = `画面表示` + `項目表示`
  (a `グリッド列表示` TC on a form is wrong → Modify to `項目表示`).

## 7. Wording  (→ `writing-rules.md`, `output-rules.md`)
- Every screen reference in PRE + EXPECTED carries `(screen_id=N)`.
- **Screen display name consistent + user-facing** (§nav-button-modal): the same screen is named the
  same way in sheet 1 (1.概要 N36), the file name, and every `[<name> (screen_id=X)]` reference — and
  it uses the page-title / open-button name. Flag **[Modify]** if a short `alias_nm` name disagrees
  with the fuller page title (e.g. refs say `出荷指示登録` but the ページタイトル TC says
  `W3 mimosa | 出荷指示登録・修正`) → unify to the fuller user-facing name.
- **PRE-CONDITION = one action per numbered line + a terse landing** (§precondition): flag a PRE line
  that crams open-screen + (don't-)select-rows + click into one line → **[Modify]** split it (EN/JP
  mirror). The navigation may end with one terse landing line `The [<target> (screen_id=Y)] screen is
  displayed.` — but flag **[Modify]** any landing that narrates the **mode/state** (`opens in
  new-registration / edit mode`, `(empty form)`, `(the form is pre-filled …)`, `the selected record
  is loaded`): drop that tail (the mode is set by the select / don't-select step; the loaded data is
  what STEPS/EXPECTED verify).
- **One outcome per line** (§expected): flag a long compound EXPECTED bundling ≥2 outcomes (error
  modal + loading hides + no save + stays on form) on one line → **[Modify]** split into sub-numbered
  lines (3.1 / 3.2 / …), one short sentence each.
- **Validation message verbatim** (§expected / §be-first): an S3 error EXPECTED must quote the real
  message 「…」 (+ E0xx), not a paraphrase like "a message indicating that X is required" → **[Modify]**.
- **Each numbered / sub-numbered item on its own physical line** (output-rules §6): flag a run-on
  `1.1 … 1.2 … 1.3 …` cell → [Modify].
- **Multi-field lists comma-separated, every field spelled out** (§enumerate): flag `・`/`&`/`;`-jammed
  lists, and any collapsed range like `送状備考1〜3` (must be `送状備考1 , 送状備考2 , 送状備考3`).
- Button labels = exact JP from `trans()` / `uba.nm` (no synonym / generic / English). `設定アイコン`
  → 「画面設定」; `展開ボタン` → 「全画面表示」.
- Modals described with title + message verbatim (form/検索 modal → label/input/columns/buttons).
- EXPECTED concrete + passive; 🚫 not "identical to AngularJS" / "same as Angular". **No DB-column
  verify for display/list TCs** — BUT a form/edit/create **success** TC DOES verify DB persistence (§4b / §verify-db).
- EXPECTED numbering maps 1-to-1 with STEPS (prep step → `N. -`, no skipped numbers).
- No forbidden literal tokens (`stopLoading`, `$scope`, `.error()`, `dataBound`, …); no user actions
  in EXPECTED; non-technical wording (no raw URL / function names / DB columns in steps/expected).

## 8. Performance (S5)
- ≥1 perf TC (30k); scenario matches how the screen receives data; 500 ids[] only if opted in.
