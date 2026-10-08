import glob
import pandas as pd

# 1. 读取所有文件，拼成一个长表
files = glob.glob('priceData/fund_prices_*.csv', recursive=True)
df = pd.concat(
    (pd.read_csv(f, encoding='utf-8-sig') for f in files),
    ignore_index=True
)

# 2. 清洗
df['price'] = (df['price'].str.replace('MOP', '', regex=False)
                          .str.strip()
                          .astype(float))
df['price_date'] = pd.to_datetime(df['price_date'])
df = df.drop_duplicates(subset=['price_date', 'fund_name'], keep='last')
df = df.sort_values('price_date').reset_index(drop=True)

# 3. 透视成宽表：每行一个日期，每列一只基金
table = df.pivot(index='price_date', columns='fund_name', values='price')
table = table.sort_index()

print(table.head())
# fund_name    「安匯」退休基金  「安裕」退休基金  ...  MPFM騰龍基金
# price_date
# 2023-11-29        188.37        141.57                  160.52
# 2023-11-30        189.02        142.10                  161.03

# 4. 保存
table.to_csv('fund_prices_table.csv', encoding='utf-8-sig')
print(f'共 {table.shape[0]} 天 × {table.shape[1]} 只基金')