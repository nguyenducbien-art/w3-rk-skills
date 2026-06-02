# Per-Button TC Patterns (6-A … 6-L)

> For **each actionable button** found in the Gate A inventory, work through this checklist
> before writing any CSV row for it. Mark every item `[YES]` (applies, generated) / `N/A`
> (does not apply) / `[MISSING]` (applies but not yet written — fix first).
> **Do not write a CSV row for a button until every item is `[YES]` or `N/A`.**
>
> These are the generic patterns. W3 narrows some of them — see the **W3 override** notes
> and `mimosa-rules.md`.

---

## The checklist

```
Per-button checklist for [Button label (JP)] / $scope.[fnName]:
  [ ] 6-A  requires selection      → 選択なし (異常 / E001)
  [ ] 6-B  MAX constant used       → BVA: N+1 FAIL→S3(異常), N-1/N PASS→S4.1(正常)  [check < vs <=]
  [ ] 6-C  startLoading() used     → 読み込み中の状態 + 二重送信防止
  [ ] 6-D  API mutation            → 成功 (I001 + loading↓ + grid reload) [+ DB verify + 2-browser conflict on form/edit/create]
  [ ] 6-E  .error() handler        → APIエラー (modal variant OR no-modal variant)
  [ ] 6-J  Q-code confirm modal    → 確認モーダル ― キャンセル + 確認モーダル ― OK
  [ ] 6-K  input modal             → 入力モーダル
  [ ] 6-L  required field present  → 必須項目 ― 未入力 (+ 全必須項目未入力 if multiple)
  [ ] 6-F  navigation only         → 成功（遷移） (+ 選択なし only if the code checks it)
  [ ] 6-G  export modal helper     → modal opens (one case)
  [ ] 6-H  report modal helper     → modal opens (one case)
  [ ] 6-I  import modal helper     → modal opens (one case)
```

## Pattern details

| # | Trigger in controller | Generate | Section |
|---|---|---|---|
| **6-A** | `getCheckedRows()` + `length === 0 / < 1` → `createIModal("E001")` | `選択なし → E001` | S3 |
| **6-B** | `MAX_SELECTION` / `MAX_TRANSIT_SELECTION < n` | N+1 FAIL → **S3 (異常)**; N-1/N PASS → **S4.1 (正常)** (§s3-abnormal-only) | S3 / S4.1 |
| **6-C** | `startLoading()` before the request | loading shown + double-submit blocked | S4.1 |
| **6-D** | `$http` mutation (POST/PUT/DELETE) | success: I001 modal + loading hides + grid reloads (**+ DB-persistence verify on form/edit/create**, `mimosa-rules.md` §verify-db) | S4.1 |
| **6-E** | `.error(...)` handler | API error path (with-modal or silent stopLoading) | S4.1 / S4.2 |
| **6-F** | `$location.path(...)` navigation | navigation success (+ 選択なし only if a guard exists) | S4.1 |
| **6-G** | `showModalExports(...)` | export modal opens | S4.1 |
| **6-H** | `showReport(...)` / `printModalReports` | report modal opens | S4.1 |
| **6-I** | `showModalImports(...)` | import modal opens | S4.1 |
| **6-J** | Q-code confirm before API (`Q003`/`Q010`/…) | confirm モーダル — キャンセル + OK | S4.1 |
| **6-K** | input/prompt modal before API | input モーダル flow | S4.1 |
| **6-L** | `required` / `ng-required` field | required ― empty (+ all-empty if multiple) | S3 |

## 🔴 W3 overrides (do not apply the generic pattern blindly)

- **🔴 Every branch becomes a TC.** The analysis `Branches` table lists each button's distinct
  outcomes — generate **one TC per branch**, including every NAMED error branch (E030 no-interface,
  NG server-validation, in-use-can't-delete, external-API error, missing-token, not-installed).
  Do NOT collapse to a single generic "API error" or stop at "modal opens". Gate C verifies every
  branch → TC (`gates-workflow.md`). (Exception: CSV/帳票 error branches — see below.) This was the
  #1 miss on list screens: analysis found E030 / NG / in-use branches but generation dropped them.
- **6-A (selection guard) is NOT a default.** Only generate `選択なし → E001` if the controller
  actually checks 0 rows. Toolbar buttons (`toDetails`/`toHeaders`) often check only MAX, not
  0 — then write a navigation-with-0-rows behavior TC instead, not an E001 TC.
  See `mimosa-rules.md` §row-guards.
- **6-B BVA** uses the real constants `MAX_SELECTION = 200` (→ E024) and
  `MAX_TRANSIT_SELECTION = 500` (→ E028), operator `<` (so n=limit PASS, n=limit+1 FAIL). **Split by
  status**: the N+1 FAIL (異常) goes to S3, the N-1/N PASS (正常) go to S4.1 (`mimosa-rules.md`
  §s3-abnormal-only). See `mimosa-rules.md` §BVA + `mimosa-facts.md` for the exact messages.
- **CSV / 帳票 toolbar (`getCsv` / `doPrint`)** = 1 happy-path (S4.1) **+ the symmetric guard errors
  E017/E001 (S3)** per button — see `mimosa-rules.md` §csv-report (still skip 読み込み中/Q015キャンセル/
  ダウンロード失敗/E022). 🔴 Separately, interface import/export (`showModalImports` /
  `showModalExports`, e.g. 商品マスタ取込 / 商品マスタ出力) keep their own branches — modal opens +
  実行 success + **no-interface → E030**.
- **6-E error path = one TC per NAMED branch**, not a single generic "API error". Read the BE
  first (`writing-rules.md` §be-first) for the exact errorCode + message; each distinct failure
  (E030, server-validation NG, in-use-can't-delete, external-API error, missing-token) is its own TC.
- **6-L on a form/edit screen** expands to the FULL field-validation set per field (required +
  maxlength BVA + numeric range + type + 全必須 + edit-mode edges), **not just "required"**. See
  `mimosa-rules.md` §form-field-validation. (The #1 miss on form screens — S3 had 3 TCs instead of ~20.)
- **6-D on a form/edit/create screen** adds a **DB-persistence verify step** to the register/update/
  delete success TC (S4.1): `Run SQL: SELECT … WHERE <natural key>` → the row was created/updated/
  deleted with the entered values (also keep the UI success EXPECTED). Display/list screens do NOT
  (compare to AngularJS). See `mimosa-rules.md` §verify-db + `writing-rules.md` §expected.
- **6-D on a form/edit/create screen also adds a concurrent-conflict (2-browser) TC** in S4.1 — two
  sessions edit the same record / register the same key at once. The EXPECTED depends on the real BE
  mechanism (optimistic lock → exclusive-control error; no lock → last-write-wins; unique key →
  duplicate error) — **read BE + FE first, never guess**. See `mimosa-rules.md` §concurrent-conflict.

## After the buttons

Once every button is covered, also generate:
- **S1** (page title / header / footer / menu) — verbatim, see `writing-rules.md`.
- **S2** display config + no-data — see `test-categories.md` §6 + `mimosa-rules.md`.
- **初期表示** (one short TC) + **filter 4-TC** + **共通アイコン** in S4.1 — see `mimosa-rules.md`.
- **Row-click** navigations (pattern 6-F) from the Gate A `row-click` rows.
