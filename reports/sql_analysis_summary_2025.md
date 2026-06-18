# SQL Analysis Summary

Generated At: 2026-06-18 01:57:36

## Scope

- Dataset: UMPD Daily Crime and Incident Logs
- Year: 2025
- Database: `data/database/terp_protect.db`

## Summary Tables

### Top Crime Groups

| crime_group           |   incident_count |   incident_percentage |
|:----------------------|-----------------:|----------------------:|
| Other                 |              839 |                 44.49 |
| Theft / Property      |              360 |                 19.09 |
| Service / Assistance  |              258 |                 13.68 |
| DUI / Traffic Alcohol |              178 |                  9.44 |
| Property Damage       |               82 |                  4.35 |
| Public Order          |               43 |                  2.28 |
| Traffic / Vehicle     |               33 |                  1.75 |
| Drug / CDS            |               32 |                  1.7  |
| Assault / Violence    |               19 |                  1.01 |
| Burglary / Robbery    |               15 |                  0.8  |

### Top Crime Types

| crime_type               | crime_group           |   incident_count |
|:-------------------------|:----------------------|-----------------:|
| Injured/Sick Person      | Other                 |              388 |
| Theft                    | Theft / Property      |              308 |
| Dwi/Dui                  | DUI / Traffic Alcohol |              178 |
| Assist Other Agency      | Service / Assistance  |              155 |
| Other Incident           | Other                 |              104 |
| Emergency Petition       | Other                 |               87 |
| Suspicious Activity      | Service / Assistance  |               60 |
| Vandalism                | Property Damage       |               59 |
| Damage To State Property | Other                 |               39 |
| Cds Violation            | Drug / CDS            |               32 |

### Disposition Summary

| disposition_group   |   incident_count |   incident_percentage |
|:--------------------|-----------------:|----------------------:|
| Closed / Cleared    |              972 |                 51.54 |
| Pending / Active    |              457 |                 24.23 |
| Arrest              |              358 |                 18.98 |
| Unfounded           |               52 |                  2.76 |
| Other               |               47 |                  2.49 |

### Arrest-Related Summary

|   total_incidents |   arrest_related_incidents |   arrest_related_percentage |
|------------------:|---------------------------:|----------------------------:|
|              1886 |                        358 |                       18.98 |

### Monthly Incident Trends

|   occurred_month | occurred_month_name   |   incident_count |   arrest_related_count |   avg_report_delay_hours |
|-----------------:|:----------------------|-----------------:|-----------------------:|-------------------------:|
|                1 | January               |               86 |                     27 |                   445.19 |
|                2 | February              |              143 |                     23 |                    40.08 |
|                3 | March                 |              164 |                     37 |                   107.9  |
|                4 | April                 |              166 |                     27 |                    46.21 |
|                5 | May                   |              170 |                     26 |                   138.53 |
|                6 | June                  |               90 |                     21 |                   375.86 |
|                7 | July                  |               97 |                     29 |                   238.59 |
|                8 | August                |              136 |                     37 |                   126.15 |
|                9 | September             |              277 |                     47 |                   736.24 |
|               10 | October               |              239 |                     31 |                   119.69 |

### Location Group Summary

| location_group             |   incident_count |   incident_percentage |   arrest_related_count |
|:---------------------------|-----------------:|----------------------:|-----------------------:|
| Other Campus / Nearby Area |              919 |                 48.73 |                     81 |
| Roadway / Street           |              681 |                 36.11 |                    241 |
| Athletic / Recreation      |              177 |                  9.38 |                     21 |
| Parking Area               |               60 |                  3.18 |                      8 |
| Academic / Campus Building |               30 |                  1.59 |                      4 |
| Greek Life                 |               13 |                  0.69 |                      3 |
| Residence / Housing        |                5 |                  0.27 |                      0 |
| Unknown                    |                1 |                  0.05 |                      0 |

### Reporting Delay Summary

| delay_bucket               |   incident_count |   incident_percentage |   avg_report_delay_hours |   avg_report_delay_days |
|:---------------------------|-----------------:|----------------------:|-------------------------:|------------------------:|
| Same Day / Within 24 Hours |             1570 |                 83.24 |                     1.94 |                    0.08 |
| 1-3 Days                   |              105 |                  5.57 |                    43.84 |                    1.83 |
| 4-7 Days                   |               77 |                  4.08 |                   112.76 |                    4.7  |
| Over 7 Days                |              128 |                  6.79 |                  4514.96 |                  188.12 |
| Unknown                    |                6 |                  0.32 |                   nan    |                  nan    |

### Academic Period Summary

| occurred_semester_period   |   incident_count |   arrest_related_count |   avg_report_delay_hours |
|:---------------------------|-----------------:|-----------------------:|-------------------------:|
| Fall Semester              |              834 |                    131 |                   514.98 |
| Spring Semester            |              643 |                    113 |                    84.87 |
| Summer                     |              323 |                     87 |                   229.5  |
| Winter Break               |               86 |                     27 |                   445.19 |

### Data Quality Review

|   total_incidents |   missing_case_number_count |   invalid_occurred_datetime_count |   invalid_reported_datetime_count |   invalid_reporting_delay_count |
|------------------:|----------------------------:|----------------------------------:|----------------------------------:|--------------------------------:|
|              1886 |                           0 |                                 0 |                                 0 |                               6 |
