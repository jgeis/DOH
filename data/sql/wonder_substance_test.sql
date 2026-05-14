/****** Object:  View [dbo].[wonder_substance]    Script Date: 4/24/2026 6:05:10 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

/*remove Kalawao county (no data and inconsistent with other datasets)
Note methamphetamine translation, any other additions?
What drugs do we want to keep, way too many, should we just strip out suppressed values?*/
CREATE VIEW [dbo].[wonder_substance_test]
AS
WITH 
-- 1. Get County-level data
County_Data AS (
    SELECT 
        Year AS year, 
        SUBSTRING([Occurrence County], 1, CHARINDEX(' ', [Occurrence County]) - 1) AS county,
        CASE 
            WHEN [Multiple Cause of Death Code] = 'T40.4' THEN 'Fentanyl and other synthetic narcotics' 
            WHEN [Multiple Cause of Death Code] = 'T43.6' THEN 'Methamphetamine and other psychostimulants with abuse potential' 
            ELSE [Multiple Cause of Death] 
        END AS substance,
        COALESCE(Deaths, 0) AS deaths
    FROM dbo.['County, Year, Substance$']
    WHERE Notes <> 'Total' 
      AND [Occurrence County] <> 'Kalawao County, HI'
),

-- 2. Get State-level data
State_Data AS (
    SELECT 
        LEFT(Year, 4) AS year, 
        'Statewide' AS county,
        CASE 
            WHEN [Multiple Cause of Death Code] = 'T40.4' THEN 'Fentanyl and other synthetic narcotics' 
            WHEN [Multiple Cause of Death Code] = 'T43.6' THEN 'Methamphetamine and other psychostimulants with abuse potential' 
            ELSE [Multiple Cause of Death] 
        END AS substance,
        COALESCE(Deaths, 0) AS deaths
    FROM dbo.['State, Year, Substance$']
    WHERE Notes <> 'Total' 
      AND Deaths IS NOT NULL
),

-- 3. Combine County and State data
All_Substances AS (
    SELECT year, county, substance, deaths FROM County_Data
    UNION
    SELECT year, county, substance, deaths FROM State_Data
),

-- 4. Get a distinct list of mapped substances
Substances_With_Value AS (
    SELECT DISTINCT 
        CASE 
            WHEN [Multiple Cause of Death Code] = 'T40.4' THEN 'Fentanyl and other synthetic narcotics' 
            WHEN [Multiple Cause of Death Code] = 'T43.6' THEN 'Methamphetamine and other psychostimulants with abuse potential' 
            ELSE [Multiple Cause of Death] 
        END AS substance
    FROM dbo.['State, Year, Substance$']
    WHERE Notes <> 'Total' 
      AND Deaths IS NOT NULL
)

-- 5. Final Output and top-level mappings
SELECT 
    LEFT(a.year, 4) AS Year, 
    a.county, 
    CASE 
        WHEN a.substance IN (
            'Other and unspecified antidepressants', 
            'Other and unspecified drugs, medicaments and biological substances', 
            'Antiallergic and antiemetic drugs', 
            'Other and unspecified antipsychotics and neuroleptics', 
            'Other antiepileptic and sedative-hypnotic drugs'
        ) THEN 'Other' 
        WHEN a.substance = 'Methadone' THEN 'Other opioids' 
        ELSE a.substance 
    END AS Substance, 
    a.deaths
FROM All_Substances a
RIGHT OUTER JOIN Substances_With_Value s 
    ON a.substance = s.substance
WHERE a.deaths > 0;
GO


