# W3 Mimosa-Specific Rules

> The W3-specific decisions that override or extend the generic base. When the generic base
> and this file disagree, **this file wins** (it is the newest, resolved state).
> Facts (codes/constants/labels) → `mimosa-facts.md`. Wording → `writing-rules.md`.

---

## §is_display-vs-available — only `is_display` gates runtime; `available` does NOT

Ground truth (base branch): screen access (`getUnitScreen` / `getSubNavi` /
`verifyUrlAccess`) and grid columns (`getColumnInfo`) filter **only `is_display`**. `available`
is honored only in admin settings and the Next.js tab bar — it never locks/hides at AngularJS
runtime. Consequences for S2:

| Toggle | EXPECTED |
|---|---|
| screen `is_display=0` | screen not accessible (redirects `/top`). ✅ MANDATORY (every screen) |
| grid columns `is_display=0` | columns hidden. ✅ MANDATORY for list screens |
| **grid column `available=0`** (is_display=1) | **no-op both AngularJS & Next.js → DO NOT generate** |
| **screen `available=0`** (is_display=1) | AngularJS still shows/accessible; Next.js only hides from tab bar. Generate **only if `screens.is_top=1`** (otherwise it never appears in `getTabs` → no-op → drop). EXPECTED must say "AngularJS still displays/accesses", and must **differ** from the is_display=0 TC. |

🔴 If an `is_display=0` TC and an `available=0` TC have identical EXPECTED, the `available=0` one
is wrong — drop or fix it. Setup SQL sets the toggle for **all** columns/buttons of the
screen+roll (not one cell), to prove `is_display` is the gate.

🔴 **List vs form/edit screen — S2 differs:**
- **List screen** (has a grid): S2 = `画面表示` + `グリッド列表示` (column display via `unit_grid_columns`).
- **Form / edit screen** (no grid — an add/edit form opened from a parent list): S2 = `画面表示` +
  **`項目表示`** (input-field display), **NOT `グリッド列表示`** (a form has no grid). Name the
  field/section in 中分類/小分類. The field set comes from **this screen's own** field config —
  confirm the exact `screen_id` from the template/DB; **never borrow a sibling screen's id**.
  (Pass-1 bug on 430: emitted `グリッド列表示` with a borrowed `screen_id=467` — both wrong; should be `項目表示`.)

## §大分類 — column B = feature name

(Summary; full mapping in `test-categories.md` §3.) Col B = concrete feature/button label.
S2 config rows use `画面表示`/`グリッド列表示`/`ボタン表示`; no-data uses B`表示` 中`グリッド` 小`データなし`;
S5 uses B`応答時間`. 🚫 Never `操作`/`表示`(except no-data)/`検索`/`権限` as col B; never a section
name. If copying an old `build_csv.py`, audit col B — old files used `操作`/`表示`; drop any
"Cat 1-8 only" check in their `verify()`.

## §row-guards — 0-row → E001 is NOT a default

Verify from the controller before adding `選択なし → E001`:
- **DB-driven action button** with `if (checkedRowIds.length === 0) createIModal("E001")` → add
  `選択なし → E001` + `データなし → E001` in S3.
- **Toolbar button** (`toDetails`/`toHeaders`) that checks only MAX, not 0 → **no E001 TC**;
  instead an S4.1 behavior TC "navigate with 0 rows (empty ids[])" describing the real behavior.
- Any API mutation that fails server-side returns an error modal (every `HttpFactory.create*`
  has `.error(handleError)` → server NG always shows the server message). Never write "silent /
  no modal" for a failed mutation — EXPECTED = "error modal 「<server message>」 + loading hides + no save/nav".

## §s3-abnormal-only — S3 (バリデーション) holds 異常 cases only; 正常 → S4.1

🔴 `3. バリデーション確認` (S3) contains **only 異常 (rejection / error) cases** — the input the screen
must REJECT. Any **正常 (valid / boundary-PASS / accepted) case moves to `4.1 業務処理の確認` (S4.1)**
as a business-success TC. Consequences: a boundary triple SPLITS (N+1 FAIL → S3; N-1 / N PASS →
S4.1); a required-empty / over-limit / wrong-type case is 異常 → S3, while a valid submit at the
boundary is 正常 → S4.1. `build_csv.py`'s `verify()` warns on any 正常 TC placed under the `3.` marker.

## §BVA — boundary value analysis (split by status per §s3-abnormal-only)

For any action/filter with a MAX, cover the boundary at N-1 / N / N+1, but **split by section**:
- **S3 (異常):** `上限超過（(N+1)…）` → E024/E028 — the rejection (this is the validation TC).
- **S4.1 (正常):** `境界値 ― 上限ちょうど（N…）` (succeeds at the limit) + `境界値 ― 上限未満（(N-1)…）`
  (succeeds below) — business-success TCs (中分類 = the action, 小分類 = the boundary case).

Constants: `MAX_SELECTION=200`→E024, `MAX_TRANSIT_SELECTION=500`→E028. **Confirm the operator** in
code: `MAX < n` ⇒ n=MAX PASS (正常→S4.1), n=MAX+1 FAIL (異常→S3).

**Date-range filter** (list screen with `適用` + from/to date, `reload()` checks a range max, e.g.
`HISTORY_SEARCH_MAX_RANGE=90` → E027): same split —
- **S3 (異常):** `上限超過（(MAX+1)日）` → E027, `開始日 > 終了日`（dateDiff<0 → E027）, and the
  partial/empty-input cases (`終了日未入力` / `開始日未入力` / `開始日・終了日とも未入力` → click `適用`).
- **S4.1 (正常):** `上限ちょうど（MAX日）` + `上限未満（(MAX-1)日）` happy reloads (中=`適用`).

For the partial/empty cases write the **code-derived** outcome concretely (e.g. `reload()` calls
`getDateDiff(from,to)` — a null date breaks it → the period search does not run / the grid is
unchanged), **not** "same as AngularJS"; confirm on stg if the picker's empty behavior is unclear.

## §form-field-validation — input-field validation (form / edit screens)

For a screen with input fields (an add/edit form), cover **each field by its TYPE** — not one
required case. Read the BE (`$rules` in the API Controller + the `<Entity>Observer`) for the exact
limits, type, uniqueness and messages, and generate only the cases that apply to each field.
**Assign by status** (§s3-abnormal-only): 異常 (rejection) → **S3**; the matching 正常 (accepted /
boundary-PASS) → **S4.1**. 中分類 = field name (`商品コード`/`入荷限界設定日数`…), 小分類 = the case.

**Per required field — one TC EACH (never lump):**
- `必須 ― 未入力` — leave the field empty / **clear it then 登録** → required error 「<label>は必須項目です。」
  (異常 → S3). Generate a **separate** TC for **every** required field.

**Across fields:**
- `全必須項目未入力 ― エラー一覧` — leave ALL required fields empty → 登録 → error list (異常 → S3).
- `必須項目のみ入力（任意項目すべて空）` — fill only the required fields, leave every optional field
  empty → 登録 succeeds (正常 → S4.1).

**Per string field with `maxlength = N`** (N = that field's real limit, e.g. 100 / 500 — read `$rules`):
- `上限超過（N+1文字）` → length error (異常 → S3) · `境界値 ― 上限ちょうど（N文字）` → accepted (正常 → S4.1).

**Per numeric field** (use the field's real bounds):
- `負数（マイナス値）` — if negative not allowed → error (異常 → S3).
- `ゼロ（0）` — if 0 not allowed → error (異常 → S3); if allowed it is the `下限ちょうど` boundary (正常 → S4.1).
- `下限未満` / `上限超過（桁あふれ）` (e.g. int max 2147483647) → error (異常 → S3).
- `数値以外 ― 文字（文字列入力）` / `数値以外 ― 小数（整数項目）` → error / UI block (異常 → S3).
- `境界値 ― 下限ちょうど` / `上限ちょうど（N）` → accepted (正常 → S4.1).

**Per email field (if any):**
- `メール形式不正`（no `@`, bad format）→ format error (異常 → S3); a valid address rides the success TC (正常 → S4.1).

**Per unique field / key (ID / code):**
- `新規登録時 ― 既存コードと重複` — register a NEW record whose key already exists in the DB → duplicate
  error 「既に登録されています」 (異常 → S3). (Single-user pre-existing dup — distinct from the 2-tab race in §concurrent-conflict.)
- `編集時重複（他レコードの既存値に変更／自レコードは対象外）` → duplicate error (異常 → S3).

**Edit-mode edges (正常 → S4.1):** `編集時クリア（任意項目を空文字で更新）` · `部分更新（1項目のみ変更、他は保持）`.

🚫 Do NOT collapse to "required only" — the #1 miss on form screens; a form's S3 (異常 only) is
substantial. Generate only cases the field's type/constraints actually support (no email TC if no
email field, no 負数 TC if the field is a free string). Gold reference: `references/example-edit-430.csv`.

## §verify-db — form/edit/create screens add a DB-persistence verify (S4.1)

🔴 **Screen-type-scoped exception to "compare to AngularJS, not DB" (`writing-rules.md` §expected).**
For a **Create / Edit / form screen** (screen_type Edit-Form — a screen whose job is to write a
record), the **success TC** of the register/update/delete action gets an extra **DB-persistence
verify step** in S4.1 — a UI success modal alone doesn't prove the write landed. (List / Detail /
display screens keep the no-DB rule: functional equivalence vs AngularJS, no DB-column check.)

🔴 **Prefix the verify step.** A STEP that runs a check SELECT *after* submit is tagged so it reads
as a DB check, not a user action: EN `N. [verify DB] Run SQL: SELECT …`; JP
`N. [DB確認] SQLを実行: SELECT …`. (Setup SQL in PRE-CONDITION keeps the plain `Run SQL:` /
`SQLを実行:` — the `[verify DB]` / `[DB確認]` tag is ONLY for the post-submit verification step in STEPS.)

- **Create (登録/保存 → I001):** add a final step `[verify DB] Run SQL: SELECT … FROM <entity> WHERE <natural key>`
  → EXPECTED: a new row exists with the entered values (name the key fields).
- **Edit (更新 → I001):** → EXPECTED: the row is updated to the new values **and** fields not edited
  are preserved (verify both).
- **Delete:** → EXPECTED: the row is removed, or soft-deleted (`deleted_at` set) per the Observer.

SELECT by the business **natural key** (e.g. `商品コード`), never a hard-coded local id; this is a
read-only verify (no restore needed). The DB step is **added**, not a replacement — keep the UI
EXPECTED too (success modal / grid reload / navigation). `build_csv.py`'s `verify()` warns when
`SCREEN_TYPE` is form/edit/create but no S4.1 TC carries a verify `Run SQL: SELECT` step, and when a
STEP runs a verify SELECT without the `[verify DB]` / `[DB確認]` prefix.

Also add a concurrency-conflict TC → §concurrent-conflict.

## §concurrent-conflict — form/edit/create: a 2-browser concurrency TC (S4.1)

🔴 **Form/edit/create screens add a concurrent-conflict TC** — two browsers (= two users/sessions)
acting on the same record/key at once, to test data integrity under concurrency. **The EXPECTED is
NOT assumable — read the BE *and* FE deeply first** (the actual mechanism decides the outcome), then
write the code-derived result, never a guessed "conflict error":

- **Edit (更新):** Browser A and B both open the SAME record (same loaded state). A edits → saves
  (success). B (holding the stale copy) edits → saves. Outcome depends on the BE:
  - **Optimistic lock present** — the Model/Observer/Controller compares a version / `updated_at` /
    `lock_*` column on update → B is rejected with an exclusive-control error (quote the real
    message from `MessageController.php`, e.g. 「他のユーザーによって更新されています…」).
  - **No lock** (last-write-wins) → B silently overwrites A's change (lost update). Write THAT as the
    expected and flag it (usually a defect to confirm with the team) — do not invent a conflict error.
- **Register (新規登録):** A and B both open a new form and enter the SAME unique key (e.g. `商品コード`).
  A registers (success) → B registers → duplicate-key error (quote the real message, e.g.
  「既に登録されています」). This is the unique-constraint conflict.

**Determine the mechanism — read both layers, never guess:**
- BE: `app/Models/<Entity>.php` + `<Entity>Observer.php` — a version / `updated_at` / `lock_version`
  column compared on update? a unique index? what error is raised (errorCode + message)?
- BE: API `<Entity>Controller.php` `$rules` / the Service — any optimistic-lock guard before save?
- FE: the AngularJS save `$scope.fn` — does it send back the loaded version/`updated_at`, and how does
  it handle the conflict response (modal? force-reload?)? Confirm Next.js mirrors it.
- Modal text verbatim from `MessageController.php`.

Placement: **S4.1**, a named branch of the 登録/更新 action. Kind 異常 if it errors; 正常 (with a
defect note) if last-write-wins. PRE/STEPS describe the real 2-session flow, NOT raw API calls. Even
when there is no lock/constraint (both saves just succeed), **still write the TC to document the
last-write-wins behavior** — only skip if two concurrent actors on the same data is genuinely
impossible for this screen. `build_csv.py`'s `verify()` warns when `SCREEN_TYPE` is form/edit/create
but no S4.1 TC mentions a concurrency scenario.

**Canonical 2-tab shape** — interleave the two sessions ("1st tab / 2nd tab" = `1つ目/2つ目のタブ`; a
second browser is equivalent). On a form screen this is usually two TCs, 中分類 = the register button:

- *Edit conflict* (both edit the SAME existing record) — PRE selects **one** record in each tab:
  - PRE (EN): `1. In the 1st tab, open the [<alias> (screen_id=X)] screen.` / `2. In the 1st tab,
    select only one record.` / `3. In the 1st tab, click the 「<edit button>」 button.` / `4.–6.` repeat
    1–3 in the 2nd tab. (JP mirrors: `1つ目のタブで…` / `2つ目のタブで…`.)
  - STEPS (EN): `- On Tab 1:` `1. Modify valid values in all required fields.` `- On Tab 2:`
    `2. Modify the same valid values.` `3. (Tab 1) Click the 「登録」 button.` `4. (Tab 2) Click 「登録」.`
    `5. (Tab 1) Click 「OK」.` `6. (Tab 2) Click 「OK」.` — **Note: enter the SAME values in both tabs.**
- *Register conflict* (both create NEW) — identical, but PRE step 2/5 = `don't select any record`.

**EXPECTED = code-derived (the whole point):**
- **No lock / last-write-wins** (e.g. screen 488 届け先追加・編集 — no version check, no unique constraint
  on the entered values): BOTH 登録 return I001「正常に完了しました。」, both modals close and navigate back
  to the parent list — the 2nd write overwrites the 1st (state it, and flag the data-integrity risk).
- **Optimistic lock present**: the 2nd 登録 is rejected — exclusive-control error verbatim from
  `MessageController.php`; the modal stays / forces a reload.
- **Unique-key constraint** (register conflict): the 2nd 登録 fails with the duplicate error (e.g.
  「既に登録されています」).

🔴 The 2-tab example above shows the **no-lock** outcome — do NOT copy it onto a screen that actually
locks or has a unique key. Read BE + FE (`analyze-screen.md` step 6) to pick the real outcome.

## §filter — マイフィルタ / 並べ替え = a set of 4 TCs

Only when the view has a grid filter + `printModalMySearch()`. Generate exactly 4 in S4.1
(col B = feature name):

| # | 大分類 | Scenario |
|---|---|---|
| 1 | `マイフィルタ` | 初期表示 ― 保存済みフィルターなし (dropdown shows only 「フィルタなし」, no filter on load) |
| 2 | `マイフィルタ` | フィルター変更・削除（×）(filter a column → change condition → click × to clear) |
| 3 | `並べ替え` | フィルターあり ― 昇順/降順 (sort asc/desc — **sort IS tested**) |
| 4 | `フィルター + 並べ替え` | combined (both correct at once) |

EXPECTED concrete (filtered grid / sort order correct), not "identical to AngularJS", no DB
verify. Canonical = screen 589 (TC №19-22). 🚫 Do not revive the old 5-TC / 9-lifecycle / 列フィルタ
versions, and don't add `新しいフィルターを保存`.

## §csv-report — CSV / 帳票 = 1 happy-path (S4.1) + selection/permission error TCs (S3)

🔴 **Team standard: each output button gets its happy-path AND its guard errors** (confirm each
branch in the controller — `getCsv` / `_doPrint`; values verbatim from the repo's `MessageController.php`).

- **Happy-path** (1 TC each, Kind=正常, in **S4.1**):
  - **CSV** (中=`CSV`, 小=`成功 ― ファイル出力`): PRE opens screen + (if can_csv defaults 0)
    `Run SQL: UPDATE unit_screens SET can_csv=1 WHERE screen_id=<X> AND unit_roll_id=<test_user_roll>`.
    STEPS: check 1+ rows → click 「CSV」 (+ 「OK」 on Q015 if present). EXPECTED: file downloaded in the
    correct format (`<alias>_<YYYY>_<M>_<D>_<HH>_<MM>_<SS>.csv`). ServerSync → no I001.
  - **帳票** (中=`帳票`, 小=`成功 ― 帳票出力`): PRE opens screen + 帳票設定 configured
    (ユニット設定＞帳票設定＞帳票情報設定, ≥1 report available) + check 1+ rows. STEPS: check rows → click
    「帳票」 → select a report type → click 「実行」. EXPECTED: 帳票 selection popup shown → report exported.

- **Guard error TCs** (Kind=異常, in **S3**) — the symmetric 4-case set (verify reachability in code):
  - **CSV → E017** (中=`権限なし`): `can_csv=0` → E017 (checked **before** selection; PRE `Run SQL: … SET can_csv=0 …`).
  - **CSV → E001** (中=`選択なし`): `can_csv=1` + 0 rows checked → E001.
  - **帳票 → E017** (中=`利用可能帳票なし`): ≥1 row checked but no report available (`showModalReports` → `getUnitReports` empty) → E017.
  - **帳票 → E001** (中=`選択なし`): 0 rows checked (also fires when the grid has no record) → E001.

  **Cell shape (S3 error rows)** — `大分類 | 中分類 | 小分類 | 異常 | PRE | STEPS | EXPECTED`:
  - `CSV | 権限なし | (空)` → PRE: `Run SQL: … SET can_csv=0 …` + open. STEP: click 「CSV」.
    EXPECTED: error modal (E017), title+message **verbatim** from `MessageController.php`.
  - `CSV | 選択なし | (空)` → PRE: `Run SQL: … SET can_csv=1 …` + open + no rows checked. STEP: click 「CSV」.
    EXPECTED: error modal (E001).
  - `帳票 | 利用可能帳票なし | (空)` → PRE: open + no report configured + check 1+ rows. STEP: click 「帳票」.
    EXPECTED: error modal (E017).
  - `帳票 | 選択なし | (空)` → PRE: open + no rows checked. STEP: click 「帳票」. EXPECTED: error modal (E001).
  - 🚫 Do NOT mimic the CSV/帳票 rows of `example-589.csv` — that gold predates this standard (happy-path only).

- 🚫 Still skip the cosmetic/deep branches: `読み込み中` / `Q015キャンセル` / `ダウンロード失敗` /
  `成功 ― 閉じる ×`, and **E022** (帳票タイプ未選択, deep inside the publish modal) — unless explicitly requested.
- Exception: an **unwired** CSV/帳票 button (no `getCsv` / `doPrint` in the controller, e.g. 627) →
  keep a single no-op TC `操作なし(未実装ボタン)`; do not force a happy-path or errors.

## §ids — `ids[]` from a previous screen = navigation flow, not a raw URL

When a screen reads `ids[]` from `$location.search()`, test it as the **real navigation flow**:
PRE opens the upstream screen (with `(screen_id=X)`, ≥N rows); STEP tick N rows → click the
navigate button; EXPECTED navigates to the target, grid shows the N records. Find the upstream by
grepping `$location.path('/<route>').search({"ids[]": …})`. No upstream → don't generate an ids[]
TC. 🚫 Never `PRE/STEP = "Open the URL /…?ids[]=…"` (white-box) **for the happy-path data flow**.
Same for dates: test via the date picker + 「適用」, not `?from_date=…`. (Exception: the deep-link
robustness edge cases in §direct-url-access DO open the URL directly — that is the case under test.)

🔴 **Carry-over check.** When the navigate button passes search/filter state in the SAME
`$location.search({...})` (e.g. `from_date`/`to_date`, status, filters) — grep the
`$location.path(...).search({...})` payload — set a **non-default** value before navigating and make
EXPECTED verify that state is **carried over and preserved** on the target (e.g. the 表示期間 shown
on the detail matches the source), not merely that navigation occurred.

## §direct-url-access — form/edit screen reached by an item id: test direct deep-link entry

🔴 When a **form/edit screen loads ONE record by an id taken from a parent screen** (select an item →
click 追加・編集 → it opens carrying that id), ALSO test entering the page **directly by URL** (bypassing
the parent). Three TCs — **EXPECTED is code-derived: read FE routing + controller + the BE id-lookup,
never guess** (Next.js may guard/redirect differently from AngularJS — that is exactly what this catches):

1. **No id** (`/<route>` with no id param) → how the screen handles a missing id: new-registration
   (empty) form? redirect to the parent list? error? (Read how the controller treats an absent id.)
2. **Valid id** (`/<route>?<idparam>=<existing>`) → the record loads in edit mode, same as via the
   parent flow (deep-link works) → 正常.
3. **Invalid id** (`/<route>?<idparam>=<non-existent>`, not in DB) → error modal / empty form /
   redirect / not-found (read the BE lookup + how the FE handles an empty/❌ response).

Find the id param name + handling by grepping the FE route/controller (`$location.search()` /
`$routeParams` / the Next.js route segment) and the load API. Place in **S2 (表示確認)**, 中分類 =
`直接URLアクセス`, 小分類 = `IDなし` / `有効なID` / `存在しないID`; kind = 正常 for the valid-id load (and a
graceful new-mode/redirect), 異常 for an error outcome. PRE/STEP for THESE three **do** open the URL
directly (that IS the case under test) — the deliberate exception to §ids' "never a raw URL" (which
governs the happy-path data flow). `build_csv.py`'s `verify()` warns when `ID_FROM_PARENT=True` but no
direct-URL-access TC is present.

## §form-accordion — collapsible form sections (全て開く / 全て閉じる / per-section ≫)

Form/edit screens often group fields into **collapsible sections** (e.g. `基本情報` / `荷姿情報`), each
with a chevron (`≫`) toggle, plus **全て開く / 全て閉じる** buttons (screen 469 商品荷姿追加・編集 is the
canonical example). 🔴 These are **distinct from** the list `展開ボタン→全画面表示` and the grid `展開行`
sub-screen — don't conflate. When the form has them, add UI-toggle TCs in **S4.1** (中分類 = the control):

- **Per-section `≫` toggle** — click → that section collapses (its fields hide); click again → expands.
  One TC covering collapse + re-expand (one per section only if they behave differently).
- **全て開く** — click → ALL sections expand (every field visible).
- **全て閉じる** — click → ALL sections collapse (only the section headers remain).

Pure UI (no data change, no API) → EXPECTED compares the Next.js ↔ AngularJS show/hide behavior, no DB.
Read the view for the section list + toggle markup (the ng-click toggling a collapse class / the
全て開く・全て閉じる handlers) and quote the exact button labels verbatim. Skip if the form has no
collapsible sections. `build_csv.py`'s `verify()` warns when `HAS_COLLAPSIBLE_SECTIONS=True` but no
toggle TC is present.

## §guide-button — 「ご利用ガイド」 header button (only when `screens.how_to_url` is set)

The app header renders a 「ご利用ガイド」 button **only when `screens.how_to_url` is non-empty**
(`ViewHelpers.php`: `if (!empty($currentUnitScreen->screen->how_to_url))` → a button
`ng-click="openHowto('<how_to_url>')"`; `BaseController.openHowto(url)` = `window.open(url,
'_blank')`). So it is screen-specific and opens **that screen's** guide URL in a NEW browser tab.

- **Button shown** (the screen has a `how_to_url` — confirm via `SELECT how_to_url FROM screens
  WHERE id=<X>`, or it is visible on stg): add **one** TC (Kind 正常), 中分類 = `ご利用ガイド`, in
  **S4.1** with the 共通アイコン group (§S4.1-order #9):
  - STEPS `1. Click the 「ご利用ガイド」 button in the header.` (JP `1. ヘッダーの「ご利用ガイド」ボタンをクリックする。`)
  - EXPECTED `1. A new browser tab opens showing this screen's user guide (its how_to_url).`
    (JP `1. 新しいブラウザタブで本画面のご利用ガイド（how_to_url）が開くこと。`)
- **`how_to_url` empty** → the button is NOT rendered → **no TC** (don't invent it).
- Pure external navigation (new tab) — no DB write, no in-app modal. Set `HAS_HOWTO_GUIDE=True` in
  `build_csv.py` when the button is present so `verify()` checks the TC exists.

## §S4.1-order — strict group order

1. **初期表示** (short form — `writing-rules.md` §initial-display)
2. **Real mutation buttons** (full per-button: 読み込み中 → 成功(I001) → APIエラー → 確認モーダル if Q-code).
   This group also holds the **正常 cases moved out of S3** (§s3-abnormal-only): boundary-PASS
   (N-1 / N), and valid-input / boundary-maxlength success for the create/update action. **On a
   form/edit/create screen the success TC also adds a DB-persistence verify step** (§verify-db).
3. **マイフィルタ / 並べ替え** (4-TC, §filter)
4. **Navigation** (明細/一覧 button → row-click 詳細(小) variants)
5. **Date filter** (適用 reload — Mimosa-specific)
6. **CSV** → **帳票** (1 TC each, §csv-report)
7. **Sub-screen** (展開行 — placed last among features)
8. **共通アイコン** (last): `設定アイコン`→「画面設定」 (→画面設定（項目表示設定）画面へ遷移); `展開ボタン`→「全画面表示」
   (→全画面表示になる). Mandatory for screens with a table/grid. Don't reorder.
   (**Form screens** (no grid): instead, place the **collapsible-section toggles** here —
   全て開く / 全て閉じる / per-section `≫` — see §form-accordion.)
9. **「ご利用ガイド」** (only if `screens.how_to_url` is set — independent of grid/form): 1 TC, click →
   the screen's guide opens in a new browser tab. See §guide-button. Skip if no `how_to_url`.

## §perf — S5 performance

Default = 1 TC (`応答時間` / `画面応答時間`): load with 30,000 records → display completes +
pagination + search/period still responsive. Pick the scenario matching how the screen receives
data: (1) selects many records → 100+ rows; (2) one record with many child products → that record;
(3) form with no add-row → PRE 30k in DB, register smooth / grid loads acceptably.
**500 ids[] from a previous screen** is opt-in only (clear upstream flow, or user requests it).

## §setup-sql — local DB modifications

`unit_*` SQL (`unit_screens`/`unit_grid_columns`/`unit_button_apis`) is ALLOWED for setting up
config-driven TCs and CSV/帳票 permission tests, **but**:
1. Show the SQL preview to the user and wait for confirm before running (local DB only).
2. Restore (reverse UPDATE / DELETE) right after the user verifies.
3. Never `INSERT unit_button_apis` with a `func` that doesn't exist in the controller (crashes UI).
4. In generated PRE-CONDITION SQL: `Run SQL:` wording, JOIN via `screen_id` (master) + `uba.func`
   / `gc.cls` + `unit_roll_id = <test_user_roll>` placeholder — **never a hard-coded local id**
   (they are per-environment). Save all session SQL (setup/find/verify/restore) to
   `<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=<X>)/sql/test-data-sql.md` with purpose + restore for each block.

## §assume-all-enabled — button inventory

(Canonical definition in `gates-workflow.md` §assume-all-enabled.) Generate TCs for every real button, including
`is_display=0` / un-seeded-locally ones. Ground truth = controller + BaseController + stg UI, not
the local seed or func-mapping `is_display`. Enable hidden buttons via PRE-CONDITION setup SQL.
