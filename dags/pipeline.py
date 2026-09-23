import sys
sys.path.append("/opt/airflow/src")

from datetime import datetime
import pandas as pd
from airflow.decorators import dag, task

from datastore360.extract import load_raw_csv, load_to_staging
from datastore360.clean import (
    normalize_text_columns, parse_dates, fix_typos, fix_known_row_id_conflicts,
    handle_missing_ship_date_mode, handle_missing_sales_quantity,
    handle_missing_postal_code, handle_missing_customer_name,
    validate_discount, validate_quantity, remove_duplicates,
    add_delivery_time, add_profit_margin, hash_customer_name
)
from datastore360.load import clear_core_tables, load_customers, load_products, load_orders
from datastore360.db import get_engine


RAW_CSV_PATH = "/opt/airflow/data/raw/store-data-360.csv"
CLEAN_CSV_PATH = "/opt/airflow/data/processed/superstore_clean.csv"


@dag(
    dag_id="datastore360_pipeline",
    description="Extract, clean, and load data into staging/core",
    schedule=None,
    start_date=datetime(2026, 9, 1),
    catchup=False,
)
def datastore360_pipeline():

    @task
    def extract_and_load_staging():
        engine = get_engine()
        raw_df = load_raw_csv(RAW_CSV_PATH)
        load_to_staging(raw_df, engine)
        return RAW_CSV_PATH 

    @task
    def clean_data(raw_csv_path):
        df = pd.read_csv(raw_csv_path)

        df = normalize_text_columns(df)
        df = parse_dates(df)
        df = fix_typos(df)
        df = fix_known_row_id_conflicts(df)
        df = handle_missing_ship_date_mode(df)
        df = handle_missing_sales_quantity(df)
        df = handle_missing_postal_code(df)
        df = handle_missing_customer_name(df)
        df = validate_discount(df)
        df = validate_quantity(df)
        df = remove_duplicates(df)
        df = add_delivery_time(df)
        df = add_profit_margin(df)
        df = hash_customer_name(df)

        df.to_csv(CLEAN_CSV_PATH, index=False)
        return CLEAN_CSV_PATH

    @task
    def load_core_tables(clean_csv_path):
        engine = get_engine()
        df = pd.read_csv(clean_csv_path)

        clear_core_tables(engine)
        load_customers(df, engine)
        load_products(df, engine)
        load_orders(df, engine)

    load_core_tables(clean_data(extract_and_load_staging()))


datastore360_pipeline()