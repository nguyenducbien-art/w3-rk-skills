# Test Categories & Section Structure

> This file defines **which sections the test set has, what each section holds, and how
> markers are assigned.** Per-button TC patterns → `per-button-patterns.md`. W3-specific
> rules (CSV/帳票 1-TC, filter 4-TC, is_display vs available, BVA, perf) → `mimosa-rules.md`.
> Cell-wording rules → `writing-rules.md`.
>
> Gold references to compare against — **pick by screen type**:
> - **List screen** → `references/example-589.csv` (screen 589 入荷実績 実績).
> - **Form / edit screen** → `references/example-edit-430.csv` (screen 430 商品追加・編集 — field-validation depth).
>
> ⚠️ **The gold files PREDATE several current standards** — follow the rules **over** the example for:
> - **CSV/帳票** (both files): they show only the *happy-path*; add the E017/E001 guard TCs (S3) per
>   `mimosa-rules.md` §csv-report.
> - **`example-edit-430.csv` (form)** also predates **§s3-abnormal-only** (it may keep 正常 boundary
>   cases in S3 — move them to S4.1), **§verify-db** (no DB-persistence verify step — add one),
>   **§concurrent-conflict** (no 2-browser conflict TC — add one), and the **expanded
>   §form-field-validation** (it may lack negative / zero / register-duplicate / email-format /
>   only-required-filled cases — generate them per the rule, not just what 430 happens to show).
>
> The examples remain authoritative for everything else (S1 boilerplate, filter 4-TC, sub-screen,
> 共通アイコン, numbering, cell shape, comma-separated field lists).

---

## 1. The 5-section spine (matches the Excel template)

| Section | JP name | Holds | Marker (`0.Config!I..`) |
|---|---|---|---|
| **S1** | `1. 共通確認` | Page title / header / footer / menu | I21 |
| **S2** | `2. 表示確認` | 画面表示 / グリッド列表示 / ボタン表示 / 初期表示データなし | I22 |
| **S3** | `3. バリデーション確認` | **異常 (rejection) only** — row-selection guard (E001) / boundary FAIL (BVA N+1) / invalid field input. 正常 / boundary-PASS → S4.1 (`mimosa-rules.md` §s3-abnormal-only) | I25 |
| **S4** | `4. 業務処理の確認` | (parent header — holds NO test case directly) | I26 |
| **S4.1** | `4.1 業務処理の確認` | Action buttons / navigate / Q-confirm / filter 4-TC / 初期表示 / CSV / 帳票 / sub-screen / 共通アイコン | I27 |
| **S4.2** | `4.2 その他処理の確認` | Network error / silent failures | I28 |
| **S5** | `5. 性能確認` | 30k records (+ 500 ids[] only if opted in) | I29 |

## 2. Section markers — default 7 markers (S2 is FLAT)

`0.Config` defines 9 markers I21..I29. **Default render = 7**:
```
I21 1. 共通確認
I22 2. 表示確認        ← holds TCs directly (FLAT)
I25 3. バリデーション確認
I26 4. 業務処理の確認   ← parent header, NO TC under it
I27 4.1 業務処理の確認
I28 4.2 その他処理の確認
I29 5. 性能確認
```
- `2. 表示確認` (I22) is **FLAT**: display TCs sit directly under I22. The parent marker `4.`
  (I26) renders only a header row; its TCs live in I27/I28.
- **Split into 9 markers** (add I23 `2.1. 初期表示確認` + I24 `2.2. 条件表示の確認`) **only**
  when the screen has BOTH static display AND action/condition-triggered display.
  List/detail screens → 7 markers.

## 3. 大分類 (column B) = FEATURE NAME, not an abstract category

🔴 Column `大分類` (col B of each TC) = the **concrete feature/button label** a tester
recognizes (`内容確定`/`CSV`/`帳票`/`マイフィルタ`/`明細`…), **not** an abstract category like
`操作`/`表示`/`検索`.
- Exceptions: S1 = `ページタイトル`/`ヘッダー`/`フッター`/`メニュー`; S2 config =
  `画面表示`/`グリッド列表示`/`ボタン表示`; no-data = B`表示`, 中`グリッド`, 小`データなし`; S5 = B`応答時間`.
- 中分類 = the action (`「実行」ボタンをクリックする`/`選択なし`); 小分類 = the case (`単一選択`/`複数選択`).
- Details + common mistakes → `mimosa-rules.md` §大分類. (This is a major override vs generic — see §5.)

## 4. Mapping generic Categories 1-8 → the 5 sections

The generic QA base classifies by Category 1-8. When generating for W3, map them in:

| Generic category | → W3 section |
|---|---|
| Cat 1-4 (ページタイトル/ヘッダー/フッター/メニュー) | **S1** |
| Cat 5 表示 (display / initial state) | **S2** (config + no-data); 初期表示 moves down to **S4.1** |
| Cat 6 操作 (operations) | guards/BVA → **S3**; business flow → **S4.1** |
| Cat 7 検索 (search / filter / sort) | **S4.1** (filter 4-TC set) |
| Cat 8 権限 (permissions/auth) | ❌ **DROPPED** (covered by DEV common test suite) |
| (not in generic) 性能 | **S5** (W3 addition) |

## 5. Where W3 overrides the generic base (resolved — no ambiguity)

> The generic QA base and the W3 layer used to conflict on the points below. This is the
> resolved state — **follow the W3 column**:

| Point | Generic says | → W3 (keep this) |
|---|---|---|
| 並べ替え (sort) | excluded | **tested** (inside filter 4-TC, S4.1) |
| Cat 8 権限 | own category | **dropped** (DEV common) |
| 性能 | none | **add S5** (30k) |
| CSV / 帳票 | many ad-hoc cases | **1 happy-path (S4.1) + guard errors E017/E001 (S3)** per button (`mimosa-rules.md` §csv-report) |
| 大分類 (col B) | category name (操作/表示) | **feature name** (§3) |
| `成功 ― 閉じる ×` (modal dismiss) | — | dropped (DEV common) |

## 6. TC count per section (guidance)

- **S1 = EXACTLY 4 TCs**, copied verbatim (page title / header / footer / menu) — see
  `writing-rules.md` §S1-verbatim. Only swap screen name + page title.
- **S2** — branches by screen type (see `mimosa-rules.md` §is_display-vs-available):
  - **List screen**: `画面表示` + `グリッド列表示` + `ボタン表示` (if the screen has buttons) + `初期表示データなし`
    (date-range list → make it concrete: set a 表示期間 with no matching records → 「適用」 → empty grid,
    not just "no data exists")
    + a **counter-display** TC if the screen shows a `{{ num_* }}` count (e.g. 商品種類数)
    + (recommended) `グリッド列 デフォルト状態` (labels & order match AngularJS).
    Do NOT generate `available=0` for grid columns (no-op).
  - **Form / edit screen**: `画面表示` + **`項目表示`** (field display) — **NOT `グリッド列表示`** (no grid).
    If it loads a record by an **id from a parent screen**, also add 「直接URLアクセス」 variants
    (IDなし / 有効なID / 存在しないID — direct deep-link entry) → `mimosa-rules.md` §direct-url-access.
- **S3 — 異常 (rejection) cases ONLY** (`mimosa-rules.md` §s3-abnormal-only); 正常 / boundary-PASS →
  S4.1. Branches by screen type:
  - **List/detail**: per guard in the controller → row-selection (E001) + boundary BVA **N+1 FAIL**
    if a MAX applies (N-1/N PASS → S4.1) + CSV/帳票 guard errors (E017/E001, `mimosa-rules.md`
    §csv-report). Verify from code, never by default (`per-button-patterns.md` 6-A + §BVA).
  - **Form / edit**: per-field **異常** validation (required-empty + maxlength N+1 + numeric
    out-of-range + wrong type + 全必須) → `mimosa-rules.md` §form-field-validation. Still ~10-18 TCs,
    **not 3**; the matching 正常 (boundary-PASS / accepted) cases sit in S4.1.
- **S4.1**: strict group order — `初期表示` → real mutation buttons → `マイフィルタ`/`並べ替え`
  (4-TC) → navigate/明細 → CSV → 帳票 → sub-screen (展開) → 共通アイコン (画面設定/全画面表示).
  Full order → `mimosa-rules.md` §S4.1-order. If the screen has a `検索エリア` with several search
  fields, cover the representative fields (code / name / date-range / combined / no-match), not one
  combined TC. A list that caps displayed rows → add `表示件数超過 (E029)`. **On a form/edit/create
  screen, the register/update/delete success TC adds a DB-persistence verify step** (`mimosa-rules.md`
  §verify-db) **+ a 2-browser concurrent-conflict TC** (`mimosa-rules.md` §concurrent-conflict); also
  lands here are the 正常 boundary/valid cases moved out of S3 (§s3-abnormal-only). A form with
  **collapsible sections** also gets section-toggle TCs (全て開く / 全て閉じる / per-section ≫ — §form-accordion).
- **S4.2**: ≥1 network error (grid load failure / mutation failure).
- **S5**: 1 perf TC (30k) by default; 500 ids[] only when opted in.

## 7. Excluded — do NOT generate (covered by DEV common test suite / library default)

| Excluded | Why |
|---|---|
| Top-nav hamburger / grid icon (`fa-th`) | common component |
| Modal `×` / overlay-click dismiss, `成功 ― 閉じる ×` | library default / DEV common |
| Cat 8 権限 (screen-level access, button-level perm, session expiry, unauthenticated redirect) | DEV common test suite |
| Session timeout (F5), 404 URL, unlogged-in redirect | generic auth/Laravel |
| Tick row / select-all checkbox | Kendo grid default |
| Grid pagination, column-filter UI mechanics | library default (the **filter 4-TC** in S4.1 covers my-filter + sort) |
| `グリッド列 available=0` | no-op both sides (see `mimosa-rules.md` §is_display-vs-available) |

> Note the W3 reversals: column **sorting** IS tested (filter 4-TC), and `設定アイコン`/`展開ボタン`
> ARE tested (1 TC each at end of S4.1) — they are NOT excluded. See `mimosa-rules.md` §S4.1-order.
