/****** Object:  View [dbo].[discharge_data_view_demographics_test]    Script Date: 3/3/2026 3:28:45 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[discharge_data_view_demographics_test]
AS
WITH 
-- 1. Combine all years of Demographics
All_Demographics AS (
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2018 AS year, zip FROM dbo.Outpatient_Demographics_2018_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2019 AS year, zip FROM dbo.Outpatient_Demographics_2019_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2020 AS year, zip FROM dbo.Outpatient_Demographics_2020_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2021 AS year, zip FROM dbo.Outpatient_Demographics_2021_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2022 AS year, zip FROM dbo.Outpatient_Demographics_2022_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2023 AS year, zip FROM dbo.Outpatient_Demographics_2023_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2024 AS year, zip FROM dbo.Outpatient_Demographics_2024_NO_PII UNION
    SELECT record_id, hnum, Age_Group, sex, race_ethnicity, 2025 AS year, zip FROM dbo.Outpatient_Demographics_2025_NO_PII
),

-- 2. Combine all years of Diagnoses
All_DX AS (
    SELECT record_id, 2018 AS year FROM dbo.Outpatient_DX_2018 UNION
    SELECT record_id, 2019 AS year FROM dbo.Outpatient_DX_2019 UNION
    SELECT record_id, 2020 AS year FROM dbo.Outpatient_DX_2020 UNION
    SELECT record_id, 2021 AS year FROM dbo.Outpatient_DX_2021 UNION
    SELECT record_id, 2022 AS year FROM dbo.Outpatient_DX_2022 UNION
    SELECT record_id, 2023 AS year FROM dbo.Outpatient_DX_2023 UNION
    SELECT record_id, 2024 AS year FROM dbo.Outpatient_DX_2024 UNION
    SELECT record_id, 2025 AS year FROM dbo.Outpatient_DX_2025
),

-- 3. Map the raw demographics to the Crosswalk and Race code tables
Mapped_Demographics AS (
    SELECT 
        d.record_id, 
        cw.Facility_By_County_County AS county, 
        cw.City AS city, 
        d.zip, 
        d.Age_Group AS age_group, 
        CASE 
            WHEN d.sex = 1 THEN 'male' 
            WHEN d.sex = 2 THEN 'female' 
        END AS sex, 
        rc.Description AS race_ethnicity, 
        d.year
    FROM All_Demographics d
    INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes rc 
        ON d.race_ethnicity = rc.Code 
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] cw 
        ON d.hnum = cw.hnum
)

-- 4. Final Output: Clean up NULLs and apply formatting logic
SELECT 
    COALESCE(dx.record_id, demo.record_id) AS record_id, 
    COALESCE(demo.county, 'Unknown') AS county, 
    COALESCE(demo.city, 'Unknown') AS city, 
    COALESCE(CAST(demo.zip AS varchar), 'Unknown') AS zip, 
    CASE 
        WHEN demo.zip IS NULL OR demo.zip = '99999' OR demo.zip = '' THEN 'Unknown' 
        WHEN demo.zip >= '96701' AND demo.zip <= '96898' THEN 'Resident' 
        ELSE 'Non-resident' 
    END AS hawaii_residency, 
    COALESCE(demo.age_group, 'Unknown') AS age_group, 
    CASE 
        WHEN demo.sex = 'male' THEN 'Male' 
        WHEN demo.sex = 'female' THEN 'Female' 
        ELSE 'Unknown' 
    END AS sex, 
    COALESCE(demo.race_ethnicity, 'Unknown') AS race_ethnicity,
    COALESCE(dx.year, demo.year) AS year
FROM Mapped_Demographics demo
RIGHT OUTER JOIN All_DX dx 
    ON demo.record_id = dx.record_id;
GO


