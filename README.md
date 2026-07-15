# The gole of this project to show real world use case of using data engineering concepts and tools.

## Pre-requisites:
1. E-commerce shop that functions on InSales (Shopyfy-like CRM and more)
2. Company leaders constantly look for a way to reduce costs and transition to self-hosted shop on woocommerce looks like a deal-breaker in a current situation.
3. I dont use ready-to-use software (like Cart2Cart) bc the goal is to make not one-time transition but to create one more istance of the shop that gets all the data from the old one in a realtine to make the lunch and beta-testin as smooth as possible.

## Project structure

Medalion principle:
- Bronze: Extracting data from InSales (Commercial ecommerce CRM) to S3 Data Lake
- Silver: Preparing data for transition to Silver level (Postgres/Snowflake)
- Gold: Importing data (orders, products, customers) to Woocommerce MySQL database.

## Pipeline schema

[InSales API] 
       │
       ▼  (Extraction: Airflow orchestrates PySpark)
   [ AWS S3 (MiniO) ] (Raw JSON/CSV Landing Zone)
       │
       ▼  (Loading)
  [ Snowflake ] (Raw Schemas)
       │
       ▼  (Transformation & Modeling: dbt)
  [ Snowflake ] (Transformed / Cleaned schemas mapped to WooCommerce)
       │
       ▼  (Reverse ETL: Airflow/PySpark script calls WC REST API)
[ WooCommerce Store ]

## Main Concepts

### Distributed Storage

### Partitioning / Sharding

- Bronze layer: File path structuring in a tree-like structure of folders
    -- Orders: Time-based partitioning 
        (Example: bronze/orders/year=2026/month=03/day=15/orders_12034.json)
    -- Products: Category-based partitioning
        (Example: bronze/products/category=electronics/products.json)
    -- Customers: Hash-partitioning (Sharding)
        (Example: bronze/customers/shard=0/customer_1.json)
- Silver Layer: 
- Gold Layer:

### Message Queues / Streaming

### Transactions & ACID

## Why is that important

## Airflow Docker Environment
If your Airflow will be in a separate Docker container than add
    environment:
        - VAULT_ADDR=http://hashicorp_vault:8200  # or http://host.docker.internal:8200



