\# Serverless Cloud Weather Data Pipeline



An enterprise-grade, zero-trust data pipeline that extracts live, time-series weather observations for Colorado Springs (KCOS) and streams the data into a secure cloud environment.



\## Architecture \& Security Posture

\- \*\*Infrastructure Hardening:\*\* Designed under a strict Zero-Trust access model. No database strings, application tokens, or contact points are hardcoded or stored in flat text files.

\- \*\*Secrets Management:\*\* Integrates \*\*Doppler Secrets Manager\*\* to securely inject encrypted credentials natively into execution memory at runtime.

\- \*\*Data Layer:\*\* Connected to a cloud-native, serverless \*\*DataStax Astra DB / Apache Cassandra\*\* NoSQL cluster running on Microsoft Azure.



&#x20;                         ┌────────────────────────┐

&#x20;                         │  NWS API Data Stream            │

&#x20;                         └───────────┬────────────┘

&#x20;                                         │

&#x20;                                         ▼

&#x20;                       ┌───────────────────────────┐

&#x20;                       │    GitHub Actions VM                │◀─── \[Scheduled Every Hour]

&#x20;                       │   (Serverless Compute)              │

&#x20;                       └──────┬─────────────┬──────┘

&#x20;                                 │                 │

&#x20;                 (Azure Network) │                 │ (GCP Network)

&#x20;                                 ▼                 ▼

&#x20;                 ┌─────────────────┐   ┌─────────────────┐

&#x20;                 │ Azure Astra DB         │   │  GCP BigQuery         │

&#x20;                 │   (NoSQL app)          │   │(Data Warehouse)       │

&#x20;                 └────────┬────────┘   └────────┬────────┘

&#x20;                             │                            │

&#x20;                             └──────────┬──────────┘

&#x20;                                            ▼

&#x20;                       ┌───────────────────────────┐

&#x20;                       │   Grafana Cloud/Looker              │◀─── \[Live Dashboard Graphs]

&#x20;                       │    (Visual Monitoring)              │

&#x20;                       └───────────────────────────┘



Astra DB → stores raw hourly observations

Python ETL → writes to Astra

Doppler → secrets

GitHub Actions → scheduling

Python forecast script → writes predictions → BigQuery

Python daily summary script → reads Astra → writes actuals → BigQuery

BigQuery SQL → computes accuracy → BigQuery

Grafana → visualizes accuracy



Weather Cloud Pipeline — Forecast, Observed, and Accuracy Engine

This project is a fully‑cloud‑native weather analytics pipeline built on:



Astra DB (hourly observations)



BigQuery (daily forecast, observed summary, accuracy)



GitHub Actions (scheduled ingestion + computation)



Doppler (zero‑trust secret management)



The pipeline ingests live weather data, computes daily summaries, calculates forecast accuracy, and stores everything in BigQuery for visualization in Grafana or Looker.



Architecture Overview

1\. Hourly Observations → Astra DB

Script: weather\_pipeline.py  

Workflow: .github/workflows/observed\_ingestion.yml



Runs every hour



Fetches latest NWS observation



Streams into Astra DB collection



Stores fields like temperature, humidity, wind, summary, timestamp



2\. Daily Forecast → BigQuery

Script: weather\_forecast\_daily.py  

Workflow: .github/workflows/forecast\_ingestion.yml



Runs daily



Fetches NWS daily forecast



Loads into BigQuery using batch load jobs



Stores predicted high/low temps, POP, summary



3\. Daily Observed Summary → BigQuery

Script: weather\_observed\_daily.py  

Workflow: .github/workflows/observed\_ingestion.yml (hourly)

Summary workflow: .github/workflows/accuracy\_compute.yml (daily)



Reads hourly Astra data



Computes daily high/low temps, rainfall, summary



Loads into BigQuery



4\. Daily Accuracy → BigQuery

Script: weather\_accuracy\_daily.py  

Workflow: .github/workflows/accuracy\_compute.yml



Compares forecast vs observed



Computes error metrics



Stores accuracy results in BigQuery



BigQuery Tables

weather\_forecast\_daily

Column	Type

date	DATE

source\_run\_time	STRING

high\_predicted\_f	INT64

low\_predicted\_f	INT64

pop\_predicted	INT64

summary\_predicted	STRING





weather\_observed\_daily

Column	Type

date	DATE

source\_run\_time	STRING

high\_actual\_f	INT64

low\_actual\_f	INT64

rain\_actual\_mm	FLOAT64

summary\_actual	STRING





weather\_accuracy\_daily

Column	Type

date	DATE

source\_run\_time	STRING

high\_error\_f	FLOAT64

low\_error\_f	FLOAT64

rain\_error\_mm	FLOAT64

summary\_match\_score	FLOAT64





GitHub Actions Workflows

Hourly Observed Ingestion

Code

.github/workflows/observed\_ingestion.yml

Daily Forecast Ingestion

Code

.github/workflows/forecast\_ingestion.yml

Daily Accuracy Computation

Code

.github/workflows/accuracy\_compute.yml

All workflows use:



Doppler CLI Action



Python 3.11



Your scripts



BigQuery batch load jobs



Secrets (Doppler)

Your gcp\_personal config must contain:



Astra

ASTRA\_DB\_APPLICATION\_TOKEN



ASTRA\_DB\_API\_ENDPOINT



Google Cloud

GOOGLE\_APPLICATION\_CREDENTIALS\_JSON



BQ\_PROJECT\_ID



BQ\_FORECAST\_TABLE



BQ\_OBSERVED\_TABLE



BQ\_ACCURACY\_TABLE



Local Development

Run any script locally using Doppler:



Code

doppler run --config gcp\_personal -- python weather\_forecast\_daily.py

doppler run --config gcp\_personal -- python weather\_observed\_daily.py

doppler run --config gcp\_personal -- python weather\_accuracy\_daily.py

Grafana / Looker Integration

Once BigQuery is populated:



Connect BigQuery as a data source



Build dashboards for:



Daily forecast



Daily observed



Accuracy trends



Error metrics

