# Mimosa Facts (lookup tables)

> Cached facts from ONE repo snapshot — read this first as a **hint**, not ground truth. Paths
> relative to `CODE_REPO`. 🔴 **Modal title/message text VARIES by vendor/version** — the cached
> values below can be wrong for your `CODE_REPO` (observed: E001 title/message and the E017 message
> differ in some repos). **Verify EVERY modal code you actually use — even ones listed here — by
> grepping the current `MessageController.php`, and quote it verbatim.** Never ship a cached value
> you have not confirmed against the repo under test.

---

## 1. Modal codes (from `app/Http/Controllers/Directs/MessageController.php`)

| Code | Title | Message | Trigger |
|---|---|---|---|
| E001 | 行未選択エラー | 対象とする行を選択して、当ボタンを再度クリックしてください。 | 0 rows checked |
| E017 | 権限エラー | 申し訳ございませんが、現在利用権限がございません。ご利用される場合は、責任者にお問合せください。 (E017) | no permission |
| E022 | 帳票タイプ未選択エラー | 帳票タイプが選択されていません。選択後に再度クリックしてください。 | 帳票 publish without type |
| E024 | 選択数超過 | 選択明細件数が200件を超えております。… | > MAX_SELECTION (200) |
| E028 | 選択数超過 | 選択明細件数が500件を超えております。 | > MAX_TRANSIT_SELECTION (500) |
| E030 | 利用可能CSV無し | 現在利用可能なテンプレートがありません。CSV設定をご確認ください | UnitIfApi available=0 |
| E999 | システムエラー | 予期せぬエラーが発生しました。 (E999) | HTTP failure on publish |
| I001 | 正常完了 | 正常に完了しました。 | success |
| Q003 | 警告 | 入力された内容が登録されませんがよろしいですか？ | (verify per screen) |
| Q015 | 確認 | チェックしたレコードをファイルに出力します。よろしいですか？ | CSV download confirm |

> E027 (date range exceeded) and other Q-codes vary by screen — grep the exact string.

## 2. MAX constants (from `resources/assets/javascripts/settings/Consts.js`)

| Constant | Value | Exceed → | Operator |
|---|---|---|---|
| `MAX_SELECTION` | 200 | E024 | `<` → n=200 PASS, n=201 FAIL |
| `MAX_TRANSIT_SELECTION` | 500 | E028 | `<` → n=500 PASS, n=501 FAIL |

> Always re-confirm the operator in the controller (`<` vs `<=`) before writing BVA — see
> `mimosa-rules.md` §BVA.

## 3. Button labels — trace exact `trans(...)` from helpers (`app/Helpers/ViewHelpers.php`)

| Element | Helper | Note |
|---|---|---|
| Toolbar buttons | `printToolButtons` | `$allowDetail=true` → `明細` (toDetails); `false` → `一覧` (toHeaders); + `CSV` / `帳票` |
| Search-area buttons | `printSearchToolSet` | `$searchDate=true` → `適用`; `$searchSingleDate=true` → `検索`; + `マイフィルタ`/`保存`/`クリア` |
| 帳票 modal | `printModalReports` | publish button = `実行` (NOT 出力); close = `閉じる` |
| Per-row icons | `addToolButton` (BaseController) | `詳細` (`_show_to_detail_button`) / `一覧` (`_show_to_header_button`) |
| 共通 toolbar icons | `ViewHelpers.php:906 / :926` | `設定アイコン` title = **画面設定** (gear); `展開ボタン` title = **全画面表示** |

> Never paraphrase a button label — quote the exact JP from `trans()` / `uba.nm`. Wording rule
> → `writing-rules.md` §nav-button-modal.

## 4. CSV download filename pattern

```
<screen_alias>_<YYYY>_<M>_<D>_<HH>_<MM>_<SS>.csv
```
(not `download.csv`). CSV is ServerSync → no I001 success modal.

## 5. Permission checks (on action buttons)

| API | DB column | Error |
|---|---|---|
| `getUnitScreensCanCsv` | `unit_screens.can_csv` | E017 |
| `getUnitScreensCanDisplaySetting` | `unit_screens.is_display` of row `screen_id=444` | E017 |
| `unit_button_apis.is_display=0` | (button hidden) | — |

## 6. Screen-Driven UI (background)

UI is rendered from DB, not hardcoded: `screens` (master) vs `unit_screens` (per-roll override);
buttons from `unit_button_apis`; grid columns from `unit_grid_columns`; sub-nav grouped by
`screens.grp`. **Only `is_display` gates visibility/access at runtime; `available` does NOT** —
the single most important Mimosa rule, detailed in `mimosa-rules.md` §is_display-vs-available.
A ticket saying "screen_id=X" usually means `screens.id`; query `unit_screens WHERE screen_id=X`.
