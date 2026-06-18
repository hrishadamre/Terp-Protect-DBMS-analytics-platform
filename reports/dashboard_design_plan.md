# Power BI Dashboard Design Plan

## Dashboard Title
Terp Protect: Campus Safety Incident Analytics

## Dashboard Purpose
This dashboard analyzes UMPD Daily Crime and Incident Log records for 2025. It is designed to help users understand incident volume, incident categories, case outcomes, reporting delays, location patterns, and time-based trends.

The dashboard is built from the cleaned and modeled Terp Protect DBMS pipeline rather than directly from raw webpages.

## Data Used in Version 1
- Source: UMPD Daily Crime and Incident Logs
- Year: 2025
- Records: 1,886 incidents
- Dashboard input folder: `dashboard/powerbi/data/`

## Dashboard Pages

### Page 1: Executive Overview

#### Purpose
Provide a high-level summary of the 2025 incident dataset.

#### KPI Cards
- Total incidents
- Arrest-related incidents
- Arrest-related percentage
- Most common crime group
- Most common disposition group
- Average reporting delay
- Top location group

#### Visuals
- Incidents by month
- Incidents by crime group
- Incidents by disposition group
- Incidents by location group
- Reporting delay bucket distribution

#### Filters
- Month
- Crime group
- Disposition group
- Location group
- Semester period

#### Business Questions Answered
- What is the overall incident volume?
- What types of incidents are most common?
- What are the most common case outcomes?
- How often are incidents arrest-related?
- Which location groups appear most often?

---

### Page 2: Incident Trends

#### Purpose
Analyze incident activity over time.

#### KPI Cards
- Total incidents
- Peak month
- Peak weekday
- Peak hour
- Weekend incident percentage

#### Visuals
- Monthly incident trend
- Weekday incident trend
- Hourly incident trend
- Incidents by semester period
- Crime group trend by month

#### Filters
- Month
- Weekday
- Crime group
- Semester period

#### Business Questions Answered
- Which months have the highest incident volume?
- Which weekdays have the most incidents?
- What time of day has the highest incident activity?
- Do incident patterns change across academic periods?

---

### Page 3: Incident Outcomes

#### Purpose
Analyze dispositions and case outcome patterns.

#### KPI Cards
- Total incidents
- Arrest-related incidents
- Pending / active incidents
- Closed / cleared incidents
- Unfounded incidents

#### Visuals
- Disposition group breakdown
- Detailed disposition breakdown
- Crime group by disposition group
- Arrest-related rate by crime group
- Monthly arrest-related incident trend

#### Filters
- Crime group
- Disposition group
- Month
- Location group

#### Business Questions Answered
- What are the most common case outcomes?
- Which incident groups are more likely to be arrest-related?
- Are pending incidents concentrated in certain categories?
- How does arrest-related activity vary by month?

---

### Page 4: Reporting Delay Analysis

#### Purpose
Analyze how long it takes for incidents to be reported.

#### KPI Cards
- Average reporting delay in hours
- Average reporting delay in days
- Same-day reporting percentage
- Over-7-day reporting count

#### Visuals
- Reporting delay bucket distribution
- Average reporting delay by crime group
- Average reporting delay by location group
- Average reporting delay by month
- Table of highest-delay incident records

#### Filters
- Delay bucket
- Crime group
- Location group
- Month
- Disposition group

#### Business Questions Answered
- How quickly are incidents reported?
- Which incident types have longer reporting delays?
- Which locations have longer reporting delays?
- Are delayed reports concentrated in specific months?

---

### Page 5: Location Analysis

#### Purpose
Analyze where incidents are concentrated.

#### KPI Cards
- Total unique locations
- Top location
- Top location group
- Arrest-related incidents in top location group

#### Visuals
- Top 20 locations by incident count
- Incident count by location group
- Arrest-related count by location group
- Average reporting delay by location group
- Location group by crime group matrix

#### Filters
- Location group
- Crime group
- Disposition group
- Month

#### Business Questions Answered
- Which locations have the most reported incidents?
- Which location groups are most active?
- Are certain incident groups concentrated in specific location types?
- Which locations have higher arrest-related incident counts?

---

### Page 6: Data Quality

#### Purpose
Show transparency around data completeness and processing quality.

#### KPI Cards
- Total records
- Valid case number count
- Valid occurred datetime count
- Valid reported datetime count
- Valid reporting delay count

#### Visuals
- Data quality flag summary
- Missing/invalid field counts
- Records needing review table
- Records by source month

#### Filters
- Month
- Data quality flag
- Crime group
- Disposition group

#### Business Questions Answered
- How complete is the dataset?
- Are there missing or invalid records?
- Which fields need review?
- Is the data usable for analysis and modeling?

---

## Recommended Dashboard Theme

### Style
Clean, professional, public-sector analytics style.

### Colors
Use a simple University of Maryland-inspired palette:
- Dark red for key highlights
- Gold/yellow for secondary highlights
- Dark gray for text
- Light gray background
- White visual cards

### Design Guidelines
- Use KPI cards across the top of each page.
- Use consistent filters on the left or top.
- Avoid too many pie charts.
- Prefer bar charts, line charts, matrix visuals, and cards.
- Add short insight text boxes where useful.
- Keep each page focused on one analytical theme.

## Recommended Power BI Data Files

Load these files from `dashboard/powerbi/data/`:

- `incident_detail.csv`
- `monthly_incident_trends.csv`
- `crime_group_summary.csv`
- `disposition_summary.csv`
- `reporting_delay_summary.csv`
- `location_summary.csv`

## Core Measures to Create in Power BI

### Total Incidents
`Total Incidents = COUNTROWS(incident_detail)`

### Arrest-Related Incidents
`Arrest Related Incidents = SUM(incident_detail[is_arrest_related])`

### Arrest-Related Percentage
`Arrest Related % = DIVIDE([Arrest Related Incidents], [Total Incidents])`

### Average Reporting Delay Hours
`Avg Reporting Delay Hours = AVERAGE(incident_detail[report_delay_hours])`

### Average Reporting Delay Days
`Avg Reporting Delay Days = AVERAGE(incident_detail[report_delay_days])`

### Unique Case Count
`Unique Cases = DISTINCTCOUNT(incident_detail[case_number])`

### Unique Location Count
`Unique Locations = DISTINCTCOUNT(incident_detail[location_raw])`

## Version 1 Dashboard Scope
Version 1 will include only 2025 Daily Crime and Incident Logs.

## Future Dashboard Enhancements
- Add Arrest Logs and incident-to-arrest conversion analysis
- Add CSA Logs comparison page
- Add Uniform Crime Reports validation page
- Add forecasting page after multi-year data is collected
- Add charge text classification page after Arrest Logs are integrated