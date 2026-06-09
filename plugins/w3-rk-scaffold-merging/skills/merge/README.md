# merge — W3 scaffold merging

Carefully merge several **child scaffold PRs** (that all edit the same Kanaya code-gen SSOT
`w3-frontend-standard.md` + `frontend-screen-*/SKILL.md`) into **one integration branch**, resolving
rule-ID collisions, duplicate rules and §0 counter drift **by hand** so the scaffold (足場) never
silently breaks. A naive `git merge` would append duplicate IDs and wrong counters; this skill applies each
PR's intent edit-by-edit and proves the result with `scripts/verify_scaffold.py`.

Distributed as the `merge` skill of the **`w3-rk-scaffold-merging`** plugin (marketplace
`w3-rk-skills`). Everything is bundled; open Claude Code **in the W3 code repo** and invoke:

```
/w3-rk-scaffold-merging:merge #10007 #9999 #9981 #10003
```

or just say *"scaffold merge these PRs"* / *"merge the child scaffold PRs"*.

**Output:** a new integration branch (the skill asks you to name it) with one commit per merged PR +
a counter-reconcile commit, `verify_scaffold.py` clean — **local by default**. On your explicit
go-ahead it then pushes, opens a PR into the **sprint branch** (discovered from the PRs, else asked),
and closes the child PRs.

**Authoring / maintenance:** see the repo's `CONTRIBUTING.md`. The four checkable invariants live in
`references/verify-rules.md` and are enforced by `scripts/verify_scaffold.py`
(`python3 scripts/verify_scaffold.py --self-test`).
