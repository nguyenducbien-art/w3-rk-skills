# Merge workflow — step by step

> The spine of a scaffold merge. Each step cites the reference that governs it. The golden rule
> (`conflict-resolution.md §manual-not-merge`): you **never raw `git merge` the child branches** — you
> apply each PR's intent by hand so renames / counter bumps / duplicate-drops stay under control and
> the scaffold (足場) never silently breaks. Communicate with the user in their language; commit messages
> and file content are English/Japanese only.

## §inputs

Collect, then stop-and-ask for anything missing:
- **The child PRs** (numbers or URLs) — the scaffold PRs to merge. Required.
- Confirm `CODE_REPO` (`project-config.md §repo`) and that `gh` can read the PRs (`gh pr view <n>`).

Then **classify** the PRs — this skill applies only when they are *scaffold* PRs that **overlap**:
`gh pr view <n> --json files` for each; confirm they edit the shared SSOT / sub-skill files
(`project-config.md §scaffold-files`) and that 2+ of them touch the **same** file. If they don't
overlap, a normal review/merge is enough — say so and stop. Note who authored each (some are
teammates' — relevant at §finish).

## §baseline

Read the **sprint branch's current** SSOT §0 — this is the authoritative ground truth all counters
reconcile to, NOT any PR's idea of the base:
```bash
git -C <repo> fetch origin <sprint-branch>
git -C <repo> show origin/<sprint-branch>:.claude/skills/frontend-mig-shared/rules/w3-frontend-standard.md | sed -n '1,40p'
```
Record: 新規追加 N, 合計, Anti-Pattern N, and the §0 ID-table per-prefix counts. These give the **next
free number** for every prefix (e.g. `UI-NEW` = 18 ⇒ next free = `UI-NEW-19`) — the key input to
collision renaming (`conflict-resolution.md §id-collision`).

## §diagnose

For each child PR, get its relationship to the sprint branch:
```bash
git -C <repo> merge-base origin/<sprint> origin/<pr-head>          # how old is its base
git -C <repo> rev-list --left-right --count origin/<sprint>...origin/<pr-head>   # behind / ahead
```
A PR that is **far behind** (large left count) branched off an **old** sprint tip → its own §0
counters are stale and **must be reconciled against §baseline, not trusted**. A PR that is `0 behind`
(based on the current tip) merges cleanest. Sort the merge order with the cleanest/most-foundational
PR first (§trunk-first).

## §integration-branch

Create ONE integration branch off the **current sprint tip**, in a clean clone:
```bash
git -C <repo> checkout -B <integration-branch> origin/<sprint-branch>
```
- **Ask the user for the branch name** (do not invent one). A sensible suggestion:
  `<vendor>/frontend/scaffold/integrate-<N>pr` or `…/integrate-<ticket>`.
- 🔴 **Unset the upstream so it does NOT track the sprint/base branch** (project rule — a feature/
  integration branch must not point its upstream at the base):
  ```bash
  git -C <repo> branch --unset-upstream
  ```
  (It auto-tracked the base because you branched off `origin/<sprint>`. Unset now; it will track its
  own `origin/<integration-branch>` after the first push at §finish.)

## §trunk-first

Pick the **trunk PR** (most rules / cleanest counters / based on the current tip / least conflict) and
merge it first. If it is exactly 1+ commits ahead of the sprint tip with no divergence, a plain
fast-forward applies it with **no new commit and no conflict**:
```bash
git -C <repo> merge --ff-only origin/<trunk-pr-head>
```
Then read the merged SSOT §0 — this is the **new baseline** for the next PR (the next-free-number map
has shifted). Run `verify_scaffold.py` once here to confirm the trunk is clean.

## §per-pr-loop

For **each remaining PR**, in order, do all of the following — never skip the verify:

1. **Read the PR's full single-commit diff** (`git -C <repo> show origin/<pr-head> --format=`),
   excluding huge data-file regens you'll glance at separately. Inventory every change.
2. **Verify landing zones** on the integration branch: for each region the PR edits, check whether an
   already-merged PR also touched it (`grep` the anchor). A region touched by both = a **hot zone**
   (the SSOT §0 counters, the parity §C grep table, implementation Step 8 are the usual ones). Read
   the real current text there so your `old_string` matches.
3. **Resolve conflicts** (`conflict-resolution.md`): detect ID collisions (`§id-collision` → rename to
   the next free number) and content duplicates (`§content-duplicate` → keep one canonical, drop the
   other, salvage unique-valuable bits re-tagged).
4. **Apply by hand, edit by edit** (`§manual-not-merge`): apply each `+` hunk verbatim **except** the
   renamed IDs; reconcile the §0 counters incrementally (`§counter-accounting`). Use `Edit` with
   exact `old_string` (you must `Read` each file first). DROP the parts you decided to drop.
5. **Verify** (`§verify-each-step`): run `python3 scripts/verify_scaffold.py <SSOT>` → must be `OK`;
   then grep-confirm each distinctive phrase of the PR is present, the renamed ID appears the right
   number of times, and **no un-renamed collision ID is left** in the PR's kept content.
6. **Commit** this PR (`project-config.md §git-rules`):
   `feat: [mimosa][frontend] integrate PR #<n> into <sprint> (<renames/drops summary>) #<n>`.
   Stage only the scaffold files you changed; **do not push** here.

## §reconcile

After all PRs are applied, run a **counter-reconciliation pass** (one separate commit) —
`conflict-resolution.md §counter-reconcile`. The per-PR accounting keeps counters *consistent with
each PR's deltas*, but the SSOT may carry **pre-existing drift** (a counter that was already wrong on
the sprint branch). Use the grep-actual numbers (`verify_scaffold.py` prints them) as truth: fix §0
新規追加 / 合計 / ID-table, and any mirror counters in the sub-skills (e.g. parity-review's
"現在 N ID" breakdown + "Anti-Pattern N 項目" + "1〜N 通し番号"). Finish with `verify_scaffold.py` → `OK`
and a final sweep that no stale number remains. Commit `chore: … reconcile drift counters …`.

## §finish

The integration branch now holds every PR's content, conflict-free and counter-consistent, all
**local**. Then **ask the user** (do not assume — these are outward-facing, hard-to-reverse):

1. **Push?** "Publish `<integration-branch>` to origin?" — only on an explicit yes (and respect the
   project's standing no-push rule; in auto mode require an explicit go-ahead). On yes:
   `git -C <repo> push -u origin <integration-branch>` (this sets its own upstream — the §integration-branch
   unset is what kept it off the base).
2. **PR into the sprint branch?** "Open a PR `<integration-branch>` → `<sprint-branch>`?" If you don't
   know the current sprint branch, ask (`project-config.md §sprint-branch`). On yes, **show the PR
   title + body draft and get OK** before `gh pr create` (body = the conflict-resolution table + the
   commit list + the list of superseded PRs; no footer).
3. **Close the child PRs?** "Close #<list> now? (some are teammates')" If yes, `gh pr comment` each
   with a per-PR note pointing at the integration PR and stating how that PR's content was handled
   (renamed/dropped/kept), then `gh pr close`. ⚠️ Flag to the user: the integration branch does NOT
   contain the children's original commits (you rebuilt the content by hand), so closing them is
   close-not-merge (their commit attribution is lost) — they should tell the team. Offer "close only
   mine / close all / close none".
