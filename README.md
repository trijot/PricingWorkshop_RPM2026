# PricingWorkshop_RPM2026
This is the Repository to be used for the PricingWorkshop for March RPM 2026
we all can access files from here, make changes to the files and demonstrate how we use Git to manage our project.


| Segment | Description | Contributors |
|--------|-------------|--------------|
| Welcome & Framing | Introduction, objectives, agenda overview, speaker introductions | Wasim |
| Session 1 | GitHub introduction, version control basics, tool access, validation, reading/writing workflows, establishing a single source of truth | Try / Sean |
| Session 2 | On-leveling techniques, exposure extensions, waterfall concepts | Try / WTW |
| Session 3 | Mix change analysis, GBM overview (data & assumptions), RADAR integration | WTW |
| Break | — | — |
| Session 4 | Claims development to ultimate: CDF tools, Power Pivot, curve fitting, macros, Clark method and other Part 7 techniques | Sean / Try |
| Session 5 | Territory smoothing and relativity analysis | WTW |
| Collaborative Exercise | Small-group case study; parallel implementation using RADAR and Python | Sean (All participate) |
| Wrap-Up & Takeaways | Key takeaways, Q&A, feedback collection | Wasim |


# DataFile - Dictionary

| Column              | Type    |   Unique_Values |   Missing_% | Example_Values                                                                  |
|:--------------------|:--------|----------------:|------------:|:--------------------------------------------------------------------------------|
| Affinity_Scheme     | object  |               2 |           0 | No, Yes                                                                         |
| Agency              | int64   |              50 |           0 | 30, 10, 48, 34, 19                                                              |
| Claims_free_years   | object  |               5 |           0 | 3 years, 4+ years, 1 years, 2 years, 0 years                                    |
| COLL_Claim_Count    | int64   |               2 |           0 | 0, 1                                                                            |
| COLL_Loss           | int64   |            2644 |           0 | 0, 4336, 1356, 2348, 3080                                                       |
| ConversionIndicator | int64   |               2 |           0 | 1, 0                                                                            |
| Convictions         | object  |               2 |           0 | Yes, No                                                                         |
| Driver_Training     | object  |               2 |           0 | No, Yes                                                                         |
| Driving_Restriction | object  |               3 |           0 | Any, IOD, Named                                                                 |
| Exposure            | int64   |               1 |           0 | 1                                                                               |
| Good_Student        | object  |               2 |           0 | No, Yes                                                                         |
| Homeowner           | object  |               3 |           0 | No, Yes, Unknown                                                                |
| Loss_Year           | int64   |               3 |           0 | 2020, 2021, 2022                                                                |
| Marital_Status      | object  |               2 |           0 | Married, Single                                                                 |
| Multi_Car           | object  |               2 |           0 | Yes, No                                                                         |
| Passive_Restraint   | object  |               2 |           0 | Yes, No                                                                         |
| PolicyEffectiveDate | object  |          366592 |           0 | 4/18/2020 12:33, 8/7/2019 3:22, 7/5/2019 1:31, 12/23/2019 7:17, 7/11/2019 18:18 |
| Policyholder_Age    | int64   |              60 |           0 | 46, 47, 48, 49, 50                                                              |
| Policyholder_Sex    | object  |               2 |           0 | Female, Male                                                                    |
| PolicyVehicleKey    | int64   |          293700 |           0 | 753562, 853562, 953562, 1053562, 1153562                                        |
| Sample_Factor       | int64   |              10 |           0 | 7, 3, 6, 9, 8                                                                   |
| Tenure              | int64   |              11 |           0 | 9, 1, 2, 6, 0                                                                   |
| TNC_Coverage        | object  |               2 |           0 | Yes, No                                                                         |
| Vehicle_Age         | int64   |              22 |           0 | 6, 11, 3, 4, 5                                                                  |
| Vehicle_Symbol      | float64 |              20 |           0 | 7.0, 4.0, 5.0, 3.0, 6.0                                                         |
| Vehicle_Use         | object  |               3 |           0 | Pleasure, Commute, Business Use                                                 |
| Vehicle_Value       | int64   |              16 |           0 | 4, 5, 2, 6, 7                                                                   |
| Vendor_Mileage      | float64 |              15 |           0 | 10000.0, 15000.0, 4000.0, 9000.0, 11000.0                                       |
| Vendor_VHS          | int64   |             601 |           0 | 503, 687, 473, 947, 930                                                         |
| VolXs               | int64   |               5 |           0 | 1, 3, 5, 4, 2                                                                   |
| Years_Insured       | int64   |              10 |           0 | 0, 2, 3, 1, 4                                                                   |
| Zipcode             | int64   |            1114 |           0 | 93203, 91345, 93291, 93662, 95076                                               |
| State               | object  |               5 |           0 | IL, AZ, OH, CA, NJ                                                              |
| Current Premium     | float64 |           27229 |           0 | 336.64, 0.0, 209.31, 287.84, 304.46                                             |
