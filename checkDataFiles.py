import glob
import csv
import os
from datetime import date, timedelta

DATA_DIR = 'priceData'
START = date(2012, 1, 1)
END   = date(2026, 9, 30)

# ── 收集已有的日期 ──
existing = set()
for f in glob.glob(f'{DATA_DIR}/fund_prices_*.csv', recursive=True):
    d = f.replace('fund_prices_', '').replace('.csv', '')[-10:]  # 取 YYYY-MM-DD
    existing.add(d)

# ── 检查行数 ──
bad = []
for f in sorted(glob.glob(f'{DATA_DIR}/fund_prices_*.csv', recursive=True)):
    with open(f, encoding='utf-8-sig') as fh:
        rows = [r for r in list(csv.reader(fh))[1:] if any(c.strip() for c in r)]
    if len(rows) != 9:
        bad.append(f)
        print(f'行数不足: {f} ({len(rows)} 行)')

# ── 检查缺失的工作日 ──
missing = []
d = START
while d <= END:
    if d.weekday() < 5:  # 周一~周五
        ds = d.isoformat()
        if ds not in existing:
            missing.append(ds)
    d += timedelta(days=1)

print(f'\n共 {len(existing)} 个文件，{len(bad)} 个不完整')
if missing:
    print(f'\n缺失 {len(missing)} 个工作日（含可能的公众假期）:')
    for ds in missing:
        print(f'  {ds}  周{"一二三四五"[date.fromisoformat(ds).weekday()]}')
else:
    print('\n没有缺失的工作日')