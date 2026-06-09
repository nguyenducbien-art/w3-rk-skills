# Conflict resolution — how to merge without breaking the scaffold (足場)

> When several child PRs edit the **same SSOT + sub-skill files**, the danger is not a normal text
> conflict — it is **silent semantic breakage**: two PRs add the *same rule ID* with *different
> content*, or the *same rule* under *different IDs*, or each bumps a §0 counter assuming it is the
> only PR. Resolve these by the rules below, then `verify_scaffold.py` proves it (`verify-rules.md`).

## §manual-not-merge

🔴 **Do NOT raw `git merge` the child branches.** Reasons:
- A PR branched far behind the sprint tip 3-way-merges against an **old** base; non-conflicting hunks
  apply silently — including a **second `UI-NEW-12` row** git happily appends next to the first (no
  text conflict, but the scaffold is now broken).
- Renaming a colliding ID (`UI-NEW-12` → `UI-NEW-19`) and dropping a duplicate rule **cannot be
  expressed by merge** — they need deliberate edits.
- The §0 counters need per-PR arithmetic, not a line merge.

Instead: read each PR's single-commit diff as a **spec of intent**, and apply it by hand with `Edit`
(exact `old_string`; `Read` the file first). Apply every `+` hunk **verbatim except the renamed IDs
and the dropped parts**. This is slower but it is the only way the result is correct.

## §id-collision  — same ID, different content

Two PRs define the same `{PREFIX}-NEW-{n}` with **different** rules (they each picked "the next free
number" off the same base, unaware of each other). Resolve:

1. Pick **one keeper** for that ID (usually the PR merged first / the trunk). It keeps the number.
2. **Renumber the other** to the **next free number** for that prefix (from §baseline / the running
   map). e.g. base `UI-NEW`=18, trunk took `UI-NEW-12` ⇒ the other PR's rule → **`UI-NEW-19`**.
3. **Rename every occurrence** of the moved ID in that PR's content — not just the §2 row: the §0 ID
   header (`UI-NEW-01〜18` → `〜19`), the sub-skill notes, the parity grep rows, the reference
   templates, the worked examples. `grep -c 'UI-NEW-12'` in the renamed PR's files must be **0**.
4. Bump the §0 ID-table + 新規追加 for the moved rule's prefix (`§counter-accounting`).

✅ `UI-NEW-12` = funcRegistry-key (trunk) kept; external-integration rule → `UI-NEW-19`, all its refs renamed.
❌ Leave both as `UI-NEW-12` → `verify_scaffold.py` `§no-dup-id` fires; the second silently shadows the first.

**Anti-Pattern numbers collide the same way** (`#24` taken by two PRs) — give the later one the next
free §3 number (`#35`/`#36`) and update its cross-reference.

## §content-duplicate  — same rule, different ID

Two PRs express the **same rule** under different IDs (e.g. "column-filter value must be operator
shape" filed as `SDUI-NEW-05` by one PR and `FILTER-NEW-01` by another). Don't keep both:

1. Choose the **canonical home** (the clearer ID / the PR that owns that concept). Keep it.
2. **Drop** the duplicate rule + its anti-pattern entry + its sub-skill mirrors from the other PR.
3. **Salvage** anything the dropped side had that the keeper lacks (a deeper test, an extra example) —
   re-tag it to the canonical ID and graft it onto the keeper's section. Confirm with the user when
   the salvage is non-trivial.

✅ `FILTER-NEW-01` (PR-B) is the canonical filter-value rule; PR-A's `SDUI-NEW-05`(operator) dropped,
   but PR-A's `toKendoFilter` round-trip test salvaged into the FILTER-NEW-01 test guidance.
❌ Keep both `FILTER-NEW-01` and `SDUI-NEW-05`(operator) → two rules say the same thing; reviewers and
   the generator drift on which to follow.

> Distinguish from §id-collision: collision = same **ID**, different rule (rename one); duplicate =
> same **rule**, different ID (drop one, keep the canonical).

## §counter-accounting  — keep §0 consistent per PR

The SSOT §0 carries `新規追加`, `合計` (= 既存 + 新規), `Anti-Pattern`, and a per-prefix ID table. After
applying a PR, update them by its **net deltas**:
- +k new rule rows in §2 ⇒ 新規追加 += k, 合計 += k, and the ID-table prefix counts += their share.
- +m new anti-patterns ⇒ `Anti-Pattern` += m **and** the `## 3. … (N 件)` heading += m. A *modified*
  (not new) anti-pattern does **not** bump the count.
- A new prefix (e.g. `FILTER-NEW`) ⇒ add a new ID-table row; a section header like
  `(SDUI-NEW-01〜04)` that gains a member ⇒ bump to `〜05`.

Run `verify_scaffold.py` after each PR — `§counter-newcount` / `§counter-idtable` /
`§counter-antipattern` confirm the arithmetic against the real rows.

## §counter-reconcile  — fix pre-existing drift once, at the end

Per-PR accounting keeps counters *consistent with each PR's deltas*, but the SSOT may have arrived
with **drift already baked in** (a counter that was wrong on the sprint branch before any of these
PRs). At §reconcile, trust the **grep-actual** numbers (`verify_scaffold.py` prints `§2 rules=…`,
`§3 anti-patterns=…`) and set the declared counters to them in **one `chore:` commit**:
- §0 新規追加 / 合計 / ID-table → the real §2 counts (fix even a long-standing wrong prefix count, e.g.
  `EDIT-NEW` table said 2 but §2 has 6).
- **Mirror counters in sub-skills** drift too — reconcile them in the same pass. For W3 parity-review:
  `現在 N ID` (×several) + the per-prefix breakdown + `Anti-Pattern N 項目` + `1〜N 通し番号` — tie the
  ID number to the §2 count, the 項目/通し番号 to §3's anti-pattern count.

Pick a defensible interpretation when a loose label is ambiguous (e.g. tie "Anti-Pattern N 項目" to §3
= the authoritative anti-pattern count, since the surrounding text says "§3 から抽出 / 1〜N 通し番号").
Finish with a sweep that no old number string remains anywhere, and `verify_scaffold.py` → `OK`.

## §verify-each-step

After **every** per-PR apply, before committing, do all three — a clean `git diff` is not enough:
1. `python3 scripts/verify_scaffold.py <SSOT>` → `OK` (no dup ID, counters consistent).
2. **Phrase presence**: `grep -cF` a distinctive phrase from each change the PR intended — each = 1.
   (`grep` with backticks in the pattern: include them, or pick a phrase without them.)
3. **No stray collision ID**: in files where you renamed `X→Y`, `grep -c 'X'` of the renamed concept
   = 0 (the only `X` left should be the legitimate keeper's, in its own file). And the renamed ID `Y`
   appears the expected number of times.

A grep that returns 0 where you expect ≥1 (or vice-versa) means an edit silently failed or a rename
was missed — fix before committing.
