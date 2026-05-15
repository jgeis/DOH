--select count(*) from dbo.discharge_data_view_diagnosis;
--select distinct geo_description from dbo.WITS_Payor_Adjudication;

-- show create view DOES NOT WORK, use 'select definition code below
--show create view dbo.discharge_data_view_demographics;

/*
select definition
from sys.objects     o
join sys.sql_modules m on m.object_id = o.object_id
where o.object_id = object_id('dbo.discharge_data_view_demographics')
  and o.type      = 'V';
*/


--CREATE VIEW dbo.discharge_data_view_demographics AS
ALTER VIEW dbo.discharge_data_view_demographics AS
SELECT
  COALESCE(dx.record_id, demo.record_id) as record_id,
  CASE
    WHEN county is NULL THEN 'Unknown'
    ELSE county
  END as county,
  CASE
    WHEN city is NULL THEN 'Unknown'
    ELSE city
  END as city,
  CASE
    WHEN zip is NULL THEN 'Unknown'
    ELSE CAST(zip as varchar)
  END as zip,
  CASE
    WHEN zip is NULL OR zip = 99999 OR zip = '' THEN 'Unknown'
	WHEN zip >= 96701 AND zip <= 96898 THEN 'Resident' 
	ELSE 'Non-resident'
  END as hawaii_residency,
  CASE
    WHEN age_group is NULL THEN 'Unknown'
    ELSE age_group
  END as age_group,
  CASE
    WHEN sex = 'male' THEN 'Male'
    WHEN sex = 'female' THEN 'Female'
    ELSE 'Unknown'
  END as sex,
  COALESCE(dx.year, demo.year) as year
FROM
  (
    SELECT
      record_id,
      Facility_By_County_County as county,
      City as city,
      zip,
      Age_Group as age_group,
      CASE
        WHEN sex = 1 THEN 'male'
        WHEN sex = 2 THEN 'female'
      END as sex,
      Description as race_ethnicity,
      year
    FROM
      (
        SELECT
          record_id,
          hnum,
          Age_Group,
          sex,
          race_ethnicity,
          2018 as year,
          zip
        FROM
          Outpatient_Demographics_2018_NO_PII
        UNION
        SELECT
          record_id,
          hnum,
          Age_Group,
          sex,
          race_ethnicity,
          2019 as year,
          zip
        FROM
          Outpatient_Demographics_2019_NO_PII
        UNION
        SELECT
          record_id,
          hnum,
          Age_Group,
          sex,
          race_ethnicity,
          2020 as year,
          zip
        FROM
          Outpatient_Demographics_2020_NO_PII
        UNION
        SELECT
          record_id,
          hnum,
          Age_Group,
          sex,
          race_ethnicity,
          2021 as year,
          zip
        FROM
          Outpatient_Demographics_2021_NO_PII
      ) as discharge_demographics
      JOIN Laulima_Data_Alliance_Race_Codes ON discharge_demographics.race_ethnicity = Laulima_Data_Alliance_Race_Codes.Code
      JOIN [outpt_facility_hnum_county_crosswalk_2022-08-26] ON discharge_demographics.hnum = [outpt_facility_hnum_county_crosswalk_2022-08-26].hnum
  ) as demo
  RIGHT JOIN (
    SELECT
      record_id,
      2018 as year
    FROM
      Outpatient_DX_2018
    UNION
    SELECT
      record_id,
      2019 as year
    FROM
      Outpatient_DX_2019
    UNION
    SELECT
      record_id,
      2020 as year
    FROM
      Outpatient_DX_2020
    UNION
    SELECT
      record_id,
      2021 as year
    FROM
      Outpatient_DX_2021
  ) as dx ON demo.record_id = dx.record_id;

select hawaii_residency, count(*) from discharge_data_view_demographics group by hawaii_residency;
select count(*) from discharge_data_view_demographics;
-- 104,229


select zip, count(*) as ct from Outpatient_Demographics_2018_NO_PII group by zip order by ct;

select distinct zip from discharge_data_view_demographics order by zip;
select distinct hawaii_residency from discharge_data_view_demographics;

select zip, count(*) as ct from discharge_data_view_demographics group by zip order by ct;


select count(zip) from discharge_data_view_demographics where LEN(zip) = 0;
select count(hawaii_residency) from discharge_data_view_demographics where LEN(hawaii_residency) = 0;

select county, count(*) from discharge_data_view_demographics group by county;

select distinct county from discharge_data_view_demographics;

select distinct age_group from discharge_data_view_demographics;


-------------------------------------------------------------
/*
  CASE 
    WHEN AgeAtAdmission < 18 THEN '< 18'
	WHEN AgeAtAdmission > 17 AND AgeAtAdmission < 45 THEN '18-44'
	WHEN AgeAtAdmission > 44 AND AgeAtAdmission < 65 THEN '45-64'
	WHEN AgeAtAdmission > 64 AND AgeAtAdmission < 75 THEN '65-74'
	WHEN AgeAtAdmission > 74 THEN '75+'
    ELSE 'Unknown'
  END as age_group,
 */


ALTER VIEW dbo.teds_data_view AS
select distinct
  Caseid,
  AgeAtAdmission,
  YearOfAdmission,
  Gender,
  SubstanceUsePrimary,
  SubstanceUseSecondary,
  SubstanceUseTertiary
from import.tedsa_concatyears;



select distinct AgeAtAdmission from import.tedsa_concatyears;

select distinct SubstanceUsePrimary from import.tedsa_concatyears;
select distinct SubstanceUseSecondary from import.tedsa_concatyears;
select distinct SubstanceUseTertiary from import.tedsa_concatyears;

select SubstanceUsePrimary, count(*) from import.tedsa_concatyears group by SubstanceUsePrimary;


select distinct SubstanceUseType from import.tedsa_concatyears;
select distinct CensusDivision from import.tedsa_concatyears;
select distinct CensusStateFipsCode from import.tedsa_concatyears;

--ALTER VIEW dbo.teds_data_view AS
select distinct
  Caseid,
  AgeAtAdmission,
  YearOfAdmission,
  Gender,
  SubstanceUsePrimary,
  SubstanceUseSecondary,
  SubstanceUseTertiary,
  CASE
    WHEN SubstanceUsePrimary = 'None' Then 0
    WHEN SubstanceUseSecondary = 'None' THEN 1
	WHEN SubstanceUseTertiary = 'None' THEN 2
	Else 3
  END as num_substances
from import.tedsa_concatyears;


-------------------------------------------------------------

select definition
from sys.objects     o
join sys.sql_modules m on m.object_id = o.object_id
where o.object_id = object_id('dbo.adad_service_view');

select
 VIEW_CATALOG,
 VIEW_SCHEMA,
 VIEW_NAME
from INFORMATION_SCHEMA.VIEW_TABLE_USAGE
where
 TABLE_NAME = 'WITS_Client_Diagnosis';
-- adad_mh_dx_view
-- adad_su_dx_view

select
 VIEW_CATALOG,
 VIEW_SCHEMA,
 VIEW_NAME
from INFORMATION_SCHEMA.VIEW_TABLE_USAGE
where
 TABLE_NAME = 'WITS_Payor_Adjudication';
-- adad_service_view


/*
TEDS->WITS data
- Which date? program_enroll_date, start_date, adjucated_date, or created_timestamp? 
Adjudication table - use (James will get back to me, or I can look at Jared’s WITS 
visual to see what he filtered on) Calculated date based on start/end dates. 
James is going to connect the two tables so that diagnosis and treatment are more directly related.

- Filtering out everything that's not an 'admission' given they wanted teds-A. Ok? Nope, use all.

- Do you want all three diagnoses, or just primary? NSDUH yes, TEDS, no. 
“For your consideration - the 1 + 2 + 3 substances used (polysubstance use and 
knowingly / unknowingly adding in fentanyl) infographic is a current interest and
concern nationally?” WITS, how many people are receiving treatment. NSDUH, shows prevalence. WITS=treatments

- Which codes to use for each drug type?
Please use the following titles for the dashboards where applicable for the ICD 10 mental health groups. 
This will help where MH group titles are not as descriptive, we recognize these are lengthier titles. 
The highlighted MH disorders are based on the prevalence of primary MH disorder with secondary SUD in the Laulima dataset.
Highlighted disorders have be added for F0, F3, F4, F5, F6, and F9. The idea is to have the whole description available on hover.
· F01-F09 Mental disorders due to known physiological conditions (includes post-concussional syndrome)
· F10-F19 Mental and behavioral disorders due to psychoactive substance use
o F10 - Alcohol related disorders
o F11 - Opioid related disorders (includes fentanyl)
o F12 - Cannabis related disorders
o F13 - Sedative, hypnotic, or anxiolytic related disorders
o F14 - Cocaine related disorders
o F15 - Other stimulant related disorders (includes methamphetamine)
o F16 - Hallucinogen related disorders
o F17 - Nicotine dependence
o F18 - Inhalant related disorders
o F19 - Other psychoactive substance related disorders
· F20-F29 Schizophrenia, schizotypal, delusional, and other non-mood psychotic disorders
· F30-F39 Mood [affective] disorders (includes major depressive and bipolar disorders)
· F40-F48 Anxiety, dissociative, stress-related, somatoform and other nonpsychotic mental disorders (includes adjustment and post-traumatic stress disorders)
· F50-F59 Behavioral syndromes associated with physiological disturbances and physical factors (includes insomnia-related disorders)
· F60-F69 Disorders of adult personality and behavior (includes borderline personality and anti-social personality disorders)
· F70-F79 Intellectual disabilities
· F80-F89 Pervasive and specific developmental disorders
· F90-F98 Behavioral and emotional disorders with onset usually occurring in childhood and adolescence (includes conduct, oppositional defiant and attention deficit hyperactivity disorder (ADHD))
· F99-F99 Unspecified mental disorder
*/

CREATE VIEW dbo.adad_service_view AS WITH date_expand AS (
  SELECT
    unique_client_number as client_id,
    geo_description as county,
    modality_type_description as modality,
    start_date as date,
    end_date
  FROM
    WITS_Payor_Adjudication
  UNION
  ALL
  SELECT
    client_id,
    county,
    modality,
    DATEADD(day, 1, date) as date,
    end_date
  FROM
    date_expand
  WHERE
    date < end_date
)
SELECT
  client_id,
  county,
  modality,
  date
FROM
  date_expand;

select top 10 * from import.tedsa_concatyears;


select definition
from sys.objects     o
join sys.sql_modules m on m.object_id = o.object_id
where o.object_id = object_id('import.tedsa_concatyears');


SELECT *
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'tedsa_concatyears';

Select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS
where TABLE_NAME='tedsa_concatyears';

select distinct YearOfAdmission from import.tedsa_concatyears;
-- 2015 through 2019

select count(*) from import.tedsa_concatyears;
-- 23,248 


