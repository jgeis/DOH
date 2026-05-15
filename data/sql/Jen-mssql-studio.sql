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

CREATE VIEW dbo.teds_d_data_view AS
select distinct
  Caseid,
  AgeAtAdmission,
  YearOfDischarge,
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
from dbo.TEDS_D;

-------------------------------------------------------------

-- adad = alcohol and drug abuse division

select definition
from sys.objects     o
join sys.sql_modules m on m.object_id = o.object_id
where o.object_id = object_id('dbo.adad_service_view')
  and o.type      = 'V';

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
Adjudication table - use (James will get back to me, or I can look at Jared�s WITS 
visual to see what he filtered on) Calculated date based on start/end dates. 
James is going to connect the two tables so that diagnosis and treatment are more directly related.

- Filtering out everything that's not an 'admission' given they wanted teds-A. Ok? Nope, use all.

- Do you want all three diagnoses, or just primary? NSDUH yes, TEDS, no. 
�For your consideration - the 1 + 2 + 3 substances used (polysubstance use and 
knowingly / unknowingly adding in fentanyl) infographic is a current interest and
concern nationally?� WITS, how many people are receiving treatment. NSDUH, shows prevalence. WITS=treatments

- Which codes to use for each drug type?
Please use the following titles for the dashboards where applicable for the ICD 10 mental health groups. 
This will help where MH group titles are not as descriptive, we recognize these are lengthier titles. 
The highlighted MH disorders are based on the prevalence of primary MH disorder with secondary SUD in the Laulima dataset.
Highlighted disorders have be added for F0, F3, F4, F5, F6, and F9. The idea is to have the whole description available on hover.
� F01-F09 Mental disorders due to known physiological conditions (includes post-concussional syndrome)
� F10-F19 Mental and behavioral disorders due to psychoactive substance use
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
� F20-F29 Schizophrenia, schizotypal, delusional, and other non-mood psychotic disorders
� F30-F39 Mood [affective] disorders (includes major depressive and bipolar disorders)
� F40-F48 Anxiety, dissociative, stress-related, somatoform and other nonpsychotic mental disorders (includes adjustment and post-traumatic stress disorders)
� F50-F59 Behavioral syndromes associated with physiological disturbances and physical factors (includes insomnia-related disorders)
� F60-F69 Disorders of adult personality and behavior (includes borderline personality and anti-social personality disorders)
� F70-F79 Intellectual disabilities
� F80-F89 Pervasive and specific developmental disorders
� F90-F98 Behavioral and emotional disorders with onset usually occurring in childhood and adolescence (includes conduct, oppositional defiant and attention deficit hyperactivity disorder (ADHD))
� F99-F99 Unspecified mental disorder
*/

-- service modality likely means the type of service

CREATE VIEW dbo.adad_service_view AS WITH date_expand AS (
--select dbo.adad_service_view AS WITH date_expand AS (
CREATE VIEW dbo.adad_service_view_jen AS WITH date_expand AS (
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




select count(*) from dbo.adad_service_view;



select count(*) from dbo.TEDSA_2020;
-- 24,703

select count(*) from dbo.TEDS_combined_data_Hawaii_2015_2020;
-- 24,703

select count(*) from import.tedsa_concatyears;
-- 23,248


select top 50 * from dbo.adad_su_dx_view;

select diagnosis, count(*) as ct from dbo.adad_su_dx_view where is_primary = 1 group by diagnosis order by ct;
select diagnosis, count(*) as ct from dbo.adad_mh_dx_view where is_primary = 1 group by diagnosis order by ct;

select distinct diagnosis from dbo.adad_su_dx_view;
select distinct diagnosis from dbo.adad_mh_dx_view;


-- One for each island for WITS data for top substance use and mental health diagnoses. 

select distinct Stabl_Location_Value from dbo.AMHD_Crisis_Stabilization_Bed;
select distinct program_city from dbo.AMHD_Crisis_Mobile_Outreach;


select count(*) from dbo.NSDUH_JEN;

drop table dbo.NSDUH_JEN;

select count(*) from dbo.NSDUH;
select * from dbo.NSDUH;

select distinct county from dbo.NSDUH;
update dbo.NSDUH set county='Maui' where county='Maui County';
update dbo.NSDUH set county='Hawaii' where county='Hawaii County';
update dbo.NSDUH set county='Honolulu' where county='Honolulu County';
update dbo.NSDUH set county='Hawaii' where county='Hawaii Island';
update dbo.NSDUH set county='Kauai' where county='Kauai County';

select distinct row_type from dbo.NSDUH;
update dbo.NSDUH set row_type='Gender' where row_type='gender - imputation revised';
update dbo.NSDUH set row_type='Gender' where row_type='imputation revised gender';
update dbo.NSDUH set row_type='Age' where row_type='age range';
update dbo.NSDUH set row_type='Age' where row_type='age category recode (3 levels)';
update dbo.NSDUH set row_type='Age' where row_type='rc-age category recode (3 levels)';
update dbo.NSDUH set row_type='Age' where row_type='rc-age category recode (5 levels)';

select distinct col_type from dbo.NSDUH;


select count(*) from dbo.AMHD_service_category_CO_patid;
-- 2992
select count(distinct PATID) from dbo.AMHD_service_category_CO_patid;
-- 2992

select definition
from sys.objects     o
join sys.sql_modules m on m.object_id = o.object_id
where o.object_id = object_id('dbo.AMHD_service_category_CO_patid');

select
 VIEW_CATALOG,
 VIEW_SCHEMA,
 VIEW_NAME
from INFORMATION_SCHEMA.VIEW_TABLE_USAGE
where
 TABLE_NAME = 'AMHD_service_category_CO_patid';
-- nothing

select
 VIEW_CATALOG,
 VIEW_SCHEMA,
 VIEW_NAME
from INFORMATION_SCHEMA.VIEW_TABLE_USAGE
where
 TABLE_NAME = 'AMHD_service_category_CO_patid';
-- nothing

select distinct VIEW_CATALOG from INFORMATION_SCHEMA.VIEW_TABLE_USAGE;
-- DOH_AMHD_NO_PII

select distinct VIEW_SCHEMA from INFORMATION_SCHEMA.VIEW_TABLE_USAGE;
-- dbo

select distinct VIEW_NAME from INFORMATION_SCHEMA.VIEW_TABLE_USAGE;
-- lists all views in dbo.

-- attempting to find mssql's equivalent of mysql's 'describe'
exec sp_columns AMHD_service_category_CO_patid;
exec sp_columns AMHD_service_category;
exec sp_help AMHD_service_category_CO_patid;
-- dbo, view

-- this works on discharge_data_view but not AMHD_service_category_CO_patid.  Don't know why
select * 
  from information_schema.columns 
 where table_name = 'discharge_data_view'
 order by ordinal_position;

-- this works on discharge_data_view but not AMHD_service_category_CO_patid.  Don't know why
select * From INFORMATION_SCHEMA.COLUMNS Where TABLE_NAME = 'discharge_data_view';

-- This will give you the name of each column with no results in them, and completes almost instantly with minimal overhead.  Change 0 to 1 for one set of results.
SELECT TOP 0 * FROM AMHD_service_category;

-- list all tables AND views starting with the given characters
select * from INFORMATION_SCHEMA.TABLES where TABLE_NAME like 'AMHD%';
-- AMHD_service_category does not exist

-- list all views (no tables) starting with the given characters
select * from INFORMATION_SCHEMA.VIEWS where TABLE_NAME like 'AMHD%';
-- AMHD_service_category does not exist
select diagnosis
from dbo.discharge_data_view_diag_su;


select * from NSDUH where category = 'age category recode (5 levels)';
select distinct year_range from NSDUH where category = 'age (5 levels)' order by year_range;
select distinct year_range from NSDUH where category = 'age category recode (5 levels)' order by year_range;
update NSDUH set category = 'age (5 levels)' where category = 'age category recode (5 levels)';


select distinct(year_range) from dbo.NSDUH;
select * from dbo.NSDUH;

select distinct(category) from dbo.NSDUH;
select distinct(diagnosis) from dbo.NSDUH;
select * from dbo.NSDUH where category_type = '12 or older';
select distinct diagnosis from dbo.NSDUH where category_type = '12 or older';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'alcohol abuse or dependence - past year';
update dbo.NSDUH set diagnosis='adobalc: past year alcohol dependence or abuse (12 or older)' where category_type = '12 or older' and diagnosis = 'alcohol abuse or dependence - past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'metamyr: methamphetamine use in the past year';
update dbo.NSDUH set diagnosis='metamyr: methamphetamine use in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'metamyr: methamphetamine use in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'mrjyr: past year use of marijuana';
update dbo.NSDUH set diagnosis='mrjyr: past year use of marijuana (12 or older)' where category_type = '12 or older' and diagnosis = 'mrjyr: past year use of marijuana';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'pnrnmyr: pain reliever misuse in the past year';
update dbo.NSDUH set diagnosis='pnrnmyr: pain reliever misuse in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'pnrnmyr: pain reliever misuse in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'txnospa: needing but not receiving treatment at a specialty facility for alcohol use in the past year';
update dbo.NSDUH set diagnosis='txnospa: needing but not receiving treatment at a specialty facility for alcohol use in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'txnospa: needing but not receiving treatment at a specialty facility for alcohol use in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'txnospi: needing but not receiving treatment at a specialty facility for illicit drug use in the past year';
update dbo.NSDUH set diagnosis='txnospi: needing but not receiving treatment at a specialty facility for illicit drug use in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'txnospi: needing but not receiving treatment at a specialty facility for illicit drug use in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'udpyila: substance use disorder in the past year';
update dbo.NSDUH set diagnosis='udpyila: substance use disorder in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'udpyila: substance use disorder in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'udpyill: illicit drug use disorder in the past year';
update dbo.NSDUH set diagnosis='udpyill: illicit drug use disorder in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'udpyill: illicit drug use disorder in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'udpypnr: pain reliever use disorder in the past year';
update dbo.NSDUH set diagnosis='udpypnr: pain reliever use disorder in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'udpypnr: pain reliever use disorder in the past year';
select * from dbo.NSDUH where category_type = '12 or older' and diagnosis = 'txnpila: needing but not receiving treatment at a specialty facility for substance use in the past year';
update dbo.NSDUH set diagnosis='txnpila: needing but not receiving treatment at a specialty facility for substance use in the past year (12 or older)' where category_type = '12 or older' and diagnosis = 'txnpila: needing but not receiving treatment at a specialty facility for substance use in the past year';

select distinct diagnosis from dbo.NSDUH where category_type = '18 or older';
select * from dbo.NSDUH where category_type = '18 or older' and diagnosis = 'amiyr: any mental illness (ami) in the past year';
update dbo.NSDUH set diagnosis='amiyr: any mental illness (ami) in the past year (18 or older)' where category_type = '18 or older' and diagnosis = 'amiyr: any mental illness (ami) in the past year';
select * from dbo.NSDUH where category_type = '18 or older' and diagnosis = 'smiyr: serious mental illness (smi) in the past year';
update dbo.NSDUH set diagnosis='smiyr: serious mental illness (smi) in the past year (18 or older)' where category_type = '18 or older' and diagnosis = 'smiyr: serious mental illness (smi) in the past year';
select * from dbo.NSDUH where category_type = '18 or older' and diagnosis = 'txrec3: received mental health services in the past year';
update dbo.NSDUH set diagnosis='txrec3: received mental health services in the past year (18 or older)' where category_type = '18 or older' and diagnosis = 'txrec3: received mental health services in the past year';



select * from dbo.NSDUH where data_source like '%Shapefile%';
select distinct diagnosis, year_range from dbo.NSDUH where data_source like '%Shapefile%' order by year_range;
-- adobalc, amiyr, mrjyr, smiyr, txrec3


select distinct diagnosis from NSDUH where data_source like '%Shapefile%';
select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'adobalc: past year alcohol dependence or abuse (12 or older)';
update dbo.NSDUH set diagnosis = 'past year alcohol dependence or abuse (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'adobalc: past year alcohol dependence or abuse (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'amiyr: any mental illness (ami) in the past year (18 or older)';
update dbo.NSDUH set diagnosis = 'any mental illness (ami) in the past year (18 or older)' where data_source like '%Shapefile%' and diagnosis = 'amiyr: any mental illness (ami) in the past year (18 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'metamyr: methamphetamine use in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'methamphetamine use in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'metamyr: methamphetamine use in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'mrjyr: past year use of marijuana (12 or older)';
update dbo.NSDUH set diagnosis = 'past year use of marijuana (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'mrjyr: past year use of marijuana (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'pnrnmyr: pain reliever misuse in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'pain reliever misuse in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'pnrnmyr: pain reliever misuse in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'smiyr: serious mental illness (smi) in the past year (18 or older)';
update dbo.NSDUH set diagnosis = 'serious mental illness (smi) in the past year (18 or older)' where data_source like '%Shapefile%' and diagnosis = 'smiyr: serious mental illness (smi) in the past year (18 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'txnospa: needing but not receiving treatment at a specialty facility for alcohol use in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'needing but not receiving treatment at a specialty facility for alcohol use in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'txnospa: needing but not receiving treatment at a specialty facility for alcohol use in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'txnospi: needing but not receiving treatment at a specialty facility for illicit drug use in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'needing but not receiving treatment at a specialty facility for illicit drug use in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'txnospi: needing but not receiving treatment at a specialty facility for illicit drug use in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'txnpila: needing but not receiving treatment at a specialty facility for substance use in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'needing but not receiving treatment at a specialty facility for substance use in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'txnpila: needing but not receiving treatment at a specialty facility for substance use in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'txrec3: received mental health services in the past year (18 or older)';
update dbo.NSDUH set diagnosis = 'received mental health services in the past year (18 or older)' where data_source like '%Shapefile%' and diagnosis = 'txrec3: received mental health services in the past year (18 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'udpyila: substance use disorder in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'substance use disorder in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'udpyila: substance use disorder in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'udpyill: illicit drug use disorder in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'illicit drug use disorder in the past year (12 or older)' where data_source like '%Shapefile%' and diagnosis = 'udpyill: illicit drug use disorder in the past year (12 or older)';

select * from dbo.NSDUH where data_source like '%Shapefile%' and diagnosis = 'udpypnr: pain reliever use disorder in the past year (12 or older)';
update dbo.NSDUH set diagnosis = 'pain reliever use disorder in the past year (12 or older))' where data_source like '%Shapefile%' and diagnosis = 'udpypnr: pain reliever use disorder in the past year (12 or older)';



select count(*) from dbo.TEDSA_2020;
-- 24,703
select top 1 * from dbo.TEDSA_2020;
select count(*) from dbo.TEDSA_2020 where YearOfAdmission = '2015';
-- 6486
select count(*) from dbo.TEDSA_2020 where YearOfAdmission = '2016';
-- 6265
select count(*) from dbo.TEDSA_2020 where YearOfAdmission = '2017';
-- 5234
select count(*) from dbo.TEDSA_2020 where YearOfAdmission = '2018';
-- 2779
select count(*) from dbo.TEDSA_2020 where YearOfAdmission = '2019';
-- 2484
select count(*) from dbo.TEDSA_2020 where YearOfAdmission = '2020';
-- 1455

select * from dbo.TEDS_XWALK_LOS;
select * from dbo.TEDS_XWALK_ARRESTS_D;
--UPDATE dbo.TEDS_XWALK_ARRESTS_D SET value = 'Once' WHERE id = 1;
select count(*) from dbo.TEDS_D_combined_data_Hawaii_2015_2021;
-- doesn't exist
select count(*) from dbo.TEDS_A_combined_data_Hawaii_2015_2021;
-- doesn't exist
select count(*) from dbo.TEDS_D_combined_data_Hawaii_2015_2020;
-- doesn't exist
select count(*) from dbo.TEDS_combined_data_Hawaii_2015_2020;
-- 24,703

select count(*) from teds_data_view;
select count(*) from import.tedsa_concatyears;


select count(*) from TEDS_D;
select TOP 5 * from TEDS_D;
select distinct YearOfDischarge from TEDS_D;



EXEC sp_rename 'dbo.TEDS_D.CASEID', 'Caseid', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.CBSA', 'CoreBasedStatisticalArea', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PMSA', 'PrimaryMetropolitanStatisticalAreas', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DISYR', 'YearOfDischarge', 'COLUMN'; 
EXEC sp_rename 'dbo.TEDS_D.NUMSUBS', 'NumSubstancesAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.STFIPS', 'CensusStateFipsCode', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.EDUC', 'Education', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.MARSTAT', 'MaritalStatus', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SERVICES', 'TypeOfTreatmentServiceSetting', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DETCRIM', 'DetailedCriminalJusticeReferral', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.NOPRIOR', 'PreviousSubstanceUseTreatmentEpisodes', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PSOURCE', 'ReferralSource', 'COLUMN'; 
EXEC sp_rename 'dbo.TEDS_D.ARRESTS', 'ArrestsInPast30Days', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.EMPLOY', 'EmploymentStatus', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.METHUSE', 'MedicationAssistedOpioidTherapy', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PSYPROB', 'CoOccurringMentalAndSubstanceUseDisorders', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PREG', 'PregnantAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.GENDER', 'Gender', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.VET', 'VeteranStatus', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.LIVARAG', 'LivingArrangements', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DAYWAIT', 'DaysWaitingToEnterSubstanceUseTreatment', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DSMCRIT', 'DsmDiagnosisSuds4OrSuds19', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.AGE', 'AgeAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.RACE', 'Race', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ETHNIC', 'Ethnicity', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DETNLF', 'DetailedNotInLaborForce', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PRIMINC', 'SourceOfIncomeSupport', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SUB1', 'SubstanceUsePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SUB2', 'SubstanceUseSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SUB3', 'SubstanceUseTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ROUTE1', 'RouteOfAdministrationPrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ROUTE2', 'RouteOfAdministrationSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ROUTE3', 'RouteOfAdministrationTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ1', 'FrequencyOfUsePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ2', 'FrequencyOfUseSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ3', 'FrequencyOfUseTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FRSTUSE1', 'AgeAtFirstUsePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FRSTUSE2', 'AgeAtFirstUseSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FRSTUSE3', 'AgeAtFirstUseTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.HLTHINS', 'HealthInsurance', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PRIMPAY', 'PaymentSourcePrimaryExpectedOrActual', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ_ATND_SELF_HELP', 'AttendanceAtSubstanceUseSelfHelpGroupsInPast30', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ALCFLG', 'AlcoholReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.COKEFLG', 'CocaineCrackReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.MARFLG', 'MarijuanaHashishReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.HERFLG', 'HeroinReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.METHFLG', 'NonRxMethadoneReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.OPSYNFLG', 'OtherOpiatesSyntheticsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.PCPFLG', 'PcpReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.HALLFLG', 'HallucinogensReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.MTHAMFLG', 'MethamphetamineSpeedReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.AMPHFLG', 'OtherAmphetaminesReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.STIMFLG', 'OtherStimulantsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.BENZFLG', 'BenzodiazepinesReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.TRNQFLG', 'OtherTranquilizersReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.BARBFLG', 'BarbituratesReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SEDHPFLG', 'OtherSedativesHypnoticsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.INHFLG', 'InhalantsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.OTCFLG', 'OverTheCounterMedicationReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.OTHERFLG', 'OtherDrugReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DIVISION', 'CensusDivision', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.REGION', 'CensusRegion', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.IDU', 'CurrentIvDrugUseReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ALCDRUG', 'SubstanceUseType', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.LOS', 'LengthOfStayInTreatment', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SERVICES_D', 'ServiceTypeAtDischarge', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.REASON', 'DischargeReason', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.EMPLOY_D', 'EmploymentStatusAtDischarge', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.LIVARAG_D', 'LivingArrangementsAtDischarge', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.ARRESTS_D', 'ArrestsBeforeDischarge', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.DETNLF_D', 'DetailedNotInLaborForceAtDischarge', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SUB1_D', 'SubstanceUseAtDischargePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SUB2_D', 'SubstanceUseAtDischargeSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.SUB3_D', 'SubstanceUseAtDischargeTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ1_D', 'FrequencyOfUseAtDischargePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ2_D', 'FrequencyOfUseAtDischargeSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ3_D', 'FrequencyOfUseAtDischargeTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_D.FREQ_ATND_SELF_HELP_D', 'AttendanceAtSubstanceUseSelfHelpGroupsInPast30B4Discharge', 'COLUMN';





select count(*) from import.tedsa_concatyears;
--23248 - I'm pretty sure this is just TEDS_A with all the years in it.
select count(*) from dbo.tedsa_concatyears;

select count(*) from dbo.teds_data_view_suppression_calculation_group;


CREATE VIEW dbo.teds_d_data_view AS
select distinct
Caseid,
AgeAtAdmission,
YearOfDischarge,
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
from dbo.TEDS_D;

select distinct AgeAtAdmission from dbo.TEDS_D order by AgeAtAdmission;
update dbo.TEDS_D set AgeAtAdmission = '12-14 Years Old' where AgeAtAdmission = '12-14' or AgeAtAdmission = '12-14 Years';
update dbo.TEDS_D set AgeAtAdmission = '15-17 Years Old' where AgeAtAdmission = '15-17' or AgeAtAdmission = '15-17 Years';
update dbo.TEDS_D set AgeAtAdmission = '18-20 Years Old' where AgeAtAdmission = '18-20' or AgeAtAdmission = '18-20 Years';
update dbo.TEDS_D set AgeAtAdmission = '21-24 Years Old' where AgeAtAdmission = '21-24' or AgeAtAdmission = '21-24 Years';
update dbo.TEDS_D set AgeAtAdmission = '25-29 Years Old' where AgeAtAdmission = '25-29' or AgeAtAdmission = '25-29 Years';
update dbo.TEDS_D set AgeAtAdmission = '30-34 Years Old' where AgeAtAdmission = '30-34' or AgeAtAdmission = '30-34 Years';
update dbo.TEDS_D set AgeAtAdmission = '35-39 Years Old' where AgeAtAdmission = '35-39' or AgeAtAdmission = '35-39 Years';
update dbo.TEDS_D set AgeAtAdmission = '40-44 Years Old' where AgeAtAdmission = '40-44' or AgeAtAdmission = '40-44 Years';
update dbo.TEDS_D set AgeAtAdmission = '45-49 Years Old' where AgeAtAdmission = '45-49' or AgeAtAdmission = '45-49 Years';
update dbo.TEDS_D set AgeAtAdmission = '50-54 Years Old' where AgeAtAdmission = '50-54' or AgeAtAdmission = '50-54 Years';
update dbo.TEDS_D set AgeAtAdmission = '55-64 Years Old' where AgeAtAdmission = '55-64' or AgeAtAdmission = '55-64 Years';
update dbo.TEDS_D set AgeAtAdmission = '65 Years And Older' where AgeAtAdmission = '65 And Older';


select distinct YearOfDischarge from dbo.TEDS_D where AgeAtAdmission = '55 And Over';
select distinct AgeAtAdmission from dbo.TEDS_D order by AgeAtAdmission;
select distinct AgeAtAdmission from dbo.teds_d_data_view order by AgeAtAdmission;

select count(*) from TEDS_A;
-- Just imported this on 1/17/2025 @ 3:30pm

ALTER TABLE dbo.TEDS_A ALTER COLUMN ROUTE3 VARCHAR(80);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN ROUTE2 VARCHAR(80);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN ROUTE1 VARCHAR(80);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN PRIMPAY VARCHAR(100);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN EDUC VARCHAR(90);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN DSMCRIT VARCHAR(80);   


select distinct SubstanceUsePrimary from TEDS_D;
update dbo.TEDS_D set SubstanceUsePrimary = 'Over-The-Counter Medications' where SubstanceUsePrimary = 'Overthecounter Medications';
update dbo.TEDS_D set SubstanceUseSecondary = 'Over-The-Counter Medications' where SubstanceUseSecondary = 'Overthecounter Medications';
update dbo.TEDS_D set SubstanceUseTertiary = 'Over-The-Counter Medications' where SubstanceUseTertiary = 'Overthecounter Medications';

update dbo.TEDS_D set SubstanceUsePrimary = 'Non-Prescription Methadone' where SubstanceUsePrimary = 'Nonprescription Methadone';  
update dbo.TEDS_D set SubstanceUseSecondary = 'Non-Prescription Methadone' where SubstanceUseSecondary = 'Nonprescription Methadone';  
update dbo.TEDS_D set SubstanceUseTertiary = 'Non-Prescription Methadone' where SubstanceUseTertiary = 'Nonprescription Methadone';  

select count(*) from dbo.TEDS_D where  SubstanceUsePrimary = 'Methamphetamine';  
update dbo.TEDS_D set SubstanceUsePrimary = 'Methamphetamine/Speed' where SubstanceUsePrimary = 'Methamphetamine';  
update dbo.TEDS_D set SubstanceUseSecondary = 'Methamphetamine/Speed' where SubstanceUseSecondary = 'Methamphetamine';  
update dbo.TEDS_D set SubstanceUseTertiary = 'Methamphetamine/Speed' where SubstanceUseTertiary = 'Methamphetamine';  





select distinct ADMYR from dbo.TEDS_A;

ALTER TABLE dbo.TEDS_A ALTER COLUMN ROUTE3 VARCHAR(80);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN ROUTE2 VARCHAR(80);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN ROUTE1 VARCHAR(80);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN PRIMPAY VARCHAR(100);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN EDUC VARCHAR(90);   
ALTER TABLE dbo.TEDS_A ALTER COLUMN DSMCRIT VARCHAR(80);   

select count(*) from dbo.TEDS_A;
select TOP 5 * from dbo.TEDS_A;


EXEC sp_rename 'dbo.TEDS_A.CASEID', 'Caseid', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.CBSA', 'CoreBasedStatisticalArea', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PMSA', 'PrimaryMetropolitanStatisticalAreas', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ADMYR', 'YearOfAdmission', 'COLUMN'; 
EXEC sp_rename 'dbo.TEDS_A.NUMSUBS', 'NumSubstancesAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.STFIPS', 'CensusStateFipsCode', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.EDUC', 'Education', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.MARSTAT', 'MaritalStatus', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.SERVICES', 'TypeOfTreatmentServiceSetting', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.DETCRIM', 'DetailedCriminalJusticeReferral', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.NOPRIOR', 'PreviousSubstanceUseTreatmentEpisodes', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PSOURCE', 'ReferralSource', 'COLUMN'; 
EXEC sp_rename 'dbo.TEDS_A.ARRESTS', 'ArrestsInPast30Days', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.EMPLOY', 'EmploymentStatus', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.METHUSE', 'MedicationAssistedOpioidTherapy', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PSYPROB', 'CoOccurringMentalAndSubstanceUseDisorders', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PREG', 'PregnantAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.GENDER', 'Gender', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.VET', 'VeteranStatus', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.LIVARAG', 'LivingArrangements', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.DAYWAIT', 'DaysWaitingToEnterSubstanceUseTreatment', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.DSMCRIT', 'DsmDiagnosisSuds4OrSuds19', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.AGE', 'AgeAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.RACE', 'Race', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ETHNIC', 'Ethnicity', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.DETNLF', 'DetailedNotInLaborForce', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PRIMINC', 'SourceOfIncomeSupport', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.SUB1', 'SubstanceUsePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.SUB2', 'SubstanceUseSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.SUB3', 'SubstanceUseTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ROUTE1', 'RouteOfAdministrationPrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ROUTE2', 'RouteOfAdministrationSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ROUTE3', 'RouteOfAdministrationTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FREQ1', 'FrequencyOfUsePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FREQ2', 'FrequencyOfUseSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FREQ3', 'FrequencyOfUseTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FRSTUSE1', 'AgeAtFirstUsePrimary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FRSTUSE2', 'AgeAtFirstUseSecondary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FRSTUSE3', 'AgeAtFirstUseTertiary', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.HLTHINS', 'HealthInsurance', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PRIMPAY', 'PaymentSourcePrimaryExpectedOrActual', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.FREQ_ATND_SELF_HELP', 'AttendanceAtSubstanceUseSelfHelpGroupsInPast30', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ALCFLG', 'AlcoholReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.COKEFLG', 'CocaineCrackReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.MARFLG', 'MarijuanaHashishReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.HERFLG', 'HeroinReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.METHFLG', 'NonRxMethadoneReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.OPSYNFLG', 'OtherOpiatesSyntheticsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.PCPFLG', 'PcpReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.HALLFLG', 'HallucinogensReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.MTHAMFLG', 'MethamphetamineSpeedReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.AMPHFLG', 'OtherAmphetaminesReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.STIMFLG', 'OtherStimulantsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.BENZFLG', 'BenzodiazepinesReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.TRNQFLG', 'OtherTranquilizersReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.BARBFLG', 'BarbituratesReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.SEDHPFLG', 'OtherSedativesHypnoticsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.INHFLG', 'InhalantsReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.OTCFLG', 'OverTheCounterMedicationReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.OTHERFLG', 'OtherDrugReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.DIVISION', 'CensusDivision', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.REGION', 'CensusRegion', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.IDU', 'CurrentIvDrugUseReportedAtAdmission', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.ALCDRUG', 'SubstanceUseType', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.LOS', 'LengthOfStayInTreatment', 'COLUMN';
EXEC sp_rename 'dbo.TEDS_A.REASON', 'DischargeReason', 'COLUMN';

select distinct AgeAtAdmission from dbo.TEDS_A;
select distinct SubstanceUsePrimary from dbo.TEDS_A;

select count(*) from dbo.teds_a_data_view;

select count(*) from dbo.TEDS_A where SubstanceUseTertiary = '';
select count(*) from dbo.teds_d_data_view where num_substances = 2;

drop view dbo.teds_a_data_view;
CREATE VIEW dbo.teds_a_data_view AS  
select distinct  
Caseid,  
AgeAtAdmission,  
YearOfAdmission,  
Gender,  
SubstanceUsePrimary,  
SubstanceUseSecondary,  
SubstanceUseTertiary,  
CASE  
WHEN SubstanceUsePrimary = '' Then 0  
WHEN SubstanceUseSecondary = '' THEN 1  
WHEN SubstanceUseTertiary = '' THEN 2  
Else 3  
END as num_substances  
from dbo.TEDS_A;  

select TOP 10 * from dbo.teds_a_data_view;

select distinct SubstanceUsePrimary from dbo.teds_d_data_view order by SubstanceUsePrimary;
select distinct SubstanceUsePrimary from dbo.teds_a_data_view order by SubstanceUsePrimary;


select * from dbo.teds_d_data_view where SubstanceUsePrimary = 'Overthecounter Medications';
update dbo.TEDS_D set SubstanceUsePrimary = 'Over-The-Counter Medications' where SubstanceUsePrimary = 'Overthecounter Medications';  
update dbo.TEDS_D set SubstanceUseSecondary = 'Over-The-Counter Medications' where SubstanceUseSecondary = 'Overthecounter Medications';  
update dbo.TEDS_D set SubstanceUseTertiary = 'Over-The-Counter Medications' where SubstanceUseTertiary = 'Overthecounter Medications';  
update dbo.TEDS_D set SubstanceUsePrimary = 'Non-Prescription Methadone' where SubstanceUsePrimary = 'Nonprescription Methadone';  
update dbo.TEDS_D set SubstanceUseSecondary = 'Non-Prescription Methadone' where SubstanceUseSecondary = 'Nonprescription Methadone';  
update dbo.TEDS_D set SubstanceUseTertiary = 'Non-Prescription Methadone' where SubstanceUseTertiary = 'Nonprescription Methadone';  




select count(*) from dbo.wonder_substance;
-- 109
select count(*) from dbo.wonder_overview;
-- 25

select sum(deaths) from dbo.wonder_substance;
-- 3883
select sum(deaths) from dbo.wonder_overview;
-- 2812

select distinct county from dbo.wonder_substance;

select distinct year, county, deaths from dbo.wonder_substance;
select distinct year, county, deaths from dbo.wonder_overview;
select distinct year from dbo.wonder_substance;


select TOP 10 * from dbo.wonder_all;
select distinct value from dbo.wonder_all where type = 'substance';
select distinct type from dbo.wonder_all;

select sum(deaths) from dbo.wonder_all where type = 'substance';

select distinct county from dbo.wonder_substance where Substance = 'Fentanyl and other synthetic narcotics' or Substance = 'Heroin' or Substance = 'Other opioids';

