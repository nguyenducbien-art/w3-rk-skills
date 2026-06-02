---
name: review
description: >
  Review an existing integration test-case spec (結合テスト仕様書 .xlsx) for ONE screen of the W3
  Mimosa AngularJS → React migration. Reads the TC file + the real screen (AngularJS controller +
  Laravel backend) and reports what to Add / Modify / Delete — does NOT edit the TC file. The
  highest-value check is branch coverage: every screen branch must have a test case. Shares the W3
  conventions with the generation skill (reads ../generation/references/). Trigger when the user
  types `/review <path.xlsx>` or says "review the TC set / check the test cases /
  review <person>'s TCs for screen <id> / review this test spec".
---

# W3 Integration Test Review

Review an existing 結合テスト仕様書 against the real screen and the W3 conventions, then report
Add / Modify / Delete. **READ-ONLY** — the only file written is the review report; never edit the
reviewed TC file or the application source. Communicate with the user in **their language (default English)**.

## Input

- `TC file`: path to the `.xlsx` deliverable (sheet `3.テストケース`). Required.
- `screen_id`: required (confirm it matches the file's 1.概要 N32).

If either is missing, ask and stop.

## Reference map

This skill's own files:

| File | Read it when |
|---|---|
| `references/review-workflow.md` | The 4-step flow (dump → analyze → audit → report) + read-only guardrails. |
| `references/review-checklist.md` | The audit dimensions (structure / button / **branch** / BVA / CSV-帳票 / is_display / wording). |
| `references/report-format.md` | How to write the report (human-style, Add/Modify/Delete, cite TC №). |
| `scripts/dump_tc.py` | Read the `.xlsx` `3.テストケース` → readable CSV + suitability summary. |

🔴 **The W3 rules + facts + screen-reading are SHARED — read them from the generation skill**
(both are skills inside the same `w3-integration-test` plugin, so `../generation/` resolves):

| For | Read |
|---|---|
| Paths / DB / preflight | `../generation/references/project-config.md` |
| How to read the screen (UI + Laravel BE, branches) | `../generation/references/analyze-screen.md` |
| Section structure / per-button / gates | `…/test-categories.md` · `…/per-button-patterns.md` · `…/gates-workflow.md` |
| W3-specific rules | `…/mimosa-rules.md` |
| Wording / output format | `…/writing-rules.md` · `…/output-rules.md` |
| Modal codes / MAX / labels | `…/mimosa-facts.md` |

This keeps the review and the generation in lock-step — the review checks exactly what the
generator is supposed to produce. (Reviewing what good looks like: the gen gold examples
`…/example-589.csv` (list) and `…/example-edit-430.csv` (form).)

## Workflow (read-only)

1. **Dump + suitability** — `python scripts/dump_tc.py --xlsx "<file>"`. Confirm `screen_id`
   matches and TC rows exist; else stop and ask. Read the dumped CSV.
2. **Analyze the screen** — follow `analyze-screen.md` (gen): read FULL controller + BaseController
   + view, trace the Laravel BE (Controller → Service → Observer) → enumerate every button + every
   branch. Use `project-config.md` for paths/DB: run the preflight — **no Docker/DB → source-only
   mode** (review purely from code + docs, §3.3); DB present but misconfigured → ask (§3.2). Use
   `mimosa-facts.md` for codes.
3. **Audit** — apply `review-checklist.md` against the dumped TCs. Lead with **branch coverage**
   (every branch → a TC; flag dropped) per `gates-workflow.md` Gate C.
4. **Report** — write the findings to
   `<cwd>/w3-rk-skills-output/w3-integration-test/review/<slug>(screen_id=<X>)/TC-review_<alias>_(screen_id=<X>).md`
   per `report-format.md` (human-style, English, Add/Modify/Delete, cite TC №, **grouped into 3
   severity tiers 🔴 Critical / 🟡 Medium / ⚪ Minor, sorted most-severe first**). Stop.

## Output

A single review report at
`<cwd>/w3-rk-skills-output/w3-integration-test/review/<slug>(screen_id=<X>)/TC-review_<alias>_(screen_id=<X>).md`
(gitignore `w3-rk-skills-output/`). Nothing else is written.

## Guardrails

- **READ-ONLY.** Never edit the reviewed `.xlsx`/CSV, never modify application source. Only the
  review `.md` is written.
- No dev server / preview / browser automation — review is from static source + the dumped TCs.
- Local DB (when one exists): read-only queries to confirm metadata (preflight per
  `project-config.md`); never mutate. DB present but misconfigured / path failure → ask the user;
  **no Docker/DB at all → source-only mode** (review from code + docs, §3.3).
- This skill **reports**; it does not rewrite TCs and does not emit a fix-prompt (separate concern).
- Communicate in the user's language (default English); the report file is in English; code/comments English or Japanese only.

## Portability

Distributed as the `review` skill of the `w3-integration-test` plugin (marketplace `w3-rk-skills`),
bundled next to the `generation` skill — `../generation/references/` holds the shared rules. No
per-machine config: `CODE_REPO` resolves to the session cwd (see
`../generation/references/project-config.md`).
