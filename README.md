# DataStore360 — Sales Data Reliability Pipeline

A data engineering project for DataStore360, a retail company, to audit, clean, protect (GDPR), and structure raw sales data into a reliable, queryable PostgreSQL database — fully automated and orchestrated with Apache Airflow, running in Docker.

## Project Overview

The pipeline takes a raw sales dataset (orders, customers, products) containing real-world data quality issues — missing values, duplicates, formatting inconsistencies, unprotected personal data — and transforms it into a clean, GDPR-compliant, relational database with a two-layer architecture:

- **`staging`**: raw data, exactly as received, untouched
- **`core`**: cleaned, validated, normalized, and pseudonymized data ready for analysis

## Architecture

```
CSV (raw) → staging.superstore_raw → cleaning/GDPR → core.customers / core.products / core.orders
```

- **PostgreSQL** — data storage (staging/core schemas)
- **pgAdmin** — visual database management
- **Apache Airflow** (TaskFlow API) — pipeline orchestration
- **Docker Compose** — containerized environment
- **pandas / fg-data-profiling** — data exploration, cleaning, and automated quality profiling
- **SQLAlchemy / psycopg2** — Python ↔ PostgreSQL connectivity
- **uv** — Python dependency management

## Project Structure

```
├── dags/                  # Airflow DAG(s)
├── data/
│   ├── raw/                # Source CSV (not committed)
│   └── processed/          # Cleaned CSV output
├── include/sql/            # CREATE TABLE scripts (staging + core)
├── init-db/                # Postgres init script (creates airflow DB + schemas)
├── notebooks/               # EDA, cleaning, profiling notebooks
├── reports/                  # Data profiling HTML report
├── src/datastore360/         # Reusable Python modules (extract, clean, load, db)
├── docker-compose.yml
├── pyproject.toml / uv.lock
├── .env.example
├── DOCUMENTATION.md          # Technical logbook, decisions and justifications
└── README.md
```

## Setup

### Prerequisites
- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/)
- Python 3.12+

### 1. Clone the repository
```bash
git clone <repo-url>
cd DataStore360
```

### 2. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and set real values, notably:
- `AIRFLOW_UID` — your local user ID (run `id -u`)
- `AIRFLOW__CORE__FERNET_KEY` — generate with:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Add the dataset
Place `store_data.csv` in `data/raw/`.

### 4. Start the environment
```bash
docker compose up -d
```
This starts PostgreSQL, pgAdmin, and Airflow (webserver + scheduler). On first boot, `init-db/init-multiple-db.sh` automatically creates the `airflow` database and the `staging`/`core` schemas.

### 5. Install Python dependencies (for local notebook use)
```bash
uv sync
```

### 6. Create the database tables
Run the SQL scripts in `include/sql/` against the `datastore360` database — via pgAdmin's Query Tool (`localhost:5050`) or:
```bash
docker exec -it datastore360_postgres psql -U <user> -d datastore360 -f /opt/sql/create_staging.sql
docker exec -it datastore360_postgres psql -U <user> -d datastore360 -f /opt/sql/create_core.sql
```

### 7. Configure the Airflow ↔ Postgres connection
In the Airflow UI (`localhost:8080`) → **Admin → Connections**, create a connection with Conn Id `postgres_default`, pointing to the `postgres` service.

## Running the Pipeline

**Option A — via Airflow (recommended):**
Open `localhost:8080`, find `datastore360_pipeline`, and trigger it. It runs three tasks in sequence: extract → clean → load, populating both `staging` and `core`.

**Option B — manually, for exploration:**
Run the notebooks in order:
1. `notebooks/analyse.ipynb` — EDA
2. `notebooks/clean.ipynb` — cleaning, GDPR, derived variables
3. `notebooks/profiling.ipynb` — generates `reports/rapport_profiling.html`

## Data Quality & Compliance

- All EDA and cleaning decisions are documented with justification in [`DOCUMENTATION.md`](./DOCUMENTATION.md)
- `Customer Name` is pseudonymized via SHA-256 hashing before it ever reaches the `core` layer
- The pipeline is idempotent — re-running it does not create duplicates or errors (verified by repeated DAG runs)

## Access

| Service | URL |
|---|---|
| Airflow UI | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |
| PostgreSQL | localhost:5432 |