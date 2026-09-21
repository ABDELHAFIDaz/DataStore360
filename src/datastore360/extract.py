import pandas as pd


def load_raw_csv(path):
    return pd.read_csv(path)


def load_to_staging(df, engine):
    df = df.copy()
    df.columns = [col.lower().replace(" ", "_").replace("-", "_") for col in df.columns]
    
    df.to_sql(
        "superstore_raw",
        engine,
        schema="staging",
        if_exists="replace",
        index=False,
    )