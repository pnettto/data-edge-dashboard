from pathlib import Path
import pandas as pd

def csv_to_df(filename):
    # Pass in the same folder csv file name ("example" if "example.csv")
    HERE = Path(__file__).parent
    return pd.read_csv(HERE / f"{filename}.csv")
