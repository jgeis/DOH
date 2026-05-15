/****** Object:  View [dbo].[discharge_data_view_demographics]    Script Date: 3/3/2026 3:28:45 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[discharge_data_view_demographics]
AS
SELECT COALESCE (dx.record_id, demo.record_id) AS record_id, 
			 CASE WHEN county IS NULL THEN 'Unknown' ELSE county END AS county, 
			 CASE WHEN city IS NULL THEN 'Unknown' ELSE city END AS city, 
			 CASE WHEN zip IS NULL THEN 'Unknown' ELSE CAST(zip AS varchar) END AS zip, 
             CASE WHEN zip IS NULL OR zip = 99999 OR zip = '' THEN 'Unknown' WHEN zip >= 96701 AND zip <= 96898 THEN 'Resident' ELSE 'Non-resident' END AS hawaii_residency, 
			 CASE WHEN age_group IS NULL THEN 'Unknown' ELSE age_group END AS age_group, 
             CASE WHEN sex = 'male' THEN 'Male' WHEN sex = 'female' THEN 'Female' ELSE 'Unknown' END AS sex, 
			 CASE WHEN race_ethnicity IS NULL THEN 'Unknown' ELSE race_ethnicity END AS race_ethnicity,
			 COALESCE (dx.year, demo.year) AS year
FROM   (SELECT discharge_demographics.record_id, dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26].Facility_By_County_County AS county, dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26].City AS city, discharge_demographics.zip, 
                           discharge_demographics.Age_Group AS age_group, CASE WHEN sex = 1 THEN 'male' WHEN sex = 2 THEN 'female' END AS sex, dbo.Laulima_Data_Alliance_Race_Codes.Description AS race_ethnicity, discharge_demographics.year
             FROM    (SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2018 AS year, zip
                           FROM    dbo.Outpatient_Demographics_2018_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2019 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2019_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2020 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2020_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2021 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2021_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2022 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2022_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2023 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2023_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2024 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2024_NO_PII
                           UNION
                           SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2025 AS year, zip
                           FROM   dbo.Outpatient_Demographics_2025_NO_PII) AS discharge_demographics INNER JOIN
                           dbo.Laulima_Data_Alliance_Race_Codes ON discharge_demographics.race_ethnicity = Laulima_Data_Alliance_Race_Codes.Code INNER JOIN
                           dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] ON discharge_demographics.hnum = [outpt_facility_hnum_county_crosswalk_2022-08-26].hnum) AS demo RIGHT OUTER JOIN
                 (SELECT record_id, 2018 AS year
                 FROM    dbo.Outpatient_DX_2018
                 UNION
                 SELECT record_id, 2019 AS year
                 FROM   dbo.Outpatient_DX_2019
                 UNION
                 SELECT record_id, 2020 AS year
                 FROM   dbo.Outpatient_DX_2020
                 UNION
                 SELECT record_id, 2021 AS year
                 FROM   dbo.Outpatient_DX_2021
                 UNION
                 SELECT record_id, 2022 AS year
                 FROM   dbo.Outpatient_DX_2022
                 UNION
                 SELECT record_id, 2023 AS year
                 FROM   dbo.Outpatient_DX_2023
                 UNION
                 SELECT record_id, 2024 AS year
                 FROM   dbo.Outpatient_DX_2024
                 UNION
                 SELECT record_id, 2025 AS year
                 FROM   dbo.Outpatient_DX_2025) AS dx ON demo.record_id = dx.record_id
GO


