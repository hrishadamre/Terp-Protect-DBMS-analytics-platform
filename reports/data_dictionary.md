# Terp Protect: Data Dictionary

## Purpose

This document defines the primary datasets, database fields, derived attributes, analytical categories, quality indicators, and calculation rules used in the Terp Protect public-safety analytics project.

The data dictionary is intended to help reviewers understand:

- what each important field represents
- which fields originate from public source records
- which fields are created during cleaning or transformation
- how incidents and arrests are connected
- how dashboard metrics are calculated
- how invalid or incomplete records are handled

The project uses publicly available University of Maryland Police Department incident and arrest records covering 2023 through 2025.

> Field availability may vary between source files. The pipeline standardizes source records into a consistent analytical structure before loading them into the database.

---

## 1. Dataset Overview

The project contains two main record types:

| Dataset | Description |
|---|---|
| Incident records | Public safety incidents reported in the UMPD daily incident logs |
| Arrest records | Public arrest records published by UMPD |

The datasets are cleaned separately and later connected using normalized case-number fields where a reliable match is available.

---

## 2. Incident Dataset

### Incident Identifiers

| Field | Type | Description |
|---|---|---|
| `incident_id` | Integer or text | Project-generated unique identifier for an incident record |
| `case_number` | Text | UMPD case number associated with the incident |
| `source_year` | Integer | Year of the public source file from which the record was collected |
| `source_file` | Text | Name or reference of the source file used to load the record |
| `source_url` | Text | Public webpage or file location from which the record originated, when retained |

### Incident Date and Time Fields

| Field | Type | Description |
|---|---|---|
| `occurred_datetime` | Datetime | Standardized date and time when the incident occurred |
| `reported_datetime` | Datetime | Standardized date and time when the incident was reported |
| `occurred_date` | Date | Calendar date extracted from `occurred_datetime` |
| `reported_date` | Date | Calendar date extracted from `reported_datetime` |
| `occurred_year` | Integer | Calendar year when the incident occurred |
| `occurred_month` | Integer | Numeric month when the incident occurred |
| `occurred_month_name` | Text | Name of the occurrence month |
| `occurred_weekday` | Text | Weekday name derived from the occurrence date |
| `occurred_is_weekend` | Boolean or integer | Indicates whether the occurrence date falls on Saturday or Sunday |
| `occurred_hour` | Integer | Hour of day extracted from the occurrence datetime |
| `reported_year` | Integer | Calendar year when the incident was reported |
| `reported_month` | Integer | Numeric month when the incident was reported |
| `reported_month_name` | Text | Name of the reporting month |
| `reported_weekday` | Text | Weekday name derived from the reported date |
| `semester_period` | Text | Standardized academic-period category assigned to the occurrence date |
| `occurred_semester_period` | Text | Academic-period value joined from the date dimension |

### Incident Description Fields

| Field | Type | Description |
|---|---|---|
| `crime` | Text | Original or cleaned incident description from the source record |
| `crime_type` | Text | Source crime type or standardized incident type |
| `crime_group` | Text | Higher-level analytical category assigned to similar incident descriptions |
| `location` | Text | Original or cleaned source location description |
| `location_group` | Text | Standardized higher-level location category |
| `disposition` | Text | Source case disposition or outcome text |
| `disposition_group` | Text | Standardized analytical outcome category |
| `narrative` | Text | Additional source description, when available |

---

## 3. Standardized Incident Categories

### Crime Group

`crime_group` combines similar incident descriptions into broader analytical categories.

Common categories include:

| Crime Group | General Meaning |
|---|---|
| Medical / Welfare | Medical assistance, welfare checks, mental-health-related responses, and similar public-safety activity |
| Theft / Property | Theft, stolen property, property loss, and related incidents |
| Traffic / Vehicle | Traffic incidents, vehicle-related violations, crashes, and roadway events |
| DUI / Impaired Driving | Driving under the influence or impaired-driving incidents |
| Assault / Violence | Assault, threats, fighting, and related violent incidents |
| Fraud / Financial Crime | Fraud, identity theft, scams, payment-related incidents, and financial offenses |
| Drug / Controlled Substance | Drug possession, controlled-substance violations, and related incidents |
| Alcohol-Related | Alcohol possession, alcohol violations, intoxication, and related incidents |
| Burglary / Breaking and Entering | Burglary, unlawful entry, and breaking-and-entering incidents |
| Vandalism / Property Damage | Destruction, defacement, or damage to property |
| Harassment / Disorder | Harassment, disorderly conduct, disturbances, and similar behavior |
| Trespassing | Unauthorized presence or entry |
| Weapons | Weapons possession, display, or related violations |
| Missing Person | Missing-person and related welfare records |
| Other | Valid incidents not assigned to a major analytical category |
| Unknown | Records with missing or unusable crime-category information |

The categories are analytical groupings created for consistency. They do not replace official UMPD terminology.

---

## 4. Location Groups

`location_group` standardizes detailed source location descriptions into broader analytical categories.

Common groups include:

| Location Group | General Meaning |
|---|---|
| Roadway / Street | Streets, intersections, roadways, highways, and traffic areas |
| Residence / Housing | Residence halls, apartments, houses, and student housing |
| Academic / Administrative | Classrooms, offices, libraries, laboratories, and administrative buildings |
| Parking Area | Parking lots, parking garages, and vehicle-storage areas |
| Outdoor / Campus Grounds | Walkways, fields, plazas, courtyards, and other outdoor campus spaces |
| Retail / Commercial | Stores, restaurants, commercial facilities, and service locations |
| Recreation / Athletics | Gyms, stadiums, athletic facilities, and recreational areas |
| Transit / Transportation | Bus stops, transit centers, rail locations, and transportation facilities |
| Medical Facility | Hospitals, clinics, health centers, and medical-service locations |
| Other | Valid locations not assigned to a major standardized group |
| Unknown | Missing, unclear, or unusable location information |

Detailed source locations remain available for record-level inspection.

---

## 5. Disposition Groups

`disposition_group` standardizes source case outcomes into consistent categories.

| Disposition Group | Description |
|---|---|
| Closed / Cleared | Incident was closed, cleared, resolved, or administratively completed |
| Pending / Active | Case remains open, pending, active, suspended, or under investigation |
| Arrest-Related | Source disposition indicates arrest, custody, or a directly arrest-related outcome |
| Summons / Warrant Issued | A citation, summons, warrant, or similar legal action was issued |
| Unfounded | Report was determined to be unfounded or unsupported |
| Other | Valid disposition not assigned to a primary analytical group |
| Unknown | Missing or unusable disposition information |

The `Arrest-Related` disposition group is derived from the incident record. It is different from incident-to-arrest record linkage.

---

## 6. Reporting Delay Fields

Reporting delay measures the elapsed time between occurrence and reporting.

| Field | Type | Description |
|---|---|---|
| `report_delay_hours` | Numeric | Elapsed hours between `occurred_datetime` and `reported_datetime` |
| `report_delay_days` | Numeric | Elapsed reporting delay expressed in days, when included |
| `delay_bucket` | Text | Standardized category describing the reporting-delay interval |
| `has_valid_reporting_delay` | Boolean or integer | Indicates whether the delay is usable for analysis |

The core calculation is:

`reported_datetime - occurred_datetime`

A reporting delay is valid when:

- both datetime values are available
- both datetime values can be parsed successfully
- the reported datetime is not earlier than the occurrence datetime
- the resulting delay is non-negative

Records with invalid delay sequences remain available for review but are excluded from reporting-delay statistics.

### Reporting Delay Buckets

Common delay categories include:

| Delay Bucket | Definition |
|---|---|
| Within 1 Hour | Reported no more than one elapsed hour after occurrence |
| 1–6 Hours | Reported more than one hour and no more than six hours after occurrence |
| 6–24 Hours | Reported more than six hours and no more than 24 hours after occurrence |
| 1–3 Days | Reported more than 24 hours and no more than three days after occurrence |
| 3–7 Days | Reported more than three days and no more than seven days after occurrence |
| Over 7 Days | Reported more than seven days after occurrence |
| Invalid / Unknown | Delay could not be calculated reliably |

`Reported Within 24 Hours` is based on elapsed time and does not require occurrence and reporting on the same calendar date.

---

## 7. Academic Period Fields

`semester_period` and `occurred_semester_period` assign incident dates to simplified academic periods.

Standardized values include:

| Academic Period | Description |
|---|---|
| Spring Semester | Spring instructional period |
| Summer Break | Summer academic and break period |
| Fall Semester | Fall instructional period |
| Winter Break | Winter academic recess period |
| Unknown | Date could not be assigned reliably |

Values such as `Summer`, `Summer Semester`, and `Summer Session` are standardized as `Summer Break`.

Academic periods are simplified analytical groupings. They do not reproduce the exact University of Maryland academic calendar for every year.

### Academic-Period Incident Rate

The academic-period incident rate is calculated as:

`Distinct incidents divided by calendar weeks represented in the academic period`

The denominator includes the full represented calendar period, including dates with zero incidents.

This reduces bias that would occur if the calculation counted only weeks containing recorded incidents.

---

## 8. Date Dimension

The database uses a date dimension to support consistent time-based analysis.

Common date-dimension fields include:

| Field | Type | Description |
|---|---|---|
| `date_key` | Integer or text | Surrogate or formatted key for a calendar date |
| `full_date` | Date | Complete calendar date |
| `year` | Integer | Calendar year |
| `quarter` | Integer | Calendar quarter |
| `month` | Integer | Numeric month |
| `month_name` | Text | Calendar month name |
| `week_of_year` | Integer | Calendar week number |
| `weekday` | Text | Weekday name |
| `weekday_number` | Integer | Numeric weekday order |
| `is_weekend` | Boolean or integer | Indicates Saturday or Sunday |
| `semester_period` | Text | Simplified academic-period classification |

The date dimension supports occurrence-date and reported-date analysis without repeatedly deriving calendar values.

---

## 9. Arrest Dataset

### Arrest Identifiers

| Field | Type | Description |
|---|---|---|
| `arrest_id` | Integer or text | Project-generated unique identifier for an arrest record |
| `arrest_number` | Text | Source arrest identifier |
| `case_number` | Text | Case number associated with the arrest |
| `normalized_case_number` | Text | Cleaned case number used for matching, when retained |
| `source_year` | Integer | Year of the public source file |
| `source_file` | Text | Name or reference of the source arrest file |

### Arrest Date and Time Fields

| Field | Type | Description |
|---|---|---|
| `arrested_datetime` | Datetime | Standardized date and time of arrest |
| `arrested_date` | Date | Calendar date extracted from the arrest datetime |
| `arrested_year` | Integer | Calendar year of arrest |
| `arrested_month` | Integer | Numeric month of arrest |
| `arrested_month_name` | Text | Name of arrest month |
| `arrested_weekday` | Text | Weekday of arrest |
| `arrested_hour` | Integer | Hour of day when arrest occurred |

### Arrest Description Fields

| Field | Type | Description |
|---|---|---|
| `arrested_charge` | Text | Original or cleaned arrest charge description |
| `charge_text` | Text | Standardized charge text, when separately retained |
| `charge_category` | Text | Higher-level analytical category assigned to the charge |
| `arrest_location` | Text | Source arrest location, when available |
| `disposition` | Text | Arrest-record disposition, when available |

The project focuses on aggregate arrest and charge analysis. Personally identifying fields are not required for dashboard analysis.

---

## 10. Standardized Charge Categories

`charge_category` groups similar arrest-charge descriptions.

Common categories include:

| Charge Category | General Meaning |
|---|---|
| DUI / Impaired Driving | Driving under the influence or impaired-driving charges |
| Assault / Violence | Assault, threats, fighting, and related violent charges |
| Theft / Property | Theft, stolen property, and related offenses |
| Drug / Controlled Substance | Drug possession, distribution, and controlled-substance charges |
| Alcohol-Related | Alcohol possession, intoxication, or related violations |
| Traffic / Vehicle | Traffic, licensing, registration, and vehicle-related charges |
| Fraud / Financial Crime | Fraud, identity theft, forgery, and related financial offenses |
| Trespassing | Unauthorized entry or presence |
| Weapons | Weapons possession or related charges |
| Disorderly Conduct | Disorderly behavior, disturbance, or similar charges |
| Burglary / Breaking and Entering | Burglary and unlawful-entry charges |
| Vandalism / Property Damage | Damage or destruction of property |
| Other | Valid charge not assigned to a major analytical category |
| Unknown | Missing or unusable charge information |

Charge categories are analytical classifications derived from charge-description keywords.

---

## 11. Incident-to-Arrest Matching

Incident and arrest records are linked using cleaned case-number values.

### Matching Logic

A match generally requires:

- a non-null incident case number
- a non-null arrest case number
- consistent normalization of spaces, punctuation, and text format
- equality between normalized case numbers

The matching process does not assume that unmatched records are unrelated. A match may be unavailable because of:

- missing case numbers
- inconsistent formatting
- source-data differences
- incomplete public record coverage
- one case appearing in only one source dataset

### Match Fields

| Field | Type | Description |
|---|---|---|
| `incident_id` | Integer or text | Identifier of the matched incident |
| `arrest_id` | Integer or text | Identifier of the matched arrest |
| `case_number` | Text | Shared case number used in the linkage |
| `is_matched` | Boolean or integer | Indicates whether a valid match was created |
| `arrest_count` | Integer | Number of arrest records connected to an incident, when aggregated |

### Key Arrest Measures

#### All Cleaned Arrests

The complete cleaned arrest-record population, regardless of whether records match the selected incident dataset.

#### Linked Arrest Records

Arrest records connected to incidents in the selected incident population.

#### Distinct Linked Arrest Cases

The number of unique case numbers represented in linked arrest records.

#### Matched Incidents

Distinct incidents with at least one linked arrest record.

An incident is counted once even when it has multiple arrest records.

#### Incident-to-Arrest Match Coverage

Calculated as:

`Distinct matched incidents divided by all distinct selected incidents`

This measure does not represent the percentage of incidents that legally resulted in arrest. It represents successful linkage between the available public datasets.

#### Linked Arrest Share

Calculated as:

`Linked arrest records divided by all cleaned arrest records`

This measures the proportion of arrest records connected to the selected incident population.

---

## 12. Data Quality Fields

The pipeline creates quality indicators to identify records that are complete and usable for analysis.

### Incident Quality Flags

| Field | Type | Description |
|---|---|---|
| `has_valid_case_number` | Boolean or integer | Indicates that the incident case number is present and usable |
| `has_valid_occurred_datetime` | Boolean or integer | Indicates that the occurrence datetime parsed successfully |
| `has_valid_reported_datetime` | Boolean or integer | Indicates that the reported datetime parsed successfully |
| `has_valid_reporting_delay` | Boolean or integer | Indicates that the reporting delay is non-negative and analytically usable |

### Arrest Quality Flags

| Field | Type | Description |
|---|---|---|
| `has_valid_arrest_number` | Boolean or integer | Indicates that the arrest identifier is present and usable |
| `has_valid_case_number` | Boolean or integer | Indicates that the arrest case number is present and usable |
| `has_valid_arrested_datetime` | Boolean or integer | Indicates that the arrest datetime parsed successfully |
| `has_charge_text` | Boolean or integer | Indicates that usable arrest-charge text is available |

A value of `1` generally represents a passed check, while `0` represents a failed or unavailable check.

---

## 13. Primary Field Check Pass Rate

The dashboard calculates a weighted primary field-check pass rate.

The calculation is:

`Passed record-field checks divided by all evaluated record-field checks`

Each evaluated record-field combination contributes once.

For example, if four incident checks are applied to 5,659 incidents, the incident records contribute up to 22,636 evaluated record-field checks.

The score measures configured data completeness and usability. It does not confirm that every source value is factually accurate.

---

## 14. Records Requiring Review

A record is placed in the review panel when it fails at least one available primary quality check.

Possible review reasons include:

- missing case number
- invalid occurrence datetime
- invalid reported datetime
- reported datetime earlier than occurred datetime
- missing or unusable reporting delay
- missing arrest number
- invalid arrest datetime
- missing charge text

Review records are retained for transparency and are not automatically deleted.

Invalid values may be excluded from specific calculations while the original record remains available in the database.

---

## 15. Core Analytical Views

The database includes reusable SQL views that prepare data for analysis and dashboard use.

### `vw_incident_detail`

Provides a detailed incident-level analytical dataset containing:

- incident identifiers
- occurrence and reporting dates
- date-dimension attributes
- crime categories
- location categories
- disposition categories
- reporting-delay fields
- quality indicators

### `vw_monthly_incident_trends`

Provides monthly incident totals for trend and seasonal analysis.

### `vw_crime_group_summary`

Provides incident counts and shares by standardized crime group.

### `vw_location_summary`

Provides incident counts and shares by location or location group.

### `vw_disposition_summary`

Provides case-outcome totals and percentages.

### `vw_reporting_delay_summary`

Provides reporting-delay counts, distributions, and summary measures.

### `vw_arrest_detail`

Provides cleaned arrest records with charge categories and date attributes.

### `vw_charge_category_summary`

Provides arrest totals by standardized charge category.

### `vw_incident_arrest_match`

Provides incident-to-arrest linkage results using normalized case numbers.

### `vw_demographic_summary`

May provide aggregate demographic summaries when appropriate source fields are available.

Demographic information is not used for individual profiling or predictive risk scoring.

---

## 16. Dashboard Metric Definitions

### Total Incidents

Count of distinct selected incident records.

Preferred identifier:

`incident_id`

Fallback identifier:

`case_number`

### Total Arrest Records

Count of distinct cleaned arrest records.

Preferred identifier:

`arrest_id`

Fallback identifier:

`arrest_number`

### Closed or Cleared Share

Distinct incidents categorized as `Closed / Cleared` divided by all distinct selected incidents.

### Pending or Active Share

Distinct incidents categorized as `Pending / Active` divided by all distinct selected incidents.

### Arrest-Related Outcome Share

Distinct incidents categorized as `Arrest-Related` divided by all distinct selected incidents.

This is derived from incident disposition values.

### Reported Within 24 Hours

Valid incident records with a reporting delay of no more than 24 elapsed hours divided by all incident records with valid reporting-delay values.

### Median Reporting Delay

Median `report_delay_hours` among distinct incidents with valid, non-negative reporting delays.

### P90 Reporting Delay

The reporting-delay value at or below which 90% of valid incident records fall.

### Weekend Share

Distinct incidents occurring on Saturday or Sunday divided by all distinct selected incidents with valid occurrence dates.

### Incident-to-Arrest Match Coverage

Distinct selected incidents with at least one linked arrest divided by all distinct selected incidents.

### Linked Arrest Share

Linked arrest records divided by all cleaned arrest records.

### Primary Field Check Pass Rate

Passed configured record-field checks divided by all evaluated record-field checks.

---

## 17. Count and Percentage Rules

To avoid duplicate counting, dashboard measures use distinct record identifiers wherever possible.

### Incident Measures

Incident calculations generally use one row per:

`incident_id`

When `incident_id` is unavailable, the project may use:

`case_number`

### Arrest Measures

Arrest calculations generally use one row per:

`arrest_id`

When `arrest_id` is unavailable, the project may use:

`arrest_number`

### Percentage Denominators

Percentages use the complete eligible record population for the metric.

Examples:

- outcome shares use all selected incidents
- delay shares use incidents with valid reporting delays
- location composition uses all selected incidents within each displayed location group
- crime-group outcome composition uses all selected incidents within each displayed crime group
- arrest-linkage coverage uses all selected incidents

---

## 18. Minimum Sample Thresholds

Some comparative charts exclude groups with very small record counts.

The standard minimum threshold used in major group comparisons is generally:

`20 records`

This threshold is applied to:

- location-group composition comparisons
- crime-group outcome comparisons
- reporting-delay comparisons by group

The threshold reduces unstable percentages or medians based on very small samples.

It is an analytical display rule and does not remove the underlying records from the database.

---

## 19. Seasonal and Chronological Time Definitions

### Seasonal Calendar-Month View

Combines the same month across all selected years.

Example:

- all January incidents are combined
- all February incidents are combined
- all March incidents are combined

This view identifies recurring seasonal patterns.

### Chronological Year-Month View

Keeps each month and year separate.

Example:

- January 2023
- February 2023
- January 2024
- February 2024

This view identifies changes over time.

Chart titles specify whether the analysis is seasonal or chronological.

---

## 20. Source Year vs. Occurrence Year

These fields should not be treated as interchangeable.

### `source_year`

Represents the year assigned to the downloaded public source file.

### `occurred_year`

Represents the calendar year extracted from the incident occurrence datetime.

A source file may contain a record whose occurrence date belongs to a different calendar year.

The dashboard uses the appropriate field depending on whether the analysis concerns:

- source-file coverage
- incident occurrence timing
- chronological trends

---

## 21. Missing and Unknown Values

Missing source values are handled according to analytical purpose.

Typical rules include:

- preserve the original source record
- standardize blank text as null where appropriate
- assign `Unknown` only when a category is required for grouping
- exclude invalid values from calculations that require valid data
- retain flagged records in the review panel
- avoid silently replacing uncertain values with assumed information

`Unknown` means that the available source value could not be classified reliably.

`Other` means that a valid source value exists but does not fit a major standardized category.

---

## 22. Responsible Use of Fields

The data model is designed for aggregate public-safety analysis.

Appropriate uses include:

- descriptive reporting
- operational workload analysis
- trend identification
- data-quality review
- reporting-delay analysis
- record-linkage evaluation
- educational database analysis

The data should not be used for:

- individual behavioral prediction
- automated enforcement decisions
- profiling individuals or demographic groups
- assigning personal risk scores
- causal conclusions based only on descriptive associations

---

## 23. Important Interpretation Notes

### Incident Volume Is Not a Risk Rate

Higher incident counts may reflect:

- greater population exposure
- increased traffic
- larger physical areas
- longer operating hours
- greater police visibility
- stronger reporting activity

### Arrest-Related Outcomes Are Not the Same as Linked Arrests

`Arrest-Related` is derived from incident disposition.

Linked arrests are created by joining incident and arrest records.

The two measures may differ.

### Unmatched Records Are Not Proof of No Arrest

A record may remain unmatched because identifiers are missing, inconsistent, or unavailable in the public datasets.

### Category Assignments Are Analytical

Crime, location, disposition, and charge categories are created to support consistent analysis.

They do not replace official terminology or legal definitions.

### Reporting Delay Is Based on Available Datetimes

The calculated delay depends on the accuracy and completeness of the published occurrence and reporting timestamps.

---

## Conclusion

This data dictionary documents the core structure and analytical rules used throughout Terp Protect.

It provides a consistent reference for:

- database tables
- analytical views
- standardized categories
- dashboard measures
- quality checks
- record-linkage logic
- responsible interpretation

Together, these definitions ensure that the dashboard, SQL queries, reports, and project documentation use consistent terminology and calculation rules.