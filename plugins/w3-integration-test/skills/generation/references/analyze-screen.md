# Analyze the Screen (phase 1 → screen-analysis.md)

> Phase 1 of generation: read the AngularJS source until the screen's behavior is concrete,
> then write `screen-analysis.md`. **Extract exact values from code — never guess.** Paths are
> relative to `CODE_REPO` (see `project-config.md`).

---

## Read the screen — AngularJS UI + Laravel backend (read DEEPLY, don't guess)

1. **Route** — open `resources/assets/javascripts/apps/<Domain>App.js`, find
   `when('<angular_route>', …)`. Extract: controller name, templateUrl, page title.
2. **Metadata** — `docs/frontend_mig/screen-func-mapping/screen-id-mapping.md`: screen_id,
   api_endpoint, screen_type (List/Detail/Edit/Special), Next.js URL. (Primary route↔id↔controller
   source — `screens_url_mapping.csv` is dropped.) Cross-check with the DB query below **if a DB
   exists**; in source-only mode (`project-config.md` §3.3) this doc IS the metadata source.
3. **Controller** — `resources/assets/javascripts/controllers/<domain>/<Xxx>Controller.js`.
   Read the **ENTIRE** file. For each `$scope.fn`: selection check, API call (trace to Service
   if delegated), navigation + query params, modal type, filter ops, prereq fetch, and **every
   distinct branch** (if/else/switch/tab — 1 branch = 1 TC, never merge "A or B" into one row).
   Also read `var primaryKey` and initial `$scope.params`.
4. **Template** — `resources/views/templates/<ns>/<name>.php` (templateUrl `.`→`/`, add `.php`).
   Extract: tab names (`k-tab-strip`), expand row (`detail-template`), summary/footer row,
   row-click detail redirect, and which PHP modal helpers are rendered.
5. **Func-mapping** — `<domain>-screen-func-mapping.md`: per func → `func_name`, `is_display`,
   `api_button_id`. Used for Gate B cross-check only (stale; not button ground-truth — see
   `gates-workflow.md` §assume-all-enabled).
6. **Backend (Laravel) — trace each action's REAL behavior.** For every mutation/action, follow
   the call from the AngularJS `$scope.fn` into the BE and read it:
   - API controller `app/Http/Controllers/API/<Entity>Controller.php` — the endpoint + `$rules`.
   - The Service it delegates to: `app/Services/Standards/<Service>.php`, or an
     `app/Services/Alternatives/<vendor>/` override if the unit uses one.
   - Model `app/Models/<Entity>Observer.php` (`$this->RU(...)` → business validation: errorCode + message)
     and the Model itself for what gets written.
   - **Concurrency control (form/edit/create screens)** — does update compare a version / `updated_at`
     / `lock_*` column (optimistic lock) and what error does it raise? is there a unique index
     (duplicate-key error)? Read the FE save `$scope.fn` too (does it send the loaded version, how does
     it handle the conflict response?). This decides the §concurrent-conflict TC's EXPECTED.
   - `app/Http/Controllers/Directs/MessageController.php` for the exact modal text.
   - **External-API / integration buttons** (STREAM, Shopify, payment, IF import/export, etc.):
     trace the integration service — its failure modes (API error, missing/expired token,
     not-installed, needs-reinstall, no available interface → E030) are real branches that do
     **not** appear in the AngularJS controller. Enumerate each one in the Branches table.
   Understand **what the action actually does**: success path, every branch/condition (status/flag/
   role checks that change the outcome), side effects (which tables/fields it writes), and exact
   error codes/messages. This is what makes EXPECTED concrete and the branch list complete —
   never infer backend behavior from the AngularJS surface alone.

> Domain ← route prefix: `/sh_*`→sh (sub-folders sh_inspections/sh_results/sh_histories/…),
> `/ar_*`→ar, `/st_*` `/inv_*`→st, `/outbounds*`→outbound. If unsure, screen-id-mapping.md gives
> the exact controller path. The old `.cursor/Common Prompts/docs-mapping.md` does NOT exist —
> use the tables here + screen-id-mapping.md.

## DB metadata query (run after the preflight in project-config.md §3.1) — only if a DB exists

🟢 **No DB / no Docker → skip this section entirely** and source the same fields from docs+code per
`project-config.md` **§3.3** (SCREEN_MAPPING for screen row/tabs; controller + BaseController +
`<domain>-screen-func-mapping.md` + stg for buttons; `available`/`is_display` are not ground truth).
The queries below merely *confirm* what the code already tells you.

```sql
SELECT s.id, s.alias_nm, s.top_scr_nm, s.sub_scr_nm, s.url, s.parent_screen_id, s.is_top, s.grp, s.component_id,
       parent.alias_nm AS parent_alias_nm, parent.top_scr_nm AS parent_top_scr_nm
FROM screens s LEFT JOIN screens parent ON parent.id = s.parent_screen_id WHERE s.id = <X>;
SELECT id, alias_nm, sub_scr_nm, tab_id FROM screens WHERE parent_screen_id = <X> ORDER BY tab_id;
SELECT us.id, us.unit_roll_id, us.is_display, us.available, us.can_csv FROM unit_screens us WHERE us.screen_id = <X>;
SELECT uba.id, uba.nm, uba.func, uba.is_display, uba.ord FROM unit_button_apis uba
  JOIN unit_screens us ON us.id = uba.unit_screen_id WHERE us.screen_id = <X> ORDER BY us.unit_roll_id, uba.ord;
```
DB present but a query fails → ask the user (project-config.md §3.2). DB absent → source-only (§3.3).

## 🔴 Reading rules (do not skip)

- **Read BOTH layers deeply — understand the logic, don't guess.** Trace the full path: AngularJS
  (view → controller `$scope.fn` → BaseController) for the UI flow, AND Laravel (route → API
  controller → Service → Model/Observer) for the real backend behavior. Every EXPECTED outcome,
  branch, validation and side effect must come from code you actually read — not assumptions, not
  the AngularJS surface alone.
- **Read the WHOLE controller, plus BaseController** for inherited funcs (`getCsv`, `_doPrint`,
  `showModalMultiUpdateNeedsInvoice`, …). Counting `$scope.*` from a partial read misses
  inherited buttons. Don't confuse sibling controllers (e.g. 148 vs 172, 158 vs 601) — verify
  `$scope._screenId` / `$scope._screens["…"]`.
- **Don't drop default API params.** Initial `$scope.params` (e.g. `from_date`, `to_date`,
  `status`, `kind`) define the default filter and belong in 初期表示 context. Capture them.

## Output — `screen-analysis.md`

Write to `<cwd>/w3-rk-skills-output/w3-integration-test/generation/<slug>(screen_id=<X>)/screen-analysis.md` (see `project-config.md` §2):
Metadata (screen_id, api_endpoint, route, nextjs_url, controller_file, template_file,
screen_type, page_title) · Keys (primary_key, csv_filename, extra_params) · Component features
(expand_row, detail_redirect, summary_row) · **Concurrency control** (form/edit/create: optimistic
lock via version/`updated_at`/`lock_*`? unique index? conflict error code+message — for
§concurrent-conflict) · Functions table is_display=1 and =0 ·
**Branches** (1 branch = 1 row: branch_id, condition, outcome, source) · Function Details ·
Notes / Ambiguities.

🔴 **Record `screen_type` accurately (List / Detail / Edit-Form)** — it decides the S2/S3 patterns
and which gold example to mimic: **list** → `references/example-589.csv`; **form/edit** →
`references/example-edit-430.csv`. A form/edit screen uses `項目表示` + per-field validation
(`mimosa-rules.md` §form-field-validation), **not** `グリッド列表示` + row-guards.
