CREATE TABLE IF NOT EXISTS core.customers (
    customer_id     TEXT PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    segment         TEXT NOT NULL,
    country         TEXT NOT NULL,
    city            TEXT NOT NULL,
    state           TEXT NOT NULL,
    postal_code     TEXT,
    region          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS core.products (
    product_id      TEXT PRIMARY KEY,
    category        TEXT NOT NULL,
    sub_category    TEXT NOT NULL,
    product_name    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS core.orders (
    row_id          INTEGER PRIMARY KEY,
    order_id        TEXT NOT NULL,
    customer_id     TEXT NOT NULL REFERENCES core.customers(customer_id),
    product_id      TEXT NOT NULL REFERENCES core.products(product_id),
    order_date      DATE NOT NULL,
    ship_date       DATE NOT NULL,
    ship_mode       TEXT NOT NULL,
    sales           NUMERIC(12, 4) NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity >= 0),
    discount        NUMERIC(4, 3) NOT NULL CHECK (discount >= 0 AND discount <= 1),
    profit          NUMERIC(12, 4) NOT NULL,
    delivery_time   INTEGER CHECK (delivery_time >= 0),
    profit_margin   NUMERIC(10, 4)
);