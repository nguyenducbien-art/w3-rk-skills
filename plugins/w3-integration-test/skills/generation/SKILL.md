---
name: generation
description: >
  Generate an integration test-case specification (結合テスト仕様書) for ONE screen of the W3
  Mimosa AngularJS → React (Next.js) migration. Reads the AngularJS controller/view/BaseController
  + local DB metadata, then produces the 5-section spec as a bilingual CSV
  (via scripts/build_csv.py) and, on request, the official Excel deliverable
  (via scripts/build_xlsx.py using the bundled QA template). Self-contained: all rules are inlined
  under references/; the only per-machine edit is references/project-config.md. Trigger when the
  user types `/generation <screen_id>`, or says "gen test case / gen TC /
  結合テスト仕様書 / test spec for screen <id|JP name|AngularJS route>" for a W3 Mimosa migration screen.
---

# W3 Integration Test Generation

Generate the 結合テスト仕様書 for one W3 Mimosa screen **from source, not guesswork**. All knowledge
lives in `references/`; this file is the conductor. Communicate with the user in **Vietnamese**;
code/comments are **English or Japanese only**.

## Input

`screen_id` (required). If missing, ask for it and stop — do not analyze or generate without it.

## Reference map (read on demand — do not preload everything)

| File | Read it when |
|---|---|
| `references/project-config.md` | **First, always.** Paths, DB, branches, test-env. Per-machine + fail→ask. |
| `references/analyze-screen.md` | Phase 1 — how to read the screen + write `screen-analysis.md`. |
| `references/test-categories.md` | The 5-section structure, markers, what goes where, exclusions. |
| `references/per-button-patterns.md` | Per-button checklist 6-A…6-L. |
| `references/gates-workflow.md` | Gate A/B/C + "assume all buttons enabled". |
| `references/mimosa-rules.md` | 🔴 W3-specific rules (is_display/available, CSV/帳票 1-TC, filter 4-TC, BVA, perf, setup-SQL). |
| `references/writing-rules.md` | How to word PRE/STEPS/EXPECTED (non-tech, passive, screen_id, button labels, modals, S1 verbatim). |
| `references/output-rules.md` | CSV format, numbering, forbidden terms, pre-save self-check. |
| `references/mimosa-facts.md` | Lookup: modal codes, MAX constants, button-label helpers, filename pattern. |
| `references/example-589.csv` · `example-edit-430.csv` | Gold examples — list-screen (589) / form-edit (430) shapes to mimic (pick by screen type). |

## Workflow (regenerate-only)

1. **Config & preflight.** Read `project-config.md`. Resolve `CODE_REPO` (= the session's current
   working directory — the W3 code repo you opened Claude Code in; confirm via the §1 markers).
   Run the DB preflight (§3.1) and classify the result: **no Docker/MySQL at all →
   source-only mode** (announce it, generate 100% from code + docs, §3.3); **DB present but
   creds/name wrong → ask the user** (§3.2); a path failure → ask. With a DB, re-derive
   `<test_user_roll>`; in source-only mode keep it as a placeholder (§7).
2. **Analyze** (`analyze-screen.md`). Read DEEPLY in BOTH layers: AngularJS (FULL controller +
   BaseController + view) for the UI flow, AND Laravel (API controller → Service → Model/Observer)
   for the real backend behavior, branches and side effects. Query DB metadata **if a DB exists**;
   otherwise read the doc/source equivalents (§3.3). Write `screen-analysis.md`.
3. **Gate A + Gate B** (`gates-workflow.md`). Output the UI inventory + func-mapping cross-check.
   Resolve every gap. Apply "assume all buttons enabled".
4. **Summarize findings + planned TC count, then CONFIRM.** Show the user: metadata, button set,
   per-section TC counts, output folder. **Wait for the user to confirm before generating.**
5. **Generate.** Copy `scripts/build_csv.py` into the screen's output folder
   (`<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=<X>)/` — see
   `project-config.md` §2), fill the SCREEN CONFIG +
   the S2..S5 tuples per `test-categories` → `per-button-patterns` → `mimosa-rules` →
   `writing-rules` → `output-rules`. Run it → the bilingual CSV. The script's `verify()`
   + Gate C (`gates-workflow.md`) must pass; fix and re-run before showing the user. Save any
   setup SQL to `sql/test-data-sql.md` inside that folder.
6. **Iterate (regenerate).** The user clicks through each TC to verify the spec. On feedback,
   **edit the tuples in `build_csv.py` and re-run** (overwrite) — never hand-edit the CSV/Excel.
   Treat shared evidence (modal text, API response, DB state) as input to correct the spec,
   not as a test result.
7. **Excel (only when the user explicitly asks).** Run
   `python scripts/build_xlsx.py --csv <bilingual.csv> --screen-id <X> --screen-name <alias> --top <top_scr_nm> --sub <sub_scr_nm> --author <name> --today <YYYY-MM-DD>`.
   It uses the bundled `assets/template.xlsx`. Naming/folder → `project-config.md` §2.
   **Restore every local DB change** you made for setup.

## Deliverables

In `<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=<X>)/`: working files
`screen-analysis.md` · `build_csv.py` · `Testcase_Output_<name>_base.csv` (bilingual) ·
`sql/test-data-sql.md` (if any setup SQL); and, on request, the Excel in its own sub-folder
`<alias> (screen_id=<X>)_QAテスト/結合テスト仕様書_… ver1.0.xlsx`.

## Phase distinction

This skill **writes the spec; it does not execute tests.** When the user shares real results
(modal text, downloaded file, API response), treat them as evidence to make the spec correct —
**never tag PASS/FAIL.** Execution is a separate QA ticket that consumes this output.

## Guardrails

- **Local DB only** (when one exists), with consent: show every UPDATE/INSERT preview and wait for
  confirm; restore right after the user verifies. Never `INSERT unit_button_apis` with a `func`
  absent from the controller. DB present but misconfigured / path failure → ask the user
  (`project-config.md` §3.2); **no Docker/DB at all → source-only mode** (`§3.3`), generate from
  code + docs. Never touch stg.
- **Never modify application source** (`controllers/`, `views/`, `resources/`, `app/`, …). This
  skill only writes deliverables under `<cwd>/w3-rk-skills-output/` — never inside the plugin or the
  code repo's tracked tree.
- **Code / file comments: English or Japanese only** — never Vietnamese.
- When the user asks for a **format / suggestion / name**, return the string only — do not auto
  `mv`/`edit`/`rename`. Only rename when the user says so.
- In **auto mode, run no git operations** at all.
- **Excel is opt-in:** generate it only when the user explicitly asks (not after every CSV).

## Portability

Distributed as the `generation` skill of the `w3-integration-test` plugin (marketplace `w3-rk-skills`).
Everything is bundled (`assets/template.xlsx`, `references/`, `scripts/`); `CODE_REPO` resolves to the
**session cwd** and output goes to `<cwd>/w3-rk-skills-output/` — **no per-machine edit needed**. No
dependency on Claude Code memory files.
