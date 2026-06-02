#!/usr/bin/env python3
"""
build_csv.py — TEMPLATE. Copy this to <skill>/output/<slug>(screen_id=<X>)/ and fill
the SCREEN CONFIG + the S2..S5 tuple lists, then run it. It emits the bilingual CSV:
  - <name>_base.csv      bilingual 11-col (+ marker rows)  → input to build_xlsx.py (→ Excel)

Tuple shape (10 fields, № is auto-assigned):
  (大分類, 中分類, 小分類, kind, pre_en, pre_jp, steps_en, steps_jp, exp_en, exp_jp)
  kind ∈ {'正常','異常'}.  Multiline cells use '\\n'.  See references/example-589.csv for the gold
  shape and references/*.md for the rules. Comments/code: English/Japanese only (output-rules §7).
"""
import csv, re
from pathlib import Path

# ============================ SCREEN CONFIG — FILL ============================
SCREEN_ID   = "<X>"
SCREEN_ALIAS = "<screen_alias>"        # screens.alias_nm
PAGE_TITLE  = "<PAGE_TITLE>"            # part after "W3 mimosa | " in the App routing file
SLUG        = "<slug>"                  # kebab-case from the AngularJS URL
SCREEN_TYPE = "list"                    # "list" | "detail" | "form" — form/edit/create → §verify-db (DB-persistence verify in S4.1)
ID_FROM_PARENT = False                  # True if a form/edit screen loads a record by an id from a parent → §direct-url-access (3 deep-link TCs: IDなし / 有効なID / 存在しないID)
HAS_COLLAPSIBLE_SECTIONS = False        # True if a form has collapsible sections (全て開く / 全て閉じる / per-section ≫) → §form-accordion (toggle TCs in S4.1)
OUT_DIR     = Path(__file__).resolve().parent   # the output/<slug>(screen_id=X)/ folder this script sits in
# =============================================================================

NAME = f"{SCREEN_ALIAS}_ScreenID ({SCREEN_ID})"
DST_CSV = OUT_DIR / f"Testcase_Output_{NAME}_base.csv"

# PRE-CONDITION constants (writing-rules §precondition — every screen ref carries the screen_id)
PRE_EN = f"1. Open the [{SCREEN_ALIAS} (screen_id={SCREEN_ID})] screen."
PRE_JP = f"1. 「{SCREEN_ALIAS}（screen_id={SCREEN_ID}）」画面を開く。"
PRE_CHECK_EN = PRE_EN + "\n2. Check 1 or more rows."
PRE_CHECK_JP = PRE_JP + "\n2. 行を1行以上チェックする。"

HEADER = ['№','大分類','中分類','小分類','正常/異常','PRE-CONDITION','前提条件','STEPS','実施内容','EXPECTED RESULT','確認事項']

# ---- S1 共通確認 (verbatim boilerplate — only PAGE_TITLE / PRE_* change; writing-rules §S1-verbatim) ----
S1 = [
  ('ページタイトル','','','正常', PRE_EN, PRE_JP,
   '1. Verify the page title of the screen.', '1. 画面のページタイトルを確認する。',
   f'1. The page title is "W3 mimosa | {PAGE_TITLE}".', f'1. ページのタイトルは「W3 mimosa | {PAGE_TITLE}」です。'),
  ('ヘッダー','','','正常', PRE_EN, PRE_JP,
   '1. Verify the displays of the header.', '1. ヘッダーの表示を確認する。',
   '1. The displayed items in the header are the same as those in the AngularJS system.',
   '1. ヘッダーの表示項目がAngularJS版と一致すること。'),
  ('フッター','','','正常', PRE_EN, PRE_JP,
   '1. Verify the displays of the footer.', '1. フッターの表示を確認する。',
   '1. The displayed items in the footer are the same as those in the AngularJS system.',
   '1. フッターの表示項目がAngularJS版と一致すること。'),
  ('メニュー','','','正常', PRE_EN, PRE_JP,
   '1. Verify the displays of the menu.\n2. Click on each menu item.',
   '1. メニューの表示を確認する。\n2. 各メニュー項目をクリックする。',
   '1. The displayed items for each menu item are the same as those in the AngularJS system.\n2. Each menu item link navigates to the correct destination.',
   '1. 各メニュー項目の表示内容がAngularJS版と一致すること。\n2. 各メニュー項目が正しい遷移先に遷移すること。'),
]

# ---- FILL these from the screen (see references/mimosa-rules.md + per-button-patterns.md) ----
S2  = []   # 表示確認: 画面表示 / グリッド列表示 / ボタン表示 / 初期表示データなし
S3  = []   # バリデーション: row-guards (E001) / BVA (n-1/n/n+1) / required field
S41 = []   # 業務処理: 初期表示 → mutation buttons → filter 4-TC → nav → CSV → 帳票 → sub-screen → 共通アイコン
S42 = []   # その他: network error
S5  = []   # 性能: 1 TC (応答時間, 30k)

# 7 markers default (S2 flat). Use the 9-marker variant only if the screen has BOTH static and
# action-triggered display (test-categories §2). Parent '4.' carries no TC.
SECTIONS = [
  ('1. 共通確認', S1),
  ('2. 表示確認', S2),
  ('3. バリデーション確認', S3),
  ('4. 業務処理の確認', []),
  ('4.1 業務処理の確認', S41),
  ('4.2 その他処理の確認', S42),
  ('5. 性能確認', S5),
]
def _steps(s):  # set of TOP-LEVEL step numbers in a multiline cell (1.1/1.2 → step 1); output-rules §5
    nums = set()
    for ln in (s or '').split('\n'):
        m = re.match(r'^\s*(\d+)', ln.strip())
        if m:
            nums.add(int(m.group(1)))
    return sorted(nums)

def _pre_crammed(pre):  # writing-rules §precondition / output-rules §3: 1 action = 1 step in PRE too
    """A single PRE physical line carrying BOTH a (screen_id=…) reference AND a click is a crammed
    navigation precondition (open-screen + click bundled) → split into one action per numbered step."""
    for ln in (pre or '').split('\n'):
        if 'screen_id=' in ln and ('click' in ln.lower() or 'クリック' in ln):
            return True
    return False

def _crammed_subnums(cell):  # output-rules §6: each numbered/sub-numbered item on its OWN line
    """A physical line carrying 2+ dotted sub-numbers (e.g. '1.1 … 1.2 … 1.3 …') means sub-items
    were run together on one line instead of one-per-line (\\n-separated)."""
    for ln in (cell or '').split('\n'):
        if len(re.findall(r'\d+\.\d+', ln)) >= 2:
            return True
    return False

def _jammed_list(cell):  # writing-rules §enumerate: separate many fields with commas, not ・/&/;
    """A physical line with 4+ nakaguro '・' is very likely a jammed field enumeration that should
    be comma-separated for readability."""
    for ln in (cell or '').split('\n'):
        if ln.count('・') >= 4:
            return True
    return False

def _collapsed_range(cell):  # writing-rules §enumerate: spell out X1/X2/X3, don't collapse to X1〜3
    """A JP label directly followed by a numeric range (e.g. '送状備考1〜3') collapses several
    distinct fields into shorthand — list them individually (送状備考1, 送状備考2, 送状備考3)."""
    return re.search(r'[ぁ-んァ-ヶ一-龥ー]\d+[〜～]\d+', cell or '') is not None

def verify():
    """Self-check (output-rules §8). Prints WARN lines; does not auto-fix."""
    warn = []
    n = 0
    for _marker, items in SECTIONS:
        for t in items:
            n += 1
            cat1, cat2, cat3, kind, pe, pj, se, sj, ee, ej = t
            if cat3 and not cat2:
                warn.append(f"TC{n} {cat1}: 中分類 blank while 小分類 filled")
            if _marker.startswith('3.') and kind == '正常':
                warn.append(f"TC{n} {cat1}: 正常 case in バリデーション(S3) — move to S4.1 (S3 holds 異常 only)")
            if f"screen_id={SCREEN_ID}" not in pe or f"screen_id={SCREEN_ID}" not in pj:
                warn.append(f"TC{n} {cat1}: PRE missing (screen_id={SCREEN_ID})")
            if _pre_crammed(pe) or _pre_crammed(pj):
                warn.append(f"TC{n} {cat1}: PRE line crams screen-ref + click — split into 1 action/step")
            for label, cell in (('STEPS',se),('実施内容',sj),('EXPECTED',ee),('確認事項',ej),('PRE',pe),('前提条件',pj)):
                if _crammed_subnums(cell):
                    warn.append(f"TC{n} {cat1}: {label} runs 2+ sub-numbers on one line — put each N.N on its own line")
                if _jammed_list(cell):
                    warn.append(f"TC{n} {cat1}: {label} jams 4+ fields with ・ — separate fields with commas")
                if _collapsed_range(cell):
                    warn.append(f"TC{n} {cat1}: {label} collapses fields into a range (e.g. 送状備考1〜3) — spell out each field")
            if _steps(se) != _steps(ee):
                warn.append(f"TC{n} {cat1}: STEPS{_steps(se)} vs EXPECTED-EN{_steps(ee)} step-number mismatch")
            if _steps(sj) != _steps(ej):
                warn.append(f"TC{n} {cat1}: 実施内容{_steps(sj)} vs 確認事項{_steps(ej)} step-number mismatch")
            for tok in ('stopLoading','startLoading','$scope','$http','dataBound','.error()','createEModal','createIModal'):
                if tok in ee or tok in ej:
                    warn.append(f"TC{n} {cat1}: forbidden token '{tok}' in EXPECTED")
    # form/edit/create screens need extra S4.1 coverage: DB-persistence verify + concurrency conflict
    if SCREEN_TYPE.lower() in ('form', 'edit', 'create'):
        s41 = ' '.join((t[i] or '') for t in S41 for i in (6, 7, 8, 9))   # all S4.1 STEPS + EXPECTED
        if 'SELECT' not in s41:
            warn.append("SCREEN_TYPE form/edit/create: no 'Run SQL: SELECT' DB-persistence verify in S4.1 (§verify-db)")
        if not any(k in s41 for k in ('排他', '別ブラウザ', '2 browser', '2つのブラウザ', 'タブ', '1st tab', '2nd tab', 'another user', 'concurrent', '同時')):
            warn.append("SCREEN_TYPE form/edit/create: no concurrent-conflict (2-browser/2-tab) TC in S4.1 (§concurrent-conflict)")
    # §direct-url-access: a form that loads a record by an id from a parent needs 3 deep-link TCs
    if ID_FROM_PARENT:
        scan = ' '.join((t[i] or '') for sec in (S2, S41) for t in sec for i in (1, 2, 6, 7, 8, 9))
        if not ('URL' in scan and ('直接' in scan or 'direct' in scan.lower())):
            warn.append("ID_FROM_PARENT: no direct-URL-access TC (IDなし / 有効なID / 存在しないID) in S2/S41 (§direct-url-access)")
    # §form-accordion: a form with collapsible sections needs section-toggle TCs
    if HAS_COLLAPSIBLE_SECTIONS:
        scan = ' '.join((t[i] or '') for sec in (S2, S41) for t in sec for i in (1, 2, 6, 7, 8, 9))
        if not any(k in scan for k in ('全て開く', '全て閉じる', 'アコーディオン', '開閉', 'collapse')):
            warn.append("HAS_COLLAPSIBLE_SECTIONS: no section collapse/expand TC (全て開く / 全て閉じる / ≫) in S2/S41 (§form-accordion)")
    print("verify:", "OK" if not warn else f"{len(warn)} warning(s)")
    for w in warn: print("  WARN", w)
    return n


def write_bilingual():
    with open(DST_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(HEADER); i = 0
        for marker, items in SECTIONS:
            w.writerow([marker] + ['']*10)              # marker row (col A = marker)
            for t in items:
                i += 1
                w.writerow([i, *t])

if __name__ == "__main__":
    total = verify()
    write_bilingual()
    print(f"wrote {total} TCs → {DST_CSV.name}")
