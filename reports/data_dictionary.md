# Terp Protect: Data Dictionary

## Purpose

This document defines the main datasets, fields, categories, quality checks, and dashboard metrics used in Terp Protect.

The project uses publicly available University of Maryland Police Department incident and arrest records from 2023 through 2025.

## Dataset Overview

| Dataset | Description |
|---|---|
| Incident records | Public-safety incidents published in UMPD daily incident logs |
| Arrest records | Public arrest records published by UMPD |

The datasets are cleaned separately and connected using standardized case numbers where a reliable match is available.

## Incident Fields

| Field | Type | Description |
|---|---|---|
| `incident_id` | Integer or text | Unique project identifier for an incident |
| `case_number` | Text | UMPD case number |
| `source_year` | Integer | Year of the source file |
| `occurred_datetime` | Datetime | Date and time when the incident occurred |
| `reported_datetime` | Datetime | Date and time when the incident was reported |
| `occurred_date` | Date | Calendar date of occurrence |
| `occurred_year` | Integer | Calendar year of occurrence |
| `occurred_month` | Integer | Numeric occurrence month |
| `occurred_month_name` | Text | Occurrence month name |
| `occurred_weekday` | Text | Weekday of occurrence |
| `occurred_hour` | Integer | Hour of occurrence |
| `occurred_is_weekend` | Boolean or integer | Indicates Saturday or Sunday |
| `semester_period` | Text | Simplified academic-period category |
| `crime` | Text | Original or cleaned incident description |
| `crime_group` | Text | Standardized incident category |
| `location` | Text | Original or cleaned location description |
| `location_group` | Text | Standardized location category |
| `disposition` | Text | Source case outcome |
| `disposition_group` | Text | Standardized case-outcome category |
| `report_delay_hours` | Numeric | Elapsed hours between occurrence and reporting |
| `delay_bucket` | Text | Standardized reporting-delay interval |

## Crime Groups

`crime_group` combines similar incident descriptions into broader categories.

| Crime Group | General Meaning |
|---|---|
| Medical / Welfare | Medical assistance, welfare checks, and similar responses |
| Theft / Property | Theft, stolen property, and property-loss incidents |
| Traffic / Vehicle | Traffic, vehicle, crash, and roadway incidents |
| DUI / Impaired Driving | Impaired-driving incidents |
| Assault / Violence | Assault, threats, fighting, and violent incidents |
| Fraud / Financial Crime | Fraud, scams, identity theft, and financial offenses |
| Drug / Controlled Substance | Drug and controlled-substance incidents |
| Alcohol-Related | Alcohol violations and intoxication incidents |
| Burglary / Breaking and Entering | Burglary and unlawful-entry incidents |
| Vandalism / Property Damage | Damage or destruction of property |
| Harassment / Disorder | Harassment, disturbances, and disorderly conduct |
| Trespassing | Unauthorized entry or presence |
| Weapons | Weapons-related incidents |
| Other | Valid incidents outside the main groups |
| Unknown | Missing or unusable category information |

These are analytical categories and do not replace official UMPD terminology.

## Location Groups

| Location Group | General Meaning |
|---|---|
| Roadway / Street | Streets, intersections, and roadways |
| Residence / Housing | Residence halls, apartments, and housing |
| Academic / Administrative | Academic, office, and administrative buildings |
| Parking Area | Parking lots and garages |
| Outdoor / Campus Grounds | Walkways, fields, plazas, and outdoor spaces |
| Retail / Commercial | Stores, restaurants, and commercial locations |
| Recreation / Athletics | Athletic and recreational facilities |
| Transit / Transportation | Transit stops and transportation facilities |
| Medical Facility | Hospitals, clinics, and health centers |
| Other | Valid locations outside the main groups |
| Unknown | Missing or unclear location information |

## Disposition Groups

| Disposition Group | Description |
|---|---|
| Closed / Cleared | Case was resolved, closed, or cleared |
| Pending / Active | Case remains open, pending, or under investigation |
| Arrest-Related | Incident disposition indicates an arrest-related outcome |
| Summons / Warrant Issued | Summons, citation, or warrant was issued |
| Unfounded | Report was determined to be unfounded |
| Other | Valid outcome outside the main groups |
| Unknown | Missing or unusable outcome information |

`Arrest-Related` is derived from the incident disposition field. It is different from incident-to-arrest record matching.

## Reporting Delay

Reporting delay measures the elapsed time between `occurred_datetime` and `reported_datetime`.

A delay is valid when:

- both datetime values are available
- both values can be parsed
- the reported datetime is not earlier than the occurrence datetime
- the calculated delay is non-negative

Invalid delay records remain available for review but are excluded from delay calculations.

### Delay Buckets

| Delay Bucket | Definition |
|---|---|
| Within 1 Hour | Reported within one elapsed hour |
| 1–6 Hours | Reported after one hour and within six hours |
| 6–24 Hours | Reported after six hours and within 24 hours |
| 1–3 Days | Reported after 24 hours and within three days |
| 3–7 Days | Reported after three days and within seven days |
| Over 7 Days | Reported more than seven days after occurrence |
| Invalid / Unknown | Delay could not be calculated reliably |

`Reported Within 24 Hours` is based on elapsed time and does not require occurrence and reporting on the same calendar date.

## Academic Periods

| Academic Period | Description |
|---|---|
| Spring Semester | Spring instructional period |
| Summer Break | Summer academic and break period |
| Fall Semester | Fall instructional period |
| Winter Break | Winter recess period |
| Unknown | Date could not be assigned reliably |

Values such as `Summer`, `Summer Semester`, and `Summer Session` are standardized as `Summer Break`.

The academic-period incident rate is calculated as:

`Distinct incidents divided by calendar weeks represented in the academic period`

The denominator includes dates with zero recorded incidents.

## Arrest Fields

| Field | Type | Description |
|---|---|---|
| `arrest_id` | Integer or text | Unique project identifier for an arrest |
| `arrest_number` | Text | Source arrest identifier |
| `case_number` | Text | Case number associated with the arrest |
| `arrested_datetime` | Datetime | Date and time of arrest |
| `arrested_year` | Integer | Calendar year of arrest |
| `arrested_month` | Integer | Numeric arrest month |
| `arrested_month_name` | Text | Arrest month name |
| `arrested_weekday` | Text | Weekday of arrest |
| `arrested_hour` | Integer | Hour of arrest |
| `arrested_charge` | Text | Original or cleaned charge description |
| `charge_category` | Text | Standardized charge category |
| `arrest_location` | Text | Arrest location, when available |

## Charge Categories

| Charge Category | General Meaning |
|---|---|
| DUI / Impaired Driving | Impaired-driving charges |
| Assault / Violence | Assault and violence-related charges |
| Theft / Property | Theft and property-related charges |
| Drug / Controlled Substance | Drug and controlled-substance charges |
| Alcohol-Related | Alcohol-related charges |
| Traffic / Vehicle | Traffic and vehicle-related charges |
| Fraud / Financial Crime | Fraud and financial charges |
| Trespassing | Unauthorized entry or presence |
| Weapons | Weapons-related charges |
| Disorderly Conduct | Disturbance and disorderly conduct charges |
| Burglary / Breaking and Entering | Burglary and unlawful-entry charges |
| Vandalism / Property Damage | Property-damage charges |
| Other | Valid charges outside the main groups |
| Unknown | Missing or unusable charge information |

## Incident-to-Arrest Matching

Incident and arrest records are linked using standardized case numbers.

A reliable match generally requires:

- a valid incident case number
- a valid arrest case number
- consistent formatting
- matching normalized values

Unmatched records may result from missing identifiers, inconsistent formatting, or incomplete public record coverage.

### Key Matching Measures

| Measure | Definition |
|---|---|
| All Cleaned Arrests | Complete cleaned arrest dataset |
| Linked Arrest Records | Arrest records matched to selected incidents |
| Distinct Linked Arrest Cases | Unique matched case numbers |
| Matched Incidents | Incidents connected to at least one arrest |
| Incident-to-Arrest Match Coverage | Matched incidents divided by all selected incidents |
| Linked Arrest Share | Linked arrest records divided by all cleaned arrest records |

Incident-to-arrest match coverage measures successful record linkage. It does not represent the legal arrest rate.

## Data Quality Fields

### Incident Quality Flags

| Field | Description |
|---|---|
| `has_valid_case_number` | Incident case number is available and usable |
| `has_valid_occurred_datetime` | Occurrence datetime parsed successfully |
| `has_valid_reported_datetime` | Reported datetime parsed successfully |
| `has_valid_reporting_delay` | Reporting delay is non-negative and usable |

### Arrest Quality Flags

| Field | Description |
|---|---|
| `has_valid_arrest_number` | Arrest number is available and usable |
| `has_valid_case_number` | Arrest case number is available and usable |
| `has_valid_arrested_datetime` | Arrest datetime parsed successfully |
| `has_charge_text` | Usable charge description is available |

A value of `1` represents a passed check. A value of `0` represents a failed or unavailable check.

## Primary Field Check Pass Rate

The quality pass rate is calculated as:

`Passed record-field checks divided by all evaluated record-field checks`

The score measures configured completeness and usability. It does not confirm that every source value is factually correct.

Records failing at least one quality check remain available in the dashboard review panel.

## Core SQL Views

| View | Purpose |
|---|---|
| `vw_incident_detail` | Detailed incident-level analytical dataset |
| `vw_monthly_incident_trends` | Monthly incident trends |
| `vw_crime_group_summary` | Incident totals by crime group |
| `vw_location_summary` | Incident totals by location |
| `vw_disposition_summary` | Incident totals by outcome |
| `vw_reporting_delay_summary` | Reporting-delay summaries |
| `vw_arrest_detail` | Detailed cleaned arrest dataset |
| `vw_charge_category_summary` | Arrest totals by charge category |
| `vw_incident_arrest_match` | Incident-to-arrest linkage results |

## Dashboard Metrics

| Metric | Definition |
|---|---|
| Total Incidents | Distinct selected incident records |
| Total Arrest Records | Distinct cleaned arrest records |
| Closed or Cleared Share | Closed or cleared incidents divided by all selected incidents |
| Pending or Active Share | Pending or active incidents divided by all selected incidents |
| Arrest-Related Outcome Share | Arrest-related incident outcomes divided by all selected incidents |
| Reported Within 24 Hours | Valid incidents reported within 24 elapsed hours |
| Median Reporting Delay | Median valid reporting delay |
| P90 Reporting Delay | Delay within which 90% of valid records were reported |
| Weekend Share | Incidents occurring on Saturday or Sunday |
| Incident-to-Arrest Match Coverage | Matched incidents divided by all selected incidents |
| Linked Arrest Share | Linked arrest records divided by all cleaned arrest records |
| Primary Field Check Pass Rate | Passed checks divided by all evaluated checks |

## Counting Rules

To prevent duplicate counting:

- incident measures use distinct `incident_id` values
- arrest measures use distinct `arrest_id` values
- matched incidents are counted once even when linked to multiple arrest records

Percentages use the complete eligible population for each metric.

Examples:

- outcome shares use all selected incidents
- reporting-delay shares use incidents with valid delays
- location composition uses all incidents within each location group
- arrest coverage uses all selected incidents

## Minimum Sample Threshold

Major group comparisons generally require at least 20 eligible records.

This threshold applies to:

- location-group composition
- crime-group outcome comparisons
- reporting-delay comparisons

The threshold improves stability and does not remove records from the database.

## Important Interpretation Notes

### Incident Counts Are Not Risk Rates

High incident volume may reflect greater traffic, population exposure, reporting activity, physical size, or police visibility.

### Arrest Outcomes and Arrest Matches Are Different

Arrest-related outcomes come from incident disposition values.

Arrest matches are created by linking incident and arrest records.

### Unknown and Other Are Different

`Unknown` means the value could not be classified reliably.

`Other` means a valid value exists but does not fit a major category.

### Categories Are Analytical

Standardized categories support consistent analysis but do not replace official terminology or legal definitions.

## Responsible Use

Terp Protect is intended for:

- descriptive reporting
- operational trend analysis
- data-quality review
- reporting-delay analysis
- record-linkage evaluation
- educational analysis

It should not be used for:

- predicting individual behavior
- profiling individuals or demographic groups
- automated enforcement decisions
- assigning personal risk scores
- drawing causal conclusions from descriptive data
