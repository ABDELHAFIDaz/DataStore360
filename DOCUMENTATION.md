# DataStore360 — Technical Logbook

## EDA (Exploratory Data Analysis)

**Dataset:** `store_data.csv` — 10,064 rows, 21 columns.

**Initial structure (`df.info()`):**
- `Order Date` and `Ship Date` are loaded as text (`object`), not as dates — requires conversion (`pd.to_datetime`) before any delivery-time calculation.
- 4 numeric columns (`Sales`, `Quantity`, `Discount`, `Profit`), the rest is text.

**Missing values detected:**
| Column | Missing values |
|---|---|
| Ship Date | 101 |
| Ship Mode | 301 |
| Customer Name | 351 |
| Postal Code | 200 |
| Sales | 201 |
| Quantity | 199 |

Check performed: no missing values were hidden as text (`"N/A"`, `"null"`, etc.) — all are correctly recognized as `NaN` by pandas right from loading.

**Duplicates — initial detection (before any correction):**
- Naive check (`df.duplicated()`): **34 exact duplicates** detected.
- Duplicated `Row ID`: **70** in total — discrepancy with the 34 exact duplicates to investigate (some `Row ID` values seem to be reused for different orders). *Investigation ongoing, to be continued.*

**Formatting anomalies identified (via `.unique()` on categorical columns):**
- `Segment`: typos — `Consumerr` (→ `Consumer`), `Corporrate` (→ `Corporate`), `Home Ofice` (→ `Home Office`)
- `Category`: case inconsistency — `furniture`/`Furniture`, `office supplies`/`Office Supplies`, `technology`/`Technology`
- `Order Date`: mixed formats detected (`MM/DD/YYYY` and `YYYY-MM-DD` coexist in the same column)
- `Customer Name`: case inconsistencies (`Kunst Miller` vs `KUNST MILLER`)

**Columns checked and found clean (no anomalies):** `Ship Mode`, `Sub-Category`, `Region`, `Country`, `State`.

---

## Data Cleaning

**Text and date normalization**
- Case standardized (`.str.title()`) on: `Customer Name`, `Segment`, `City`, `State`, `Region`, `Ship Mode`, `Category`, `Sub-Category`.
- Dates parsed with `pd.to_datetime(..., format="mixed")` to handle the two coexisting formats.
- Result: after normalization, `df.duplicated()` detects **59 duplicates** (vs. 34 initially) — **25 duplicates were invisible** due to formatting inconsistencies.
- These 59 duplicates removed.

**Correcting**
- `Segment`: `Consumerr`→`Consumer`, `Corporrate`→`Corporate`, `Home Ofice`→`Home Office`.
- `Category`: case normalized (`furniture`→`Furniture`, etc. — column missed during the 1st normalization pass).
- Result: these corrections reveal **7 additional duplicates**, invisible until then due to these inconsistencies.
- These 7 duplicates removed.
- Filled and corrected the missing or invalid `Ship Date` from `Ship Mode` and vice versa
- filled the records with missing `Postal Code` with the most frequent one in the same city
- filled the records with no names with `Unknown`

**Droppin irreparable and duplicated records(rows)**
- Removed the records that have `Ship Date` < `Order Date`
- Removed records that have neither `Ship Date` or `Ship Mode`
- Removed records missing `Sales` or `Quantity` since there is nothing to estimate theme from (around 400 records dropped)
- Removed records (~10) with an invalid discount
- Removed records with negative `Quantity`

---

## GDPR/pseudonymization

- `Customer Name` is pseudonymized via SHA-256 hashing

---

## Derived business variables

- added two columns `Delivery Time` and `Profit Margin`

---

## Final Data Quality Summary

- Starting rows: 10,064
- Final rows after cleaning: 9,577
- Duplicates removed (total, across all rounds): 66 + 8 corrupted Row ID duplicates
- Quantity < 0: 0 found (rule satisfied by default, no removal needed)
- Discount > 1 or < 0: ~10 rows removed
- Ship Date < Order Date (invalid sentinel dates like 2010-01-01): corrected/removed as part of Ship Date/Mode handling

---


## Staging/Core Architecture

**Design principle:** two-layer separation between raw and transformed data.

- **`staging.superstore_raw`**: mirrors the source CSV exactly — same columns, no type constraints (everything stored as `TEXT`), no cleaning, no pseudonymization. Its purpose is to serve as an audit trail / safety net: proof of what was actually received, and a fallback if cleaning logic needs to be reworked or debugged.
- **`core.customers` / `core.products` / `core.orders`**: the cleaned, validated, normalized relational model.

---

## Airflow / Orchestration

`datastore360_pipeline` uses the TaskFlow API with 3 sequential tasks: extract to staging, clean, load to core. Idempotence is ensured via `TRUNCATE` before reload — verified by triggering the DAG twice with identical row counts both times (10,064 / 793 / 1,856 / 9,577). Airflow connects to PostgreSQL via a `postgres_default` connection configured in the UI.