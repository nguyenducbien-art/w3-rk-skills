# w3-rk-skills

Rikkeisoft **W3 (sirius/mimosa) migration** skills, distributed as a **Claude Code marketplace** so
teammates auto-update instead of downloading from SharePoint.

This repo **is** the marketplace (`.claude-plugin/marketplace.json`) and hosts its plugins under
`plugins/`.

## Plugins

| Plugin | Skills | Purpose |
|---|---|---|
| `w3-integration-test` | `generation`, `review` | Generate + review integration test-case specs (結合テスト仕様書) for one screen |

## Install (each teammate, once)

```
/plugin marketplace add <git-url-of-this-repo>      # e.g. git@<host>:<org>/w3-rk-skills.git
/plugin install w3-integration-test@w3-rk-skills
```

Then enable **auto-update** so you always get the latest: `/plugin` → **Marketplaces** tab → toggle
**Enable auto-update** for `w3-rk-skills`. (Third-party marketplaces have auto-update OFF by default.)

## Use

Open Claude Code **in the W3 code repo** (the working directory must be the repo that holds
`resources/assets/javascripts/controllers/BaseController.js`), then:

```
/generation <screen_id>         # gen the spec (CSV → Excel)
/review <path-to-.xlsx>          # review an existing spec
```

You can also just say "gen test case for screen X" / "review this TC file" — the skills auto-trigger
by description.

## Output

Deliverables are written under your **current working directory** (not in this repo, not in the
plugin install dir), one tree per skill:

```
<cwd>/w3-rk-skills-output/
└── w3-integration-test/
    ├── generation/<slug>(screen_id=X)/   # screen-analysis.md · build_csv.py · CSV · sql/ · QAテスト/…xlsx
    └── review/<slug>(screen_id=X)/        # TC-review_….md
```

Add `w3-rk-skills-output/` to the code repo's `.gitignore` (or your global git excludes) so QA
deliverables never get committed to the product repo.

## Maintain (publish an update)

Edit a skill under `plugins/w3-integration-test/skills/{generation,review}/`, then:

```
git add -A && git commit -m "…" && git push
```

`plugin.json` intentionally has **no `version`** → Claude Code uses the git commit SHA, so every push
is a new version and teammates with auto-update get it on their next session.

## Layout

```
w3-rk-skills/
├── .claude-plugin/marketplace.json
└── plugins/
    └── w3-integration-test/
        ├── .claude-plugin/plugin.json
        └── skills/
            ├── generation/   (SKILL.md · references/ · scripts/ · assets/)
            └── review/        (SKILL.md · references/ · scripts/)
```
