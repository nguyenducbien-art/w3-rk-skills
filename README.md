# w3-rk-skills

Rikkeisoft **W3 (sirius/mimosa) migration** skills, distributed as a **Claude Code marketplace** so
teammates auto-update instead of downloading from SharePoint.

This repo **is** the marketplace (`.claude-plugin/marketplace.json`) and hosts its plugins under
`plugins/`.

## Plugins

| Plugin | Skills | Purpose |
|---|---|---|
| `w3-integration-test` | `generation`, `review` | Generate + review integration test-case specs (結合テスト仕様書) for one screen |
| `w3-rk-scaffold-merging` | `merge` | Merge several child scaffold PRs (same SSOT + `frontend-screen-*` SKILLs) into one integration branch — resolve ID collisions / duplicate rules / §0 counter drift by hand |

> Adding or extending a skill? Read **`CONTRIBUTING.md`** first.

## Install (each teammate, once)

```
/plugin marketplace add <git-url-of-this-repo>      # e.g. git@<host>:<org>/w3-rk-skills.git
/plugin install w3-integration-test@w3-rk-skills
/plugin install w3-rk-scaffold-merging@w3-rk-skills   # scaffold-PR merging
```

Then enable **auto-update** so you always get the latest: `/plugin` → **Marketplaces** tab → toggle
**Enable auto-update** for `w3-rk-skills`. (Third-party marketplaces have auto-update OFF by default.)

## Update to the latest version

With auto-update enabled, a **new session** picks up the latest automatically. To pull an update
right now (or if auto-update is off), run:

```
/plugin marketplace update w3-rk-skills
```

Then **restart / open a new Claude Code session** — a session already running keeps the version it
loaded at start. Check the installed version anytime via `/plugin` → **Manage plugins**.

## Use

Open Claude Code **in the W3 code repo** (the working directory must be the repo that holds
`resources/assets/javascripts/controllers/BaseController.js`), then:

```
/generation <screen_id>         # gen the spec (CSV → Excel)
/review <path-to-.xlsx>          # review an existing spec
```

You can also just say "gen test case for screen X" / "review this TC file" — the skills auto-trigger
by description.

## Examples

### A. With a local DB — pass an env block to pin DB / role / Excel author up front

`screen_id` is the only required argument; everything else is optional. If your machine has the
local Docker DB, you can paste an **env block** right after the screen id so the skill doesn't have
to discover or ask for it (DB container/creds, the test role for setup-SQL, and the Excel
author/date):

```
/generation 633
Env this environment:
CODE_REPO = /path/to/w3package_v2_..._frontend_develop_base
DB local: container=w3package_v2_..._mysql-1, db=w3package_v2_..., user=root, pass=passw0rd
test_user_roll = 4 (login dialog, local)
Excel author (2.履歴 作成者) = BienND
Excel gen date (作成日/変更日) = 2026-06-03
```

- `CODE_REPO` defaults to the session cwd — only state it if you opened Claude Code elsewhere.
- `DB local: …` fills the §3 placeholders so the preflight uses your container/creds directly.
- `test_user_roll` becomes the `<test_user_roll>` value in setup SQL (otherwise it's re-derived
  from the DB, or left as a placeholder in source-only mode).
- `Excel author` / `Excel gen date` are only used when you later ask for the Excel.

### B. No DB / no Docker — source-only mode

If the machine has no Docker or no MySQL, just invoke with the screen id (no DB block). The skill
runs its preflight, finds no DB, **announces source-only mode**, and generates 100% from the source
code + runtime docs (controller + BaseController + view + Laravel BE + `SCREEN_MAPPING`):

```
/generation 633
(no Docker/MySQL on this machine — generate from source only)
```

- The DB only ever **confirmed** metadata; the real ground truth is the code, so coverage barely
  degrades.
- `<test_user_roll>` stays a literal placeholder — the tester resolves it on their own env.
- The one TC that needs `screens.is_top` (`画面表示 available=0`) is dropped if `SCREEN_MAPPING`
  doesn't give it (`available=0` is a no-op anyway, so dropping is safe).
- A wrong DB cred is different: if a DB **is** present but the creds/name fail, the skill asks you
  for the correct values instead of silently falling back.

### C. Review an existing spec

`/review` needs the **`.xlsx` path** + the **`screen_id`** (it confirms the id matches the file's
1.概要). It reads the screen the same way `generation` does, then writes an Add / Modify / Delete
report — it never edits the reviewed file.

```
/review "/path/to/【W3...】結合テスト仕様書_出荷状況照会 (一覧) (screen_id=633)_ver1.0.xlsx" 633
```

You can also just say "review KhoaNA's TCs for screen 633" and drag the file in. The same env rules
apply: pass a `DB local: …` block if you want it to confirm metadata against your DB, or invoke with
no DB and it runs **source-only mode** (reviews 100% from code + docs). No Excel author/date is
needed — review produces a `.md` report, not an Excel.

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

Edit a skill under `plugins/w3-integration-test/skills/{generation,review}/`, then **bump the
`version`** in `plugins/w3-integration-test/.claude-plugin/plugin.json` (semver) and push:

```
# bump version: 1.0.0 → 1.0.1 (patch) / 1.1.0 (feature) / 2.0.0 (breaking)
git add -A && git commit -m "…" && git push
```

🔴 **Auto-update fires only when `version` changes.** With an explicit `version`, a push that does
NOT bump it will NOT reach teammates — always bump the version on a release. Teammates with
auto-update enabled then get it on their next session.

## Layout

```
w3-rk-skills/
├── .claude-plugin/marketplace.json
└── plugins/
    ├── w3-integration-test/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/
    │       ├── generation/   (SKILL.md · references/ · scripts/ · assets/)
    │       └── review/        (SKILL.md · references/ · scripts/)
    └── w3-rk-scaffold-merging/
        ├── .claude-plugin/plugin.json
        └── skills/
            └── merge/         (SKILL.md · references/ · scripts/verify_scaffold.py)
```
