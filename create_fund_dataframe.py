import glob
import pandas as pd

# 1. read all CSV files and concatenate into a single DataFrame
files = glob.glob('priceData/fund_prices_*.csv', recursive=True)
df = pd.concat(
    (pd.read_csv(f, encoding='utf-8-sig') for f in files),
    ignore_index=True
)

# 2. clean up the DataFrame: remove 'MOP' from price, convert to float, parse date, drop duplicates, sort
df['price'] = (df['price'].str.replace('MOP', '', regex=False)
                          .str.strip()
                          .astype(float))
df['price_date'] = pd.to_datetime(df['price_date'])
df = df.drop_duplicates(subset=['price_date', 'fund_name'], keep='last')
df = df.sort_values('price_date').reset_index(drop=True)

# 3. pivot to wide format: each row is a date, each column is a fund
table = df.pivot(index='price_date', columns='fund_name', values='price')
table = table.sort_index()

print(table.head())
# fund_name       Fund A          Fund B      ...        Fund C
# price_date
# 2023-11-29        188.37        141.57                  160.52
# 2023-11-30        189.02        142.10                  161.03

# 4. Save
table.to_csv('fund_prices_table.csv', encoding='utf-8-sig')
print(f'{table.shape[0]} days × {table.shape[1]} funds')