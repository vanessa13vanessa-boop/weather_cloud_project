\# Serverless Cloud Weather Data Pipeline



An enterprise-grade, zero-trust data pipeline that extracts live, time-series weather observations for Colorado Springs (KCOS) and streams the data into a secure cloud environment.



\## Architecture \& Security Posture

\- \*\*Infrastructure Hardening:\*\* Designed under a strict Zero-Trust access model. No database strings, application tokens, or contact points are hardcoded or stored in flat text files.

\- \*\*Secrets Management:\*\* Integrates \*\*Doppler Secrets Manager\*\* to securely inject encrypted credentials natively into execution memory at runtime.

\- \*\*Data Layer:\*\* Connected to a cloud-native, serverless \*\*DataStax Astra DB / Apache Cassandra\*\* NoSQL cluster running on Microsoft Azure.



