import pandas as pd
def csv_to_df(f): return pd.read_csv(__file__.replace('config.py', f'{f}.csv'))


config = [
   
]
