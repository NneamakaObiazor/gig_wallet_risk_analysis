import pandas as pd
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 200)

base = '/mnt/user-data/uploads/'
channel = pd.read_csv(base+'dim_channel.csv')
date = pd.read_csv(base+'dim_date_updated.csv')
market = pd.read_csv(base+'dim_market.csv')
worker = pd.read_csv(base+'dim_worker.csv')
fact = pd.read_csv(base+'fact_transactions_Updated_.csv')

for name, df in [('channel',channel),('date',date),('market',market),('worker',worker),('fact',fact)]:
    print(f"\n=== {name} shape={df.shape} ===")
    print(df.dtypes)
    print(df.isna().sum()[df.isna().sum()>0])
