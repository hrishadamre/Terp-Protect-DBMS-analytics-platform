# Terp Protect: Analytical Summary

## Overview

Terp Protect organizes publicly available University of Maryland Police Department incident and arrest records into a structured system for easier analysis.

The dashboard helps users understand:

- common incident types
- high-activity locations
- time and seasonal patterns
- case outcomes
- reporting delays
- arrest activity
- data quality

The current analysis covers records from 2023 through 2025.

## Data Coverage

| Measure | Value |
|---|---:|
| Incident records | 5,659 |
| Cleaned arrest records | 1,175 |
| Linked arrest records | 1,103 |
| Matched incidents | 980 |
| Valid reporting-delay records | 5,644 |
| Coverage period | 2023–2025 |

## Campus Safety Overview

### Leading Incident Category

**Medical / Welfare** is the largest standardized incident group, with approximately **1,445 incidents**.

This shows that campus public-safety activity includes medical assistance, welfare checks, and emergency support in addition to traditional crime reports.

### Leading Location Group

**Roadway / Street** is the largest location group, with approximately **2,907 incidents**.

High incident counts do not automatically mean higher risk. They may also reflect more traffic, greater exposure, larger physical areas, or stronger reporting activity.

## Time and Seasonal Patterns

The dashboard shows several clear time-based patterns:

- October has the highest combined seasonal incident volume.
- Friday has the highest weekday volume.
- Midnight is the highest-volume hour.
- Saturday at 12:00 AM is the highest weekday-hour combination.
- Spring Semester has the highest normalized weekly incident rate.
- Winter Break has the lowest normalized weekly rate.

Academic-period rates are calculated using distinct incidents divided by the calendar weeks represented in each period.

## Location Patterns

The location analysis compares both detailed source locations and broader location groups.

Major location groups include:

- Roadway / Street
- Residence / Housing
- Campus Building / Facility
- Athletic / Recreation
- Parking Area

Residence / Housing locations show a notable concentration of Theft / Property incidents.

These findings are descriptive and should not be interpreted as causal relationships.

## Case Outcomes

| Outcome Group | Share |
|---|---:|
| Closed / Cleared | 49.4% |
| Pending / Active | 29.8% |
| Arrest-Related | 16.5% |
| Other outcomes | Remaining share |

Nearly half of selected incidents are closed or cleared.

Approximately three in ten remain pending or active.

DUI / Impaired Driving incidents are consistently associated with arrest-related outcomes in the current dataset.

The arrest-related outcome share comes from the incident disposition field. It is different from incident-to-arrest record matching.

## Reporting Delay

Reporting delay measures the elapsed time between when an incident occurred and when it was reported.

Only valid, non-negative delays are included in the analysis.

| Measure | Result |
|---|---:|
| Valid delay coverage | 99.7% |
| Median reporting delay | 0.2 hours |
| P90 reporting delay | 3.9 days |
| Reported within 24 hours | 81.8% |
| Reported after 7 days | 7.3% |

Most incidents are reported quickly, but a smaller group has significantly longer delays.

Fraud / Financial Crime records show some of the longest median reporting delays, which may reflect delayed discovery or later account review.

Fifteen records contain invalid reporting sequences. They remain available for review but are excluded from delay calculations.

## Arrest Analysis

The cleaned arrest dataset contains:

- 1,175 total arrest records
- 1,103 linked arrest records
- 980 distinct linked cases
- 980 matched incidents

### Incident Match Coverage

Approximately **17.3%** of incidents are linked to at least one arrest record.

Each incident is counted once, even when multiple arrest records are connected to the same case.

### Linked Arrest Share

Approximately **93.9%** of cleaned arrest records are linked to incidents in the selected analysis.

This does not mean that 93.9% of incidents resulted in arrest. It only measures how many arrest records were successfully connected to the incident dataset.

### Leading Charge Category

**DUI / Impaired Driving** is the largest standardized arrest charge category.

Other major categories include:

- Theft / Property
- Public Order
- Alcohol-Related
- Property Damage
- Assault / Violence
- Drug / Controlled Substance

## Data Quality

The project checks whether important fields are complete and usable.

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

Records requiring review are retained for transparency instead of being silently removed.

The quality score measures completeness and format validity. It does not prove that every source value is factually correct.

## Business Value

Terp Protect creates a reusable foundation for public-safety analysis by:

- reducing manual data preparation
- standardizing inconsistent categories
- improving reporting consistency
- connecting incident and arrest records
- identifying records requiring review
- supporting interactive filtering and comparison
- making complex public records easier to understand

The project can support recurring analysis, operational review, reporting, and data-quality improvement.

## Limitations

- The project uses publicly available records and does not include all internal police-system data.
- Incident counts are not population-adjusted risk rates.
- Location names may contain abbreviations or alternate descriptions.
- Arrest matching depends on available and consistent case numbers.
- Standardized categories do not replace official UMPD terminology.
- Academic periods use simplified calendar groupings.
- The analysis is descriptive and does not establish causation.

## Responsible Use

Terp Protect is intended for:

- descriptive reporting
- operational trend review
- data-quality validation
- educational analysis
- process improvement

It should not be used for:

- predicting individual behavior
- profiling individuals or demographic groups
- automated enforcement decisions
- assigning personal risk scores
- drawing causal conclusions from descriptive data
