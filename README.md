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

