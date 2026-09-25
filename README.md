<h1 align="center">🌤 Serverless Cloud Weather Intelligence Pipeline</h1>
<h3 align="center"><i>A Zero‑Trust, Cloud‑Native, Multi‑Region Weather Analytics Platform</i></h3>

<p>
This project is a fully automated, enterprise‑grade weather analytics pipeline engineered to ingest live atmospheric data, compute daily summaries, evaluate forecast accuracy, and visualize trends — all without a single server to maintain.
</p>

<p>
It is built for reliability, observability, and extensibility, following modern cloud architecture patterns and zero‑trust security principles.
</p>

<hr>

<h2>🏗️ Architecture Overview</h2>

<p>The system is composed of four major subsystems:</p>

<h3>1. Live METAR Ingestion (Hourly)</h3>
<ul>
  <li><b>Source:</b> National Weather Service (NWS) KCOS station</li>
  <li><b>Frequency:</b> Hourly</li>
  <li><b>Writes to:</b>
    <ul>
      <li>Astra DB (raw METAR snapshots)</li>
      <li>BigQuery (<code>weather_observed_metar</code>)</li>
    </ul>
  </li>
</ul>

<h3>2. Daily Observed Summary (High/Low/Conditions)</h3>
<ul>
  <li>Reads hourly METAR snapshots</li>
  <li>Computes:
    <ul>
      <li>Daily high temperature</li>
      <li>Daily low temperature</li>
      <li>Daily summary (mode of text descriptions)</li>
    </ul>
  </li>
  <li><b>Writes to:</b> BigQuery (<code>weather_observed_daily</code>)</li>
</ul>

<h3>3. Daily Forecast Ingestion</h3>
<ul>
  <li><b>Source:</b> NWS daily forecast API</li>
  <li><b>Writes to:</b> BigQuery (<code>weather_forecast_daily</code>)</li>
</ul>

<h3>4. Daily Forecast Accuracy Engine</h3>
<ul>
  <li>Compares forecast vs actual</li>
  <li>Computes:
    <ul>
      <li>High temp error</li>
      <li>Low temp error</li>
      <li>Rain error</li>
      <li>Summary match score</li>
    </ul>
  </li>
  <li><b>Writes to:</b> BigQuery (<code>weather_accuracy_daily</code>)</li>
</ul>

<hr>

<h2>🔐 Security & Zero‑Trust Posture</h2>

<h3>Zero‑Trust Secrets Management</h3>
<p>All credentials (Astra DB, BigQuery, service accounts) are injected at runtime using <b>Doppler Secrets Manager</b>.</p>

<p>No secrets exist in:</p>
<ul>
  <li>source code</li>
  <li>environment files</li>
  <li>GitHub Actions</li>
  <li>local machines</li>
</ul>

<h3>Serverless Compute</h3>
<ul>
  <li>GitHub Actions ephemeral VMs</li>
  <li>Google BigQuery managed compute</li>
  <li>Astra DB serverless NoSQL cluster</li>
</ul>

<p>No persistent servers, no SSH access, no long‑lived credentials.</p>

<h3>Encrypted Data Flow</h3>
<ul>
  <li>All API calls use HTTPS</li>
  <li>All secrets encrypted at rest and in transit</li>
  <li>All cloud storage uses provider‑managed encryption (GCP + Azure)</li>
</ul>

<hr>

<h2>☁️ Cloud Architecture Diagram</h2>

<pre>
NWS API (KCOS METAR + Forecast)
            │
            ▼
GitHub Actions (Hourly + Daily)
            │
 ┌──────────┴──────────┐
 │                     │
 ▼                     ▼
Astra DB (Azure)     BigQuery (GCP)
Raw METAR            Forecast / Summary / Accuracy
            │
            ▼
Grafana Cloud / Looker Studio
Live Dashboards & Analytics
</pre>

<hr>

<h2>📊 BigQuery Data Model</h2>

<h3><code>weather_observed_metar</code> (Hourly)</h3>
<table>
<tr><th>Field</th><th>Type</th></tr>
<tr><td>timestamp</td><td>STRING</td></tr>
<tr><td>temp</td><td>FLOAT (°C)</td></tr>
<tr><td>wind_speed</td><td>FLOAT</td></tr>
<tr><td>humidity</td><td>FLOAT</td></tr>
<tr><td>dewpoint</td><td>FLOAT</td></tr>
<tr><td>visibility</td><td>FLOAT</td></tr>
<tr><td>text_description</td><td>STRING</td></tr>
</table>

<h3><code>weather_observed_daily</code> (Daily Summary)</h3>
<table>
<tr><th>Field</th><th>Type</th></tr>
<tr><td>date</td><td>DATE</td></tr>
<tr><td>high_actual_f</td><td>FLOAT</td></tr>
<tr><td>low_actual_f</td><td>FLOAT</td></tr>
<tr><td>rain_actual_mm</td><td>FLOAT</td></tr>
<tr><td>summary_actual</td><td>STRING</td></tr>
<tr><td>source_run_time</td><td>STRING</td></tr>
</table>

<h3><code>weather_forecast_daily</code> (Daily Forecast)</h3>
<table>
<tr><th>Field</th><th>Type</th></tr>
<tr><td>date</td><td>DATE</td></tr>
<tr><td>high_predicted_f</td><td>FLOAT</td></tr>
<tr><td>low_predicted_f</td><td>FLOAT</td></tr>
<tr><td>pop_predicted</td><td>FLOAT</td></tr>
<tr><td>summary_predicted</td><td>STRING</td></tr>
<tr><td>source_run_time</td><td>STRING</td></tr>
</table>

<h3><code>weather_accuracy_daily</code> (Daily Accuracy)</h3>
<table>
<tr><th>Field</th><th>Type</th></tr>
<tr><td>date</td><td>DATE</td></tr>
<tr><td>high_error_f</td><td>FLOAT</td></tr>
<tr><td>low_error_f</td><td>FLOAT</td></tr>
<tr><td>rain_error_mm</td><td>FLOAT</td></tr>
<tr><td>summary_match_score</td><td>FLOAT</td></tr>
<tr><td>source_run_time</td><td>STRING</td></tr>
</table>

<hr>

<h2>⚙️ GitHub Actions Workflows</h2>

<h3>Hourly METAR Ingestion</h3>
<p><b>File:</b> <code>.github/workflows/observed_ingestion.yml</code><br>
<b>Runs:</b> <code>weather_observed_daily.py</code></p>

<h3>Daily Summary</h3>
<p><b>File:</b> <code>.github/workflows/daily_summary.yml</code><br>
<b>Runs:</b> <code>weather_observed_summary_daily.py</code></p>

<h3>Daily Forecast</h3>
<p><b>File:</b> <code>.github/workflows/forecast_ingestion.yml</code><br>
<b>Runs:</b> <code>weather_forecast_daily.py</code></p>

<h3>Daily Accuracy</h3>
<p><b>File:</b> <code>.github/workflows/accuracy_compute.yml</code><br>
<b>Runs:</b> <code>weather_accuracy_daily.py</code></p>

<p>All workflows use:</p>
<ul>
  <li>Doppler CLI Action</li>
  <li>Python 3.11</li>
  <li>BigQuery batch load jobs</li>
  <li>Zero‑trust secrets injection</li>
</ul>

<hr>

<h2>🧪 Local Development</h2>

<pre>
doppler run --config gcp_personal -- python weather_observed_daily.py
doppler run --config gcp_personal -- python weather_observed_summary_daily.py
doppler run --config gcp_personal -- python weather_forecast_daily.py
doppler run --config gcp_personal -- python weather_accuracy_daily.py
</pre>

<hr>

<h2>📈 Grafana Cloud Dashboards</h2>

<p>The pipeline feeds Grafana with:</p>
<ul>
  <li>Hourly METAR temperature (converted to °F)</li>
  <li>Daily observed high/low</li>
  <li>Daily forecast high/low</li>
  <li>Daily forecast error (actual − predicted)</li>
  <li>Summary match score</li>
</ul>

<h3>Future dashboards planned</h3>
<ul>
  <li>Wind speed trends</li>
  <li>Humidity / dewpoint charts</li>
  <li>Visibility degradation alerts</li>
  <li>Rolling 7‑day accuracy models</li>
  <li>Forecast bias analysis</li>
</ul>

<hr>

<h2>🚀 Phase 1 Scope (Current Release)</h2>

<h3>Supported</h3>
<ul>
  <li>KCOS METAR ingestion</li>
  <li>Daily forecast ingestion</li>
  <li>Daily observed summary</li>
  <li>Daily accuracy computation</li>
  <li>Grafana dashboards</li>
  <li>Zero‑trust secrets</li>
  <li>Serverless compute</li>
  <li>Multi‑cloud architecture (Azure + GCP)</li>
</ul>

<h3>Limitations</h3>
<ul>
  <li>Only KCOS station supported</li>
  <li>No rainfall ingestion yet</li>
  <li>No multi‑station aggregation</li>
  <li>No terrain‑specific modeling</li>
  <li>No anomaly detection</li>
  <li>No alerting yet</li>
  <li>No Terraform automation yet</li>
</ul>

<hr>

<h2>🌄 Phase 2 Roadmap (Future Enhancements)</h2>

<h3>Multi‑Station Expansion</h3>
<ul>
  <li>Woodland Park</li>
  <li>Denver</li>
  <li>Pueblo</li>
  <li>Mountain microclimates</li>
</ul>

<h3>Discord Alerting</h3>
<ul>
  <li>Severe weather alerts</li>
  <li>Forecast accuracy drops</li>
  <li>METAR anomalies</li>
</ul>

<h3>Advanced Grafana Dashboards</h3>
<ul>
  <li>Rolling accuracy windows</li>
  <li>Forecast bias heatmaps</li>
  <li>Multi‑station comparison</li>
  <li>Wind / humidity / dewpoint analytics</li>
</ul>

<h3>Terraform Automation</h3>
<ul>
  <li>BigQuery dataset creation</li>
  <li>Service account provisioning</li>
  <li>Grafana datasource setup</li>
  <li>Astra DB keyspace automation</li>
</ul>

<h3>Personal Weather Website</h3>
<ul>
  <li>Public dashboards</li>
  <li>API endpoints</li>
  <li>Forecast vs actual visualizations</li>
  <li>Historical accuracy explorer</li>
</ul>

<hr>

<h2>⚠️ Current Limitations & Known Constraints</h2>

<p>Even though the pipeline is fully functional, it intentionally operates within several constraints aligned with free‑tier cloud resources, early‑stage prototyping, and zero‑trust architecture.</p>

<h3>1. BigQuery Sandbox Limitations</h3>
<ul>
  <li>No scheduled queries</li>
  <li>60‑day table expiration</li>
  <li>No BI Engine</li>
  <li>No long‑term storage discounts</li>
</ul>

<h4>Solved this by:</h4>
<ul>
  <li>Creating permanent datasets (<code>weather_data</code>)</li>
  <li>Copying tables into non‑expiring storage</li>
  <li>Automating table recreation via GitHub Actions</li>
</ul>

<h3>2. No Deduplication Logic Yet</h3>
<ul>
  <li>Multiple NWS forecast updates</li>
  <li>Manual workflow triggers</li>
  <li>No MERGE logic yet</li>
</ul>

<h4>Phase 2 will add:</h4>
<ul>
  <li>BigQuery MERGE statements</li>
  <li>Daily partitioning</li>
  <li>Forecast versioning</li>
</ul>

<h3>3. Single‑Station Support (KCOS Only)</h3>
<ul>
  <li>Phase 1 focuses exclusively on Colorado Springs</li>
</ul>

<h4>Phase 2 expands to:</h4>
<ul>
  <li>Woodland Park</li>
  <li>Denver</li>
  <li>Pueblo</li>
  <li>Mountain microclimates</li>
</ul>

<h3>4. No Rainfall Ingestion Yet</h3>
<ul>
  <li>METAR JSON feed does not expose rainfall consistently</li>
</ul>

<h4>Phase 2 will add:</h4>
<ul>
  <li>Radar‑based rainfall estimates</li>
  <li>Snowfall detection</li>
  <li>Storm event tagging</li>
</ul>

<h3>5. Free‑Tier Cloud Constraints</h3>
<ul>
  <li>Astra DB free tier</li>
  <li>BigQuery free tier</li>
  <li>GitHub Actions free tier</li>
</ul>

<h4>Despite this, the pipeline achieves:</h4>
<ul>
  <li>Hourly ingestion</li>
  <li>Daily analytics</li>
  <li>Zero‑trust security</li>
  <li>Multi‑cloud architecture</li>
</ul>

<h3>6. No Terraform Automation Yet</h3>
<ul>
  <li>All cloud resources created manually</li>
</ul>

<h4>Phase 2 will automate:</h4>
<ul>
  <li>GCP IAM</li>
  <li>BigQuery datasets</li>
  <li>Grafana provisioning</li>
  <li>Astra DB keyspaces</li>
</ul>

<h3>7. No Alerting or Notifications Yet</h3>
<ul>
  <li>No severe weather alerts</li>
  <li>No anomaly detection</li>
  <li>No pipeline failure alerts</li>
</ul>

<h4>Phase 2 will add:</h4>
<ul>
  <li>Discord alerts</li>
  <li>Grafana alert rules</li>
  <li>BigQuery anomaly detection</li>
</ul>

<h3>8. No Public Website Yet</h3>
<ul>
  <li>No public dashboards</li>
  <li>No API endpoints</li>
</ul>

<h4>Phase 2 will introduce:</h4>
<ul>
  <li>A full weather analytics website</li>
  <li>REST API endpoints</li>
  <li>Interactive charts</li>
</ul>

<h3>9. No Multi‑Day Forecast Accuracy Yet</h3>
<ul>
  <li>Accuracy computed only for yesterday</li>
</ul>

<h4>Phase 2 will add:</h4>
<ul>
  <li>3‑day accuracy</li>
  <li>7‑day accuracy</li>
  <li>Rolling forecast bias</li>
</ul>

<h3>10. No Automated Backfilling</h3>
<ul>
  <li>Missing data is not automatically recomputed</li>
</ul>

<h4>Phase 2 will add:</h4>
<ul>
  <li>Backfill scripts</li>
  <li>Retry logic</li>
  <li>Self‑healing workflows</li>
</ul>

<hr>

<h2>💼 Why This Project Matters </h2>

<p>This pipeline demonstrates:</p>

<ul>
  <li>Cloud‑native engineering</li>
  <li>Multi‑cloud architecture (Azure + GCP)</li>
  <li>Zero‑trust security</li>
  <li>Serverless compute</li>
  <li>Automated ETL pipelines</li>
  <li>BigQuery analytics modeling</li>
  <li>Grafana observability</li>
  <li>GitHub Actions CI/CD</li>
  <li>Python ETL development</li>
  <li>Real‑time data ingestion</li>
  <li>Daily batch processing</li>
  <li>Forecast accuracy modeling</li>
</ul>

<p><b>It’s a complete, production‑grade system — built by one engineer.</b></p>
