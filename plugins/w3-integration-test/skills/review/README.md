# review — W3 integration test-case review

The `review` skill of the **`w3-integration-test`** plugin (marketplace **`w3-rk-skills`**).
Reviews an existing 結合テスト仕様書 (`.xlsx`) against the real screen + the W3 conventions and reports
**Add / Modify / Delete** in 3 severity tiers (🔴 Critical / 🟡 Medium / ⚪ Minor). **READ-ONLY** — it
never edits the TC file.

**Install / use / output → see the `w3-rk-skills` repo root README.**

- Invoke: `/review <path.xlsx>` (or say "review this TC file").
- Shares the gen rules via `../generation/references/` (both skills live in the same plugin).
- Own files: `references/` (workflow / checklist / report-format), `scripts/dump_tc.py` (xlsx → CSV +
  auto-flags).
- Output → `<cwd>/w3-rk-skills-output/w3-integration-test/review/<slug>(screen_id=X)/TC-review_….md`.
