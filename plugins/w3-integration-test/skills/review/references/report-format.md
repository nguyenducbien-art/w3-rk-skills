# Report Format

> The review reads like a senior QA's own notes — **human, not robotic**. **Write the report file
> in English** (chat with the user is in their language, default English; the `.md` deliverable is English). Findings are
> grouped into **3 severity tiers and sorted most-severe → lightest**. Write to
> `<cwd>/w3-rk-skills-output/w3-integration-test/review/<slug>(screen_id=<X>)/TC-review_<alias>_(screen_id=<X>).md`. Do not edit the TC file.

---

## Shape

1. **One lead line** — what you read (controller / BE / view / DB) + a one-sentence overall verdict,
   ending with a note that the findings are ordered most-severe → lightest.
2. **Findings grouped into 3 severity tiers, in this descending order:**

   - **## 🔴 Critical** — wrong result / missing error branch / missing mandatory coverage: a tester
     would mis-judge, or a real branch or a required group (filter 4-TC, 共通アイコン, guard errors,
     BVA, form DB-verify / concurrent / direct-URL / accordion) is untested.
   - **## 🟡 Medium** — the TC exists but is redundant, sits in the wrong section, or doesn't match
     the convention (duplicates, 正常 in S3, CSV/帳票 extras, …).
   - **## ⚪ Minor** — wording / format only (wrong button label, "same as AngularJS" used as a
     result, 大分類 not a feature name, step numbering).

   Number findings **continuously 1..N across all three tiers** (do not restart per tier). Each finding:
   `N. No.<xx> — <the concrete problem in one line>` (or `No.<xx>, No.<yy>` / `No.<xx>~<yy>` for a set),
   tagged **[Add] / [Modify] / [Delete]**, then 1–3 short body lines (source fact + concrete fix).
   Omit a tier header that has no findings.
3. **## Notes / optional** (only if needed) — valid-but-worth-noting items: a TC that is correct given
   a code quirk ("keep as-is"), an stg caveat ("may be unreachable on stg — confirm"), etc.
4. **## OK (keep)** — one closing line listing the parts that are correct, so the author isn't anxious.

## Rules (keep it human)

- One finding = one problem + one fix. Cite the **TC №** by name (explicitly `No.14`), never vague.
- State the source fact in 1 line — don't re-explain how you found it, which file you grepped, or line numbers (unless the user asks for evidence).
- Don't hedge ("maybe", "if… then…") when the source confirms the fact — state it directly.
- For a missing case: say `[Add]` + the exact case (Japanese label + expected). For a wrong one:
  `[Modify]` + the source-correct text. For a redundant/no-op one: `[Delete]` + why (e.g. "available=0 is a no-op").
- English prose, but keep JP labels / codes / messages / screen names verbatim (`削除`, `E030`,
  `「指定されたコードは既に登録されています。」`). Keep `正常` / `異常` as-is (Normal / Abnormal).
- **Tier by severity, then sort the whole list most-severe → lightest** — never leave findings in
  discovery order. If unsure between tiers: "tester gets a wrong result / a branch is untested" → 🔴;
  "exists but redundant / wrong section" → 🟡; "wording / format" → ⚪.
- No tables, no robotic template, no closing meta-commentary about the review itself.

## Canonical example (match this density + the tiering/sort)

```markdown
# Review TC — 直接出庫_履歴明細 (screen_id=414)

Read StOutstockHistoryDetailsController + BaseController (getCsv / _doPrint / showModalReports / toHeaders) + view historydetails.php + ViewHelpers + MessageController + Consts.js + DB unit_button_apis (414). 47 TC — toolbar (CSV / 帳票 / 一覧) + 表示期間 + 展開行 + perf coverage is good, but the 帳票 E017 guard and the filter set are missing, several CSV/帳票 TCs are redundant, and a few 正常 TCs sit in S3. Findings are ordered most-severe → lightest.

## 🔴 Critical

1. No.10, No.12, No.15 — E001 text taken from the wrong source. [Modify]
   createIModal pulls the message from MessageController.php, not Consts.js. The real E001 is 「選択エラー」/「対象レコードを選択してください。」. Fix the EXPECTED on all three.

2. No.12 — 帳票 is missing the E017 guard. [Add]
   showModalReports → getUnitReports empty → E017「権限エラー」. Add one 異常 TC in S3 (中分類=利用可能帳票なし, rows checked but no report available).

3. (missing) — the filter 4-TC set is absent. [Add]
   the view renders printModalMySearch() → my-filter + sort exist but are untested. Add the 4 TCs in S4.1 (§filter).

## 🟡 Medium

4. No.28, No.30, No.32, No.34 — redundant CSV/帳票 variants. [Delete]
   Per §csv-report each output button = 1 happy-path + guards. Keep No.29 (CSV) / No.33 (帳票); remove the cancel / close-modal variants.

5. No.17, No.21, No.23 — wrong section. [Modify]
   S3 holds 異常 only. Move these 正常 / boundary-PASS cases to S4.1 (§s3-abnormal-only).

## ⚪ Minor

6. No.33 — wrong 帳票 export button label. [Modify]
   In the 帳票選択 modal the export button is 「実行」, not 「出力」. Fix the STEPS wording.

## Notes / optional
請求可否一括変更 (No.15/16/38/39) is valid — keep (func is inherited from BaseController; stg has the button even if the local seed is empty). The 帳票 happy-path (No.33) may be unreachable on stg if 直接出庫 has no report seeded (always E017) — confirm on stg.

## OK (keep)
S1 4 TC; No.5 screen is_display=0; No.8 default period today→today; No.18 91日→E027; No.25 一覧 501→E028 (operator `<`); No.29 CSV happy-path; No.9 展開行 5 tabs.
```

## Anti-pattern (do NOT do this)

> No.10~12 have the wrong message. I grepped app/Models/MaterialObserver.php:142 and found `$this->RU(...)`
> returning errorCode=3, and in MessageController.php line 88… (3-column table) … needs further verification if…

Too verbose, cites internals/line numbers, hedges, uses tables. Rewrite as:
```markdown
2. No.10~12 — wrong required message. [Modify]
   The real label is 未引当数, not 増加数. Change the expected to「未引当数は必須項目です。」.
```
