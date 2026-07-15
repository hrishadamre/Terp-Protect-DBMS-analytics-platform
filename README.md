<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&height=170&color=0:111827,55:7F1D1D,100:C8102E&text=Terp%20Protect&fontColor=FFFFFF&fontSize=42&fontAlignY=40&desc=Campus%20Public%20Safety%20Data%20Management%20and%20Analytics%20Platform&descAlignY=69&descSize=15" alt="Terp Protect banner" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Inter&weight=500&size=19&duration=3600&pause=900&color=CBD5E1&center=true&vCenter=true&width=900&lines=Transforming+fragmented+public+safety+records+into+structured+insights.;Connecting+incident%2C+arrest%2C+location%2C+outcome%2C+and+reporting+data.;Supporting+clearer+analysis%2C+consistent+reporting%2C+and+better+decision-making." alt="Terp Protect summary" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-Data%20Pipeline-7F1D1D?style=for-the-badge&logo=python&logoColor=FFFFFF&labelColor=111827" alt="Python data pipeline" />
  <img src="https://img.shields.io/badge/SQLite-Relational%20Database-7F1D1D?style=for-the-badge&logo=sqlite&logoColor=FFFFFF&labelColor=111827" alt="SQLite database" />
  <img src="https://img.shields.io/badge/SQL-Analytical%20Views-991B1B?style=for-the-badge&logo=postgresql&logoColor=FFFFFF&labelColor=111827" alt="SQL analytical views" />
  <img src="https://img.shields.io/badge/Streamlit-Interactive%20Dashboard-991B1B?style=for-the-badge&logo=streamlit&logoColor=FFFFFF&labelColor=111827" alt="Streamlit dashboard" />
</p>

<h2>Project Overview</h2>
<p><b>Terp Protect</b> organizes public UMPD incident and arrest records into one clear system. It helps users quickly explore campus safety patterns, reporting delays, case outcomes, arrest activity, and data quality through an interactive dashboard.</p>

<table>
<tr>
<td width="33%" valign="top">
<h3>Problem</h3>
Public records are fragmented, inconsistently categorized, and difficult to compare across years.
</td>
<td width="33%" valign="top">
<h3>Solution</h3>
A repeatable workflow that cleans, organizes, connects, validates, and analyzes incident and arrest data.
</td>
<td width="33%" valign="top">
<h3>Value</h3>
Faster analysis, clearer reporting, consistent definitions, and improved visibility into campus safety patterns.
</td>
</tr>
</table>

 

<h2>Why This Project Matters</h2>

<p>Campus public-safety records contain information that can support operational planning, reporting, resource prioritization, and public awareness. However, raw records alone do not provide a complete or easily understandable view.</p>

<p>Terp Protect converts these records into an organized decision-support system that helps users answer questions such as:</p>

<ul>
<li>Which incident categories occur most frequently?</li>
<li>Where is public-safety activity concentrated?</li>
<li>When do incident volumes increase?</li>
<li>How quickly are incidents reported?</li>
<li>What proportion of cases are closed, pending, or arrest-related?</li>
<li>How many incident records can be connected to arrest records?</li>
<li>Which records require additional data-quality review?</li>
</ul>

 

<h2>Dashboard Preview</h2>

<p align="center">
  <img src="visuals/UI screenshots/dashboard_capture_20260714_182842/01_command_center.png" width="95%" alt="Terp Protect dashboard preview" />
</p>

 

<h2>Platform Capabilities</h2>

<table>
<tr>
<td width="50%" valign="top">
<h3>Data Consolidation</h3>
Combines multiple years of public incident and arrest records into a consistent analytical structure.
</td>
<td width="50%" valign="top">
<h3>Category Standardization</h3>
Groups inconsistent source descriptions into reusable crime, location, disposition, and charge categories.
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>Incident-to-Arrest Matching</h3>
Connects related records using standardized case numbers while preserving unmatched records for transparency.
</td>
<td width="50%" valign="top">
<h3>Reporting-Delay Analysis</h3>
Measures how quickly incidents are reported using elapsed-time calculations, medians, percentiles, and delay groups.
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>Data Quality Review</h3>
Identifies missing identifiers, invalid timestamps, unusable reporting sequences, and incomplete arrest information.
</td>
<td width="50%" valign="top">
<h3>Interactive Exploration</h3>
Enables users to filter records and compare patterns across time, locations, outcomes, crime groups, and arrests.
</td>
</tr>
</table>

 

<h2>Dashboard Sections</h2>

<table>
<tr>
<th>Section</th>
<th>Purpose</th>
</tr>
<tr>
<td><b>Command Center</b></td>
<td>Summarizes the most important incident, location, outcome, reporting, and arrest-linkage measures.</td>
</tr>
<tr>
<td><b>Time and Seasonality</b></td>
<td>Examines activity across calendar months, academic periods, weekdays, and hours.</td>
</tr>
<tr>
<td><b>Location Analysis</b></td>
<td>Identifies high-activity locations and compares incident composition across standardized location groups.</td>
</tr>
<tr>
<td><b>Incident Outcomes</b></td>
<td>Shows how cases are distributed across closed, pending, arrest-related, and other outcomes.</td>
</tr>
<tr>
<td><b>Reporting Delay</b></td>
<td>Measures how quickly incidents are reported and highlights categories with longer delays.</td>
</tr>
<tr>
<td><b>Arrest Analysis</b></td>
<td>Compares cleaned and linked arrest records, charge categories, and incident-match coverage.</td>
</tr>
<tr>
<td><b>Data Quality</b></td>
<td>Displays field-level validation results and records requiring further review.</td>
</tr>
</table>

 

<h2>Key Findings</h2>

<table>
<tr>
<td width="50%" valign="top">
<h3>Incident Activity</h3>
<ul>
<li><b>Medical / Welfare</b> is the largest standardized incident category.</li>
<li><b>Roadway / Street</b> records the highest incident volume among location groups.</li>
<li>The highest combined seasonal activity occurs during the fall period.</li>
</ul>
</td>
<td width="50%" valign="top">
<h3>Case Outcomes</h3>
<ul>
<li>Approximately <b>49.4%</b> of incidents are categorized as closed or cleared.</li>
<li>Approximately <b>29.8%</b> remain pending or active.</li>
<li>Approximately <b>16.5%</b> have an arrest-related disposition.</li>
</ul>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<h3>Reporting Timeliness</h3>
<ul>
<li>Approximately <b>81.8%</b> of valid records were reported within 24 hours.</li>
<li>The median reporting delay is approximately <b>0.2 hours</b>.</li>
<li>The 90th-percentile delay is approximately <b>3.9 days</b>.</li>
</ul>
</td>
<td width="50%" valign="top">
<h3>Arrest Linkage and Quality</h3>
<ul>
<li>Approximately <b>17.3%</b> of incidents are linked to at least one arrest.</li>
<li><b>DUI / Impaired Driving</b> is the largest arrest charge category.</li>
<li>The primary field-check pass rate is approximately <b>99.94%</b>.</li>
</ul>
</td>
</tr>
</table>

<p>Detailed interpretation is available in the <a href="reports/analytical_summary.md"><b>Analytical Summary</b></a>.</p>

 

<h2>How the System Works</h2>

<table>
<tr>
<td align="center"><b>1. Collect</b><br><sub>Load public incident and arrest records</sub></td>
<td align="center">→</td>
<td align="center"><b>2. Clean</b><br><sub>Correct formats and standardize values</sub></td>
<td align="center">→</td>
<td align="center"><b>3. Organize</b><br><sub>Store records in a relational database</sub></td>
</tr>
<tr>
<td align="center"><b>6. Present</b><br><sub>Deliver interactive dashboard views</sub></td>
<td align="center">←</td>
<td align="center"><b>5. Analyze</b><br><sub>Create reusable calculations and summaries</sub></td>
<td align="center">←</td>
<td align="center"><b>4. Connect</b><br><sub>Link incidents and arrests by case number</sub></td>
</tr>
</table>

 

<h2>Business Analysis Approach</h2>

<details open>
<summary><b>Understanding the problem</b></summary>
 
<p>The first challenge was not simply creating charts. It was understanding why the records were difficult to use and identifying the decisions the final system should support.</p>
<ul>
<li>Reviewed the structure and inconsistencies of incident and arrest records.</li>
<li>Identified repeated analytical questions across time, location, outcomes, reporting delays, and arrests.</li>
<li>Defined clear terminology so that dashboard measures would remain consistent.</li>
<li>Separated descriptive insight from assumptions about risk or causation.</li>
</ul>
</details>

<details>
<summary><b>Translating needs into requirements</b></summary>
 
<ul>
<li>Users should be able to filter the same dataset across all analytical views.</li>
<li>Incident counts should use distinct records and avoid duplicate inflation.</li>
<li>Reporting-delay calculations should exclude impossible or unusable values.</li>
<li>Incident outcomes and arrest-record linkage should remain separate measures.</li>
<li>Records failing quality checks should remain visible instead of being silently removed.</li>
<li>The dashboard should explain important calculations using concise help text.</li>
</ul>
</details>

<details>
<summary><b>Designing for practical use</b></summary>
 
<p>The final design prioritizes clarity, consistency, and traceability. Each dashboard section answers a focused group of questions, while the Command Center provides a quick overview of the complete dataset.</p>
<p>Detailed technical definitions are kept outside the main interface in the data dictionary and supporting documentation, allowing the dashboard to remain understandable without removing analytical rigor.</p>
</details>

 

<h2>Tools and Methods</h2>

<table>
<tr>
<td><b>Data preparation</b></td>
<td>Python · Pandas · Data cleaning · Validation · Category standardization</td>
</tr>
<tr>
<td><b>Database and querying</b></td>
<td>SQLite · SQL · Relational modeling · Joins · Aggregations · Analytical views</td>
</tr>
<tr>
<td><b>Dashboard and visualization</b></td>
<td>Streamlit · Plotly · Interactive filters · Data tables</td>
</tr>
<tr>
<td><b>Business analysis</b></td>
<td>Problem framing · Requirements definition · Metric design · Process mapping · Insight communication</td>
</tr>
</table>

 
<h2>Project Structure</h2>

    TERP PROTECT/
    │
    ├── dashboard/
    │   └── streamlit_app/
    │       ├── utils/
    │       ├── components/
    │       ├── sections/
    │       ├── app.py
    │       └── README.md
    │
    ├── data/
    │   ├── database/
    │   ├── processed/
    │   └── raw/
    │
    ├── reports/
    │   ├── sql_outputs/
    │   ├── analytical_summary.md
    │   ├── arrest_log_cleaning_summary_2023_2025.md
    │   ├── daily_incident_cleaning_summary_2023_2025.md
    │   ├── data_dictionary.md
    │   ├── improvement_over_official_dashboard.md
    │   └── sql_analysis_summary_2023_2025.md
    │
    ├── sql/
    │   ├── 01_schema.sql
    │   ├── 02_views.sql
    │   └── 03_business_questions.sql
    │
    ├── src/
    │   ├── analysis/
    │   ├── extract/
    │   ├── load/
    │   └── transform/
    │
    ├── visuals/
    │   ├── UI screenshots/
    │   └── capture_dashboard_screenshots.py
    │
    ├── .gitignore
    ├── README.md
    ├── requirements.txt
    ├── run_pipeline.py
    └── SETUP.md
    

<h2>Run the Project</h2>

<p>Complete installation and execution instructions are available in <a href="SETUP.md"><b>SETUP.md</b></a>.</p>

 

<h2>Documentation</h2>

<table>
<tr>
<td><a href="SETUP.md"><b>Setup and Execution Guide</b></a></td>
<td>Installation, pipeline execution, dashboard launch, and troubleshooting.</td>
</tr>
<tr>
<td><a href="reports/analytical_summary.md"><b>Analytical Summary</b></a></td>
<td>Key findings, interpretations, limitations, and responsible-use notes.</td>
</tr>
<tr>
<td><a href="reports/data_dictionary.md"><b>Data Dictionary</b></a></td>
<td>Field definitions, standardized categories, metric rules, and matching logic.</td>
</tr>
<tr>
<td><a href="docs/Terp_Protect_Business_Analysis_Report.pdf"><b>Business Analysis Report</b></a></td>
<td>Project motivation, user needs, objectives, solution, impact, and future direction.</td>
</tr>
</table>

 

<h2>Responsible Use</h2>

<p>Terp Protect is designed for descriptive reporting, operational review, data validation, and educational analysis.</p>

<p>The platform does not predict individual behavior, assign personal risk scores, support automated enforcement decisions, or establish causal relationships from descriptive data.</p>

<p>Incident counts should not be interpreted as population-adjusted risk rates. Higher activity may reflect greater traffic, exposure, reporting behavior, physical size, or operational visibility.</p>

<h2></h2>
<div align="center">

### Author - **Hrishad Amre**  
Business Analyst / Data Analyst / Product Analytics Portfolio Project  

<a href="https://www.linkedin.com/in/hrishadamre/">LinkedIn</a> • 
<a href="https://github.com/hrishadamre">GitHub</a> • 
<a href="mailto:hrishad@umd.edu">Email</a>

</div>

