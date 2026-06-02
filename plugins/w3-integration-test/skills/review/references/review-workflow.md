# Review Workflow

> Review an existing W3 integration-test-spec (.xlsx) against the real screen + the W3 conventions,
> then **report** what to Add / Modify / Delete. **READ-ONLY**: never edit the TC file; the only
> file written is the review report.
>
> The W3 rules are shared with the generation skill — read them from
> `../generation/references/` (see `SKILL.md` reference map). This skill only
> adds: how to read the TC file, the audit checklist, and the report format.

---

## Steps

1. **Dump + File Suitability Gate.** Run `scripts/dump_tc.py --xlsx "<file>"` → it reads sheet
   `3.テストケース` into a readable CSV and prints `screen_id` (1.概要 N32), screen name (N36), TC
   count, section markers. **Stop and ask the user** if: the file can't be opened, has no TC rows,
   or its `screen_id` ≠ the requested one (wrong file/sheet). Read the dumped CSV to get the TC
   inventory. It also prints **auto-flags** — text heuristics mirroring the gen `verify()` (PRE-cram,
   sub-number run-on, jammed `・` list, collapsed range like `送状備考1〜3`, 正常-in-S3, step-number
   mismatch, forbidden tokens). Fold confirmed ones into the report; they are hints — still verify
   against source. Screen-type checks (branch coverage / DB-verify / concurrent / direct-URL /
   accordion) are NOT auto-flagged — do them manually per `review-checklist.md` §3/§4/§4b.

2. **Get ground-truth from the screen** (same deep read as generation). Follow
   `../generation/references/analyze-screen.md`: read the FULL controller +
   BaseController + view, AND trace the Laravel backend (API controller → Service → Model/Observer)
   to enumerate **every button + every branch**. Use `../generation/references/`
   `project-config.md` for paths/DB: preflight → **no Docker/DB = source-only mode** (audit from
   code + docs, §3.3); DB present but misconfigured → ask (§3.2). Use `mimosa-facts.md` for modal
   codes / MAX constants / button labels. This branch list is what you audit the file against.

3. **Audit** (`review-checklist.md`). Compare the dumped TCs against the ground-truth + the W3
   conventions. The highest-value check is **branch coverage** (Gate C): every branch the screen
   has must have a TC — flag every dropped one. Also check structure, button coverage, BVA,
   CSV/帳票, is_display-vs-available, form vs list S2, screen_id, button labels, modals, wording.

4. **Write the report** (`report-format.md`) to
   `<cwd>/w3-rk-skills-output/w3-integration-test/review/<slug>(screen_id=<X>)/TC-review_<alias>_(screen_id=<X>).md`. Human-style,
   English, each finding tagged Add / Modify / Delete and citing the TC №, **grouped into 3 severity
   tiers (🔴 Critical / 🟡 Medium / ⚪ Minor) and sorted most-severe → lightest** (+ optional Notes /
   OK-keep sections). Then **stop** — do not touch the TC file.

## Read-only guardrails

- **Never edit the reviewed TC file** (.xlsx/CSV). The only thing written is the review `.md`.
- Never modify application source (`controllers/`, `app/`, `resources/`, …).
- Never start a dev server / preview / browser-automation; the review is from static source +
  the dumped TCs.
- Local DB (when one exists): read-only queries to confirm screen metadata are fine (preflight per
  `project-config.md`); do not mutate. No Docker/DB → source-only mode (§3.3); DB misconfigured → ask (§3.2).
- Communicate with the user in the current language of the conversation; the report file is in English (see `report-format.md`).
