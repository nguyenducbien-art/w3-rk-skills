# Authoring conventions (how to write a skill here)

## SKILL.md — front-matter

```yaml
---
name: <skill>              # a LABEL only (the command is the directory name; keep them equal anyway)
description: >             # 🔴 the most important field — Claude auto-triggers the skill from this text.
  <one sentence on what it does>. Use this when <concrete situations>. Trigger when the user types
  `/<plugin>:<skill> <args>`, or says "<phrase 1>" / "<phrase 2>" / ... .
---
```
- Pack the **trigger phrases** into `description` (verbatim wordings a user would say + the slash
  command). A skill with vague description never fires.
- Keep `description` to what the skill DOES + WHEN — not how. Under ~80 words.

## SKILL.md — body = a thin CONDUCTOR, not a manual

The body orchestrates; the knowledge lives in `references/`. Keep it short. Canonical sections:

1. **Input** — required args; what to do if missing (ask + stop). Optional inputs (e.g. an env block).
2. **Reference map** — a table `| file | read it when |`, telling the model to **read on demand, not
   preload everything**. This is the core of the pattern: SKILL.md stays small, references are pulled
   only when relevant.
3. **Workflow** — numbered steps, each pointing at the reference that governs it.
4. **Deliverables / Output** — exact output location + filenames.
5. **Guardrails** — hard "never do X" rules (local-only DB, never edit app source, no git in auto
   mode, comments English/Japanese only, opt-in heavy steps, …).

🚫 Do NOT inline the rules in SKILL.md. If you're tempted to explain *how* to do something, that text
belongs in a `references/*.md` §section that the reference map points to.

## references/ — one concern per file, each rule a §section

- Split by concern (`writing-rules.md`, `mimosa-rules.md`, `output-rules.md`, `project-config.md`, …).
- Give every rule a stable **`## §slug`** heading so other files (and the review checklist, and the
  verify warnings) can cite it by name. Cross-file citations use `§slug`.
- Prefer a short worked **✅ / ❌ example** per rule over prose — the model copies examples.
- When a rule changes, update its §section in ONE place; everything else cites it.

## scripts/ — self-contained Python generators

- Plain Python 3, standard lib + the libs the skill bundles (e.g. `openpyxl`). **No machine paths.**
- Resolve paths relative to the script: `OUT_DIR = Path(__file__).resolve().parent`; bundled assets
  via `Path(__file__).resolve().parents[1] / "assets" / "<file>"`.
- A "template" generator (copied per-item and filled) keeps a top **CONFIG block** + typed data
  lists + a `verify()` + a writer. See `build_csv.py`.
- Comments **English/Japanese only** (never Vietnamese). `python3 -m py_compile` must pass.

## 🔴 The verify-heuristic pattern (every machine-checkable rule gets a self-check)

A rule is only as good as its enforcement. When you add a rule that has a detectable shape, add a
**text heuristic** to the generator's `verify()` that warns when the rule is violated, e.g.:

```python
def _bundled_outcome(cell):           # §expected: ≥2 outcomes on one EXPECTED line → split
    for ln in (cell or '').split('\n'):
        low = ln.lower()
        if ('modal' in low or 'is displayed' in low) and any(k in low for k in ('loading','is hidden','stays on the form')):
            return True
    return False
# … then inside verify(): if _bundled_outcome(ee): warn.append("TC..: split outcomes (§expected)")
```
Heuristics must be **low-noise** (a false positive trains people to ignore warnings) — gate on a
specific marker, exempt legitimate cases, and unit-test the heuristic on a few strings before
shipping. `verify()` prints `OK` or a list of `WARN` lines; it never auto-fixes.

## 🔴 The gen ↔ review lock-step (for paired skills)

When a generator skill has a reviewer twin, **every rule must exist in three places, in sync**:
1. the **§section** in the generator's references (the source of truth),
2. a **`verify()` heuristic** in the generator script,
3. a **mirror** in the reviewer: a `dump_tc.py` auto-flag (same heuristic) + a `review-checklist.md`
   line that tells the reviewer to flag the violation.

So a single convention change touches: the §section, the gen verify, the review checklist, the review
auto-flag (and any worked example). Changing only one of them silently drifts the pair. This 4-5-place
update is the discipline that keeps "what the reviewer checks" == "what the generator must produce".

## Language & self-containment (non-negotiable)

- **User-facing text in the user's language (default English).** Skill files themselves are written in
  English; JP labels/messages/codes are kept **verbatim** (`「…」`, `E0xx`, `正常`/`異常`).
- **No Vietnamese anywhere in the skill** (comments, code, docs) — English or Japanese only.
- **No personal/absolute paths, no memory-file dependency.** A rule learned in one session must be
  baked into `references/` (+ verify + review mirror), not left in a personal memory note — a teammate
  on a clean install has neither your memory nor your paths.
