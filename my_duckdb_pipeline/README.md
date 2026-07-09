**Serverless Medallion Lakehouse: End-to-End Airbnb Analytics Pipeline**

An end-to-end, highly cost-optimized, and serverless modern data stack portfolio project designed for an Analytics Engineering role. This repository demonstrates how to build a fully functional Medallion Architecture (Bronze → Silver → Gold) using open-source tools, executing entirely within a localized compute environment without the overhead or billing costs of a cloud data warehouse.

Architecture Overview

The pipeline extracts raw relational Airbnb datasets (Bookings, Hostings, and Listings) from an Amazon S3 bucket, ingests them into a local columnar engine, transforms them into an optimized Star Schema, and serves downstream executive metrics via a semantic reporting layer.

The Technical Stack
• Storage Layer: Amazon S3 (Houses raw CSV data partitions).
• Ingestion (ELT): dlt (Data Load Tool) automates schema inference, tracking, and incremental landing into the Bronze layer.
• Storage & Query Engine: DuckDB (Vectorized, serverless columnar engine handling fast embedded execution).
• Transformation & Modeling: dbt (dbt-duckdb adapter manages layering, testing, documentation, and DAG orchestration).
• Semantic Visualization: Streamlit + Plotly (Python application compiling interactive, high-performance dashboards directly against DuckDB).

------------

💾 Medallion Data Engineering Framework

1. Bronze Layer (Raw Storage)
Data is extracted from S3 using dlt and loaded as-is into DuckDB tables (raw_listings, raw_bookings, raw_hosts). This layer acts as an append-only, immutable historical record with zero schema alterations or type alterations.

2. Silver Layer (Staging & Data Hygiene)
Located in models/silver/, this layer standardizes naming conventions to snake_case, handles type-casting, and implements data quality controls.
• Materialization Strategy: view. Leveraging DuckDB's exceptional single-table scan performance, materializing Silver as views entirely eliminates redundant storage footprints while ensuring downstream models ingest live logic.
• Key Interventions:
  ◦ Filter Alignment & Consistency: Implemented rigid condition hooks (e.g., isolate booking_status = 'confirmed') to ensure foundational metrics perfectly reconcile across disparate reporting layers.
  ◦ Boolean Standardization: Converted varied text string representations ('t', 'f', '1', '0') into true SQL Booleans.
  ◦ Type Hardening: Cast text strings into specific DATE fields (enabling chronological calculations) and financial strings into precise currency scales (DECIMAL(10,2)).

3. Gold Layer (Dimensional Modeling & Star Schema)
Located in transform/models/gold/, this layer models the conformed warehouse layer into an optimized Star Schema for end-user analytics consumption.
• Materialization Strategy: table. To minimize query response times for BI tools executing complex multi-way joins, Gold models are pre-computed and cached as physical tables.
• The Models:
  ◦ dim_listings: A consolidated asset dimension table. Host attributes were explicitly denormalized into this property table to completely remove a painful "join-chain" for end analysts.
  ◦ fct_bookings: A granular transactional fact table capturing core bookings. Includes pre-computed business logic for derived revenue streams (total_gross_revenue).
  ◦ fct_monthly_listing_performance: A Periodic Snapshot Fact Table. It takes a monthly "pulse" of property metrics, pre-aggregating vacancy, revenue, and cancellation volumes. This shifts heavy aggregation computation from dashboard runtime to the dbt compile-phase.

---------

🧠 Core Analytics Design Decisions

Why is price_per_night in a Dimension Table instead of a Fact Table?
A common misconception is that all monetary columns belong in fact tables. In this architecture, a clear distinction is drawn between a Price (Attribute) and an Amount (Metric):
• booking_amount is an event metric—it only exists because a financial transaction took place, and belongs in fct_bookings.
• price_per_night is a structural characteristic of the property asset. It exists independently of whether a booking event occurs. Keeping it inside dim_listings allows business analysts to cleanly bucket, filter, and slice performance by pricing tiers.

## 📊 Live Dashboard Interface

The final analytical layer is served via a high-performance Streamlit data application, querying pre-aggregated Gold metrics natively from the DuckDB instance.

![Marketplace Performance Dashboard](images/dashboard_mockup.png)

### Key Features Evident in the Analytical Interface:
* **Primary KPIs:** High-level metrics tracking Gross Revenue, Confirmed Booking counts, Platform Revenue, and Average Nightly Rates.
* **Regional Growth Dynamics:** Dynamically isolated to display the top 5 revenue-generating cities, reducing visualization noise and surfacing true seasonality spikes (such as the Q2/Q3 summer demand wave).
* **Operational Leakage Tracking:** A dedicated line-analysis chart capturing cancellation volatility across key regional markets over time.
* **Strategic Business Insights:** Automated, data-driven recommendation cards summarizing marketplace inventory density and structural risk mitigation strategies based on real-time warehouse data.


---

🛠️ Repository Directory Structure

```text
├── dlt_pipeline/            # --- INGESTION LAYER (dlt) ---
│   └── s3_to_bronze.py      # Python ingestion script targeting DuckDB
├── transform/               # --- TRANSFORMATION LAYER (dbt) ---
│   ├── dbt_project.yml      # Layer materialization routing configurations
│   ├── profiles.yml         # Target profile configuration
│   └── models/
│       ├── silver/          # Cleaned & Standardized Source Views
│       │   ├── stg_airbnb__bookings.sql
│       │   ├── stg_airbnb__hosts.sql
│       │   └── stg_airbnb__listings.sql
│       └── gold/            # Analytical Core (Star Schema Constellation)
│           ├── schema.yml   # Data Quality Guardrails & Documentation
│           ├── dim_listings.sql
│           ├── fct_bookings.sql
│           └── fct_monthly_listing_performance.sql
├── dashboard.py             # --- VISUALIZATION LAYER --- (Streamlit App)
└── README.md
---