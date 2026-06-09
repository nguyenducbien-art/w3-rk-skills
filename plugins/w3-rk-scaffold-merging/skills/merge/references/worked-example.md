# Worked example — merging 4 scaffold PRs (#10007 / #9999 / #9981 / #10003)

> A real run (W3 mimosa, sprint branch `mimosa/frontend/develop/r20260601`, 2026-06-09). Four open
> PRs each edited the same SSOT (`w3-frontend-standard.md`) + the same `frontend-screen-*/SKILL.md`
> files. Merging them naively would have produced **three duplicate rule IDs** and broken counters.
> This is the concrete shape of every section in `merge-workflow.md` / `conflict-resolution.md`.

## The four PRs (§inputs)

| PR | author | adds |
|---|---|---|
| #10007 | bien | `NAME-NEW-02` + `UI-NEW-12〜18` / `API-NEW-10`・`11` / `DATA-NEW-02` + Anti-Pattern #24-34 |
| #9999 | khoana | `API-NEW-10` (POST body key) + strengthen `UI-NEW-08/10`・`NAV-NEW-03`・AP #7 |
| #9981 | datpt | `FILTER-NEW-01` + `SDUI-NEW-05` (endpoint switch) + apiId / dead-handler (AP #35/#36) |
| #10003 | minhnn | `UI-NEW-12` (external-integration triage) + `API-NEW-02` (tMessages) + `SDUI-NEW-05` (operator) |

All four touched `rules/w3-frontend-standard.md` + `implementation/SKILL.md` + `parity-review/SKILL.md`
+ `reference-build/SKILL.md` → heavy overlap.

## §baseline

Sprint tip (`a6a768c2`, **before any of these 4 PRs**) §0: 既存 125 / 新規 58 / 合計 約183 /
Anti-Pattern 23; ID table `UI-NEW`=11, `API-NEW`=9, `SDUI-NEW`=4, `NAME-NEW`=1, `FILTER-NEW`=none.
This is the ground truth; the next-free map **starts here and advances as each PR is merged**. After
the #10007 trunk ff (it adds `UI-NEW-12〜18` / `API-NEW-10`・`11` / `DATA-NEW-02` / `NAME-NEW-02`) the
map has moved to `UI-NEW`→19, `API-NEW`→12, `SDUI-NEW`→05, `FILTER-NEW`→01 — which is exactly what
#9999 / #9981 / #10003's collisions then rename against (§trunk-first).

## The 3 collisions + 1 duplicate (§id-collision / §content-duplicate)

| Item | conflict | resolution |
|---|---|---|
| `UI-NEW-12` | #10007 (funcRegistry key) vs #10003 (external triage) | keep #10007; #10003 → **`UI-NEW-19`**, rename all its refs (templates, orchestrator, parity §B, reference-build) |
| `API-NEW-10` | #10007 (WARN/null-safe) vs #9999 (POST body key) | keep #10007; #9999 → **`API-NEW-12`** |
| `SDUI-NEW-05` | #9981 (endpoint switch) vs #10003 (operator-shape filter) | keep #9981 (endpoint); #10003's operator rule = **duplicate** of #9981's `FILTER-NEW-01` → **drop**, **salvage** #10003's `toKendoFilter` round-trip test into FILTER-NEW-01 |
| Anti-Pattern `#24` | #10007 (funcRegistry) vs #9981 vs #10003 | keep #10007 #24; #9981's → **#35/#36**; #10003's dropped with its rule |

## §trunk-first + §per-pr-loop (the merge order)

1. **#10007** (trunk — most rules, based on the tip, counters clean) → `git merge --ff-only`. New
   baseline: 新規 67, AP 34, `UI-NEW`=18, `API-NEW`=11.
2. **#9999** → applied by hand: `API-NEW-10` → **`API-NEW-12`** (section header `〜11`→`〜12`, ID-table
   `API-NEW` 11→12, 新規 +1); `UI-NEW-08/10` / `NAV-NEW-03` / AP #7 text extended verbatim. Commit.
3. **#9981** → `FILTER-NEW-01` + `SDUI-NEW-05`(endpoint) used as-is (slots free); its AP #24/#25 →
   **#35/#36**; new prefix row `FILTER-NEW`=1; `SDUI-NEW` 4→5; header `(SDUI-NEW-01〜04)`→`〜05`. Commit.
4. **#10003** → `UI-NEW-12`→**`UI-NEW-19`** (+ all refs); `API-NEW-02`(tMessages) kept; orchestrator
   warning-triage kept; `SDUI-NEW-05`(operator) + its AP **dropped** (dup); round-trip test salvaged
   to FILTER-NEW-01. Commit.

After each: `verify_scaffold.py` → `OK`, then phrase-grep + "no stray un-renamed ID" grep
(`§verify-each-step`). e.g. after #10003: `grep -c 'UI-NEW-12'` in the 4 templates + orchestrator = 0
(all became `UI-NEW-19`), while `UI-NEW-12` = funcRegistry stays exactly once in the SSOT.

## §reconcile (the drift that pre-dated these PRs)

`verify_scaffold.py` after the 4 PRs showed the **declared** §0 counters lagged the **real** rows
(pre-existing drift, not caused by the PRs): §2 actually had **97** rules but 新規追加 read 71; the
ID-table `EDIT-NEW` said 2 but §2 had `EDIT-NEW-01..06` (=6). One `chore:` commit set 新規追加→97,
合計→222, `EDIT-NEW`→6; and reconciled parity-review's mirrors: `現在 72 ID`→**97** (×4 + breakdown),
`Anti-Pattern 25 項目`→**36** (tied to §3=36), `1〜25 通し番号`→`1〜36`. Final `verify_scaffold.py`:
`OK (§2 rules=97, §3 anti-patterns=36, declared 新規追加=97 / Anti-Pattern=36)`.

**Lesson (a PR reviewer / Copilot caught what this pass missed):** the first reconcile fixed
parity-review but left two mirrors stale — orchestrator's `内部フロー` (`規約 約72`→97, `Anti-Pattern
16 項目`→36, and a hard-coded `16 共通 TC` that parity-review §D itself calls wrong) and parity-review's
必須参照 line `Anti-Pattern 25 個` (a `個` spelling the `項目` sweep didn't match). Both were `verify_scaffold.py`-clean (the script checks the SSOT, not the mirrors). Fix: sweep **every** sub-skill
and **every** spelling (`個` / `項目` / `件`) at `§reconcile` — `conflict-resolution.md §verify-each-step`
item 4. This is exactly why §counter-reconcile now enumerates the mirror locations.

## §finish

5 commits on the integration branch (4 integrations + 1 reconcile). Then, **on the user's explicit
go-ahead each**: unset upstream off the sprint branch → `git push -u origin <integration-branch>` →
`gh pr create` into `r20260601` (body = the collision table above + commit list) → `gh pr comment`
+ `gh pr close` each of #10007/#9999/#9981/#10003 with a per-PR note (how its content was
handled). ⚠️ Flagged to the user: the integration branch did **not** carry the children's original
commits (content rebuilt by hand for the renames/drops) → closing them is close-not-merge.
