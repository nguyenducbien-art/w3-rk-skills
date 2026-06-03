# Project Config — W3 Mimosa

> This file is the single source of paths, DB credentials, branch, and test-environment values.
> Distributed as a **plugin** (`w3-integration-test` @ `w3-rk-skills`): the skill lives in the plugin
> install dir, NOT in the code repo. So **`CODE_REPO` = the session cwd** (the W3 repo you opened
> Claude Code in) and **output goes to `<cwd>/w3-rk-skills-output/`** — see §1 / §2.
>
> **No per-machine edit is needed** for paths — cwd is the anchor. The only optional per-machine
> thing is the local **DB** (§3) — discovered via the §3.1 preflight (fail→ask), or skipped via
> source-only mode (§3.3).
>
> 🔴 **DB connection + unit values are machine-specific.** The DB container/name/password (§3)
> are **placeholders to fill** (or discover the container via the §3.1 preflight). The
> unit_id / unit_roll_id (§7) are example values to **re-derive** on this machine. **Never
> assume; never guess a container name or fabricate a unit_roll_id.** Run the §3.1 preflight
> before relying on any DB value; if a docker/SQL command fails or a lookup returns
> empty/different — **STOP and ask the user** (§3.2).
>
> 🟢 **The DB is OPTIONAL — it only confirms metadata.** When the machine has **no Docker / no
> MySQL at all**, do NOT block: switch to **source-only mode** and generate 100% from the source
> code + the runtime docs (`SCREEN_MAPPING` + func-mapping + controller/view/BE). See **§3.3**.
> The ground truth for buttons/branches is the code anyway (§assume-all-enabled), so a missing DB
> degrades almost nothing. Distinguish "no DB exists" (→ §3.3 fallback) from "a DB exists but the
> creds/name are wrong" (→ §3.2 ask).

---

## 1. CODE_REPO = the session's current working directory

🔴 The skill is installed as a **plugin** (not inside the code repo), so it resolves the code under
test from the **session cwd** — the repo you opened Claude Code in:
```
CODE_REPO = the current working directory of the Claude Code session
```

**Confirm `CODE_REPO` is really the W3 code repo** (look for these markers under cwd):
- `resources/assets/javascripts/controllers/BaseController.js`
- `docs/frontend_mig/screen-func-mapping/screen-id-mapping.md`

Markers **not** found → you opened Claude Code somewhere else, or the code is laid out differently
on this machine → **ask the user** for the code-repo path (do not guess). Same fail→ask rule as §3.2.

> If the base branch is missing something the screen needs, the user may point you at a
> feature-branch clone (`CODE_REPO_V2`) — ask; don't guess a path.

## 2. Output location — under the session cwd (NOT inside the plugin)

🔴 Deliverables are written under the **session cwd**, mirroring the skill identity
`<marketplace>/<plugin>/<skill>/`, so they survive plugin updates and never pollute the product repo:
```
<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=<X>)/
```
`<slug>` = kebab-case from the AngularJS URL (e.g. `/st_inventory_creates` → `st-inventory-creates`),
so screen 313 → `st-inventory-creates(screen_id=313)`. The screen's `build_csv.py` is copied INTO this
folder, so its `OUT_DIR = Path(__file__).resolve().parent` resolves correctly once it sits there.
🔴 Add `w3-rk-skills-output/` to the code repo's `.gitignore` (or global excludes) — never commit QA
deliverables into the product repo. If the user wants another location, honor it.

**Working files for one screen** (all directly in the screen folder):
`screen-analysis.md` · `build_csv.py` · `Testcase_Output_<alias>_ScreenID (X)_base.csv` (bilingual) ·
`sql/test-data-sql.md` (if any setup SQL).

**The Excel deliverable goes in its OWN sub-folder** (the IT-delivery folder), on request:
```
<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=<X>)/
├── screen-analysis.md · build_csv.py · Testcase_Output_…_base.csv · sql/   (working files)
└── <alias> (screen_id=<X>)_QAテスト/                                       (Excel delivery folder)
    └── 【W3 フロントエンドマイグレーション】結合テスト仕様書_<top_scr_nm> (<sub_scr_nm>) (screen_id=<X>)_ver1.0.xlsx
```
- Excel folder = `<alias> (screen_id=<X>)_QAテスト` (alias = `screens.alias_nm`). `build_xlsx.py`
  creates it automatically next to the CSV.
- `<top_scr_nm>` = `screens.top_scr_nm`; if the target is a sub-screen with empty `top_scr_nm`,
  use the **parent** screen's (e.g. 172 empty → parent 158 = `検品作業実績`).
- `<sub_scr_nm>` = `screens.sub_scr_nm`. Initial version `ver1.0`. Excel only when the user explicitly asks (not auto).
- 🔴 **Screen display name** (1.概要 N36 + the file name + every `[<name> (screen_id=X)]` reference):
  prefer the screen's **user-facing name** — the App-routing page title (after `W3 mimosa | `) / the
  open-button label — when it is fuller than DB `alias_nm` (e.g. `出荷指示登録・修正`, not the shorter
  `出荷指示登録`). Keep it consistent with the page-title TC and all references; don't name the same
  screen two ways (`writing-rules.md` §nav-button-modal).

## 3. Local DB (Docker — runs on CODE_REPO) — OPTIONAL, FILL per machine (or skip → §3.3)

| Key | Value (fill per machine — placeholders) |
|---|---|
| Container | `<mysql-container>` |
| Database | `<db-name>` |
| User / Password | `<db-user>` / `<db-pass>` |

Query command template (substitute the values above; discover the container via §3.1):
```bash
docker exec <mysql-container> \
  mysql -u<db-user> -p<db-pass> -D <db-name> -e "<SQL>"
```
Permission: may run any SQL related to the screen being generated — **local DB only**, never stg.

### 3.1. Preflight — run ONCE before the first DB query

Confirm the container + DB are reachable before depending on any DB value:
```bash
# (a) is the container running? prints the name if found, empty if not
docker ps --format '{{.Names}}' | grep -i mysql
# (b) can we reach the DB? prints the screens count, errors if db/creds wrong
docker exec <CONTAINER> mysql -u<USER> -p<PASS> -D <DB> -e "SELECT COUNT(*) FROM screens;"
```
Classify the result before deciding what to do:
- **No DB exists at all** — `docker` not installed (`command not found`), the daemon is down
  (`Cannot connect to the Docker daemon`), or (a) finds **no mysql container** → there is nothing
  to connect to → **go to §3.3 (source-only mode)**, do not ask for creds.
- **A DB exists but is unreachable** — (a) finds a mysql container but (b) errors (access denied /
  unknown database / no such container name) → the creds/name are wrong → **§3.2 (ask)**.
- **Both pass** → use the DB normally (the metadata queries in `analyze-screen.md`).

### 3.2. 🔴 DB exists but misconfigured → ASK the user (do NOT guess)

If a mysql container **is present** but the preflight or a later SQL command fails (wrong
creds/db/name), **stop and ask the user** for the correct values, then use the answers for the
rest of the session (and offer to update this file). Ask concisely, e.g.:

> "The local DB command failed (`<paste the error>`). Please provide the MySQL **docker
> container** name, the **database** name, and **user/password** — or run the SQL yourself
> and paste the result."

(Phrase the actual question to the user in their language — default English — per SKILL.md's
communication rule; the example above is the wording to use, since skill files are kept English.)

Never: invent a container name, try random names in a loop, or fall back to stg. When a DB
genuinely exists, prefer it over the source-only fallback — but a **wrong cred** does not force
the session to halt forever: if the user says "no DB / just use the source", switch to §3.3.

### 3.3. 🟢 No DB / no Docker → SOURCE-ONLY mode (generate 100% from code + docs)

When there is no DB to reach (per §3.1 classification), or the user states the machine has no
Docker/DB, **announce it once** ("No DB on this machine → generating TCs 100% from source code + docs") and
generate from source. The DB only ever **confirmed** metadata; the real ground truth is the code.
Replace each DB query (`analyze-screen.md` §DB metadata query) with its source/doc equivalent:

| DB query (when a DB exists) | Source-only equivalent (no DB) |
|---|---|
| `screens` row — alias_nm, top_scr_nm, sub_scr_nm, url, screen_type, parent_screen_id, is_top | `SCREEN_MAPPING` (§5): 画面名, screen_id, 種別→screen_type, AngularJS URL, Controller. Split 画面名 on `_` → `top` / `sub` for Excel naming (e.g. `出荷状況照会_一覧` → top=`出荷状況照会`, sub=`一覧`), or take the user's `--top`/`--sub`/`--screen-name`. |
| child screens / tabs (`parent_screen_id=X`) | rows in `SCREEN_MAPPING` sharing the same top name + the `k-tab-strip` tabs in the view |
| `unit_screens` — is_display / available / can_csv | **not needed**: `available`=runtime no-op; `is_display` is not button ground-truth (§assume-all-enabled); `can_csv` is enabled via the setup-SQL placeholder in PRE, not read here |
| `unit_button_apis` — nm / func / is_display / ord | button ground-truth = **controller + BaseController + `<domain>-screen-func-mapping.md`** (func, nm, is_display, api_button_id) **+ stg UI** — the PREFERRED source even when a DB exists (§assume-all-enabled). The local seed was never authoritative. |

What degrades (handle, don't block):
- **`is_top` is unknown without the DB.** The S2 `画面表示 (available=0)` edge TC is only valid when
  `screens.is_top=1` (`mimosa-rules.md`). If `SCREEN_MAPPING` doesn't give it, **drop that one TC** —
  `available=0` is a no-op regardless, so dropping is always safe.
- **Excel naming** (`top_scr_nm` / `sub_scr_nm` / `alias`) → from 画面名 above or the user's CLI args;
  `build_xlsx.py` takes `--top/--sub/--screen-name` and needs no DB.
- **Setup SQL inside the TCs is unaffected** — it always uses the `<test_user_roll>` placeholder and
  JOINs via `screen_id` (never a local id, §7 / `writing-rules.md`); the **tester** runs it on their
  own stg/local env, so the generating machine needs no DB for it.

Still never **fabricate** a screen name/type. If `SCREEN_MAPPING` lacks the screen AND you cannot
grep it from `apps/*.js` + the controller folder, ask the user for the **route / controller** (not
DB creds). Source-only mode changes the *source* of metadata, not the rule "extract from what you
actually read, never guess".

## 4. Git source branch

| Key | Value (project-specific — set per project) | Purpose |
|---|---|---|
| Base branch | `mimosa/frontend/develop/base` | The branch to read code from (source of truth for TC generation) |

Read the code at this branch (or whatever the repo is currently checked out to). No cross-branch diff is performed.

## 5. Runtime docs in CODE_REPO (runtime input — read live, NOT bundled)

| Key | Path (relative to `CODE_REPO`) | Used for |
|---|---|---|
| `SCREEN_MAPPING` | `docs/frontend_mig/screen-func-mapping/screen-id-mapping.md` | screen_id ↔ alias ↔ AngularJS URL ↔ controller ↔ Next.js URL (PRIMARY lookup) |
| `FUNC_MAPPING` | `docs/frontend_mig/screen-func-mapping/<domain>-screen-func-mapping.md` | Gate B cross-check only (stale — NOT button ground-truth) |

> ⚠️ `screens_url_mapping.csv` is **dropped — never use it.** For route↔screen_id, use
> `SCREEN_MAPPING` (always the primary), or — only when a DB exists — `SELECT id, alias_nm, url
> FROM screens WHERE url='/xxx'`. If `SCREEN_MAPPING` is missing: with a DB, fall back to that
> query; in **source-only mode (§3.3)**, grep `apps/*.js` (`$routeProvider.when('/xxx', …)`) + the
> controller folder; if still not found, ask the user for the route/controller.

## 6. Source-code paths in CODE_REPO (read live to confirm behavior)

| What | Path (relative to `CODE_REPO`) |
|---|---|
| AngularJS controllers | `resources/assets/javascripts/controllers/<domain>/<Xxx>Controller.js` |
| BaseController (inherited funcs) | `resources/assets/javascripts/controllers/BaseController.js` |
| View templates | `resources/views/templates/<ns>/<name>.php` |
| App routing (page title) | `resources/assets/javascripts/apps/<Domain>App.js` |
| Toolbar/modal helpers | `app/Helpers/ViewHelpers.php` |
| Modal message codes | `app/Http/Controllers/Directs/MessageController.php` |
| MAX constants | `resources/assets/javascripts/settings/Consts.js` |
| API validation (`$rules`) | `app/Http/Controllers/API/<Entity>Controller.php` |
| Business validation | `app/Models/<Entity>Observer.php` |

> The hard facts already extracted from these files (modal codes, MAX values, helper
> line numbers, CSV filename pattern) are cached in `mimosa-facts.md` — read that first,
> open the source only to confirm a screen-specific detail.

## 7. Test environment (for setup SQL placeholders `<test_user_roll>`) — DEFAULTS, verify per machine

| Env | Unit | `unit_id` | `unit_roll_id` | Notes |
|---|---|---|---|---|
| **stg** | `rk-unit11` | 852 | **4535** | primary, full data |
| **stg** | `rk-unit22` | — | — | empty 棚卸調査 (empty-state TC) |
| **local** | `ユニット (シーダー)` | 1 | **4** | login `dialog` (user_id=1); both rolls seed all screens |

stg AngularJS URL: `https://mimosa-stg-legacy.dialog-wms.com/` (old `mimosa-stg.dialog-wms.com` is dead — do not use).

🔴 **`unit_id` / `unit_roll_id` are per-environment — NEVER hard-code them into setup SQL.**
The local values above are defaults from one machine; on another machine the seed may give
different ids. **Always re-derive on this machine before writing any setup SQL**, and if the
query returns empty or a value different from the default, use the derived value (or ask the
user which login/unit to target):
```sql
-- replace <login> with the local login (default: dialog)
SELECT ur.id AS unit_roll_id, ur.unit_id FROM unit_rolls ur
JOIN unit_user_permissions uup ON uup.unit_roll_id=ur.id
JOIN users u ON u.id=uup.user_id
WHERE u.act_nm='<login>' AND ur.deleted_at IS NULL;
```
- Query empty / login unknown on this machine → **ask the user**: which login + unit_roll to
  use as `<test_user_roll>`.
- **Source-only mode (§3.3): you cannot re-derive without a DB — do NOT ask for it.** Just leave
  `<test_user_roll>` as the literal placeholder; the tester resolves it on their own env (the
  table above gives the known stg/local defaults for reference). Setup SQL is run by the tester,
  not the generating machine.
- In all generated setup SQL, write `<test_user_roll>` as a **placeholder** and JOIN via
  `screen_id` (master) — never a hard-coded local id (per `writing-rules.md` / no-hardcode-id rule).

## 8. Bundled skill resources (relative to the skill folder — DO NOT edit paths)

| Resource | Path |
|---|---|
| Excel skeleton (= screen 589) | `assets/template.xlsx` |
| Gold example (readable) | `references/example-589.csv` |
| Generators | `scripts/build_csv.py`, `scripts/build_xlsx.py` |

Scripts resolve the template via `Path(__file__).resolve().parents[1] / "assets" / "template.xlsx"` —
they find it regardless of where the repo is checked out.
