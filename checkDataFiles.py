import glob
import csv
import os
from datetime import date, timedelta

DATA_DIR = 'priceData'
START = date(2012, 1, 1)
END   = date(2026, 9, 30)

# ── gather all the dates ──
existing = set()
for f in glob.glob(f'{DATA_DIR}/fund_prices_*.csv', recursive=True):
    d = f.replace('fund_prices_', '').replace('.csv', '')[-10:]  #  YYYY-MM-DD
    existing.add(d)

# ── check row count ──
bad = []
for f in sorted(glob.glob(f'{DATA_DIR}/fund_prices_*.csv', recursive=True)):
    with open(f, encoding='utf-8-sig') as fh:
        rows = [r for r in list(csv.reader(fh))[1:] if any(c.strip() for c in r)]
    if len(rows) != 9:
        bad.append(f)
        print(f'row count is not equal to 9: {f} ({len(rows)} rows)')

# ── Check missing dates ──
missing = []
d = START
while d <= END:
    if d.weekday() < 5:  # only check weekdays
        ds = d.isoformat()
        if ds not in existing:
            missing.append(ds)
    d += timedelta(days=1)

print(f'\n{len(existing)} files in total, {len(bad)} incomplete')
if missing:
    print(f'\n{len(missing)} missing weekdays (including possible public holidays):')
    for ds in missing:
        print(f'  {ds}  {"MonTueWedThuFri"[date.fromisoformat(ds).weekday()*3:(date.fromisoformat(ds).weekday()+1)*3]}')
else:
    print('\nNo missing weekdays')