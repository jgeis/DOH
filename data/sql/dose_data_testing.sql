--19,323
select count(distinct record_id) from dbo.Outpatient_DX_2023;

-- 14,610
select count(distinct record_id) from dbo.Outpatient_Demographics_2023_NO_PII;

-- 13,732
SELECT count(distinct dose.record_id) 
FROM 
    dbo.Outpatient_DX_2023 dose
	inner join dbo.Outpatient_Demographics_2023_NO_PII demo 
		ON dose.record_id = demo.record_id
WHERE zip >= 96701 AND zip <= 96898;

-- 14,610
SELECT count(distinct dose.record_id) 
FROM 
    dbo.Outpatient_DX_2023 dose
	inner join dbo.Outpatient_Demographics_2023_NO_PII demo 
		ON dose.record_id = demo.record_id;

-- 19 records, limited to Hawaii
select distinct city from dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26];

-- 14,604
SELECT count(distinct dose.record_id) 
FROM 
    dbo.Outpatient_DX_2023 dose
	INNER JOIN dbo.Outpatient_Demographics_2023_NO_PII demo 
		ON dose.record_id = demo.record_id
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum = facility.hnum;

-- 14,604
SELECT count(distinct dose.record_id) 
FROM 
    dbo.Outpatient_DX_2023 dose  -- limit to 2023
	INNER JOIN dbo.Outpatient_Demographics_2023_NO_PII demo 
		ON dose.record_id = demo.record_id
	-- limit to hawaii facilities
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum = facility.hnum
    INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes race
		ON demo.race_ethnicity = race.Code;

-- 3,368
SELECT COUNT(DISTINCT dx.record_id)
FROM dbo.Outpatient_DX_2023 dx
	INNER JOIN dbo.Outpatient_Demographics_2023_NO_PII demo 
		ON dx.record_id = demo.record_id
	-- limit to hawaii facilities
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum = facility.hnum
WHERE EXISTS (
    SELECT 1 
    FROM (VALUES 
        (dx_1), (dx_2), (dx_3), (dx_4), (dx_5), 
        (dx_6), (dx_7), (dx_8), (dx_9), (dx_10), 
        (dx_11), (dx_12), (dx_13), (dx_14), (dx_15), 
        (dx_16), (dx_17), (dx_18), (dx_19), (dx_20), 
        (dx_21), (dx_22), (dx_23), (dx_24), (dx_25)
    ) AS v(diagnosis)
    WHERE diagnosis LIKE 'T%'
);

SELECT 
    s.name AS SchemaName,
    t.name AS TableName,
    p.name AS Creator,
    t.create_date AS CreationDate
FROM 
    sys.tables t
INNER JOIN 
    sys.schemas s ON t.schema_id = s.schema_id
INNER JOIN 
    sys.database_principals p ON t.principal_id = p.principal_id
WHERE 
    t.name = 'Outpatient_DX_2023'
    AND s.name = 'dbo';




--------------------
-- 7,102
SELECT count(distinct record_id) FROM dbo.dose_data;
SELECT count(distinct record_id) FROM dbo.dose_data where diagnosis!='All Drugs';

select distinct diagnosis from dbo.dose_data;

-- 172,720
SELECT count(distinct record_id) FROM dbo.discharge_data_view_demographics;
------------------------------
----- 2023 -----
-- spotcheck numbers:
--    total = 1313	
--    ED Discharge = 971
--    In-Patient Hospitalization = 342

-- spotcheck number/dose_data/dose_data_test

-- total number of records (not discharges) for 2023 and 2024
-- 2023: 1313/1476/1457  -- dose_data and dose_data_test records don't match due to the Methamphetamine records, omit those and they're fine
-- 2024: 1278/1284/1258  -- dose_data and dose_data_test records don't match due to the Methamphetamine records, omit those and they're fine
SELECT demo.year, count(dose.record_id) 
FROM 
    dbo.dose_data_test dose
	inner join discharge_data_view_demographics demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023 or demo.year = 2024
GROUP BY demo.year;

-- total number of discharges for 2023 and 2024
-- 2023: 971/992/992
-- 2024: 818/878/878
SELECT demo.year, count(distinct dose.record_id) 
FROM 
    dbo.dose_data_test dose
	inner join discharge_data_view_demographics_test demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023 or demo.year = 2024
GROUP BY demo.year;


-- 14,604
SELECT count(DISTINCT dx.record_id)
FROM dbo.Outpatient_DX_2023 dx
	INNER JOIN dbo.Outpatient_Demographics_2023_NO_PII demo on dx.record_id = demo.record_id
	INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility ON demo.hnum = facility.hnum
	INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes rc ON demo.race_ethnicity = rc.Code ;
--select * from dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26];

-- sex
-- 2023	Female	435/338/338
-- 2023	Male	536/407/407
-- 2023	Unknown	???/247/247
-- 2024	Female	361/390/390
-- 2024	Male	457/488/488
SELECT demo.year, demo.sex, count(distinct dose.record_id)
FROM 
    dbo.dose_data_test dose
	inner join discharge_data_view_demographics_test demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023 or demo.year = 2024
GROUP BY demo.year, demo.sex
ORDER BY demo.year, demo.sex;

-- returned 4,713 rows, all in 2023.  Zero rows for 2024. 
-- Find patients with Diagnoses but NO Demographics in 2023
SELECT DISTINCT 
    dx.record_id, 
    2023 AS incident_year,
    'Missing Demographics' AS issue_type
FROM dbo.Outpatient_DX_2023 dx
	LEFT OUTER JOIN (
	select demo.record_id from dbo.Outpatient_Demographics_2023_NO_PII demo 
	INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum != facility.hnum) dm
	on dx.record_id = dm.record_id
WHERE dm.record_id IS NULL
ORDER BY incident_year, record_id;

select count(*) from dbo.Outpatient_Demographics_2023_NO_PII demo 
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum != facility.hnum;
 
select distinct(facility.Facility_Name) from dbo.Outpatient_Demographics_2023_NO_PII demo 
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum != facility.hnum;

-- county
-- 2023, Hawaii: 138/114/114
-- 2023, Honolulu: 578/455/455
-- 2023, Kauai: 76/70/70
-- 2023, Maui: 116/106/106
-- 2023, Outside Hawaii: 44/?/?
-- 2023, Unknown: 19/247/247
-- 2024, Hawaii: 131/137/137
-- 2024, Honolulu: 488/526/526
-- 2024, Kauai: 77/88/88
-- 2024, Maui: 106/127/127
-- 2025, Outside Hawaii: 16/?/?
-- 2024, Unknown: 0/0/0
SELECT demo.year, demo.county, count(distinct dose.record_id)
FROM 
    dbo.dose_data dose
	inner join discharge_data_view_demographics_test demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023 or demo.year = 2024
group by demo.year, demo.county
order by demo.year, demo.county;

-- categories they gave me for ethnicity spotchecks, don't know if I'm grouping correctly
--White-NH
--Black-NH
--AIAN-NH American Indian or Alaska Native
--Asian-NH
--NHOPI-NH native hawaiian or pacific islander
--Hispanic

-- ethnicity issues:
--Items ONLY in 2023:
--    Guamanian or Chamorro
--    Unknown (Note: The first list contains both "Unknown" and "Unknown/Refused" as separate entries, while the second list only contains "Unknown/Refused")
--Items ONLY in 2024:
--    Alaska Native
--    Arab/Arabian
--    Asian Indian
--    Tahitian
-------------
-- 2023 White 395/299/299
-- 2023 Black 19/13/13
-- 2023 AIAN 6/5/5
-- 2023 Asian 243/193/193
-- 2023 NHOPI 215/167/167
-- 2023 Hispanic 43/31/31
--------------
-- 2024 White 303/337/337
-- 2024 Black 32/33/33
-- 2024 AIAN 7/9/9
-- 2024 Asian 208/220/220
-- 2024 NHOPI 200/208/208
-- 2024 Hispanic 27/28/28
SELECT demo.year, demo.race_category, count(distinct dose.record_id)
FROM 
    dbo.dose_data_test dose
	inner join discharge_data_view_demographics_test demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023 or demo.year = 2024
group by demo.year, demo.race_category
order by demo.year, demo.race_category;


-- diagnosis
-- 2023	All Drugs ???/992/992  -- not a number that compares to anything in the spotcheck spreadsheet
-- 2023	Benzodiazepine	59/60/60
-- 2023	Cocaine	17/17/17
-- 2023	Fentanyl 15/15/15
-- 2023	Heroin	37/37/37
-- 2023	Methamphetamine	1/20/1
-- 2023	Opioids	289/289/289
-- 2023	Stimulants	46/46/46
------------------------
-- 2024	All Drugs ???/878/878  -- not a number that compares to anything in the spotcheck spreadsheet
-- 2024	Benzodiazepine 27/33/33
-- 2024	Cocaine 10/10/10
-- 2024	Fentanyl 19/20/20
-- 2024	Heroin 11/11/11
-- 2024	Methamphetamine 3/29/3 (meth_icd10data and [amphetam_uu])
-- 2024	Opioids 240/253/253  ([all_opioid_uu] and [fentanyl_uu])
-- 2024	Stimulants 48/50/50  ([stimulant_uu], meth_icd10data, and [cocaine_uu])
SELECT demo.year, dose.diagnosis, count(dose.record_id) 
FROM 
    dbo.dose_data_test dose
	inner join discharge_data_view_demographics_test demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023 or demo.year = 2024
GROUP BY demo.year, dose.diagnosis
ORDER BY demo.year, dose.diagnosis;

---- ??/992/992 -- not a number that compares to anything in the spotcheck spreadsheet
--	SELECT count(dose.record_id) 
--	FROM 
--		dbo.dose_data dose
--		inner join discharge_data_view_demographics_test demo 
--			ON dose.record_id = demo.record_id
--	WHERE
--		demo.year = 2023
--		AND dose.diagnosis='All Drugs';

---- 59/60/60
--SELECT count(dose.record_id) 
--FROM 
--    dbo.dose_data dose
--	inner join discharge_data_view_demographics demo 
--		ON dose.record_id = demo.record_id
--WHERE
--	demo.year = 2023
--	AND dose.diagnosis='Benzodiazepine';

---- 46/46/46
--SELECT count(dose.record_id) 
--FROM 
--    dbo.dose_data_test dose
--	inner join discharge_data_view_demographics demo 
--		ON dose.record_id = demo.record_id
--WHERE
--	demo.year = 2023
--	AND dose.diagnosis='Stimulants';

---- 289/289/289  
--SELECT count(dose.record_id) 
--FROM 
--    dbo.dose_data_test dose
--	inner join discharge_data_view_demographics demo 
--		ON dose.record_id = demo.record_id
--WHERE
--	demo.year = 2023
--	AND dose.diagnosis='Opioids';

---- 17/17/17
--SELECT count(dose.record_id) 
--FROM 
--    dbo.dose_data_test dose
--	inner join discharge_data_view_demographics demo 
--		ON dose.record_id = demo.record_id
--WHERE
--	demo.year = 2023
--	AND dose.diagnosis='Cocaine';

---- 1/20/1 
SELECT count(dose.record_id) 
FROM 
    dbo.dose_data dose
	inner join discharge_data_view_demographics demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023
	AND dose.diagnosis='Methamphetamine';

select distinct diagnosis from dbo.dose_data;
SELECT meth_icd10data AS Code FROM CDC_DOSE_Groupers; -- T43651A, T43654A
Select [amphetam_uu] FROM CDC_DOSE_Groupers; -- T43621A, T43624A

---- 15/15/15
--SELECT count(dose.record_id) 
--FROM 
--    dbo.dose_data_test dose
--	inner join discharge_data_view_demographics demo 
--		ON dose.record_id = demo.record_id
--WHERE
--	demo.year = 2023
--	AND dose.diagnosis='Fentanyl';

---- 37/37/37
--SELECT count(dose.record_id) 
--FROM 
--    dbo.dose_data_test dose
--	inner join discharge_data_view_demographics demo 
--		ON dose.record_id = demo.record_id
--WHERE
--	demo.year = 2023
--	AND dose.diagnosis='Heroin';






select distinct race_ethnicity from discharge_data_view_demographics_test;





--------------------------------
-- 13,495
select count(record_id) from dose_data_test;
-- 10,172
SELECT count(distinct record_id) FROM dbo.dose_data_test;
-- 7,102
SELECT count(distinct record_id) FROM dbo.dose_data;

select distinct diagnosis from dbo.dose_data;
select distinct diagnosis from dbo.dose_data_test;

--1856
SELECT count(dose.record_id) 
FROM 
    dbo.dose_data_test dose
	inner join discharge_data_view_demographics demo 
		ON dose.record_id = demo.record_id
WHERE
	demo.year = 2023;

-- 7,102
select count(distinct dose_data_test.record_id)
from dose_data_test 
inner join dose_data 
	on dose_data.record_id = dose_data_test.record_id;

SELECT meth_icd10data FROM CDC_DOSE_Groupers;  -- returned 2: T43651A & T43654A 
SELECT meth_icd10data AS Code FROM CDC_DOSE_Groupers; -- returned 2: T43651A & T43654A 
SELECT meth_icd10data AS Code FROM CDC_DOSE_Groupers WHERE meth_icd10data IS NOT NULL; -- returned 2: T43651A & T43654A 

-- this gives me the correct result
SELECT COUNT(DISTINCT dx.record_id)
FROM dbo.Outpatient_DX_2024 dx
	INNER JOIN dbo.Outpatient_Demographics_2024_NO_PII demo 
		ON dx.record_id = demo.record_id
	-- limit to hawaii facilities
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum = facility.hnum
WHERE EXISTS (
    SELECT 1 
    FROM (VALUES 
        (dx_1), (dx_2), (dx_3), (dx_4), (dx_5), 
        (dx_6), (dx_7), (dx_8), (dx_9), (dx_10), 
        (dx_11), (dx_12), (dx_13), (dx_14), (dx_15), 
        (dx_16), (dx_17), (dx_18), (dx_19), (dx_20), 
        (dx_21), (dx_22), (dx_23), (dx_24), (dx_25)
    ) AS v(diagnosis)
    --WHERE diagnosis IN (SELECT meth_icd10data FROM CDC_DOSE_Groupers WHERE meth_icd10data IS NOT NULL) -- gave result of zero
	WHERE diagnosis IN (SELECT REPLACE(REPLACE(meth_icd10data, CHAR(160), ''), CHAR(9), '') FROM CDC_DOSE_Groupers WHERE meth_icd10data IS NOT NULL)
	--WHERE diagnosis IN ('T43651A','T43654A')  -- gave correct result
);

Select [amphetam_uu] FROM CDC_DOSE_Groupers;

SELECT *
FROM dbo.Outpatient_DX_2023
WHERE EXISTS (
    SELECT 1
    FROM (
        VALUES (dx_1), (dx_2), (dx_3), (dx_4), (dx_5), (dx_6), (dx_7), (dx_8), (dx_9), (dx_10),
               (dx_11), (dx_12), (dx_13), (dx_14), (dx_15), (dx_16), (dx_17), (dx_18), (dx_19), (dx_20),
               (dx_21), (dx_22), (dx_23), (dx_24), (dx_25)
    ) AS Unpivoted(dx_code)
    WHERE dx_code LIKE 'T43621A%' 
       OR dx_code LIKE 'T43624A%'
);

SELECT COUNT(DISTINCT dx.record_id)
FROM dbo.Outpatient_DX_2023 dx
	INNER JOIN dbo.Outpatient_Demographics_2023_NO_PII demo 
		ON dx.record_id = demo.record_id
	-- limit to hawaii facilities
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum = facility.hnum
WHERE EXISTS (
    SELECT 1 
    FROM (VALUES 
        (dx_1), (dx_2), (dx_3), (dx_4), (dx_5), 
        (dx_6), (dx_7), (dx_8), (dx_9), (dx_10), 
        (dx_11), (dx_12), (dx_13), (dx_14), (dx_15), 
        (dx_16), (dx_17), (dx_18), (dx_19), (dx_20), 
        (dx_21), (dx_22), (dx_23), (dx_24), (dx_25)
    ) AS v(diagnosis)
    --WHERE diagnosis IN (SELECT meth_icd10data FROM CDC_DOSE_Groupers WHERE meth_icd10data IS NOT NULL) -- gave result of zero
	--WHERE diagnosis IN (SELECT TRIM(meth_icd10data) FROM CDC_DOSE_Groupers WHERE meth_icd10data IS NOT NULL)
	WHERE diagnosis IN ('T43651A','T43654A')  -- gave correct result
);
--'T43651A ' or meth_icd10data = 'T43654A ' -- values with Char(160)


SELECT 
    meth_icd10data, 
    LEN(meth_icd10data) AS Visible_Length, 
    DATALENGTH(meth_icd10data) AS Actual_Bytes
FROM CDC_DOSE_Groupers 
WHERE meth_icd10data IS NOT NULL;

SELECT 
    meth_icd10data, 
    LEN(meth_icd10data) AS Real_Length, 
    LEN(trim(meth_icd10data)) AS Trim_Length, 
	LEN(REPLACE(REPLACE(LTRIM(RTRIM(meth_icd10data)), CHAR(13), ''), CHAR(10), '')) AS Big_trim_length,
    LEN(REPLACE(REPLACE(meth_icd10data, CHAR(160), ''), CHAR(9), '')) AS Ultimate_Trim_Length,
    DATALENGTH(meth_icd10data) AS Actual_Bytes
FROM CDC_DOSE_Groupers 
WHERE meth_icd10data IS NOT NULL;

SELECT
    meth_icd10data,
    LEN(meth_icd10data) AS A,
    LEN(trim(meth_icd10data)) AS B,
    LEN(REPLACE(REPLACE(meth_icd10data, CHAR(160), ''), CHAR(9), '')) AS C
FROM CDC_DOSE_Groupers
WHERE meth_icd10data IS NOT NULL;

SELECT 
    meth_icd10data,
    LEN(REPLACE(REPLACE(meth_icd10data, CHAR(160), ''), CHAR(9), '')) AS Ultimate_Trim_Length
FROM CDC_DOSE_Groupers 
WHERE meth_icd10data IS NOT NULL;

SELECT 
    meth_icd10data,
    RIGHT(meth_icd10data, 1) AS Last_Character,
    ASCII(RIGHT(meth_icd10data, 1)) AS Ascii_Code_Of_Hidden_Char
FROM CDC_DOSE_Groupers 
WHERE meth_icd10data IS NOT NULL;

-- this is giving me the correct numbers for meth for 2023 and 2024!
SELECT COUNT(DISTINCT dx.record_id)
FROM dbo.Outpatient_DX_2024 dx
	INNER JOIN dbo.Outpatient_Demographics_2024_NO_PII demo 
		ON dx.record_id = demo.record_id
	-- limit to hawaii facilities
    INNER JOIN dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26] facility
		ON demo.hnum = facility.hnum
WHERE EXISTS (
    SELECT 1 
    FROM (VALUES 
        (dx_1), (dx_2), (dx_3), (dx_4), (dx_5), 
        (dx_6), (dx_7), (dx_8), (dx_9), (dx_10), 
        (dx_11), (dx_12), (dx_13), (dx_14), (dx_15), 
        (dx_16), (dx_17), (dx_18), (dx_19), (dx_20), 
        (dx_21), (dx_22), (dx_23), (dx_24), (dx_25)
    ) AS v(diagnosis)
    WHERE diagnosis LIKE 'T43651A' or diagnosis LIKE 'T43654A'
);

select distinct diagnosis from dbo.dose_data_test;
-- Stimulants
-- Opioids
-- Cocaine
-- Methamphetamine
-- Fentanyl
-- Heroin
-- Benzodiazepine
-- All Drugs

SELECT [stimulant_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [stimulant_i] FROM CDC_DOSE_Groupers;
SELECT [all_opioid_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [all_opioid_i] FROM CDC_DOSE_Groupers;
SELECT [cocaine_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [cocaine_i] FROM CDC_DOSE_Groupers; -- 3 results, all trimmed
SELECT meth_icd10data AS Code FROM CDC_DOSE_Groupers;
SELECT [fentanyl_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [fentanyl_i] FROM CDC_DOSE_Groupers;  -- 3 results, all trimmed
SELECT [heroin_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [heroin_i] FROM CDC_DOSE_Groupers;
SELECT benzos AS Code FROM CDC_DOSE_Groupers;


SELECT
    [fentanyl_uu],
    LEN([fentanyl_uu]) AS A,
    LEN(trim([fentanyl_uu])) AS B,
    LEN(REPLACE(REPLACE([fentanyl_uu], CHAR(160), ''), CHAR(9), '')) AS C
FROM CDC_DOSE_Groupers
WHERE [fentanyl_uu] IS NOT NULL;

-------------------------------------------
-- search script to find all "dirty values" in the CDC_DOSE_Groupers table

DECLARE @SQL NVARCHAR(MAX) = N'';
-- Build a UNION ALL query to test every column individually
SELECT @SQL = @SQL + 
    'SELECT ''' + COLUMN_NAME + ''' AS ColumnName, [' + COLUMN_NAME + '] AS DirtyValue ' +
    'FROM CDC_DOSE_Groupers ' +
    'WHERE [' + COLUMN_NAME + '] LIKE ''%'' + CHAR(160) + ''%'' ' +
    'UNION ALL ' + CHAR(10)
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'CDC_DOSE_Groupers'
  AND DATA_TYPE IN ('varchar', 'nvarchar', 'char', 'nchar');

-- Remove the final " UNION ALL " from the end of the string
SET @SQL = LEFT(@SQL, LEN(@SQL) - 11);

-- Execute the exact pinpoint search
EXEC sp_executesql @SQL;
-- only returned the two meth records
-------------------------------------------

-- search for values that need a trim
DECLARE @SQL NVARCHAR(MAX) = N'';

-- Build a UNION ALL query to test every column for leading/trailing spaces
SELECT @SQL = @SQL + 
    'SELECT ''' + COLUMN_NAME + ''' AS ColumnName, [' + COLUMN_NAME + '] AS DirtyValue ' +
    'FROM CDC_DOSE_Groupers ' +
    'WHERE DATALENGTH([' + COLUMN_NAME + ']) <> DATALENGTH(LTRIM(RTRIM([' + COLUMN_NAME + ']))) ' +
    'UNION ALL ' + CHAR(10)
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'CDC_DOSE_Groupers'
  AND DATA_TYPE IN ('varchar', 'nvarchar'); -- Excludes fixed-length char/nchar to prevent false positives

-- Remove the final " UNION ALL " from the end of the string
SET @SQL = LEFT(@SQL, LEN(@SQL) - 11);

-- Print the generated query (optional, good for debugging)
-- PRINT @SQL;

-- Execute the exact pinpoint search
EXEC sp_executesql @SQL;
-- returned no hits
-------------------------------------------



select meth_icd10data from dbo.CDC_DOSE_Groupers where meth_icd10data = 'T43651A ' or meth_icd10data = 'T43654A ';
--update dbo.CDC_DOSE_Groupers set meth_icd10data='T43651A' where meth_icd10data = 'T43651A ';
--update dbo.CDC_DOSE_Groupers set meth_icd10data='T43654A' where meth_icd10data = 'T43654A ';

SELECT TOP 10 dx_3 
FROM dbo.Outpatient_DX_2024
WHERE dx_3 IN (
    SELECT meth_icd10data 
    FROM CDC_DOSE_Groupers 
    WHERE meth_icd10data IS NOT NULL
);

SELECT * FROM dbo.Outpatient_DX_2024 
WHERE dx_3 IN ('T43651A', 'T43654A');

select count(*) from dbo.sudors_data_view_demographics$;


select count(*) from dbo.sudors_data_view_diag_su$;


