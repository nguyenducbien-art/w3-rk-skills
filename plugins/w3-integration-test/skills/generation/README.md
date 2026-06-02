# generation — W3 integration test-case generation

The `generation` skill of the **`w3-integration-test`** plugin (marketplace **`w3-rk-skills`**).
Generates the 5-section integration test-case spec (結合テスト仕様書) for ONE W3 Mimosa screen from the
AngularJS controller/view/BaseController + Laravel BE → bilingual CSV → official Excel.

**Install / use / output → see the `w3-rk-skills` repo root README.**

- Invoke: `/generation <screen_id>` (or say "gen test case for screen X").
- All rules live in `references/`; generators in `scripts/` (`build_csv.py` → CSV, `build_xlsx.py` →
  Excel); the QA Excel template in `assets/template.xlsx`.
- `CODE_REPO` = the session cwd; output → `<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=X)/`.
