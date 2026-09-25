🌤 Serverless Cloud Weather Intelligence Pipeline

A Zero‑Trust, Cloud‑Native, Multi‑Region Weather Analytics Platform

This project is a fully‑automated, enterprise‑grade weather analytics pipeline engineered to ingest live atmospheric data, compute daily summaries, evaluate forecast accuracy, and visualize trends across time — all without a single server to maintain.



It is built for reliability, observability, and extensibility, following modern cloud architecture patterns and zero‑trust security principles.



🏗️ Architecture Overview

The system is composed of four major subsystems:



1\. Live METAR Ingestion (Hourly)

Source: National Weather Service (NWS) KCOS station



Frequency: Hourly



Writes to:



Astra DB (raw METAR snapshots)



BigQuery (weather\_observed\_metar)



2\. Daily Observed Summary (High/Low/Conditions)

Reads hourly METAR snapshots



Computes:



Daily high temperature



Daily low temperature



Daily summary (mode of text descriptions)



Writes to:



BigQuery (weather\_observed\_daily)



3\. Daily Forecast Ingestion

Source: NWS daily forecast API



Writes to:



BigQuery (weather\_forecast\_daily)



4\. Daily Forecast Accuracy Engine

Compares forecast vs actual



Computes:



High temp error



Low temp error



Rain error



Summary match score



Writes to:



BigQuery (weather\_accuracy\_daily)



🔐 Security \& Zero‑Trust Posture

This pipeline is designed under strict enterprise security principles:



Zero‑Trust Secrets Management

All credentials (Astra DB, BigQuery, service accounts) are injected at runtime using Doppler Secrets Manager.

No secrets exist in:



source code



environment files



GitHub Actions



local machines



Serverless Compute

All workloads run on:



GitHub Actions ephemeral VMs



Google BigQuery managed compute



Astra DB serverless NoSQL cluster



No persistent servers, no SSH access, no long‑lived credentials.



Encrypted Data Flow

All API calls use HTTPS



All secrets encrypted at rest and in transit



All cloud storage uses provider‑managed encryption (GCP + Azure)



☁️Cloud Architecture Diagram

NWS API (KCOS METAR + Forecast)

&#x20;           │

&#x20;           ▼

GitHub Actions (Hourly + Daily)

&#x20;           │

&#x20;┌──────────┴──────────┐

&#x20;│                     │

&#x20;▼                     ▼

Astra DB (Azure)     BigQuery (GCP)

Raw METAR            Forecast / Summary / Accuracy

&#x20;           │

&#x20;           ▼

Grafana Cloud / Looker Studio

Live Dashboards \& Analytics

📊 BigQuery Data Model

weather\_observed\_metar (Hourly)

Field	Type

timestamp	STRING

temp	FLOAT (°C)

wind\_speed	FLOAT

humidity	FLOAT

dewpoint	FLOAT

visibility	FLOAT

text\_description	STRING





weather\_observed\_daily (Daily Summary)

Field	Type

date	DATE

high\_actual\_f	FLOAT

low\_actual\_f	FLOAT

rain\_actual\_mm	FLOAT

summary\_actual	STRING

source\_run\_time	STRING





weather\_forecast\_daily (Daily Forecast)

Field	Type

date	DATE

high\_predicted\_f	FLOAT

low\_predicted\_f	FLOAT

pop\_predicted	FLOAT

summary\_predicted	STRING

source\_run\_time	STRING





weather\_accuracy\_daily (Daily Accuracy)

Field	Type

date	DATE

high\_error\_f	FLOAT

low\_error\_f	FLOAT

rain\_error\_mm	FLOAT

summary\_match\_score	FLOAT

source\_run\_time	STRING





⚙️ GitHub Actions Workflows

Hourly METAR Ingestion

File: .github/workflows/observed\_ingestion.yml  

Runs: weather\_observed\_daily.py



Daily Summary

File: .github/workflows/daily\_summary.yml  

Runs: weather\_observed\_summary\_daily.py



Daily Forecast

File: .github/workflows/forecast\_ingestion.yml  

Runs: weather\_forecast\_daily.py



Daily Accuracy

File: .github/workflows/accuracy\_compute.yml  

Runs: weather\_accuracy\_daily.py



All workflows use:



Doppler CLI Action



Python 3.11



BigQuery batch load jobs



Zero‑trust secrets injection



🧪 Local Development

Run any script locally with Doppler:

doppler run --config gcp\_personal -- python weather\_observed\_daily.py

doppler run --config gcp\_personal -- python weather\_observed\_summary\_daily.py

doppler run --config gcp\_personal -- python weather\_forecast\_daily.py

doppler run --config gcp\_personal -- python weather\_accuracy\_daily.py

📈 Grafana Cloud Dashboards

The pipeline feeds Grafana with:



Hourly METAR temperature (converted to °F)



Daily observed high/low



Daily forecast high/low



Daily forecast error (actual – predicted)



Summary match score



Future dashboards planned:



Wind speed trends



Humidity / dewpoint charts



Visibility degradation alerts



Rolling 7‑day accuracy models



Forecast bias analysis



🚀 Phase 1 Scope (Current Release)

Supported

KCOS (Colorado Springs Airport) METAR ingestion



Daily forecast ingestion



Daily observed summary



Daily accuracy computation



Grafana dashboards



Zero‑trust secrets



Serverless compute



Multi‑cloud architecture (Azure + GCP)



Limitations

Only KCOS station supported



No rainfall ingestion yet



No multi‑station aggregation



No terrain‑specific modeling



No anomaly detection



No alerting yet



No Terraform automation yet



🌄 Phase 2 Roadmap (Future Enhancements)

🌐 Multi‑Station Expansion

Woodland Park



Denver



Pueblo



Mountain‑specific microclimate modeling



📣 Discord Alerting

Severe weather alerts



Forecast accuracy drops



METAR anomalies



📊 Advanced Grafana Dashboards

Rolling accuracy windows



Forecast bias heatmaps



Multi‑station comparison



Wind / humidity / dewpoint analytics



🛠 Terraform Automation

BigQuery dataset creation



Service account provisioning



Grafana datasource setup



Astra DB keyspace automation



🌐 Personal Weather Website

Public dashboards



API endpoints



Forecast vs actual visualizations



Historical accuracy explorer



⚠️ Current Limitations \& Known Constraints

Phase 1 — Colorado Springs (KCOS) Prototype

Even though the pipeline is fully functional, it intentionally operates within several constraints. These limitations are not flaws — they are design decisions aligned with free‑tier cloud resources, early‑stage prototyping, and zero‑trust architecture.



🧩 1. BigQuery Sandbox Limitations

BigQuery’s free tier (Sandbox) imposes several constraints:



⛔ No Scheduled Queries

All daily computations must run through GitHub Actions instead of BigQuery’s native scheduler.



⛔ 60‑Day Table Expiration (for sandbox datasets)

Sandbox datasets auto‑expire after 60 days unless manually copied into a permanent dataset.



You solved this by:



Creating permanent datasets (weather\_data)



Copying tables into non‑expiring storage



Automating table recreation via GitHub Actions



This shows strong cloud‑architecture awareness.



🧩 2. No Deduplication Logic Yet

Some tables (especially weather\_forecast\_daily and weather\_accuracy\_daily) may contain multiple rows per day because:



Forecast ingestion runs daily but NWS sometimes updates forecasts multiple times



Accuracy computation runs daily but may be triggered manually



No WRITE\_TRUNCATE or dedupe SQL is applied yet



This is a known Phase 1 limitation and will be addressed in Phase 2 with:



BigQuery MERGE statements



Daily partitioning



Deduplication logic



Forecast versioning



🧩 3. Single‑Station Support (KCOS Only)

Phase 1 focuses exclusively on:



Colorado Springs Airport (KCOS) METAR



Colorado Springs forecast zone



This is intentional — it keeps the pipeline simple while validating the architecture.



Phase 2 will expand to:



Woodland Park



Denver



Pueblo



Mountain microclimates



Multi‑station aggregation



Regional forecast bias modeling



🧩 4. No Rainfall Ingestion Yet

METAR data includes precipitation, but the NWS JSON feed used in Phase 1 does not expose rainfall in a consistent field.



As a result:



rain\_actual\_mm is always NULL



rain\_error\_mm is always NULL



Phase 2 will add:



Precipitation accumulation ingestion



Radar‑based rainfall estimates



Snowfall detection



Storm event tagging



🧩 5. Free‑Tier Cloud Constraints

The pipeline is intentionally built using free tiers:



Astra DB Free Tier

Limited throughput



Single region



No multi‑AZ replication



No VPC peering



BigQuery Free Tier

10 GB storage



1 TB queries per month



No BI Engine



No scheduled queries



No long‑term storage discounts



GitHub Actions Free Tier

Limited monthly minutes



No self‑hosted runners



No persistent storage



Despite these constraints, the pipeline achieves:



Hourly ingestion



Daily analytics



Zero‑trust security



Multi‑cloud architecture



Grafana dashboards



🧩 6. No Terraform Automation Yet

All cloud resources are currently created manually:



BigQuery datasets



Service accounts



Astra DB collections



Grafana datasources



Phase 2 will introduce Terraform to automate:



GCP IAM



BigQuery datasets



Grafana provisioning



Astra DB keyspaces



GitHub Actions secrets



Doppler project scaffolding



This is a major enterprise‑readiness milestone.



🧩 7. No Alerting or Notifications Yet

The pipeline does not yet send alerts for:



Severe weather



Forecast accuracy drops



METAR anomalies



Pipeline failures



Missing data



Phase 2 will add:



Discord alerting



Grafana alert rules



BigQuery anomaly detection



Daily health checks



🧩 8. No Public Website Yet

The pipeline is ready for a front‑end, but Phase 1 does not include:



A personal weather website



Public dashboards



API endpoints



Historical accuracy explorer



Forecast bias visualizations



Phase 2 will introduce:



A full weather analytics website



Public Grafana dashboards



REST API endpoints



Interactive charts



Woodland Park microclimate pages



🧩 9. No Multi‑Day Forecast Accuracy Yet

Accuracy is computed only for yesterday:



High temp error



Low temp error



Summary match score



Phase 2 will add:



3‑day accuracy



7‑day accuracy



Rolling forecast bias



Forecast drift modeling



Machine learning scoring



🧩 10. No Automated Backfilling

If a workflow fails, the pipeline does not automatically:



Recompute missing daily summaries



Recompute missing accuracy rows



Re‑ingest missing METAR snapshots



Re‑ingest missed forecasts



Phase 2 will add:



Backfill scripts



BigQuery stored procedures



Retry logic



Self‑healing workflows

