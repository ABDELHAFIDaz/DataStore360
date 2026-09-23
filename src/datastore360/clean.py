import pandas as pd
import hashlib

def normalize_text_columns(df, columns=["Customer Name", "Segment", "City", "State", "Region", "Ship Mode", "Category", "Sub-Category"]):
    df = df.copy()
    
    for col in columns:
        df[col] = df[col].str.strip().str.title()
    return df
         
        
def parse_dates(df, columns=["Order Date", "Ship Date"]):
    df = df.copy()
    
    for col in columns:
        df[col] = pd.to_datetime(df[col], format="mixed", dayfirst=False)
        
    return df

        
def fix_typos(df):
    df = df.copy()
    df["Segment"] = df["Segment"].replace({
        "Home Ofice": "Home Office",
        "Consumerr": "Consumer",
        "Corporrate": "Corporate"
    })
    
    return df
    
    
def remove_duplicates(df):
    df = df.copy()
    df = df.drop_duplicates()
    return df


def fix_known_row_id_conflicts(df: pd.DataFrame):
    df = df.copy()
    
    df = df[~((df["Row ID"] == 1385) & (df["Postal Code"] == "30080.0.0"))]

    df = df[~((df["Row ID"] == 6175) & (df["Ship Date"].isna()))]

    df = df[~((df["Row ID"].isin([6753, 9240])) & (df["Ship Date"] == "2010-01-01"))]
    
    return df


def handle_missing_ship_date_mode(df):
    df = df.copy()
    
    df = df[~((df['Ship Date'] < df['Order Date']) & (df['Ship Mode'].isnull()))]
    df = df[~((df['Ship Mode'].isnull()) & df['Ship Date'].isnull())]
    
    known = df.dropna(subset=["Ship Date", "Order Date", "Ship Mode"]).copy()
    known["delivery_days"] = (known["Ship Date"] - known["Order Date"]).dt.days

    median_by_mode = known.groupby("Ship Mode")["delivery_days"].median()
    
    missing_date = (
    (df["Ship Date"].isna() | (df["Ship Date"] < df["Order Date"]))
    & df["Ship Mode"].notna()
    )
    df.loc[missing_date, 'Ship Date'] = (
        df.loc[missing_date, 'Order Date'] + pd.to_timedelta(df.loc[missing_date, 'Ship Mode'].map(median_by_mode), unit='D')
    )

    missing_mode = df["Ship Mode"].isna() & df["Ship Date"].notna()
    actual_days = (df.loc[missing_mode, "Ship Date"] - df.loc[missing_mode, "Order Date"]).dt.days

    def closest_mode(days):
        return (median_by_mode - days).abs().idxmin()

    df.loc[missing_mode, "Ship Mode"] = actual_days.apply(closest_mode)
    
    return df


def handle_missing_sales_quantity(df):
    df = df.copy()
    
    df = df[~((df['Sales'].isna()) | (df['Quantity'].isna()))]
    
    return df

    
    
def handle_missing_postal_code(df):
    df = df.copy()
    
    city_to_postal = (
    df.dropna(subset=["Postal Code"])
    .groupby("City")["Postal Code"]
    .agg(lambda x: x.mode()[0])
    )
    
    df["Postal Code"] = df["Postal Code"].fillna(df["City"].map(city_to_postal))
    df["Postal Code"] = df["Postal Code"].fillna("Unknown")
    
    return df


def handle_missing_customer_name(df):
    df = df.copy()
    
    customer_to_name = (
    df.dropna(subset=["Customer Name"])
    .groupby("Customer ID")["Customer Name"]
    .first()
    )

    df["Customer Name"] = df["Customer Name"].fillna(df["Customer ID"].map(customer_to_name))
    df["Customer Name"] = df["Customer Name"].fillna("Unknown")
    
    return df
    
    
def validate_discount(df):
    df = df.copy()
    
    df = df[~((df['Discount'] < 0) | (df['Discount'] > 1))]
    
    return df


def validate_quantity(df):
    df = df.copy()
    
    df = df[df['Quantity'] >= 0]
    df['Quantity'] = df['Quantity'].round().astype(int)
    
    return df


def hash_customer_name(df):
    df = df.copy()

    def hash_name(name):
        return hashlib.sha256(name.encode("utf-8")).hexdigest()

    df["Customer Name"] = df["Customer Name"].apply(hash_name)
    
    return df


def add_delivery_time(df):
    df = df.copy()
    
    df['Delivery Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    return df


def add_profit_margin(df):
    df = df.copy()
    
    df['Profit Margin'] = df['Profit'] / df['Sales'].replace(0, pd.NA)
    
    return df

