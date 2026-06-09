# Verify rules — what `scripts/verify_scaffold.py` enforces

> The merge is only as safe as its self-check. After **every** per-PR apply (and after the
> reconcile pass), run `python3 scripts/verify_scaffold.py <SSOT>` and get `verify: OK` before
> committing. Each rule below is a `§slug` the script cites in its WARN lines. The script never
> auto-fixes — it tells you exactly what drifted so you fix it by hand.
>
> `<SSOT>` = the scaffold's single source of truth rules file. For W3 mimosa that is
> `.claude/skills/frontend-mig-shared/rules/w3-frontend-standard.md` (`project-config.md §scaffold-files`).

These four checks are precisely the failure modes that **break the scaffold (足場)** when several child
PRs each edit the same SSOT.

🔴 **Scope: this script checks the SSOT only.** The sub-skill *mirror* counters (parity-review
§A/§C/必須参照, orchestrator 内部フロー — `現在 N ID`, `Anti-Pattern N 個/項目`, etc.) are **not**
script-checked; sweep them by hand at `§reconcile` (`conflict-resolution.md §verify-each-step` item 4).
A green `verify: OK` here does **not** mean the mirrors are in sync.

## §no-dup-id

A `{PREFIX}-NEW-{n}` rule ID must be **defined exactly once** in §2. Two definitions of the same ID
means an **ID collision was left un-renamed** — e.g. PR-A and PR-B both add `UI-NEW-12` with
different content. The fix is in `conflict-resolution.md §id-collision` (rename the later one to the
next free number). The script collects every §2 rule row and warns on any repeated ID.

✅ `UI-NEW-12` (funcRegistry) kept, the other PR's `UI-NEW-12` renamed to `UI-NEW-19` → each ID once.
❌ Two `| UI-NEW-12 | … |` rows → `WARN §no-dup-id: rule ID 'UI-NEW-12' is defined more than once`.

## §counter-newcount

§0 `新規追加: **N 件**` must equal the **real §2 rule-row count** (`grep` of `| {PREFIX}-NEW-{n} |`
between `## 2.` and `## 3.`). After applying a PR that adds *k* new rules, bump 新規追加 by *k*; the
script verifies the declared number against the actual rows. This is the counter that drifts most
(see `conflict-resolution.md §counter-reconcile`).

✅ §2 has 97 rows ⇒ `新規追加: **97 件**`.
❌ §2 has 97 rows but text says `**71 件**` → `WARN §counter-newcount: §0 新規追加 = 71 but §2 has 97 rule rows`.

## §counter-idtable

The §0 「規約 ID 体系」 table breaks 新規追加 down by prefix. Two invariants:
1. each prefix's table count == the real `grep` count of that prefix in §2, and
2. the table sums to 新規追加.

A row whose value cell carries a suffix (`1 (規約行き分)`) still counts as the leading integer.

✅ `| EDIT-NEW | 編集画面 | 6 |` when §2 has `EDIT-NEW-01..06`.
❌ `| EDIT-NEW | 編集画面 | 2 |` while §2 has 6 → `WARN §counter-idtable: ID-table 'EDIT-NEW' = 2 but §2 has 6`.

## §counter-antipattern

§0 `Anti-Pattern: **N 件**` must equal the **§3 row count** (`| <number> | … |` data rows between
`## 3.` and `## 4.`; the `## 4.` PoC-anti-pattern section is excluded). When a PR adds anti-patterns,
bump this and the `## 3. Anti-Pattern 一覧 (N 件)` heading together.

✅ §3 has #1..#36 ⇒ `Anti-Pattern: **36 件**`.
❌ §3 has 36 rows but text says `**34 件**` → `WARN §counter-antipattern: §0 Anti-Pattern = 34 but §3 has 36 rows`.

---

## Adapting the markers

The script's regex constants (top of `verify_scaffold.py`, the `RE_*` block) match the W3
`w3-frontend-standard.md` layout (`## 2.` / `## 3.` / `## 4.`, `新規追加: **N 件**`,
`Anti-Pattern: **N 件**`, the ID-table rows). If a different scaffold lays its SSOT out another way,
change **only** those regexes — the four checks above are layout-independent. Always finish with
`python3 verify_scaffold.py --self-test` (it unit-tests all four §slugs on a good + a bad fixture)
before relying on a changed script.
