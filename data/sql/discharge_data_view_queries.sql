
select * from AMHD_dates_of_service where PATID='101161';



-- get the query that made discharge_data_view
sp_helptext 'dbo.discharge_data_view'
-- dbo.discharge_data_view stitches together the following tables:
--   dbo.Outpatient_Demographics_xxxx_NO_PII
--   dbo.Outpatient_DX_xxxx
--   dbo.Laulima_Data_Alliance_Race_Codes
-- the 'xxxx' stand for years ranging between 2018-2024.  The query also creates flags, like 'has_alcohol'

select distinct age_group from dbo.Outpatient_Demographics_2024_NO_PII;
select top 5 * from dbo.Outpatient_DX_2024;

select distinct age_group from dbo.discharge_data_view;
select distinct age_group from dbo.discharge_data_view_demographics;

-- both mental health and substance together
select top 50 * from dbo.discharge_data_view_diagnosis;

select * from dbo.discharge_data_view_demographics, count(record_id) group by record_id;
select * from dbo.discharge_data_view_diag_su;


-- just substance
select top 50 * from dbo.discharge_data_view_diag_su order by record_id;
SELECT TOP 1 * FROM dbo.discharge_data_view_demographics;
select top 5 * from dbo.NPDS;
select top 5 * from dbo.ZIP_code_to_ZCTA_crosswalk_HI;

select distinct diagnosis from dbo.discharge_data_view_diagnosis;
select distinct diagnosis from dbo.discharge_data_view_diag_mh;

select count(*) from dbo.dose_data; -- 10,440
select distinct diagnosis from dbo.dose_data;
select count(distinct record_id) from dbo.dose_data; -- 7,102


-- yet, look at the following queries, neither match.
-- 95,330
select count(distinct record_id) from dbo.discharge_data_view_diag_su;
-- 135,563
select count(record_id) from dbo.discharge_data_view_diag_su;

-- did a data refresh on powerBI data tables.  The value on the card changed from: 
-- 84,547 -> 95,330, which matches the first query.  The first query shows 
-- number of individial people, so I would argue that's the correct number.
-- the record count in the power_bi view now matches at 172,720

-- shows there are no true duplicates, just records where the person had multiple drugs
SELECT 
    record_id, 
    diagnosis, 
    COUNT(*) AS occurrence_count
FROM 
    dbo.dose_data
GROUP BY 
    record_id, 
    diagnosis
HAVING 
    COUNT(*) > 1;

-- 135,563 (no distincts)
WITH dx AS (
  SELECT record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT 
  dx.record_id,
  dx.substance,
  m.county, 
  m.city, 
  m.zip, 
  m.hawaii_residency,
  m.age_group, m.sex, m.year
FROM dx
JOIN discharge_data_view_demographics m ON m.record_id = dx.record_id;

-- returned 133,381 records (distinct in first half, not second)
WITH dx AS (
  SELECT DISTINCT record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT
  dx.record_id,
  dx.substance,
  m.county, 
  m.city, 
  m.zip, 
  m.hawaii_residency,
  m.age_group, m.sex, m.year
FROM dx
JOIN discharge_data_view_demographics m ON m.record_id = dx.record_id;

-- 135,563 (distinct in second half, not first.  same result as no distincts)
WITH dx AS (
  SELECT record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT distinct
  dx.record_id,
  dx.substance,
  m.county, 
  m.city, 
  m.zip, 
  m.hawaii_residency,
  m.age_group, m.sex, m.year
FROM dx
JOIN discharge_data_view_demographics m ON m.record_id = dx.record_id;

-- 133,381 (distincts in both halves, same as just first half)
WITH dx AS (
  SELECT distinct record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT distinct
  dx.record_id,
  dx.substance,
  m.county, 
  m.city, 
  m.zip, 
  m.hawaii_residency,
  m.age_group, m.sex, m.year
FROM dx
JOIN discharge_data_view_demographics m ON m.record_id = dx.record_id;

-- 133,381 (removed some filter categories, no diff.)
WITH dx AS (
  SELECT distinct record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT distinct
  dx.record_id,
  dx.substance,
  m.county, 
  m.age_group, 
  m.sex, 
  m.year
FROM dx
JOIN discharge_data_view_demographics m ON m.record_id = dx.record_id;



select top 5 * from dbo.discharge_data_view_diag_mh;
select top 5 * from dbo.discharge_data_view_diag_su;
select top 5 * from dbo.discharge_data_view_diagnosis;
record_id   diagnosis   is_primary
2EB7D268-155C-420E-89C7-2988BE1FE187	Alcohol	1
0746ED66-EF00-4E0D-A2C9-2988BE1FE285	Alcohol	0
0A85B5FF-133B-4DFF-81B7-2988BE1FE6C2	Alcohol	0
A1A3D9B8-FBF0-4613-BEFE-2988BE1FF2C9	Alcohol	0
67FD2502-EA8A-4A3B-8D12-2988BE1FF571	Alcohol	1
-- Get discharges by sex using COUNT(DISTINCT)
-- name: count_by_sex_distinct
SELECT 
    sex,
    COUNT(record_id) AS discharges
FROM dbo.discharge_data_view_demographics 
GROUP BY sex
ORDER BY discharges DESC;
--Male	84,511
--Female 73,516
--Unknown 4,754

-- Get discharges by sex using COUNT(*)
-- name: count_by_sex_raw
SELECT 
    m.sex,
    COUNT(*) AS discharges
FROM dbo.discharge_data_view_diag_su d
JOIN dbo.discharge_data_view_demographics m ON d.record_id = m.record_id
GROUP BY m.sex
ORDER BY discharges DESC;
-- Male	83,355
-- Female 40,845
-- Unknown 3,859

-- write queries that generate the results on the substance use discharges by sex
-- likely involves removing duplicates

SELECT 
    m.sex,
    COUNT(DISTINCT m.record_id) AS discharges
FROM dbo.discharge_data_view_diag_su d
JOIN dbo.discharge_data_view_demographics m ON d.record_id = m.record_id
GROUP BY m.sex
ORDER BY discharges DESC;
-- Male	56,651
-- Female 30,544
-- Unknown 2,735

SELECT DISTINCT
    m.record_id,
    m.sex
FROM dbo.discharge_data_view_diag_su d
JOIN dbo.discharge_data_view_demographics m ON d.record_id = m.record_id
ORDER BY m.record_id DESC;

SELECT 
    m.record_id,
    m.sex,
    COUNT(*) OVER(PARTITION BY m.record_id, m.sex) AS duplicate_count
FROM dbo.discharge_data_view_diag_su d
JOIN dbo.discharge_data_view_demographics m ON d.record_id = m.record_id
ORDER BY m.record_id DESC;

SELECT COUNT(*) FROM dbo.discharge_data_view_demographics;
-- 162,781

SELECT COUNT(*) FROM dbo.discharge_data_view_diag_su;
-- 128,059


select top 5 * from dbo.sudors_data_view_diag_su_STAGING;
select top 5 * from dbo.sudors_data_view_diagnosis_STAGING;
select top 5 * from dbo.sudors_data_view_indicators$;
select top 5 * from dbo.sudors_data_view_indicators_STAGING;
select top 5 * from dbo.sudors_demographics;
-- select top 5 * from dbo.sudors_diag_su;
select top 5 * from dbo.sudors_indicators;
select top 5 * from dbo.sudors_data_view_demographics$$;
select top 5 * from dbo.Laulima_Data_Alliance_Race_Codes;
select top 5 * from dbo.icd10cm_codes_2022;
select top 10 * from [dbo].[ICD_10_Substance Related Disorders]; --only has 10 rows in the whole table



SELECT TOP 5 * FROM dbo.Outpatient_Demographics_2024_NO_PII;
SELECT TOP 5 * FROM dbo.Outpatient_DX_2024;

select * from dbo.icd10cm_codes_2022 where Code='E11649';
select * from dbo.icd10cm_codes_2022 where Code='F10239';

select * from [dbo].[ICD_10_Substance Related Disorders] where [ICD 10 Code]='F10';

select * from dbo.icd10cm_codes_2022 where Description like '%xylazine%';
select * from dbo.icd10cm_codes_2022 where Description like '%xylxcine%';
select * from dbo.icd10cm_codes_2022 where Description like '%xylacine%';
select * from dbo.icd10cm_codes_2022 where Description like '%myelopathy%';

select * from dbo.icd10cm_codes_2022 where Code like 'T65%';


select top 5 * from dbo.discharge_data_view_diagnosis;
select top 5 * from dbo.discharge_data_view_diag_su;

SELECT TOP 5 * FROM dbo.Outpatient_Primary_Substance_Use_Disorder_2021;
SELECT TOP 5 * FROM dbo.[outpt_facility_hnum_county_crosswalk_2022-08-26];


select * from dbo.discharge_data_view_diagnosis where diagnosis like '%myelopathy%';
SELECT * FROM dbo.Outpatient_DX_2024 where dx_6 like 'T65.%';

select count(*) from dbo.dose_data;
-- 14,804
select count(*) from dbo.dose_data where diagnosis = 'All Drugs';
-- 10,511
select count(*) from dbo.dose_data where diagnosis = 'Benzodiazepine';
-- 689
select count(*) from dbo.dose_data where diagnosis = 'Cocaine';
-- 91
select count(*) from dbo.dose_data where diagnosis = 'Fentanyl';
-- 57
select count(*) from dbo.dose_data where diagnosis = 'Heroin';
-- 342
select count(*) from dbo.dose_data where diagnosis = 'Methamphetamine';
-- 669
select count(*) from dbo.dose_data where diagnosis = 'Opioids';
-- 1823
select count(*) from dbo.dose_data where diagnosis = 'Stimulants';
-- 622
select count(*) from dbo.dose_data where diagnosis = 'All Drugs' or diagnosis = 'Benzodiazepine'
or diagnosis = 'Cocaine' or diagnosis = 'Fentanyl' or diagnosis = 'Heroin' 
or diagnosis = 'Methamphetamine' or diagnosis = 'Opioids' or diagnosis = 'Stimulants';
-- 14,804
select count(*) from dbo.dose_data where diagnosis != 'All Drugs' and diagnosis != 'Benzodiazepine'
and diagnosis != 'Cocaine' and diagnosis != 'Fentanyl' and diagnosis != 'Heroin'
and diagnosis != 'Methamphetamine' and diagnosis != 'Opioids' and diagnosis != 'Stimulants';
-- 0

select top 5 * from dbo.dose_data;
select distinct diagnosis from dbo.dose_data;
select top 5 * from dbo.CDC_DOSE_Groupers;

select top 5 * from dbo.wonder_race;

select top 5 * from dbo.sudors_data_view_demographics$;
select top 5 * from dbo.sudors_demographics; -- no longer exists, it disappeared one day

select distinct age_cat from dbo.sudors_data_view_demographics$;

select distinct race_ethnicity from dbo.sudors_data_view_demographics$;
select top 5 * from dbo.sudors_data_view_demographics$ where race_ethnicity = 'Multiracial, non hispanic';

update dbo.sudors_data_view_demographics$ 
set race_ethnicity = 'Multiracial, non-Hispanic' 
where race_ethnicity = 'Multiracial, non hispanic';


SELECT last_user_update
FROM sys.dm_db_index_usage_stats
WHERE object_id = OBJECT_ID('dbo.discharge_data_view_diag_su')
AND database_id = DB_ID('DOH_AMHD_NO_PII');

-- get all the columns in a table
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'CDC_DOSE_Groupers' -- Replace with your table name
-- AND TABLE_SCHEMA = 'dbo'     -- Uncomment if you have multiple schemas
ORDER BY ORDINAL_POSITION;

SELECT DISTINCT 
    REPLACE(REPLACE(COLUMN_NAME, '_uu', ''), '_i', '') AS CleanColumnName
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'CDC_DOSE_Groupers'
  AND TABLE_SCHEMA = 'dbo'
ORDER BY CleanColumnName;
