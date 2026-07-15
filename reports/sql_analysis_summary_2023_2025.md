# Terp Protect: SQL Analysis Summary 2023–2025

## Overview

This document summarizes the main findings generated from the Terp Protect SQL database.

The analysis uses publicly available University of Maryland Police Department incident and arrest records from 2023 through 2025.

The SQL workflow supports analysis across:

- incident volume and timing
- crime and location patterns
- case outcomes
- reporting delays
- arrests and charge categories
- incident-to-arrest matching
- data quality

## Data Coverage

| Measure | Value |
|---|---:|
| Incident records | 5,659 |
| Cleaned arrest records | 1,175 |
| Linked arrest records | 1,103 |
| Distinct linked arrest cases | 980 |
| Matched incidents | 980 |
| Valid reporting-delay records | 5,644 |
| Coverage period | 2023–2025 |

## Incident Trends

Incident activity remained relatively consistent across the three source years.

| Year | Incident Count |
|---|---:|
| 2023 | 1,850 |
| 2024 | 2,019 |
| 2025 | 1,913 |

Small differences may occur between source-year and occurrence-year analysis because some records were reported in one source file but occurred in another calendar year.

### Main Time Patterns

- October has the highest combined seasonal incident volume.
- Friday records the highest weekday incident count.
- Midnight is the highest-volume hour.
- Saturday at 12:00 AM is the highest weekday-hour combination.
- Spring Semester has the highest normalized weekly incident rate.
- Winter Break has the lowest normalized weekly rate.

The academic-period rate is based on distinct incidents divided by represented calendar weeks.

## Crime Patterns

### Leading Crime Groups

| Crime Group | Approximate Incident Count |
|---|---:|
| Medical / Welfare | 1,445 |
| Theft / Property | Major recurring category |
| Service / Assistance | Major recurring category |
| Property Damage | Major recurring category |
| DUI / Impaired Driving | 400 |

Medical / Welfare is the largest standardized incident category.

This indicates that public-safety activity includes medical assistance, welfare checks, emergency responses, and other non-criminal services in addition to traditional crime reports.

## Location Patterns

### Leading Location Group

| Location Group | Incident Count |
|---|---:|
| Roadway / Street | 2,907 |

Roadway and street locations account for the largest share of recorded activity.

Other major groups include:

- Residence / Housing
- Campus Building / Facility
- Athletic / Recreation
- Parking Area

High incident volume should not be interpreted as a population-adjusted risk rate. It may reflect greater traffic, exposure, physical size, operating hours, or reporting activity.

## Case Outcomes

| Outcome Group | Share |
|---|---:|
| Closed / Cleared | 49.4% |
| Pending / Active | 29.8% |
| Arrest-Related | 16.5% |
| Other outcomes | Remaining share |

Nearly half of the selected incidents are categorized as closed or cleared.

Approximately three in ten remain pending or active.

DUI / Impaired Driving records are consistently associated with arrest-related outcomes in the current dataset.

Arrest-related outcome share is based on the incident disposition field and is different from incident-to-arrest record matching.

## Reporting Delay

Reporting delay measures the elapsed time between incident occurrence and reporting.

Only valid, non-negative delays are included in the calculations.

| Measure | Result |
|---|---:|
| Valid delay records | 5,644 |
| Valid delay coverage | 99.7% |
| Median delay | 0.2 hours |
| P90 delay | 3.9 days |
| Reported within 24 hours | 81.8% |
| Reported after 7 days | 7.3% |

The delay distribution is strongly right-skewed.

Most incidents are reported quickly, while a smaller number have significantly longer delays.

Fraud / Financial Crime records show some of the longest median reporting delays, which may reflect delayed discovery or later account review.

Fifteen incident records contain invalid reporting sequences and are excluded from delay calculations.

## Arrest Analysis

### Arrest Volume

| Year | Arrest Count |
|---|---:|
| 2023 | 300 |
| 2024 | 435 |
| 2025 | 440 |

Arrest volume increased from 2023 to 2024 and remained similar in 2025.

### Charge Categories

DUI / Impaired Driving is the largest standardized charge category.

Other major categories include:

- Theft / Property
- Public Order
- Alcohol-Related
- Property Damage
- Assault / Violence
- Drug / Controlled Substance

The arrest analysis distinguishes between:

- all cleaned arrest records
- arrest records linked to selected incidents
- distinct linked arrest cases
- matched incidents

## Incident-to-Arrest Matching

| Measure | Value |
|---|---:|
| Linked arrest records | 1,103 |
| Distinct linked arrest cases | 980 |
| Matched incidents | 980 |
| Incident match coverage | 17.3% |
| Linked arrest share | 93.9% |

Incident match coverage is calculated as:

`Distinct incidents with at least one linked arrest divided by all selected incidents`

Each incident is counted once, even when multiple arrest records are linked to the same case.

Linked arrest share is calculated as:

`Linked arrest records divided by all cleaned arrest records`

These measures describe record linkage and should not be interpreted as legal arrest rates.

## Data Quality

The SQL workflow checks the completeness and usability of important incident and arrest fields.

Primary checks include:

- incident case number
- occurrence datetime
- reported datetime
- reporting-delay validity
- arrest number
- arrest case number
- arrest datetime
- charge description

| Quality Measure | Result |
|---|---:|
| Primary field-check pass rate | 99.94% |
| Incident records requiring review | 15 |
| Arrest records requiring review | 0 |

Records requiring review remain available for inspection instead of being silently removed.

## Core SQL Views

| View | Purpose |
|---|---|
| `vw_incident_detail` | Detailed incident-level analysis |
| `vw_monthly_incident_trends` | Monthly and yearly trends |
| `vw_crime_group_summary` | Incident totals by crime group |
| `vw_location_summary` | Incident totals by location |
| `vw_disposition_summary` | Case-outcome analysis |
| `vw_reporting_delay_summary` | Reporting-delay analysis |
| `vw_arrest_detail` | Detailed arrest analysis |
| `vw_charge_category_summary` | Charge-category totals |
| `vw_incident_arrest_match` | Incident-to-arrest linkage |

## Key Business Questions Answered

The SQL analysis supports questions such as:

- Which incident categories occur most frequently?
- Which locations have the highest recorded activity?
- When does incident activity increase?
- What proportion of cases are closed or pending?
- How quickly are incidents reported?
- Which crime groups have longer reporting delays?
- What are the most common arrest charge categories?
- How many incidents can be linked to arrest records?
- Which records require additional data-quality review?
