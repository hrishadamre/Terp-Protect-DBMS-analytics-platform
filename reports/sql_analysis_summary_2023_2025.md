# SQL Analysis Summary 2023-2025

## Overview

This report summarizes SQL-based analysis outputs generated from the Terp Protect database.

Data included:
- UMPD Daily Crime and Incident Logs, 2023-2025
- UMPD Arrest Logs, 2023-2025

## Database Analysis Areas

- Yearly incident and arrest volume
- Monthly, weekday, and hourly trends
- Crime group and crime type distribution
- Disposition and case outcome patterns
- Reporting delay analysis
- Location-based incident analysis
- Arrest charge category analysis
- Arrest demographic summary
- Incident-to-arrest matching
- Data quality checks

## Yearly Incident Summary

|   occurred_year |   incident_count |   arrest_related_count |   pending_count |   closed_count |   avg_report_delay_hours |
|----------------:|-----------------:|-----------------------:|----------------:|---------------:|-------------------------:|
|            2002 |                1 |                      0 |               0 |              0 |                192885    |
|            2003 |                1 |                      0 |               1 |              0 |                175335    |
|            2004 |                1 |                      0 |               0 |              1 |                175320    |
|            2005 |                2 |                      0 |               1 |              1 |                175418    |
|            2017 |                1 |                      0 |               0 |              1 |                 66053.4  |
|            2020 |                1 |                      0 |               0 |              1 |                 35298.3  |
|            2021 |                2 |                      0 |               0 |              2 |                 19675.4  |
|            2022 |               27 |                      3 |              20 |              2 |                  3845.04 |
|            2023 |             1818 |                    258 |             634 |            877 |                   156.28 |
|            2024 |             1947 |                    313 |             589 |            949 |                   100.26 |
|            2025 |             1858 |                    357 |             443 |            961 |                    48.95 |

## Top Crime Groups

|   occurred_year | crime_group               |   incident_count |   arrest_related_count |   arrest_related_percentage |   avg_report_delay_hours |
|----------------:|:--------------------------|-----------------:|-----------------------:|----------------------------:|-------------------------:|
|            2002 | Harassment / Threats      |                1 |                      0 |                        0    |                192885    |
|            2003 | Theft / Property          |                1 |                      0 |                        0    |                175335    |
|            2004 | Medical / Welfare         |                1 |                      0 |                        0    |                175320    |
|            2005 | Theft / Property          |                1 |                      0 |                        0    |                175511    |
|            2005 | Property Damage           |                1 |                      0 |                        0    |                175325    |
|            2017 | Sex Offense / Title IX    |                1 |                      0 |                        0    |                 66053.4  |
|            2020 | Other Incident            |                1 |                      0 |                        0    |                 35298.3  |
|            2021 | Service / Assistance      |                1 |                      0 |                        0    |                 13046.9  |
|            2021 | Medical / Welfare         |                1 |                      0 |                        0    |                 26304    |
|            2022 | Theft / Property          |               15 |                      2 |                       13.33 |                  1797.38 |
|            2022 | Property Damage           |                4 |                      0 |                        0    |                  4116.38 |
|            2022 | Sex Offense / Title IX    |                2 |                      0 |                        0    |                  4258.05 |
|            2022 | Harassment / Threats      |                2 |                      0 |                        0    |                 13631.2  |
|            2022 | Fraud / Financial Crime   |                2 |                      1 |                       50    |                  9530.9  |
|            2022 | Service / Assistance      |                1 |                      0 |                        0    |                  5375.4  |
|            2022 | Lost / Recovered Property |                1 |                      0 |                        0    |                   174.08 |
|            2023 | Medical / Welfare         |              455 |                      0 |                        0    |                    14.9  |
|            2023 | Theft / Property          |              412 |                     47 |                       11.41 |                   211.16 |
|            2023 | Service / Assistance      |              239 |                      2 |                        0.84 |                   132.4  |
|            2023 | Property Damage           |              161 |                     12 |                        7.45 |                   172.11 |
|            2023 | Other Incident            |              107 |                      0 |                        0    |                   315.83 |
|            2023 | DUI / Impaired Driving    |               96 |                     96 |                      100    |                     0    |
|            2023 | Harassment / Threats      |               55 |                      0 |                        0    |                   529.36 |
|            2023 | Public Order              |               41 |                     29 |                       70.73 |                     0.71 |
|            2023 | Assault / Violence        |               40 |                     13 |                       32.5  |                     3.18 |
|            2023 | Traffic / Vehicle         |               38 |                      3 |                        7.89 |                     5.04 |
|            2023 | Drug / CDS                |               33 |                     12 |                       36.36 |                     0.06 |
|            2023 | Sex Offense / Title IX    |               25 |                      6 |                       24    |                   961.3  |
|            2023 | Fire / Hazard             |               25 |                      0 |                        0    |                     0.13 |
|            2023 | Fraud / Financial Crime   |               23 |                      4 |                       17.39 |                  1724.69 |

## Top Crime Types

|   occurred_year | crime_type                | crime_group               |   incident_count |
|----------------:|:--------------------------|:--------------------------|-----------------:|
|            2002 | Telephone/EMail Misuse    | Harassment / Threats      |                1 |
|            2003 | Theft                     | Theft / Property          |                1 |
|            2004 | Injured/Sick Person       | Medical / Welfare         |                1 |
|            2005 | Damaged Property          | Property Damage           |                1 |
|            2005 | Theft                     | Theft / Property          |                1 |
|            2017 | Rape                      | Sex Offense / Title IX    |                1 |
|            2020 | Other Incident            | Other Incident            |                1 |
|            2021 | Assist Other Agency       | Service / Assistance      |                1 |
|            2021 | Injured/Sick Person       | Medical / Welfare         |                1 |
|            2022 | Theft                     | Theft / Property          |               15 |
|            2022 | Fraud                     | Fraud / Financial Crime   |                2 |
|            2022 | Vandalism                 | Property Damage           |                2 |
|            2022 | Damage to State Property  | Property Damage           |                1 |
|            2022 | Dept Property Damage/Loss | Property Damage           |                1 |
|            2022 | Hate Bias Incident        | Harassment / Threats      |                1 |
|            2022 | Lost Property             | Lost / Recovered Property |                1 |
|            2022 | Rape                      | Sex Offense / Title IX    |                1 |
|            2022 | Sex Offense               | Sex Offense / Title IX    |                1 |
|            2022 | Suspicious Activity       | Service / Assistance      |                1 |
|            2022 | Telephone/EMail Misuse    | Harassment / Threats      |                1 |
|            2023 | Injured/Sick Person       | Medical / Welfare         |              361 |
|            2023 | Theft                     | Theft / Property          |              335 |
|            2023 | Assist Other Agency       | Service / Assistance      |              157 |
|            2023 | Other Incident            | Other Incident            |              107 |
|            2023 | Vandalism                 | Property Damage           |              106 |
|            2023 | DWI/DUI                   | DUI / Impaired Driving    |               96 |
|            2023 | Emergency Petition        | Medical / Welfare         |               62 |
|            2023 | Suspicious Activity       | Service / Assistance      |               46 |
|            2023 | Assault                   | Assault / Violence        |               33 |
|            2023 | CDS Violation             | Drug / CDS                |               32 |

## Disposition Summary

|   occurred_year | disposition_group        | disposition           |   incident_count |   incident_percentage |
|----------------:|:-------------------------|:----------------------|-----------------:|----------------------:|
|            2002 | Unfounded                | Unfounded             |                1 |                100    |
|            2003 | Pending / Active         | Investigation Pending |                1 |                100    |
|            2004 | Closed / Cleared         | CBE                   |                1 |                100    |
|            2005 | Closed / Cleared         | CBE                   |                1 |                 50    |
|            2005 | Pending / Active         | Investigation Pending |                1 |                 50    |
|            2017 | Closed / Cleared         | CBE                   |                1 |                100    |
|            2020 | Closed / Cleared         | CBE                   |                1 |                100    |
|            2021 | Closed / Cleared         | CBE                   |                2 |                100    |
|            2022 | Pending / Active         | Investigation Pending |               13 |                 48.15 |
|            2022 | Pending / Active         | Active/Pending        |                7 |                 25.93 |
|            2022 | Arrest                   | Arrest                |                3 |                 11.11 |
|            2022 | Closed / Cleared         | CBE                   |                2 |                  7.41 |
|            2022 | Unfounded                | Unfounded             |                2 |                  7.41 |
|            2023 | Closed / Cleared         | CBE                   |              877 |                 48.24 |
|            2023 | Pending / Active         | Active/Pending        |              320 |                 17.6  |
|            2023 | Pending / Active         | Investigation Pending |              314 |                 17.27 |
|            2023 | Arrest                   | Arrest                |              257 |                 14.14 |
|            2023 | Unfounded                | Unfounded             |               30 |                  1.65 |
|            2023 | Summons / Warrant Issued | Warrant Issued        |               10 |                  0.55 |
|            2023 | Summons / Warrant Issued | Summons Issued        |                9 |                  0.5  |
|            2023 | Arrest                   | Juvenile Arrest       |                1 |                  0.06 |
|            2024 | Closed / Cleared         | CBE                   |              949 |                 48.74 |
|            2024 | Pending / Active         | Investigation Pending |              391 |                 20.08 |
|            2024 | Arrest                   | Arrest                |              310 |                 15.92 |
|            2024 | Pending / Active         | Active/Pending        |              198 |                 10.17 |
|            2024 | Unfounded                | Unfounded             |               41 |                  2.11 |
|            2024 | Summons / Warrant Issued | Summons Issued        |               37 |                  1.9  |
|            2024 | Summons / Warrant Issued | Warrant Issued        |               18 |                  0.92 |
|            2024 | Arrest                   | Juvenile Arrest       |                3 |                  0.15 |
|            2025 | Closed / Cleared         | CBE                   |              961 |                 51.72 |

## Monthly Incident Trends

|   occurred_year |   occurred_month | occurred_month_name   |   incident_count |
|----------------:|-----------------:|:----------------------|-----------------:|
|            2002 |                8 | August                |                1 |
|            2003 |               10 | October               |                1 |
|            2004 |                3 | March                 |                1 |
|            2005 |                9 | September             |                1 |
|            2005 |               11 | November              |                1 |
|            2017 |                1 | January               |                1 |
|            2020 |                2 | February              |                1 |
|            2021 |               10 | October               |                2 |
|            2022 |                1 | January               |                2 |
|            2022 |                2 | February              |                1 |
|            2022 |                5 | May                   |                1 |
|            2022 |                7 | July                  |                1 |
|            2022 |                8 | August                |                1 |
|            2022 |               10 | October               |                2 |
|            2022 |               11 | November              |                1 |
|            2022 |               12 | December              |               18 |
|            2023 |                1 | January               |               97 |
|            2023 |                2 | February              |              164 |
|            2023 |                3 | March                 |              162 |
|            2023 |                4 | April                 |              170 |
|            2023 |                5 | May                   |              164 |
|            2023 |                6 | June                  |              100 |
|            2023 |                7 | July                  |               80 |
|            2023 |                8 | August                |              110 |
|            2023 |                9 | September             |              221 |
|            2023 |               10 | October               |              242 |
|            2023 |               11 | November              |              205 |
|            2023 |               12 | December              |              103 |
|            2024 |                1 | January               |              103 |
|            2024 |                2 | February              |              178 |

## Weekday Incident Trends

|   occurred_year | occurred_weekday   |   incident_count |
|----------------:|:-------------------|-----------------:|
|            2002 | Tuesday            |                1 |
|            2003 | Sunday             |                1 |
|            2004 | Friday             |                1 |
|            2005 | Monday             |                1 |
|            2005 | Saturday           |                1 |
|            2017 | Sunday             |                1 |
|            2020 | Wednesday          |                1 |
|            2021 | Friday             |                1 |
|            2021 | Saturday           |                1 |
|            2022 | Monday             |                8 |
|            2022 | Tuesday            |                2 |
|            2022 | Wednesday          |                4 |
|            2022 | Thursday           |                2 |
|            2022 | Friday             |                5 |
|            2022 | Saturday           |                6 |
|            2023 | Monday             |              228 |
|            2023 | Tuesday            |              260 |
|            2023 | Wednesday          |              247 |
|            2023 | Thursday           |              250 |
|            2023 | Friday             |              325 |
|            2023 | Saturday           |              283 |
|            2023 | Sunday             |              225 |
|            2024 | Monday             |              268 |
|            2024 | Tuesday            |              283 |
|            2024 | Wednesday          |              256 |
|            2024 | Thursday           |              279 |
|            2024 | Friday             |              351 |
|            2024 | Saturday           |              285 |
|            2024 | Sunday             |              225 |
|            2025 | Monday             |              226 |

## Hourly Incident Trends

|   occurred_year |   occurred_hour |   incident_count |
|----------------:|----------------:|-----------------:|
|            2002 |              15 |                1 |
|            2003 |              18 |                1 |
|            2004 |               9 |                1 |
|            2005 |              12 |                1 |
|            2005 |              16 |                1 |
|            2017 |               8 |                1 |
|            2020 |              17 |                1 |
|            2021 |               9 |                1 |
|            2021 |              22 |                1 |
|            2022 |               0 |                3 |
|            2022 |               5 |                1 |
|            2022 |               8 |                3 |
|            2022 |               9 |                1 |
|            2022 |              11 |                1 |
|            2022 |              12 |                4 |
|            2022 |              13 |                1 |
|            2022 |              14 |                5 |
|            2022 |              15 |                1 |
|            2022 |              16 |                2 |
|            2022 |              17 |                1 |
|            2022 |              18 |                1 |
|            2022 |              20 |                3 |
|            2023 |               0 |              164 |
|            2023 |               1 |              108 |
|            2023 |               2 |               87 |
|            2023 |               3 |               36 |
|            2023 |               4 |               34 |
|            2023 |               5 |                8 |
|            2023 |               6 |               22 |
|            2023 |               7 |               40 |

## Location Group Summary

|   occurred_year | location_group                  |   incident_count |   arrest_related_count |   avg_report_delay_hours |
|----------------:|:--------------------------------|-----------------:|-----------------------:|-------------------------:|
|            2002 | Roadway / Street                |                1 |                      0 |                192885    |
|            2003 | Residence / Housing             |                1 |                      0 |                175335    |
|            2004 | Roadway / Street                |                1 |                      0 |                175320    |
|            2005 | Roadway / Street                |                2 |                      0 |                175418    |
|            2017 | Residence / Housing             |                1 |                      0 |                 66053.4  |
|            2020 | Campus Service / Administrative |                1 |                      0 |                 35298.3  |
|            2021 | Roadway / Street                |                1 |                      0 |                 26304    |
|            2021 | Other Campus / Nearby Area      |                1 |                      0 |                 13046.9  |
|            2022 | Residence / Housing             |               12 |                      1 |                  2100.09 |
|            2022 | Roadway / Street                |                8 |                      1 |                  3582.73 |
|            2022 | Campus Building / Facility      |                5 |                      1 |                  9974.45 |
|            2022 | Parking Area                    |                1 |                      0 |                    66.27 |
|            2022 | Athletic / Recreation           |                1 |                      0 |                    14.58 |
|            2023 | Roadway / Street                |              669 |                    152 |                   192.51 |
|            2023 | Residence / Housing             |              421 |                     31 |                   125.15 |
|            2023 | Campus Building / Facility      |              390 |                     47 |                   143.89 |
|            2023 | Athletic / Recreation           |              159 |                      8 |                   212.6  |
|            2023 | Parking Area                    |              136 |                     17 |                    88.46 |
|            2023 | Other Campus / Nearby Area      |               31 |                      3 |                     7.38 |
|            2023 | Campus Service / Administrative |               12 |                      0 |                    39.05 |
|            2024 | Roadway / Street                |              738 |                    180 |                   151.55 |
|            2024 | Residence / Housing             |              477 |                     49 |                    52.36 |
|            2024 | Campus Building / Facility      |              401 |                     50 |                    83.85 |
|            2024 | Athletic / Recreation           |              187 |                     11 |                   104.46 |
|            2024 | Parking Area                    |              117 |                     21 |                    38.32 |
|            2024 | Other Campus / Nearby Area      |               24 |                      2 |                    26.65 |
|            2024 | Campus Service / Administrative |                3 |                      0 |                   113.38 |
|            2025 | Roadway / Street                |             1487 |                    309 |                    42.73 |
|            2025 | Athletic / Recreation           |              184 |                     23 |                    92.49 |
|            2025 | Campus Building / Facility      |               77 |                     11 |                    35.51 |

## Top Locations

|   occurred_year | location_raw                                                                                                      | location_group                  |   incident_count |
|----------------:|:------------------------------------------------------------------------------------------------------------------|:--------------------------------|-----------------:|
|            2002 | 7700 block of Baltimore Ave                                                                                       | Roadway / Street                |                1 |
|            2003 | Cumberland Hall at 4250 Farm Dr                                                                                   | Residence / Housing             |                1 |
|            2004 | 7600 block of Preinkert Dr                                                                                        | Roadway / Street                |                1 |
|            2005 | 3800 block of Campus Dr                                                                                           | Roadway / Street                |                1 |
|            2005 | 7000 block of Preinkert Dr                                                                                        | Roadway / Street                |                1 |
|            2017 | Denton, Denton Hall at 3854 Stadium Dr                                                                            | Residence / Housing             |                1 |
|            2020 | Litton, Police Services & Training Facility at 7147 51st Ave                                                      | Campus Service / Administrative |                1 |
|            2021 | 7700 block of Baltimore Ave                                                                                       | Roadway / Street                |                1 |
|            2021 | 9600 block of Milestone Way                                                                                       | Other Campus / Nearby Area      |                1 |
|            2022 | 4200 block of Valley Dr                                                                                           | Roadway / Street                |                2 |
|            2022 | 96, Cambridge, Cambridge Hall at 4230 Farm Dr                                                                     | Residence / Housing             |                2 |
|            2022 | Denton, Denton Hall at 3854 Stadium Dr                                                                            | Residence / Housing             |                2 |
|            2022 | Ellicott Area Dining Hall, Ellicott Dining Hall at 4028 Stadium Dr                                                | Residence / Housing             |                2 |
|            2022 | 300 block of Ehrensberger Dr                                                                                      | Roadway / Street                |                1 |
|            2022 | 3400 block of Tulane Dr                                                                                           | Roadway / Street                |                1 |
|            2022 | 3800 block of Campus Dr                                                                                           | Roadway / Street                |                1 |
|            2022 | 7, Pocomoke, Pocomoke Building, Police, UMDPS, UMPD at 7569 Baltimore Ave                                         | Campus Building / Facility      |                1 |
|            2022 | 7700 block of Adelphi Rd                                                                                          | Roadway / Street                |                1 |
|            2022 | 8100 block of Boteler Ln                                                                                          | Roadway / Street                |                1 |
|            2022 | 84, Kirwan Hall, Mathematics, Mathematics Building, William E. Kirwan Hall, William Kirwan Hall at 4176 Campus Dr | Residence / Housing             |                1 |
|            2022 | 88, Martin Hall at 4298 Campus Dr                                                                                 | Residence / Housing             |                1 |
|            2022 | A James Clark Hall, A. James Clark Hall, A.J. Clark Hall, Clark, Clark Hall at 8278 Paint Branch Dr               | Residence / Housing             |                1 |
|            2022 | A.V. Williams Building, AV Williams at 8223 Paint Branch Dr                                                       | Campus Building / Facility      |                1 |
|            2022 | Benjamin, Benjamin Bldg, Benjamin Building at 3942 Campus Dr                                                      | Campus Building / Facility      |                1 |
|            2022 | Club House, Golf Course Club House at 3800 Golf Course Rd                                                         | Athletic / Recreation           |                1 |
|            2022 | Dairy, Stamp, Stamp Student Union, Student Union, Union at 3972 Campus Dr                                         | Campus Building / Facility      |                1 |
|            2022 | Johnson-Whittle Hall at 4118 Stadium Dr                                                                           | Residence / Housing             |                1 |
|            2022 | La Plata Hall at 8160 La Plata Dr                                                                                 | Residence / Housing             |                1 |
|            2022 | LeonardtownLeonardtown #201Leonardtown ApartmentLeonardtown Office Building at 4725 Rossborough Ln                | Residence / Housing             |                1 |
|            2022 | Lot 19, Lot U2, MLG, Mowatt Garage, Mowatt Lane Garage, Mowatt Lane Parking Garage, PG5 at 7591 Mowatt Ln         | Parking Area                    |                1 |

## Reporting Delay Summary

|   occurred_year | delay_bucket               |   incident_count |   avg_report_delay_hours |   avg_report_delay_days |
|----------------:|:---------------------------|-----------------:|-------------------------:|------------------------:|
|            2002 | Over 7 Days                |                1 |                192885    |                 8036.86 |
|            2003 | Over 7 Days                |                1 |                175335    |                 7305.64 |
|            2004 | Over 7 Days                |                1 |                175320    |                 7305    |
|            2005 | Over 7 Days                |                2 |                175418    |                 7309.07 |
|            2017 | Over 7 Days                |                1 |                 66053.4  |                 2752.22 |
|            2020 | Over 7 Days                |                1 |                 35298.3  |                 1470.76 |
|            2021 | Over 7 Days                |                2 |                 19675.4  |                  819.81 |
|            2022 | Over 7 Days                |               24 |                  4321.29 |                  180.05 |
|            2022 | 1-3 Days                   |                2 |                    45.23 |                    1.88 |
|            2022 | Same Day / Within 24 Hours |                1 |                    14.58 |                    0.61 |
|            2023 | Same Day / Within 24 Hours |             1437 |                     2.87 |                    0.12 |
|            2023 | 1-3 Days                   |              145 |                    44.47 |                    1.85 |
|            2023 | Over 7 Days                |              142 |                  1855.48 |                   77.31 |
|            2023 | 4-7 Days                   |               92 |                   106.11 |                    4.42 |
|            2023 | Unknown                    |                2 |                   nan    |                  nan    |
|            2024 | Same Day / Within 24 Hours |             1607 |                     2.51 |                    0.1  |
|            2024 | Over 7 Days                |              134 |                  1311.32 |                   54.64 |
|            2024 | 1-3 Days                   |              116 |                    46.69 |                    1.95 |
|            2024 | 4-7 Days                   |               83 |                   112.33 |                    4.68 |
|            2024 | Unknown                    |                7 |                   nan    |                  nan    |
|            2025 | Same Day / Within 24 Hours |             1570 |                     1.94 |                    0.08 |
|            2025 | 1-3 Days                   |              104 |                    43.73 |                    1.82 |
|            2025 | Over 7 Days                |              101 |                   736.31 |                   30.68 |
|            2025 | 4-7 Days                   |               77 |                   112.76 |                    4.7  |
|            2025 | Unknown                    |                6 |                   nan    |                  nan    |

## Academic Period Summary

|   occurred_year | occurred_semester_period   |   incident_count |
|----------------:|:---------------------------|-----------------:|
|            2002 | Summer                     |                1 |
|            2003 | Fall Semester              |                1 |
|            2004 | Spring Semester            |                1 |
|            2005 | Fall Semester              |                2 |
|            2017 | Winter Break               |                1 |
|            2020 | Spring Semester            |                1 |
|            2021 | Fall Semester              |                2 |
|            2022 | Fall Semester              |               21 |
|            2022 | Winter Break               |                2 |
|            2022 | Summer                     |                2 |
|            2022 | Spring Semester            |                2 |
|            2023 | Fall Semester              |              771 |
|            2023 | Spring Semester            |              660 |
|            2023 | Summer                     |              290 |
|            2023 | Winter Break               |               97 |
|            2024 | Spring Semester            |              749 |
|            2024 | Fall Semester              |              722 |
|            2024 | Summer                     |              373 |
|            2024 | Winter Break               |              103 |
|            2025 | Fall Semester              |              816 |
|            2025 | Spring Semester            |              641 |
|            2025 | Summer                     |              317 |
|            2025 | Winter Break               |               84 |

## Yearly Arrest Summary

|   arrested_year |   arrest_count |
|----------------:|---------------:|
|            2023 |            300 |
|            2024 |            435 |
|            2025 |            440 |

## Arrest Charge Category Summary

|   arrested_year | charge_category              |   arrest_count |   alcohol_related_count |   drug_related_count |   theft_related_count |   arrest_percentage |
|----------------:|:-----------------------------|---------------:|------------------------:|---------------------:|----------------------:|--------------------:|
|            2023 | DUI / Impaired Driving       |             96 |                      96 |                   96 |                    96 |               32    |
|            2023 | Theft / Property             |             83 |                       0 |                   83 |                    83 |               27.67 |
|            2023 | Public Order                 |             42 |                       0 |                    0 |                     0 |               14    |
|            2023 | Assault / Violence           |             14 |                      14 |                    0 |                     0 |                4.67 |
|            2023 | Property Damage              |             11 |                       0 |                    0 |                     0 |                3.67 |
|            2023 | Burglary / Robbery           |             11 |                       0 |                   11 |                    11 |                3.67 |
|            2023 | Alcohol / Public Consumption |             11 |                      11 |                    0 |                     0 |                3.67 |
|            2023 | Drug / CDS                   |             10 |                       0 |                   10 |                     0 |                3.33 |
|            2023 | Sex Offense                  |              8 |                       0 |                    8 |                     0 |                2.67 |
|            2023 | Fraud / Identity             |              8 |                       0 |                    0 |                     0 |                2.67 |
|            2023 | Weapon-Related               |              4 |                       4 |                    4 |                     4 |                1.33 |
|            2023 | Traffic / Vehicle            |              1 |                       1 |                    0 |                     0 |                0.33 |
|            2023 | No Charge / Suspicion        |              1 |                       0 |                    1 |                     1 |                0.33 |
|            2024 | DUI / Impaired Driving       |            138 |                     138 |                  138 |                   138 |               31.72 |
|            2024 | Theft / Property             |            130 |                       0 |                  130 |                   130 |               29.89 |
|            2024 | Public Order                 |             44 |                       0 |                    0 |                     0 |               10.11 |
|            2024 | Property Damage              |             33 |                       0 |                    0 |                     0 |                7.59 |
|            2024 | Alcohol / Public Consumption |             23 |                      23 |                    0 |                     0 |                5.29 |
|            2024 | Sex Offense                  |             15 |                       0 |                   15 |                     0 |                3.45 |
|            2024 | Drug / CDS                   |             13 |                       0 |                   13 |                     0 |                2.99 |
|            2024 | Assault / Violence           |             11 |                      11 |                    0 |                     0 |                2.53 |
|            2024 | Fraud / Identity             |             10 |                       0 |                    0 |                     0 |                2.3  |
|            2024 | Burglary / Robbery           |              7 |                       0 |                    7 |                     7 |                1.61 |
|            2024 | Weapon-Related               |              4 |                       4 |                    4 |                     4 |                0.92 |
|            2024 | Traffic / Vehicle            |              4 |                       4 |                    0 |                     0 |                0.92 |
|            2024 | No Charge / Suspicion        |              3 |                       0 |                    3 |                     3 |                0.69 |
|            2025 | DUI / Impaired Driving       |            186 |                     186 |                  186 |                   186 |               42.27 |
|            2025 | Theft / Property             |            109 |                       0 |                  109 |                   109 |               24.77 |
|            2025 | Alcohol / Public Consumption |             32 |                      32 |                    0 |                     0 |                7.27 |
|            2025 | Public Order                 |             31 |                       0 |                    0 |                     0 |                7.05 |

## Arrest Demographic Summary

|   arrested_year | race                             | sex     | age_group   |   arrest_count |   arrest_percentage |
|----------------:|:---------------------------------|:--------|:------------|---------------:|--------------------:|
|            2023 | Black                            | Male    | Unknown     |            152 |               50.67 |
|            2023 | White                            | Male    | Unknown     |             84 |               28    |
|            2023 | White                            | Female  | Unknown     |             17 |                5.67 |
|            2023 | Asian                            | Male    | Unknown     |             12 |                4    |
|            2023 | Black                            | Female  | Unknown     |             12 |                4    |
|            2023 | Unknown                          | Unknown | Unknown     |             11 |                3.67 |
|            2023 | Unknown                          | Male    | Unknown     |              7 |                2.33 |
|            2023 | Asian                            | Female  | Unknown     |              3 |                1    |
|            2023 | American Indian/Alaskan          | Male    | Unknown     |              2 |                0.67 |
|            2024 | White                            | Male    | Unknown     |            208 |               47.82 |
|            2024 | Black                            | Male    | Unknown     |            156 |               35.86 |
|            2024 | White                            | Female  | Unknown     |             18 |                4.14 |
|            2024 | Asian                            | Male    | Unknown     |             15 |                3.45 |
|            2024 | Black                            | Female  | Unknown     |             13 |                2.99 |
|            2024 | Unknown                          | Unknown | Unknown     |             11 |                2.53 |
|            2024 | Asian                            | Female  | Unknown     |              7 |                1.61 |
|            2024 | Unknown                          | Male    | Unknown     |              4 |                0.92 |
|            2024 | Unknown                          | Female  | Unknown     |              2 |                0.46 |
|            2024 | Native Hawaiian/Pacific Islander | Male    | Unknown     |              1 |                0.23 |
|            2025 | White                            | Male    | Unknown     |            207 |               47.05 |
|            2025 | Black                            | Male    | Unknown     |            168 |               38.18 |
|            2025 | White                            | Female  | Unknown     |             18 |                4.09 |
|            2025 | Asian                            | Male    | Unknown     |             17 |                3.86 |
|            2025 | Black                            | Female  | Unknown     |             15 |                3.41 |
|            2025 | Unknown                          | Unknown | Unknown     |              9 |                2.05 |
|            2025 | Unknown                          | Male    | Unknown     |              4 |                0.91 |
|            2025 | American Indian/Alaskan          | Male    | Unknown     |              1 |                0.23 |
|            2025 | Native Hawaiian/Pacific Islander | Male    | Unknown     |              1 |                0.23 |

## Monthly Arrest Trends

|   arrested_year |   arrested_month | arrested_month_name   |   arrest_count |
|----------------:|-----------------:|:----------------------|---------------:|
|            2023 |                1 | January               |             16 |
|            2023 |                2 | February              |             32 |
|            2023 |                3 | March                 |             37 |
|            2023 |                4 | April                 |             23 |
|            2023 |                5 | May                   |             34 |
|            2023 |                6 | June                  |             19 |
|            2023 |                7 | July                  |             43 |
|            2023 |                8 | August                |             13 |
|            2023 |                9 | September             |             17 |
|            2023 |               10 | October               |             20 |
|            2023 |               11 | November              |             30 |
|            2023 |               12 | December              |             16 |
|            2024 |                1 | January               |             20 |
|            2024 |                2 | February              |             45 |
|            2024 |                3 | March                 |             40 |
|            2024 |                4 | April                 |             36 |
|            2024 |                5 | May                   |             27 |
|            2024 |                6 | June                  |             24 |
|            2024 |                7 | July                  |             40 |
|            2024 |                8 | August                |             58 |
|            2024 |                9 | September             |             23 |
|            2024 |               10 | October               |             39 |
|            2024 |               11 | November              |             28 |
|            2024 |               12 | December              |             55 |
|            2025 |                1 | January               |             42 |
|            2025 |                2 | February              |             25 |
|            2025 |                3 | March                 |             34 |
|            2025 |                4 | April                 |             41 |
|            2025 |                5 | May                   |             38 |
|            2025 |                6 | June                  |             16 |

## Incident Arrest Match Summary

|   incident_source_year |   has_matching_arrest |   incident_count |   incident_percentage |
|-----------------------:|----------------------:|-----------------:|----------------------:|
|                   2023 |                     1 |              313 |                 16.92 |
|                   2023 |                     0 |             1537 |                 83.08 |
|                   2024 |                     1 |              420 |                 20.8  |
|                   2024 |                     0 |             1599 |                 79.2  |
|                   2025 |                     1 |              370 |                 19.34 |
|                   2025 |                     0 |             1543 |                 80.66 |

## Matched Incident Charge Summary

|   incident_source_year | charge_category              |   matched_incident_count |   avg_hours_from_incident_to_arrest |
|-----------------------:|:-----------------------------|-------------------------:|------------------------------------:|
|                   2023 | DUI / Impaired Driving       |                       96 |                                0.28 |
|                   2023 | Theft / Property             |                       77 |                             3524.34 |
|                   2023 | Public Order                 |                       44 |                              975.25 |
|                   2023 | Property Damage              |                       23 |                             2250.65 |
|                   2023 | Assault / Violence           |                       15 |                              637.51 |
|                   2023 | Drug / CDS                   |                       12 |                             1172.41 |
|                   2023 | Alcohol / Public Consumption |                       11 |                                0.18 |
|                   2023 | Sex Offense                  |                       10 |                             1173.91 |
|                   2023 | Fraud / Identity             |                       10 |                             1170.56 |
|                   2023 | Burglary / Robbery           |                        8 |                             1881.28 |
|                   2023 | Weapon-Related               |                        5 |                             3893.93 |
|                   2023 | Traffic / Vehicle            |                        1 |                             4421.23 |
|                   2023 | No Charge / Suspicion        |                        1 |                                0.05 |
|                   2024 | Theft / Property             |                      140 |                             2550.9  |
|                   2024 | DUI / Impaired Driving       |                      128 |                               13.22 |
|                   2024 | Public Order                 |                       42 |                              854.73 |
|                   2024 | Property Damage              |                       26 |                             2529.8  |
|                   2024 | Alcohol / Public Consumption |                       23 |                               -0.4  |
|                   2024 | Sex Offense                  |                       13 |                              372.52 |
|                   2024 | Drug / CDS                   |                       11 |                              993.54 |
|                   2024 | Assault / Violence           |                       11 |                             1745.96 |
|                   2024 | Fraud / Identity             |                       10 |                             1893.85 |
|                   2024 | Burglary / Robbery           |                        6 |                             2225.95 |
|                   2024 | Weapon-Related               |                        4 |                              406.77 |
|                   2024 | Traffic / Vehicle            |                        3 |                              755.54 |
|                   2024 | No Charge / Suspicion        |                        3 |                                0.46 |
|                   2025 | DUI / Impaired Driving       |                      177 |                                0.52 |
|                   2025 | Theft / Property             |                       67 |                             1155.96 |
|                   2025 | Alcohol / Public Consumption |                       31 |                               -0.74 |
|                   2025 | Public Order                 |                       27 |                              635.76 |

## Data Quality Review

|   source_year | record_type      |   total_records |   invalid_case_number_count |   invalid_datetime_count |   invalid_reported_datetime_count |   missing_or_invalid_detail_count |
|--------------:|:-----------------|----------------:|----------------------------:|-------------------------:|----------------------------------:|----------------------------------:|
|          2023 | Arrest Records   |             300 |                           0 |                        0 |                               nan |                                 0 |
|          2023 | Incident Records |            1813 |                           0 |                        0 |                                 0 |                                 2 |
|          2024 | Arrest Records   |             435 |                           0 |                        0 |                               nan |                                 0 |
|          2024 | Incident Records |            1960 |                           0 |                        0 |                                 0 |                                 7 |
|          2025 | Arrest Records   |             440 |                           0 |                        0 |                               nan |                                 0 |
|          2025 | Incident Records |            1886 |                           0 |                        0 |                                 0 |                                 6 |
