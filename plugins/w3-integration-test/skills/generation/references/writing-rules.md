# Cell Wording Rules

> How to word PRE-CONDITION / STEPS / EXPECTED. Structural/format rules → `output-rules.md`.
> Fact lookups (modal text, button labels) → `mimosa-facts.md`.

---

## §precondition — screen_id on every reference + ONE action per numbered step

**(a) Every screen reference carries `(screen_id=X)`.** Many screens share an `alias_nm`, so the
screen_id disambiguates. Use:
- EN: `1. Open the [<alias> (screen_id=<X>)] screen.`
- JP: `1. 「<alias>（screen_id=<X>）」画面を開く。`

Applies to all PRE-CONDITION shapes (plain open / check-N-rows / setup-SQL / reference-other-TC).
Define `PRE_*` constants once in `build_csv.py` and reuse.

**(b) 🔴 ONE action per numbered step — do NOT cram a chain into one line.** The "1 action = 1
step" rule (`output-rules.md` §3) applies to PRE-CONDITION just as much as to STEPS. Split a
compound precondition — *open/land on a screen → (don't) select rows → click a button → land on the
target* — into separate numbered lines, one action each, and mirror EN and JP line-for-line.

❌ Crammed into one step:
> `1. On the [配送関連_配送業者サービスマスタ (screen_id=433)] screen, without checking any row, click the 「配送業者サービス追加・編集」 button to open the [配送関連_配送業者サービス追加・編集 (screen_id=434)] screen in new-registration mode (empty form).`

✅ One action per step + a terse landing line (apply to BOTH the EN and JP columns):

| EN (PRE-CONDITION) | JP (前提条件) |
|---|---|
| `1. On the [配送関連_配送業者サービスマスタ (screen_id=433)] screen.` | `1. 「配送関連_配送業者サービスマスタ（screen_id=433）」画面を開く。` |
| `2. Don't select any row.` | `2. いずれの行もチェックしない。` |
| `3. Click the 「配送業者サービス追加・編集」 button.` | `3. 「配送業者サービス追加・編集」ボタンをクリックする。` |
| `4. The [配送関連_配送業者サービス追加・編集 (screen_id=434)] screen is displayed.` | `4. 「配送関連_配送業者サービス追加・編集（screen_id=434）」画面が表示される。` |

- **DO state the landing** as its own terse step naming the target screen + its `(screen_id=Y)`, so
  the reader sees the test navigated there — but the landing line is just `The [<target>
  (screen_id=Y)] screen is displayed.`, nothing more.
- 🔴 **DROP the mode/state tail.** Never append `in new-registration mode` / `in edit mode` /
  `(empty form)` / `(the form is pre-filled with the selected shipment)` / `(the selected record is
  loaded)`. The mode is already fixed by the select / don't-select step (select a row → edit, select
  none → new) and the loaded data is exactly what the STEPS/EXPECTED verify — restating it in PRE is
  the redundant wordiness a reviewer cuts.
- This is the navigation-from-upstream shape (a form opened from a parent list; cf. §ids): the PRE
  lists the navigation actions atomically **+ the landing**, never bundling "click X to open Y" into
  one line and never narrating "in mode Z".
- `build_csv.py`'s `verify()` warns when a single PRE line carries both a `(screen_id=…)` reference
  AND a click (crammed nav — split it), and when a PRE line narrates the landed screen's mode/state
  (`opens in … mode` / `empty form` / `pre-filled` — drop it, keep the landing terse).

## §non-tech — non-technical wording

The reader is a QA tester, not a developer. Translate implementation detail to user-facing text:

| Don't write | Write instead |
|---|---|
| URL paths (`/sh_result_details`, `/api/v2/…`) | the screen name (`検品作業実績_明細`) / "the export request" |
| function names (`$scope.cancel()`, `getCsv()`) | the button/icon (`「検品キャンセル」`, the `詳細(小)` icon) |
| DB columns in steps/expected (`unit_screens.is_display`) | the behavior ("set the user's permission to 0") |
| API endpoint / DevTools commands | "the cancel request" / "make the request fail (block the network)" |
| HTML class/id, JSON payload schema, framework names (AngularJS/React) | what is visible on screen |

The exact forbidden source tokens (`stopLoading()`, `$scope`, `.error()`, `dataBound`, …) →
`output-rules.md` §4. Setup SQL in PRE-CONDITION is the **only** place raw DB/SQL is allowed.

## §expected — EXPECTED = concrete + passive

- **Concrete:** name the destination screen / exact message (verbatim) / popup (I/E/Q code +
  title) / which row/column changed. 🚫 Never use `identical to AngularJS` / `same as Angular` /
  `correct destination` / `AngularJS版と一致すること` as the result (S1 is the only exception, §10).
  Comparing to AngularJS is a *test method* (the tester opens both) → put it in STEPS, not EXPECTED.
- **Compare to Next.js↔AngularJS behavior, NOT DB columns — for display/read TCs.** Migration =
  functional equivalence; for list/detail/display screens do not verify DB column values in EXPECTED.
  **Exception — form/edit/create screens:** the register/update/delete **success** TC adds a
  DB-persistence verify step in S4.1 (a UI success modal doesn't prove the write landed) — see
  `mimosa-rules.md` §verify-db.
- **Passive voice**, subject = the UI element: `The error modal is displayed`, `The × icon is
  removed`, `The screen is navigated to the … screen`, `The CSV file is downloaded`. Avoid
  `Clicking × removes…` / `The user sees…`. JP keeps the 「〜こと」 ending (表示されること / 削除されること /
  遷移すること). Never alter modal text inside 「」.
- Map 1 outcome ↔ 1 step (numbering rules → `output-rules.md` §5).

## §enumerate — list fields comma-separated, every field spelled out

When a cell enumerates several fields / columns / items (a form's read-only vs editable field
list, the displayed columns, a set of options…), separate them with a **comma + space** so the
list is scannable. Do NOT jam them with `・` / `;` / mixed separators — a 10-field wall of `・` is
unreadable. (A single trailing `&` / "and" before the last item is fine: `A , B , C & D`.)

**🔴 Spell out every distinct field — never collapse a range.** If fields differ only by a trailing
number, list each one. On AngularJS `送状備考1` / `送状備考2` / `送状備考3` are three separate fields →
write `送状備考1 , 送状備考2 , 送状備考3`, **never** `送状備考1〜3` (the tester can't tell how many fields
there are, nor their exact labels).

❌ `配送業者名 & 配送業者連携区分・用途・顧客管理番号・配達可能日数; the editable 初期表示・送状品名・送状備考1〜3・顧客管理番号(Unit)・キャリア専用コード・海外出荷 利用通貨…`

✅ `初期表示 , 送状品名 , 送状備考1 , 送状備考2 , 送状備考3 , 顧客管理番号(Unit) , キャリア専用コード , 海外出荷 利用通貨 , …`

- When there are two sets, give each a short lead-in: `Read-only: A , B , C. Editable: D , E , F.`
  (JP `参照のみ：A 、 B 、 C。 編集可：D 、 E 、 F。` — JP cells may use the Japanese comma `、`).
- Keep each field's exact JP label (don't abbreviate, range-collapse, or merge two fields into one `・` token).
- `build_csv.py`'s `verify()` warns on a line with 4+ `・`, or a `<label><n>〜<m>` collapsed range.

**Canonical 項目表示 (form display) EXPECTED shape** — one sub-result per line, comma-separated,
every field spelled out:
```
1.1 The displayed fields, their labels and their order are the same as those in the AngularJS version.
1.2 The サービス名 / 便種名 dropdowns are displayed.
1.3 The read-only fields are shown: 配送業者名 , 配送業者連携区分 , 用途 , 顧客管理番号 & 配達可能日数.
1.4 The editable fields are shown: 初期表示 , 送状品名 , 送状備考1 , 送状備考2 , 送状備考3 , 顧客管理番号(Unit) , キャリア専用コード , 海外出荷 利用通貨 , 海外出荷 利用通貨小数点桁数 , インコタームズ , 海外出荷 保険コード & 海外出荷 保険タイプ.
```

## §steps-full — STEPS = complete, no shortcuts

Spell out every action from PRE-CONDITION to the observed result; never assume an unestablished state.
- Opening a modal/sub-screen: state which button → which modal (e.g. "click 「予定外在庫追加」 → the
  「商品マスタ選択」 modal opens"). Don't write a bare "open the X modal".
- A field needing a sub-flow (e.g. ロケ chosen via a 「検索」 modal): don't hide it under "fill valid
  values" — list the field + how to fill it, or split into its own step.
- Hard-to-reach starting state (deep inside a modal): move the opening flow into PRE-CONDITION
  (and spell that out too) so the STEP is just the action under test.

## §be-first — read BE code first (behavior + validation messages)

Before writing any outcome/error/errorCode/message, read the BE: API `$rules` in
`app/Http/Controllers/API/<Entity>Controller.php`, the Service it delegates to
(`app/Services/Standards/` or an `Alternatives/` override), business validation in
`app/Models/<Entity>Observer.php` (`$this->RU(...)`), modal codes in `MessageController.php`.
Don't stop at the message — understand the **full behavior** (success path, branches, what gets
written); the deep-trace procedure is `analyze-screen.md` step 6.
EXPECTED must be concrete: ✅ "server returns NG errorCode=1, popup 「引当数は必須項目です。」" —
❌ "if the server rejects it, an error popup is shown". Only test on stg when the BE is unclear
(dynamic DB config) or visual behavior must be confirmed.

## §nav-button-modal — navigation, button labels, modals

- **Navigation:** every screen named in PRE (open) and EXPECTED (target) carries `(screen_id=N)`.
  ✅ `「セット品崩し_セット品候補一覧 (screen_id=627)」へ戻る`. Get the target id from the route in the
  controller (`$location.path('/xxx')`) → screen-id-mapping.md / DB.
- **Screen display name = the user-facing name, used consistently everywhere.** Name the screen by
  its actual page title (App routing, the part after `W3 mimosa | `) / the label of the button that
  opens it. When that is **fuller than DB `alias_nm`** — e.g. a register+edit screen whose `alias_nm`
  is `出荷指示登録` but whose page title and open-button are **`出荷指示登録・修正`** — use the fuller
  page-title name for the screen **everywhere**: sheet 1 (`1.概要` N36), the file name
  (`build_xlsx --screen-name` / `--sub`), AND every `[<name> (screen_id=X)]` reference. Never let the
  spec name the same screen two ways (short `alias_nm` in the refs while the page-title TC says the
  fuller name). `build_csv.py`'s `verify()` warns when `SCREEN_ALIAS` and `PAGE_TITLE` are short/long
  forms of each other.
- **Button label = exact JP** from the template (`trans('…')`) or DB `uba.nm` — no synonym /
  generic / English. The two shared toolbar icons: `設定アイコン` → button **「画面設定」**;
  `展開ボタン` → button **「全画面表示」**. Keep the `(gear icon)` / `(full-screen display)` hint
  but include the real name: ✅ `Click the 「画面設定」 button (gear icon).`
- **Modal described fully:** title + message verbatim (`mimosa-facts.md`). If it is a form/検索
  modal, also describe its contents: labels + inputs (検索条件), grid columns (一覧), buttons inside
  (「選択」「キャンセル」). (An E-modal via `createEModalByServerData` shows the message in the
  title area → message-only is acceptable.)

## §initial-display — 初期表示 TC = short form

One step, one line. STEPS `1. Verify the initial display of the screen.` EXPECTED
`1. The corresponding data is retrieved and correctly mapped to the appropriate fields.`
(JP `該当データが取得され、正しい項目に正しく反映されること。`). PRE adds the default filter as context
(`kind=…, status=…`). 🚫 No side-by-side compare steps, no per-column listing, no "same on both
screens" (the グリッド列 default-state TC in S2 covers columns).

➕ **Default search-filter display.** If the screen has a default search filter (date range / status
/ …), add a **separate** display TC (distinct from the short-form above) that verifies the default
filter VALUES are shown — e.g. 開始日/終了日 both default to today — **and** that the grid is filtered
accordingly. Don't fold this into the generic 初期表示 line; it is its own TC (中分類 = the field, e.g.
`表示期間`).

## §setup-sql-wording — setup SQL wording

In PRE-CONDITION write `Run SQL:` / `SQLを実行:` — never "Coordinate with admin/dev to set:".
Never hard-code a local `unit_screens.id`/`unit_grid_columns.id`/`unit_button_apis.id` — JOIN via
`screen_id` (master) + `unit_roll_id = <test_user_roll>` placeholder (see `mimosa-rules.md` §setup-sql).

## §S1-verbatim — S1 共通確認 copy VERBATIM (the only place "AngularJS版と一致" is allowed)

The 4 S1 TCs are fixed boilerplate. Only swap `<PAGE_TITLE>` (the part after `W3 mimosa | ` from
the App routing file) and the screen name in `PRE_*`. §3 (no "identical to AngularJS") does NOT
apply to S1.

```python
S1 = [
  ('ページタイトル','','','正常', PRE_EN, PRE_JP,
   '1. Verify the page title of the screen.', '1. 画面のページタイトルを確認する。',
   '1. The page title is "W3 mimosa | <PAGE_TITLE>".', '1. ページのタイトルは「W3 mimosa | <PAGE_TITLE>」です。'),
  ('ヘッダー','','','正常', PRE_EN, PRE_JP,
   '1. Verify the displays of the header.', '1. ヘッダーの表示を確認する。',
   '1. The displayed items in the header are the same as those in the AngularJS system.',
   '1. ヘッダーの表示項目がAngularJS版と一致すること。'),
  ('フッター','','','正常', PRE_EN, PRE_JP,
   '1. Verify the displays of the footer.', '1. フッターの表示を確認する。',
   '1. The displayed items in the footer are the same as those in the AngularJS system.',
   '1. フッターの表示項目がAngularJS版と一致すること。'),
  ('メニュー','','','正常', PRE_EN, PRE_JP,
   '1. Verify the displays of the menu.\n2. Click on each menu item.',
   '1. メニューの表示を確認する。\n2. 各メニュー項目をクリックする。',
   '1. The displayed items for each menu item are the same as those in the AngularJS system.\n2. Each menu item link navigates to the correct destination.',
   '1. 各メニュー項目の表示内容がAngularJS版と一致すること。\n2. 各メニュー項目が正しい遷移先に遷移すること。'),
]
```
