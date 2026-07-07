# SQL Analysis Summary 2025

## Overview
This report summarizes SQL-based analysis outputs generated from the Terp Protect database.

Current data included:
- UMPD Daily Crime and Incident Logs, 2025
- UMPD Arrest Logs, 2025

## Database Analysis Areas
- Incident volume and trends
- Crime group distribution
- Disposition and case outcome patterns
- Reporting delay analysis
- Location-based incident analysis
- Arrest charge category analysis
- Arrest demographic summary
- Incident-to-arrest matching using UMPD case number
- Data quality checks

## Top Crime Groups

| crime_group           |   incident_count |   arrest_related_count |   arrest_related_percentage |   avg_report_delay_hours |
|:----------------------|-----------------:|-----------------------:|----------------------------:|-------------------------:|
| Other                 |              839 |                     69 |                        8.22 |                   297.45 |
| Theft / Property      |              360 |                     55 |                       15.28 |                   736.4  |
| Service / Assistance  |              258 |                      3 |                        1.16 |                    94.54 |
| DUI / Traffic Alcohol |              178 |                    178 |                      100    |                     0    |
| Property Damage       |               82 |                      5 |                        6.1  |                    72.04 |
| Public Order          |               43 |                     18 |                       41.86 |                     0.18 |
| Traffic / Vehicle     |               33 |                      5 |                       15.15 |                    26.25 |
| Drug / CDS            |               32 |                     10 |                       31.25 |                     0.04 |
| Assault / Violence    |               19 |                      5 |                       26.32 |                    48.62 |
| Fraud / Identity      |               15 |                      2 |                       13.33 |                  2604.44 |
| Burglary / Robbery    |               15 |                      4 |                       26.67 |                    50.88 |
| Sex Offense           |               12 |                      4 |                       33.33 |                   761.97 |

## Top Crime Types

| crime_type                | crime_group           |   incident_count |
|:--------------------------|:----------------------|-----------------:|
| Injured/Sick Person       | Other                 |              388 |
| Theft                     | Theft / Property      |              308 |
| Dwi/Dui                   | DUI / Traffic Alcohol |              178 |
| Assist Other Agency       | Service / Assistance  |              155 |
| Other Incident            | Other                 |              104 |
| Emergency Petition        | Other                 |               87 |
| Suspicious Activity       | Service / Assistance  |               60 |
| Vandalism                 | Property Damage       |               59 |
| Damage To State Property  | Other                 |               39 |
| Cds Violation             | Drug / CDS            |               32 |
| Alcohol Violation         | Other                 |               31 |
| Warrant/Summons Service   | Other                 |               31 |
| Suspicious Person/Auto    | Service / Assistance  |               25 |
| Trespassing               | Public Order          |               25 |
| Dept Property Damage/Loss | Property Damage       |               23 |
| Assault                   | Assault / Violence    |               19 |
| Disorderly Conduct        | Public Order          |               18 |
| Accident                  | Traffic / Vehicle     |               17 |
| Fire                      | Other                 |               17 |
| Fraud                     | Fraud / Identity      |               15 |

## Disposition Summary

| disposition_group   | disposition           |   incident_count |   incident_percentage |
|:--------------------|:----------------------|-----------------:|----------------------:|
| Closed / Cleared    | Cbe                   |              972 |                 51.54 |
| Arrest              | Arrest                |              351 |                 18.61 |
| Pending / Active    | Investigation Pending |              242 |                 12.83 |
| Pending / Active    | Active/Pending        |              215 |                 11.4  |
| Unfounded           | Unfounded             |               52 |                  2.76 |
| Other               | Summons Issued        |               36 |                  1.91 |
| Other               | Warrant Issued        |               11 |                  0.58 |
| Arrest              | Juvenile Arrest       |                7 |                  0.37 |

## Monthly Incident Trends

|   occurred_year |   occurred_month | occurred_month_name   |   incident_count |
|----------------:|-----------------:|:----------------------|-----------------:|
|            2005 |                9 | September             |                1 |
|            2005 |               11 | November              |                1 |
|            2023 |                1 | January               |                1 |
|            2023 |                6 | June                  |                1 |
|            2023 |                7 | July                  |                1 |
|            2023 |                9 | September             |                1 |
|            2024 |                1 | January               |                1 |
|            2024 |                3 | March                 |                1 |
|            2024 |                5 | May                   |                1 |
|            2024 |                6 | June                  |                1 |
|            2024 |                7 | July                  |                1 |
|            2024 |                8 | August                |                2 |
|            2024 |                9 | September             |                1 |
|            2024 |               10 | October               |                5 |
|            2024 |               11 | November              |                1 |
|            2024 |               12 | December              |                8 |
|            2025 |                1 | January               |               84 |
|            2025 |                2 | February              |              143 |
|            2025 |                3 | March                 |              163 |
|            2025 |                4 | April                 |              166 |

## Weekday Incident Trends

| occurred_weekday   |   incident_count |
|:-------------------|-----------------:|
| Monday             |              232 |
| Tuesday            |              267 |
| Wednesday          |              253 |
| Thursday           |              291 |
| Friday             |              311 |
| Saturday           |              287 |
| Sunday             |              245 |

## Hourly Incident Trends

|   occurred_hour |   incident_count |
|----------------:|-----------------:|
|               0 |              137 |
|               1 |              120 |
|               2 |               79 |
|               3 |               47 |
|               4 |               35 |
|               5 |               23 |
|               6 |               19 |
|               7 |               35 |
|               8 |               68 |
|               9 |               76 |
|              10 |               65 |
|              11 |               77 |
|              12 |              100 |
|              13 |               68 |
|              14 |               95 |
|              15 |               88 |
|              16 |              113 |
|              17 |              105 |
|              18 |               91 |
|              19 |               73 |

## Location Group Summary

| location_group             |   incident_count |   arrest_related_count |   avg_report_delay_hours |
|:---------------------------|-----------------:|-----------------------:|-------------------------:|
| Other Campus / Nearby Area |              919 |                     81 |                   541.5  |
| Roadway / Street           |              681 |                    241 |                    97.84 |
| Athletic / Recreation      |              177 |                     21 |                   154.07 |
| Parking Area               |               60 |                      8 |                    50.01 |
| Academic / Campus Building |               30 |                      4 |                    60.94 |
| Greek Life                 |               13 |                      3 |                    21.63 |
| Residence / Housing        |                5 |                      0 |                     0.73 |
| Unknown                    |                1 |                      0 |                    13.9  |

## Top Locations

| location_raw                    | location_group             |   incident_count |
|:--------------------------------|:---------------------------|-----------------:|
| University Blvd                 | Roadway / Street           |               99 |
| 3900 Block Of Campus Dr         | Other Campus / Nearby Area |               82 |
| 3900 Block Of Denton Service Ln | Other Campus / Nearby Area |               57 |
| Baltimore Ave                   | Roadway / Street           |               57 |
| 4100 Block Of Stadium Dr        | Athletic / Recreation      |               53 |
| 3400 Block Of Tulane Dr         | Roadway / Street           |               52 |
| 7500 Block Of Baltimore Ave     | Roadway / Street           |               50 |
| 4100 Block Of Campus Dr         | Other Campus / Nearby Area |               37 |
| 8500 Block Of Paint Branch Dr   | Other Campus / Nearby Area |               36 |
| 4000 Block Of Stadium Dr        | Athletic / Recreation      |               34 |
| 4300 Block Of Knox Rd           | Roadway / Street           |               33 |
| 7300 Block Of Baltimore Ave     | Roadway / Street           |               33 |
| 8000 Block Of Regents Dr        | Other Campus / Nearby Area |               33 |
| 8200 Block Of Paint Branch Dr   | Other Campus / Nearby Area |               33 |
| 4200 Block Of Valley Dr         | Other Campus / Nearby Area |               32 |
| 4100 Block Of Valley Dr         | Other Campus / Nearby Area |               30 |
| 7500 Block Of Mowatt Ln         | Other Campus / Nearby Area |               30 |
| 3800 Block Of Stadium Dr        | Athletic / Recreation      |               28 |
| 7000 Block Of Preinkert Dr      | Other Campus / Nearby Area |               28 |
| 4200 Block Of Farm Dr           | Other Campus / Nearby Area |               26 |

## Reporting Delay Summary

| delay_bucket               |   incident_count |   avg_report_delay_hours |   avg_report_delay_days |
|:---------------------------|-----------------:|-------------------------:|------------------------:|
| Same Day / Within 24 Hours |             1570 |                     1.94 |                    0.08 |
| Over 7 Days                |              128 |                  4514.96 |                  188.12 |
| 1-3 Days                   |              105 |                    43.84 |                    1.83 |
| 4-7 Days                   |               77 |                   112.76 |                    4.7  |
| Unknown                    |                6 |                   nan    |                  nan    |

## Academic Period Summary

| occurred_semester_period   |   incident_count |
|:---------------------------|-----------------:|
| Fall                       |              834 |
| Spring                     |              643 |
| Summer                     |              323 |
| Winter Break               |               86 |

## Arrest Charge Category Summary

| charge_category               |   arrest_count |   alcohol_related_count |   drug_related_count |   theft_related_count |   arrest_percentage |
|:------------------------------|---------------:|------------------------:|---------------------:|----------------------:|--------------------:|
| DUI / Alcohol-Related Driving |            186 |                     186 |                  186 |                   186 |               42.27 |
| Theft / Property              |            115 |                       0 |                  115 |                   115 |               26.14 |
| Other                         |             72 |                      72 |                    0 |                     0 |               16.36 |
| Public Order                  |             23 |                       0 |                    0 |                     0 |                5.23 |
| Drug / CDS                    |             15 |                      15 |                   15 |                     0 |                3.41 |
| Assault / Violence            |             14 |                       0 |                    0 |                     0 |                3.18 |
| Traffic / Vehicle             |              7 |                       0 |                    0 |                     0 |                1.59 |
| Fraud / Identity              |              3 |                       0 |                    0 |                     0 |                0.68 |
| Burglary / Robbery            |              3 |                       0 |                    0 |                     0 |                0.68 |
| Weapon-Related                |              2 |                       0 |                    0 |                     0 |                0.45 |

## Arrest Demographic Summary

| race                    | sex     | age_group   |   arrest_count |   arrest_percentage |
|:------------------------|:--------|:------------|---------------:|--------------------:|
| White                   | Male    | Unknown     |            207 |               47.05 |
| Black                   | Male    | Unknown     |            168 |               38.18 |
| White                   | Female  | Unknown     |             18 |                4.09 |
| Asian                   | Male    | Unknown     |             17 |                3.86 |
| Black                   | Female  | Unknown     |             15 |                3.41 |
| Unknown                 | Unknown | Unknown     |             10 |                2.27 |
| Unknown                 | Male    | Unknown     |              4 |                0.91 |
| American Indian/Alaskan | Male    | Unknown     |              1 |                0.23 |

## Monthly Arrest Trends

|   arrested_year |   arrested_month | arrested_month_name   |   arrest_count |
|----------------:|-----------------:|:----------------------|---------------:|
|            2025 |                1 | January               |             42 |
|            2025 |                2 | February              |             25 |
|            2025 |                3 | March                 |             34 |
|            2025 |                4 | April                 |             41 |
|            2025 |                5 | May                   |             38 |
|            2025 |                6 | June                  |             16 |
|            2025 |                7 | July                  |             35 |
|            2025 |                8 | August                |             37 |
|            2025 |                9 | September             |             55 |
|            2025 |               10 | October               |             39 |
|            2025 |               11 | November              |             42 |
|            2025 |               12 | December              |             36 |

## Incident Arrest Match Summary

|   has_matching_arrest |   incident_count |   incident_percentage |
|----------------------:|-----------------:|----------------------:|
|                     1 |              370 |                 19.34 |
|                     0 |             1543 |                 80.66 |

## Matched Incident Charge Summary

| charge_category               |   matched_incident_count |   avg_hours_from_incident_to_arrest |
|:------------------------------|-------------------------:|------------------------------------:|
| DUI / Alcohol-Related Driving |                      177 |                                0.52 |
| Theft / Property              |                       72 |                             1109.19 |
| Other                         |                       59 |                              441.07 |
| Public Order                  |                       23 |                              290.88 |
| Drug / CDS                    |                       13 |                              125.24 |
| Assault / Violence            |                       13 |                              949.52 |
| Traffic / Vehicle             |                        7 |                                0.39 |
| Fraud / Identity              |                        3 |                                2.8  |
| Burglary / Robbery            |                        2 |                                0.53 |
| Weapon-Related                |                        1 |                                0.15 |

## Data Quality Review

| record_type      |   total_records |   invalid_case_number_count |   invalid_occurred_datetime_count |   invalid_reported_datetime_count |   invalid_reporting_delay_count |
|:-----------------|----------------:|----------------------------:|----------------------------------:|----------------------------------:|--------------------------------:|
| Incident Records |            1886 |                           0 |                                 0 |                                 0 |                               6 |
| Arrest Records   |             440 |                           0 |                                 0 |                               nan |                               0 |
