import pandas as pd
from sqlalchemy import text


def clear_core_tables(engine):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE core.orders, core.customers, core.products CASCADE"))


def load_customers(df, engine):
    customers = df[[
        "Customer ID", "Customer Name", "Segment",
        "Country", "City", "State", "Postal Code", "Region"
    ]].drop_duplicates(subset="Customer ID")
    customers.columns = ["customer_id", "customer_name", "segment", "country", "city", "state", "postal_code", "region"]
    customers.to_sql("customers", engine, schema="core", if_exists="append", index=False)


def load_products(df, engine):
    products = df[[
        "Product ID", "Category", "Sub-Category", "Product Name"
    ]].drop_duplicates(subset="Product ID")
    products.columns = ["product_id", "category", "sub_category", "product_name"]
    products.to_sql("products", engine, schema="core", if_exists="append", index=False)


def load_orders(df, engine):
    orders = df[[
        "Row ID", "Order ID", "Customer ID", "Product ID", "Order Date", "Ship Date",
        "Ship Mode", "Sales", "Quantity", "Discount", "Profit", "Delivery Time", "Profit Margin"
    ]].copy()
    orders.columns = [
        "row_id", "order_id", "customer_id", "product_id", "order_date", "ship_date",
        "ship_mode", "sales", "quantity", "discount", "profit", "delivery_time", "profit_margin"
    ]
    orders.to_sql("orders", engine, schema="core", if_exists="append", index=False)