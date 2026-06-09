#!/usr/bin/env python3
"""
verify_scaffold.py — self-check for a W3 scaffold SSOT rules file after a merge step.

Run it after EVERY per-PR apply and after the counter-reconcile pass, on the merged
SSOT (`.claude/skills/frontend-mig-shared/rules/w3-frontend-standard.md`):

    python3 verify_scaffold.py <path-to-w3-frontend-standard.md>

It does NOT auto-fix. It prints `verify: OK` or `verify: N warning(s)` + one WARN per
violation, each citing the §slug in references/verify-rules.md. The checks are exactly
the failure modes that "break the scaffold (足場)" when child scaffold PRs are merged:

  §no-dup-id          a {PREFIX}-NEW-{n} rule defined twice in §2 (= an ID collision left
                      un-renamed, e.g. two screens both add UI-NEW-12).
  §counter-newcount   §0 「新規追加: **N 件**」 must equal the real §2 rule-row count.
  §counter-idtable    §0 ID table: per-prefix count must equal the real §2 grep count, and
                      the table must sum to 新規追加.
  §counter-antipattern §0 「Anti-Pattern: **N 件**」 must equal the §3 row count.

Self-test (no file needed):  python3 verify_scaffold.py --self-test
Comments/code: English/Japanese only.
"""
import re
import sys
from pathlib import Path

# ============================ MARKERS — adapt per scaffold ============================
# These match the W3 `w3-frontend-standard.md` §0 / §2 / §3 layout. If a project lays the
# SSOT out differently, change ONLY these regexes (project-config.md §scaffold-files).
RE_SEC2_START = re.compile(r'^##\s*2\.\s')          # "## 2. 新規追加規約"
RE_SEC3_START = re.compile(r'^##\s*3\.\s')          # "## 3. Anti-Pattern 一覧 (N 件)"
RE_SEC4_START = re.compile(r'^##\s*4\.\s')          # "## 4. ..." (PoC anti-patterns — excluded)
RE_RULE_ROW   = re.compile(r'^\|\s*([A-Z]+-NEW)-(\d+)\s*\|')      # §2 rule-definition row
RE_AP_ROW     = re.compile(r'^\|\s*(\d+)\s*\|')                   # §3 anti-pattern data row
RE_IDTBL_ROW  = re.compile(r'^\|\s*\*{0,2}([A-Z]+-NEW)\*{0,2}\s*\|[^|]*\|\s*(\d+)')  # §0 ID-table row
RE_NEWCOUNT   = re.compile(r'新規追加:\s*\*\*\s*(?:約\s*)?(\d+)\s*件')   # §0 新規追加: **N 件**
RE_APCOUNT    = re.compile(r'Anti-Pattern:\s*\*\*\s*(\d+)\s*件')         # §0 Anti-Pattern: **N 件**
# =====================================================================================


def _section(lines, start_re, end_res):
    """Return the [start, end) line slice of a section: from the line matching start_re
    to the first later line matching any of end_res (or EOF)."""
    start = None
    for i, ln in enumerate(lines):
        if start_re.match(ln):
            start = i
            break
    if start is None:
        return []
    for j in range(start + 1, len(lines)):
        if any(r.match(lines[j]) for r in end_res):
            return lines[start:j]
    return lines[start:]


def parse(text):
    """Parse the SSOT into the numbers the checks compare. Returns a dict."""
    lines = text.splitlines()
    sec2 = _section(lines, RE_SEC2_START, [RE_SEC3_START, RE_SEC4_START])
    sec3 = _section(lines, RE_SEC3_START, [RE_SEC4_START])

    rule_ids = []                         # ['UI-NEW-12', ...] in order, for dup detection
    prefix_count = {}                     # {'UI-NEW': 19, ...} real §2 grep count
    for ln in sec2:
        m = RE_RULE_ROW.match(ln)
        if m:
            rid = f"{m.group(1)}-{m.group(2)}"
            rule_ids.append(rid)
            prefix_count[m.group(1)] = prefix_count.get(m.group(1), 0) + 1

    ap_rows = sum(1 for ln in sec3 if RE_AP_ROW.match(ln))

    # §0 ID table lives before §2 — scan the whole head (lines before §2 start)
    head = lines[: (lines.index(sec2[0]) if sec2 else len(lines))]
    idtbl = {}
    for ln in head:
        m = RE_IDTBL_ROW.match(ln)
        if m:
            idtbl[m.group(1)] = int(m.group(2))

    def _first(rx):
        for ln in head or lines:
            m = rx.search(ln)
            if m:
                return int(m.group(1))
        return None

    return {
        'rule_ids': rule_ids,
        'rule_count': len(rule_ids),
        'prefix_count': prefix_count,
        'ap_rows': ap_rows,
        'idtbl': idtbl,
        'declared_new': _first(RE_NEWCOUNT),
        'declared_ap': _first(RE_APCOUNT),
    }


def verify(text):
    """Return a list of WARN strings (empty = OK). Never raises on a well-formed file."""
    d = parse(text)
    warn = []

    # §no-dup-id — the same {PREFIX}-NEW-{n} must not be defined twice (= un-renamed collision)
    seen, dups = set(), set()
    for rid in d['rule_ids']:
        if rid in seen:
            dups.add(rid)
        seen.add(rid)
    for rid in sorted(dups):
        warn.append(f"§no-dup-id: rule ID '{rid}' is defined more than once in §2 "
                    f"(ID collision left un-renamed — rename the later one to the next free number)")

    # §counter-newcount — §0 新規追加 must equal the real §2 rule-row count
    if d['declared_new'] is None:
        warn.append("§counter-newcount: could not find §0 「新規追加: **N 件**」 — check the marker")
    elif d['declared_new'] != d['rule_count']:
        warn.append(f"§counter-newcount: §0 新規追加 = {d['declared_new']} but §2 has "
                    f"{d['rule_count']} rule rows — set 新規追加 to {d['rule_count']}")

    # §counter-idtable — per-prefix table count must equal the real grep count; table must sum to 新規追加
    for prefix in sorted(set(d['idtbl']) | set(d['prefix_count'])):
        tbl = d['idtbl'].get(prefix)
        real = d['prefix_count'].get(prefix, 0)
        if tbl is None:
            warn.append(f"§counter-idtable: prefix '{prefix}' appears {real}× in §2 but is missing "
                        f"from the §0 ID table — add a row")
        elif tbl != real:
            warn.append(f"§counter-idtable: ID-table '{prefix}' = {tbl} but §2 has {real} "
                        f"'{prefix}-*' rows — set it to {real}")
    tbl_sum = sum(d['idtbl'].values())
    if d['idtbl'] and d['declared_new'] is not None and tbl_sum != d['declared_new']:
        warn.append(f"§counter-idtable: §0 ID-table sums to {tbl_sum} but 新規追加 = {d['declared_new']} "
                    f"— they must match (both = §2 rule count {d['rule_count']})")

    # §counter-antipattern — §0 Anti-Pattern count must equal the §3 row count
    if d['declared_ap'] is None:
        warn.append("§counter-antipattern: could not find §0 「Anti-Pattern: **N 件**」 — check the marker")
    elif d['declared_ap'] != d['ap_rows']:
        warn.append(f"§counter-antipattern: §0 Anti-Pattern = {d['declared_ap']} but §3 has "
                    f"{d['ap_rows']} rows — set it to {d['ap_rows']}")

    return warn, d


def _print(warn, d):
    print(f"verify: {'OK' if not warn else f'{len(warn)} warning(s)'}  "
          f"(§2 rules={d['rule_count']}, §3 anti-patterns={d['ap_rows']}, "
          f"declared 新規追加={d['declared_new']} / Anti-Pattern={d['declared_ap']})")
    for w in warn:
        print("  WARN", w)
    return len(warn)


# ------------------------------------- self-test -------------------------------------
_GOOD = """## 0. メタ情報
### 規約件数
- 新規追加: **3 件**
- Anti-Pattern: **2 件**
### 規約 ID 体系
| 接頭辞 | 領域 | 件数 |
|---|---|---|
| UI-NEW | UI | 2 |
| **API-NEW** | API | 1 (規約行き分) |
## 2. 新規追加規約
| ID | 規約名 | 内容 | 該当バグ |
|---|---|---|---|
| UI-NEW-01 | a | x | - |
| UI-NEW-02 | b | y | - |
| API-NEW-01 | c | z | - |
## 3. Anti-Pattern 一覧 (2 件)
| # | Anti-Pattern | React 代替 | 規約 |
|---|---|---|---|
| 1 | foo | bar | UI-NEW-01 |
| 2 | baz | qux | API-NEW-01 |
## 4. PoC 自身のアンチパターン
| 1 | poc-ap | - | - |
"""

# BAD: UI-NEW-02 defined twice (collision), 新規追加 says 3 but §2 has 4 rows,
#      ID table UI-NEW=2 but real=3, Anti-Pattern says 2 but §3 has 1 row.
_BAD = """## 0. メタ情報
### 規約件数
- 新規追加: **3 件**
- Anti-Pattern: **2 件**
### 規約 ID 体系
| 接頭辞 | 領域 | 件数 |
|---|---|---|
| UI-NEW | UI | 2 |
| API-NEW | API | 1 |
## 2. 新規追加規約
| UI-NEW-01 | a | x | - |
| UI-NEW-02 | b | y | - |
| UI-NEW-02 | b-dup | y | - |
| API-NEW-01 | c | z | - |
## 3. Anti-Pattern 一覧 (2 件)
| # | Anti-Pattern | React 代替 | 規約 |
|---|---|---|---|
| 1 | foo | bar | UI-NEW-01 |
## 4. PoC
| 1 | poc | - | - |
"""


def _self_test():
    ok_warn, _ = verify(_GOOD)
    assert ok_warn == [], f"GOOD should be clean, got: {ok_warn}"
    bad_warn, _ = verify(_BAD)
    joined = "\n".join(bad_warn)
    checks = {
        "§no-dup-id (UI-NEW-02 twice)": "§no-dup-id" in joined and "UI-NEW-02" in joined,
        "§counter-newcount (3 vs 4)": "§counter-newcount" in joined,
        "§counter-idtable (UI-NEW 2 vs 3)": "§counter-idtable" in joined,
        "§counter-antipattern (2 vs 1)": "§counter-antipattern" in joined,
    }
    print("self-test:")
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"  GOOD → {len(ok_warn)} warn (expect 0) ; BAD → {len(bad_warn)} warn (expect ≥4)")
    if not all(checks.values()) or ok_warn:
        print("self-test: FAILED")
        return 1
    print("self-test: OK")
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "--self-test":
        return _self_test()
    if len(argv) != 2:
        print(__doc__)
        print("usage: python3 verify_scaffold.py <path-to-w3-frontend-standard.md> | --self-test")
        return 2
    p = Path(argv[1])
    if not p.is_file():
        print(f"error: file not found: {p}")
        return 2
    warn, d = verify(p.read_text(encoding="utf-8"))
    return 1 if _print(warn, d) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
