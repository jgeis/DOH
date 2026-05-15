select count(*) from dbo.sudors_hi_25apr22;
select count(*) from dbo.[Inbound Phone Volume];
select * from dbo.[Inbound Phone Volume];
SELECT * FROM INFORMATION_SCHEMA.TABLES;
select * from dbo.sudors_hi_25apr22;


select * from dbo.[CARES Call Variables]; 


SELECT COLUMN_NAME
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE 
    table_schema = 'dbo'
    AND table_name = 'sudors_hi_25apr22'
    AND column_name like '%Gender%';
    
select * from dbo.sudors_hi_25apr22 
where SubstanceId_1 is null;
-- zero results

select count(*) from dbo.sudors_hi_25apr22 
where SubstanceId_2 is null;
-- 18 results

select count(*) from dbo.sudors_hi_25apr22 
where SubstanceId_3 is null;
-- 58 results

select count(*) from dbo.sudors_hi_25apr22 
where SubstanceId_3 is not null and SubstanceId_2 is null;
-- zero results

--create table dbo.phone_jen select * from dbo.[Inbound Phone Volume];
--CREATE TABLE bar (m INT) SELECT n FROM foo;

select distinct Phone from dbo.[Inbound Phone Volume];
select count(*) from dbo.[Inbound Phone Volume] where Phone = 'null';

select 
  CAST(Date as date) as Date, 
  Phone,
  Total_Calls,
  Offered,
  Handled,
  Abandoned,
  Abandon_Rate,
  Service_Level,
  Avg_Speed_of_Answer_ASA,
  Avg_Abandon_Time,
  Total_Talk_Time,
  Total_Hold_Time,
  Total_Wrapup_Time,
  Total_Handle_Time,
  Average_Talk_Time,
  Average_Hold_Time,
  Average_Wrapup_Time,
  Average_Handle_Time
from dbo.[Inbound Phone Volume]
WHERE
    Date != 'Total' AND Date IS NOT NULL;


select 
  CAST(Date as date) as Date, 
  SUM(CAST(Total_Calls AS INT)) as Total_Calls
from dbo.[Inbound Phone Volume]
WHERE
    Date != 'Total' AND Date IS NOT NULL
GROUP BY
    Date;


select 
  CAST(Date as date) as Date, 
  Phone,
  SUM(CAST(Total_Calls AS INT)) as Total_Calls ,
  SUM(CAST(Offered AS INT)) as Offered,
  SUM(CAST(Handled AS INT)) as Handled ,
  SUM(CAST(Abandoned AS INT)) as Abandoned ,
  ((SUM(CAST(Abandoned AS INT)) / SUM(CAST(Offered AS INT))) * 100) as Abandon_Rate
from dbo.[Inbound Phone Volume]
WHERE
    Date != 'Total' AND Date IS NOT NULL
GROUP BY
    Date, Phone;


-- was trying to create table where a phone number mapped to a service
-- but it turns out there are about 30 numbers, so that was wrong.
select 
  CAST(Date as date) as Date, 
  Phone as Phone_Number,
  "Service_Name" =   
      CASE   
         WHEN Phone =  '8087552801' THEN 'AMHD'  
         WHEN Phone = '8087552802' THEN 'ADAD'  
         WHEN Phone = '8087552802' THEN 'CAMHD'    
         ELSE 'Undefined'  
      END  
  --Total_Calls
from dbo.[Inbound Phone Volume];

select * from dbo.cares_calls_clean;

select * from dbo.Outpatient_DX_2021;

select count(*) from dbo.discharge_data_view;

/*
Number per 10,000K discharges:
percentage of discharges: 
(1) related to co-occurring SUD (primary diagnosis) and MH disorder (secondary diagnoses), 
(2) related to co-occurring MH disorder (primary diagnosis) and SUD (secondary diagnoses)
(3) related to polysubstance use
*/

select 
  top 50 *
from dbo.discharge_data_view;

select 
  top 50 *
from dbo.discharge_data_view_demographics;


select 
  top 50 *
from dbo.discharge_data_view_diagnosis;

select count(distinct record_id) 
from dbo.discharge_data_view_diag_su;
-- 55812

select count(record_id) 
from dbo.discharge_data_view_diag_su;

select count(*)
from dbo.batch_claim_svc_detail;

select count(distinct record_id) 
from dbo.discharge_data_view
where num_substance >= 1;
-- 52793

select * from dbo.discharge_universe_by_year;

/* discharges related to co-occurring SUD (primary) and MH disorder (secondary)*/
select count(distinct record_id)
from dbo.discharge_data_view
where 
  su_primary = 1
  and num_mental > 0;

select count(distinct v.record_id)
from 
  dbo.discharge_data_view as v
  inner join dbo.discharge_data_view_diag_su as su 
    on v.record_id = su.record_id
where 
  v.su_primary = 1
  and v.num_mental > 0;


select count(*) from dbo.discharge_data_view_diagnosis;
-- 182,932

select count(distinct (CONCAT(record_id, diagnosis)))  from dbo.discharge_data_view_diagnosis;
-- 176,991

select count(distinct (CONCAT(record_id, diagnosis, diagnosis_type, is_primary))) from dbo.discharge_data_view_diagnosis;
-- 178,401

select distinct record_id, diagnosis, diagnosis_type, is_primary from dbo.discharge_data_view_diagnosis;


--select count(*) from dbo.discharge_data_view;
--select count(*) from dbo.discharge_data_view_diag_su;
--select count(*) from dbo.AMHD_Client_Diagnosis_Entry;
--select count(*) from dbo.batch_claim_svc_detail;


--ALTER VIEW dbo.jen_testing_view
--drop view dbo.jen_testing_view;

--CREATE VIEW dbo.jen_testing_view
--WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary, diagnosis_type
FROM (
    SELECT record_id,
    CASE WHEN diagnosis LIKE 'F10%' THEN 'Alcohol' WHEN diagnosis LIKE 'F11%' THEN 'Opioid' WHEN diagnosis LIKE 'F12%' THEN 'Cannabis' WHEN diagnosis LIKE 'F13%' THEN 'Sedative, Hypnotic, or Anxiolytic' WHEN diagnosis LIKE 'F14%' THEN 'Cocaine' WHEN diagnosis LIKE 'F15%' THEN 'Other Stimulant (Includes Methamphetamine)' WHEN diagnosis LIKE 'F16%' THEN 'Hallucinogen' WHEN diagnosis LIKE 'F17%' THEN 'Nicotine' WHEN diagnosis LIKE 'F18%' THEN 'Inhalant' WHEN diagnosis LIKE 'F19%' THEN 'Other Psychoactive Substance'
        WHEN diagnosis LIKE 'F0%' THEN 'Mental Disorder Due to Physiological Condition' WHEN diagnosis LIKE 'F2%' THEN 'Schizophrenia, Schizotypal, Delusional, or Other Non-Mood Psychotic Disorder' WHEN diagnosis LIKE 'F3%' THEN 'Mood (Affective) Disorder' WHEN diagnosis LIKE 'F4%' THEN 'Anxiety, Dissacociative, Stress-Related, Somatoform, or Other Nonpsychotic Disorder' WHEN diagnosis LIKE 'F5%' THEN 'Behavioral Syndromes Associated with Physiological Disturbances or Physical Factors' WHEN diagnosis LIKE 'F6%' THEN 'Adult Personality and Behavioral Disorder' WHEN diagnosis LIKE 'F7%' THEN 'Intellectual Disabilities' WHEN diagnosis LIKE 'F8%' THEN 'Pervasive or Specific Developmental Disorder' WHEN diagnosis LIKE 'F9[0-8]%' THEN 'Childhood/Adolescent Onset Behavioral and Emotional Disorders' WHEN diagnosis LIKE 'F99' THEN 'Unspecified'
        END as diagnosis,
    CASE WHEN diagnosis LIKE 'F1%' THEN 'su' WHEN diagnosis LIKE 'F[^1]%' THEN 'mh' END as diagnosis_type,
    is_primary
    FROM (
        SELECT distinct record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2018
            UNION ALL
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2019
            UNION ALL
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2020
            UNION ALL
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2021
        ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis, diagnosis_type;
-- 176,991

--CREATE UNIQUE CLUSTERED INDEX record_index
--ON dbo.discharge_testing_view(record_id, diagnosis, diagnosis_type);

/*
CREATE VIEW dbo.Outpatient_DX_All
WITH SCHEMABINDING AS
*/

--CREATE VIEW dbo.Outpatient_DX_All
--WITH SCHEMABINDING AS
    SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
    FROM dbo.Outpatient_DX_2018
    UNION ALL
    SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
    FROM dbo.Outpatient_DX_2019
    UNION ALL
    SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
    FROM dbo.Outpatient_DX_2020
    UNION ALL
    SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
    FROM dbo.Outpatient_DX_2021;
-- 104229
/* Msg 10116, Level 16, State 1, Line 1
Cannot create index on view 'DOH_AMHD_NO_PII.dbo.Outpatient_DX_All' because it contains one or more UNION, INTERSECT, or EXCEPT operators. Consider creating a separate indexed view for each query that is an input to the UNION, INTERSECT, or EXCEPT operators of the original view. */

--CREATE UNIQUE CLUSTERED INDEX IDX_Outpatient_DX_All ON dbo.Outpatient_DX_All (record_id);
--drop view dbo.Outpatient_DX_All;
/*
SELECT 
  record_id,
  CASE WHEN diagnosis LIKE 'F10%' THEN 'Alcohol' WHEN diagnosis LIKE 'F11%' THEN 'Opioid' WHEN diagnosis LIKE 'F12%' THEN 'Cannabis' WHEN diagnosis LIKE 'F13%' THEN 'Sedative, Hypnotic, or Anxiolytic' WHEN diagnosis LIKE 'F14%' THEN 'Cocaine' WHEN diagnosis LIKE 'F15%' THEN 'Other Stimulant (Includes Methamphetamine)' WHEN diagnosis LIKE 'F16%' THEN 'Hallucinogen' WHEN diagnosis LIKE 'F17%' THEN 'Nicotine' WHEN diagnosis LIKE 'F18%' THEN 'Inhalant' WHEN diagnosis LIKE 'F19%' THEN 'Other Psychoactive Substance'
      WHEN diagnosis LIKE 'F0%' THEN 'Mental Disorder Due to Physiological Condition' WHEN diagnosis LIKE 'F2%' THEN 'Schizophrenia, Schizotypal, Delusional, or Other Non-Mood Psychotic Disorder' WHEN diagnosis LIKE 'F3%' THEN 'Mood (Affective) Disorder' WHEN diagnosis LIKE 'F4%' THEN 'Anxiety, Dissacociative, Stress-Related, Somatoform, or Other Nonpsychotic Disorder' WHEN diagnosis LIKE 'F5%' THEN 'Behavioral Syndromes Associated with Physiological Disturbances or Physical Factors' WHEN diagnosis LIKE 'F6%' THEN 'Adult Personality and Behavioral Disorder' WHEN diagnosis LIKE 'F7%' THEN 'Intellectual Disabilities' WHEN diagnosis LIKE 'F8%' THEN 'Pervasive or Specific Developmental Disorder' WHEN diagnosis LIKE 'F9[0-8]%' THEN 'Childhood/Adolescent Onset Behavioral and Emotional Disorders' WHEN diagnosis LIKE 'F99' THEN 'Unspecified'
  END as diagnosis,
  CASE 
    WHEN diagnosis LIKE 'F1%' THEN 'su' 
    WHEN diagnosis LIKE 'F[^1]%' THEN 'mh' 
  END as diagnosis_type,
  is_primary
FROM dbo.Outpatient_DX_All as diagnosis
CROSS APPLY (
    VALUES
    (dx_1, 1),
    (dx_2, 0),
    (dx_3, 0),
    (dx_4, 0),
    (dx_5, 0),
    (dx_6, 0),
    (dx_7, 0),
    (dx_8, 0),
    (dx_9, 0),
    (dx_10, 0),
    (dx_11, 0),
    (dx_12, 0),
    (dx_13, 0),
    (dx_14, 0),
    (dx_15, 0),
    (dx_16, 0),
    (dx_17, 0),
    (dx_18, 0),
    (dx_19, 0),
    (dx_20, 0),
    (dx_21, 0),
    (dx_22, 0),
    (dx_23, 0),
    (dx_24, 0),
    (dx_25, 0)
) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL;
-- 2,605,725
*/
--select count(*) from dbo.jen_testing_view;
-- 176,991

--CREATE UNIQUE CLUSTERED INDEX IDX_jen_testing_view
--ON dbo.jen_testing_view(record_id, diagnosis, diagnosis_type);
-- Msg 10109, Level 16, State 1, Line 1
-- Cannot create index on view "DOH_AMHD_NO_PII.dbo.jen_testing_view" because it references derived table "diag_translated" (defined by SELECT statement in FROM clause). Consider removing the reference to the derived table or not indexing the view.

--CREATE VIEW dbo.jen_testing_view
--WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary, diagnosis_type
FROM (
    SELECT 
      record_id,
      CASE WHEN diagnosis LIKE 'F10%' THEN 'Alcohol' WHEN diagnosis LIKE 'F11%' THEN 'Opioid' WHEN diagnosis LIKE 'F12%' THEN 'Cannabis' WHEN diagnosis LIKE 'F13%' THEN 'Sedative, Hypnotic, or Anxiolytic' WHEN diagnosis LIKE 'F14%' THEN 'Cocaine' WHEN diagnosis LIKE 'F15%' THEN 'Other Stimulant (Includes Methamphetamine)' WHEN diagnosis LIKE 'F16%' THEN 'Hallucinogen' WHEN diagnosis LIKE 'F17%' THEN 'Nicotine' WHEN diagnosis LIKE 'F18%' THEN 'Inhalant' WHEN diagnosis LIKE 'F19%' THEN 'Other Psychoactive Substance'
          WHEN diagnosis LIKE 'F0%' THEN 'Mental Disorder Due to Physiological Condition' WHEN diagnosis LIKE 'F2%' THEN 'Schizophrenia, Schizotypal, Delusional, or Other Non-Mood Psychotic Disorder' WHEN diagnosis LIKE 'F3%' THEN 'Mood (Affective) Disorder' WHEN diagnosis LIKE 'F4%' THEN 'Anxiety, Dissacociative, Stress-Related, Somatoform, or Other Nonpsychotic Disorder' WHEN diagnosis LIKE 'F5%' THEN 'Behavioral Syndromes Associated with Physiological Disturbances or Physical Factors' WHEN diagnosis LIKE 'F6%' THEN 'Adult Personality and Behavioral Disorder' WHEN diagnosis LIKE 'F7%' THEN 'Intellectual Disabilities' WHEN diagnosis LIKE 'F8%' THEN 'Pervasive or Specific Developmental Disorder' WHEN diagnosis LIKE 'F9[0-8]%' THEN 'Childhood/Adolescent Onset Behavioral and Emotional Disorders' WHEN diagnosis LIKE 'F99' THEN 'Unspecified'
      END as diagnosis,
      CASE 
        WHEN diagnosis LIKE 'F1%' THEN 'su' 
        WHEN diagnosis LIKE 'F[^1]%' THEN 'mh' 
      END as diagnosis_type,
      is_primary
    FROM dbo.Outpatient_DX_All as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis, diagnosis_type;

--CREATE VIEW dbo.jen_testing_view_part_2
--WITH SCHEMABINDING AS
SELECT 
  record_id, diagnosis, is_primary
FROM dbo.Outpatient_DX_All
CROSS APPLY (
    VALUES
    (dx_1, 1),
    (dx_2, 0),
    (dx_3, 0),
    (dx_4, 0),
    (dx_5, 0),
    (dx_6, 0),
    (dx_7, 0),
    (dx_8, 0),
    (dx_9, 0),
    (dx_10, 0),
    (dx_11, 0),
    (dx_12, 0),
    (dx_13, 0),
    (dx_14, 0),
    (dx_15, 0),
    (dx_16, 0),
    (dx_17, 0),
    (dx_18, 0),
    (dx_19, 0),
    (dx_20, 0),
    (dx_21, 0),
    (dx_22, 0),
    (dx_23, 0),
    (dx_24, 0),
    (dx_25, 0)
) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL;

CREATE UNIQUE CLUSTERED INDEX IDX_jen_testing_view_part_2
ON dbo.jen_testing_view_part_2(record_id, diagnosis, is_primary);

select count(*) from dbo.AMHD_CMHC_HSH_Dx;
-- 32,069


select o.name, sum(p.rows) as RowsCount, o.type, concat('select ''', o.name, ''' as ObjectName, count(*) as RowsCount from dbo.', o.name, ' union all ')
from sys.objects o
left join sys.partitions p on p.object_id = o.object_id
where o.type in ('V')
group by o.name, o.type
order by o.name;




select 'adad_indicators_view' as ObjectName, count(*) as RowsCount from dbo.adad_indicators_view union all 
select 'adad_mh_dx_view' as ObjectName, count(*) as RowsCount from dbo.adad_mh_dx_view union all 
select 'adad_service_view' as ObjectName, count(*) as RowsCount from dbo.adad_service_view union all 
select 'adad_su_dx_view' as ObjectName, count(*) as RowsCount from dbo.adad_su_dx_view union all 
select 'AMHD_CMHC_HSH_Dx' as ObjectName, count(*) as RowsCount from dbo.AMHD_CMHC_HSH_Dx union all 
select 'AMHD_service_category' as ObjectName, count(*) as RowsCount from dbo.AMHD_service_category union all 
select 'cares_calls_clean' as ObjectName, count(*) as RowsCount from dbo.cares_calls_clean union all 
select 'discharge_data_view' as ObjectName, count(*) as RowsCount from dbo.discharge_data_view union all 
select 'discharge_data_view_demographics' as ObjectName, count(*) as RowsCount from dbo.discharge_data_view_demographics union all 
select 'discharge_data_view_diag_mh' as ObjectName, count(*) as RowsCount from dbo.discharge_data_view_diag_mh union all 
select 'discharge_data_view_diag_su' as ObjectName, count(*) as RowsCount from dbo.discharge_data_view_diag_su union all 
select 'discharge_data_view_diagnosis' as ObjectName, count(*) as RowsCount from dbo.discharge_data_view_diagnosis union all 
select 'discharge_testing_view' as ObjectName, count(*) as RowsCount from dbo.discharge_testing_view union all 
select 'discharge_universe_by_year' as ObjectName, count(*) as RowsCount from dbo.discharge_universe_by_year union all 
select 'DOSE_Stimulants' as ObjectName, count(*) as RowsCount from dbo.DOSE_Stimulants union all 
select 'Outpatient_Primary_Mental_Health_Disorder_2018' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Mental_Health_Disorder_2018 union all 
select 'Outpatient_Primary_Mental_Health_Disorder_2019' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Mental_Health_Disorder_2019 union all 
select 'Outpatient_Primary_Mental_Health_Disorder_2020' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Mental_Health_Disorder_2020 union all 
select 'Outpatient_Primary_Mental_Health_Disorder_2021' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Mental_Health_Disorder_2021 union all 
select 'Outpatient_Primary_Mental_Health_Disorder_final' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Mental_Health_Disorder_final union all 
select 'Outpatient_Primary_Mental_Health_Disorder_union' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Mental_Health_Disorder_union union all 
select 'Outpatient_Primary_Substance_Use_Disorder_2018' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Substance_Use_Disorder_2018 union all 
select 'Outpatient_Primary_Substance_Use_Disorder_2019' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Substance_Use_Disorder_2019 union all 
select 'Outpatient_Primary_Substance_Use_Disorder_2020' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Substance_Use_Disorder_2020 union all 
select 'Outpatient_Primary_Substance_Use_Disorder_2021' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Substance_Use_Disorder_2021 union all 
select 'Outpatient_Primary_Substance_Use_Disorder_final' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Substance_Use_Disorder_final union all 
select 'Outpatient_Primary_Substance_Use_Disorder_union' as ObjectName, count(*) as RowsCount from dbo.Outpatient_Primary_Substance_Use_Disorder_union union all 
select 'overview' as ObjectName, count(*) as RowsCount from dbo.overview union all 
select 'sudors_data_view' as ObjectName, count(*) as RowsCount from dbo.sudors_data_view union all 
select 'sudors_data_view_demographics' as ObjectName, count(*) as RowsCount from dbo.sudors_data_view_demographics union all 
select 'sudors_data_view_diag_mh' as ObjectName, count(*) as RowsCount from dbo.sudors_data_view_diag_mh union all 
select 'sudors_data_view_diag_su' as ObjectName, count(*) as RowsCount from dbo.sudors_data_view_diag_su union all 
select 'sudors_data_view_diagnosis' as ObjectName, count(*) as RowsCount from dbo.sudors_data_view_diagnosis union all 
select 'sudors_data_view_indicators' as ObjectName, count(*) as RowsCount from dbo.sudors_data_view_indicators;


select distinct * from dbo.DOSE_Stimulants;
select count(*) from dbo.DOSE_Stimulants;
-- 376

select count(*) from dbo.CDC_DOSE_groupers;
-- 76
select distinct * from dbo.CDC_DOSE_groupers;

select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.DOSE_Stimulants', 'V');

select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.jen_testing_view_part_2', 'V');
select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.AMHD_CMHC_HSH_Dx', 'V');
select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.discharge_data_view', 'V');
select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.Outpatient_Primary_Mental_Health_Disorder_union', 'V');
select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.Outpatient_Primary_Mental_Health_Disorder_2018', 'V');
select m.definition from sys.sql_modules m where m.object_id = object_id('dbo.discharge_data_view_diagnosis', 'V');


-- Jared's query that creates the discharge_data_view_diagnosis view
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary, diagnosis_type
FROM (
    SELECT record_id,
    CASE WHEN diagnosis LIKE 'F10%' THEN 'Alcohol' WHEN diagnosis LIKE 'F11%' THEN 'Opioid' WHEN diagnosis LIKE 'F12%' THEN 'Cannabis' WHEN diagnosis LIKE 'F13%' THEN 'Sedative, Hypnotic, or Anxiolytic' WHEN diagnosis LIKE 'F14%' THEN 'Cocaine' WHEN diagnosis LIKE 'F15%' THEN 'Other Stimulant (Includes Methamphetamine)' WHEN diagnosis LIKE 'F16%' THEN 'Hallucinogen' WHEN diagnosis LIKE 'F17%' THEN 'Nicotine' WHEN diagnosis LIKE 'F18%' THEN 'Inhalant' WHEN diagnosis LIKE 'F19%' THEN 'Other Psychoactive Substance'
        WHEN diagnosis LIKE 'F0%' THEN 'Mental Disorder Due to Physiological Condition' WHEN diagnosis LIKE 'F2%' THEN 'Schizophrenia, Schizotypal, Delusional, or Other Non-Mood Psychotic Disorder' WHEN diagnosis LIKE 'F3%' THEN 'Mood (Affective) Disorder' WHEN diagnosis LIKE 'F4%' THEN 'Anxiety, Dissacociative, Stress-Related, Somatoform, or Other Nonpsychotic Disorder' WHEN diagnosis LIKE 'F5%' THEN 'Behavioral Syndromes Associated with Physiological Disturbances or Physical Factors' WHEN diagnosis LIKE 'F6%' THEN 'Adult Personality and Behavioral Disorder' WHEN diagnosis LIKE 'F7%' THEN 'Intellectual Disabilities' WHEN diagnosis LIKE 'F8%' THEN 'Pervasive or Specific Developmental Disorder' WHEN diagnosis LIKE 'F9[0-8]%' THEN 'Childhood/Adolescent Onset Behavioral and Emotional Disorders' WHEN diagnosis LIKE 'F99' THEN 'Unspecified'
        END as diagnosis,
    CASE WHEN diagnosis LIKE 'F1%' THEN 'su' WHEN diagnosis LIKE 'F[^1]%' THEN 'mh' END as diagnosis_type,
    is_primary
    FROM (
        SELECT distinct record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2018
            UNION ALL
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2019
            UNION ALL
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2020
            UNION ALL
            SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
            FROM dbo.Outpatient_DX_2021
        ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis, diagnosis_type;


/* ------------------------------------------------------------------------------------*/
-- DOSE stuff

SELECT distinct 
    Year,
    record_id,
    hnum,
    Age_Group,
    sex,
    Race_ethnicity,
    language,
    dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25,
    'Stimulants' as DOSE_Grouper
FROM (
    SELECT '2018' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2018_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2018 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2019' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2019_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2019 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2020' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2020_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2020 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2021' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2021_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2021 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
) as dose
WHERE
  -- at least one diagnosis must fit one of these.
  dx_1 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')    
  OR dx_2 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_3 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_4 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_5 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_6 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_7 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_8 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_9 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_10 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_11 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_12 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_13 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_14 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_15 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_16 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_17 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_18 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_19 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_20 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_21 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_22 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_23 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_24 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_25 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A');


-- First version of merging all the tables via a much shorter query.  
-- Keep this unmodified as a backup while I add the cross apply to a copy of it (above)
SELECT distinct 
    Year,
    record_id,
    hnum,
    Age_Group,
    sex,
    Race_ethnicity,
    language,
    dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25,
    'Stimulants' as DOSE_Grouper
FROM (
    SELECT '2018' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2018_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2018 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2019' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2019_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2019 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2020' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2020_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2020 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2021' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2021_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2021 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
) as dose
WHERE
  dx_1 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')    
  OR dx_2 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_3 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_4 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_5 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_6 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_7 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_8 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_9 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_10 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_11 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_12 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_13 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_14 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_15 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_16 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_17 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_18 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_19 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_20 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_21 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_22 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_23 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_24 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR dx_25 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A');



-- experiment to remove demographics and make sure I can get it via another table
SELECT distinct 
    Year,
    demo.record_id,
    Age_Group,
    sex,
    dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25,
    'Stimulants' as DOSE_Grouper
  FROM (
  SELECT 
  DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
    FROM dbo.Outpatient_DX_2018 AS DX
  UNION ALL
    SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
    FROM dbo.Outpatient_DX_2019 AS DX
  UNION ALL
    SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
    FROM dbo.Outpatient_DX_2020 AS DX
  UNION ALL
    SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
    FROM dbo.Outpatient_DX_2021 AS DX
) as Outpatient_DX
inner join dbo.discharge_data_view_demographics as demo on Outpatient_DX.record_id = demo.record_id;

SELECT
    '2018' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
FROM
    dbo.Outpatient_Demographics_2018_NO_PII AS Demo
    INNER JOIN dbo.Outpatient_DX_2018 AS DX ON Demo.record_id = DX.record_id
    INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
WHERE
  DX.dx_1 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')    
  OR DX.dx_2 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_3 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_4 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_5 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_6 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_7 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_8 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_9 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_10 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_11 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_12 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_13 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_14 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_15 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_16 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_17 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_18 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_19 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_20 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_21 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_22 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_23 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_24 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_25 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A');


-- email: 9/9, original, but abbreviated, plus moved stimulants line
-- also mentioned in 9/14 email.  Did a search on "DOSE_Stimulants" to find them
--CREATE VIEW DOSE_Stimulants as WITH DOSE_Stimulants as (
SELECT
    '2018' AS Year,
    Demo.record_id,
    Demo.hnum,
    Demo.Age_Group,
    Demo.sex,
    Race.Description AS Race_ethnicity,
    Demo.language,
    DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25,
    'Stimulants' as DOSE_Grouper
FROM
    dbo.Outpatient_Demographics_2018_NO_PII AS Demo
    INNER JOIN dbo.Outpatient_DX_2018 AS DX ON Demo.record_id = DX.record_id
    INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
WHERE
  DX.dx_1 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')    
  OR DX.dx_2 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_3 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_4 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_5 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_6 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_7 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_8 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_9 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_10 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_11 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_12 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_13 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_14 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_15 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_16 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_17 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_18 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_19 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_20 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_21 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_22 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_23 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_24 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A')  
  OR DX.dx_25 IN   ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A','T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A', 'T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A' ,'T43621A','T43692A');

-- select * from dbo.DOSE_Stimulants where record_id = '222A9AE6-1A5E-4A77-BFEA-2AA8056BDE04';
-- select * from dbo.discharge_data_view_demographics where record_id = '222A9AE6-1A5E-4A77-BFEA-2AA8056BDE04';


-- intermediary which gave me the list of T-codes I need to deal with
SELECT DISTINCT diagnosis, SUM(is_primary) as is_primary
FROM (
  SELECT distinct 
    dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
  FROM (
    SELECT '2018' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2018_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2018 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2019' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2019_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2019 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2020' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2020_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2020 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
    UNION ALL
      SELECT '2021' AS Year, Demo.record_id, Demo.hnum, Demo.Age_Group, Demo.sex, Race.Description AS Race_ethnicity, Demo.language, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
      FROM dbo.Outpatient_Demographics_2021_NO_PII AS Demo
      INNER JOIN dbo.Outpatient_DX_2021 AS DX ON Demo.record_id = DX.record_id
      INNER JOIN dbo.Laulima_Data_Alliance_Race_Codes AS Race ON Demo.race_ethnicity = Race.Code
  ) as grouped_years 
) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    AND diagnosis in ('T405X1A','T405X2A' ,'T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A')
GROUP BY diagnosis;
/*
T405X1A - Poisoning by cocaine, accidental (unintentional), initial encounter
T405X2A - Poisoning by cocaine, intentional self-harm, initial encounter
T405X4A - Poisoning by cocaine, undetermined, initial encounter

T43602A - Poisoning by unspecified psychostimulants, intentional self-harm, initial encounter
T43601A - Poisoning by unspecified psychostimulants, accidental (unintentional), initial encounter
T43604A - Poisoning by unspecified psychostimulants, undetermined, initial encounter

T43611A - Poisoning by caffeine, accidental (unintentional), initial encounter
T43612A - Poisoning by caffeine, intentional self-harm, initial encounter
T43614A - Poisoning by caffeine, undetermined, initial encounter

T43621A - Poisoning by amphetamines, accidental (unintentional), initial encounter
T43622A - Poisoning by amphetamines, intentional self-harm, initial encounter
T43624A - Poisoning by amphetamines, undetermined, initial encounter

T43631A - Poisoning by methylphenidate, accidental (unintentional), initial encounter
T43632A - Poisoning by methylphenidate, intentional self-harm, initial encounter
T43634A - Poisoning by methylphenidate, undetermined, initial encounter

T43641A - Poisoning by ecstasy, accidental (unintentional), initial encounter
T43642A - Poisoning by ecstasy, intentional self-harm, initial encounter
T43644A - Poisoning by ecstasy, undetermined, initial encounter

T43691A - Poisoning by other psychostimulants, accidental (unintentional), initial encounter
T43692A - Poisoning by other psychostimulants, intentional self-harm, initial encounter
T43694A - Poisoning by other psychostimulants, undetermined, initial encounter

*/ 

--select count(*) from dbo.dose_stimulants_v2;
-- 617


/*
- Am I correct in understanding that this view was intended to be used to handle row 3? Yes
- If so, why no heroin?  Ok to add?  Yes
- This is only a subset of each type, if I match on a wild card like T405X% I get a lot more hits.  Do they really only want these?  
   - Only care about initial encounter? Yep.
   - Omitting things like assault and underdoses - assuming intentional.  Go with it.
- Should labels include the "poisoning"?  Yes

change stimulants and opioid requirements to related to cocaine, meth, heroin instead
once done, let them know, explain decisions, and get feedback
double check discharges on overview page
Look into make new overview page using a single table view for performance

Tiana and James
Drug overdose surveillance and epidemiology
https://www.cdc.gov/drugoverdose/nonfatal/case.html


- label
- fix bar chart settings
- do per 10k 
- fix green box label
*/


--select * from dbo.dose_stimulants_v2 where diagnosis like '%ecstasy%'


--select * from dbo.dose_stimulants_v2 where diagnosis like '%heroin%'

--drop view dbo.dose_stimulants_v2;
--CREATE VIEW dbo.dose_stimulants_v2 WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_stimulants_v2 WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id,
    CASE 
      WHEN diagnosis LIKE 'T402X%' THEN 'Poisoning by other opiods' 
      WHEN diagnosis LIKE 'T405X%' THEN 'Poisoning by cocaine' 
      WHEN diagnosis LIKE 'T4360%' THEN 'Poisoning by unspecified psychostimulants' 
      WHEN diagnosis LIKE 'T4361%' THEN 'Poisoning by caffeine' 
      WHEN diagnosis LIKE 'T4362%' THEN 'Poisoning by amphetamines' 
      WHEN diagnosis LIKE 'T4363%' THEN 'Poisoning by methylphenidate' 
      WHEN diagnosis LIKE 'T4364%' THEN 'Poisoning by ecstasy' 
      WHEN diagnosis LIKE 'T4369%' THEN 'Poisoning by other psychostimulants' 
      WHEN diagnosis LIKE 'T401X%' THEN 'Poisoning by heroin' 
    END as diagnosis,
    is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    AND diagnosis IN   ('T402X1A','T402X2A','T402X4A','T401X1A','T401X2A','T401X4A','T405X1A','T405X2A','T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A')
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;


select * from dbo.CDC_DOSE_groupers;


select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu is not null AND heroin_uu != 'NA';
select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu like 'T%';

select distinct heroin_i from CDC_DOSE_groupers where heroin_i is not null AND heroin_i != 'NA';
select distinct heroin_i from CDC_DOSE_groupers where heroin_i like 'T%';

select distinct heroin_uu from CDC_DOSE_groupers;
select distinct heroin_i from CDC_DOSE_groupers;
select distinct all_opioid_uu from CDC_DOSE_groupers;
select distinct all_opioid_i from CDC_DOSE_groupers;
select distinct stimulant_uu from CDC_DOSE_groupers;
select distinct stimulant_i from CDC_DOSE_groupers;

select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu like 'T%'
union 
select distinct heroin_i from CDC_DOSE_groupers where heroin_i like 'T%';
-- T401X1A, T401X2A, T401X4A

select distinct all_opioid_uu from CDC_DOSE_groupers where all_opioid_uu like 'T%'
union 
select distinct all_opioid_i from CDC_DOSE_groupers where all_opioid_i like 'T%';
-- returned 30 records

select distinct stimulant_uu from CDC_DOSE_groupers where stimulant_uu like 'T%'
union 
select distinct stimulant_i from CDC_DOSE_groupers where stimulant_i like 'T%';
-- returned 21 records




-- working here!  This is the one I used to create the view.
-- dropped demographics as can get that from another table elsewhere
--CREATE VIEW dbo.dose_data WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_data WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id,
    CASE 
      --WHEN diagnosis LIKE 'T401X%' THEN 'Heroin' 
      WHEN diagnosis in (
        select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu like 'T%'
        union 
        select distinct heroin_i from CDC_DOSE_groupers where heroin_i like 'T%'
      ) THEN 'Heroin' 
      --WHEN diagnosis LIKE 'T405X%' THEN 'Stimulants'
      WHEN diagnosis in (
        select distinct stimulant_uu from CDC_DOSE_groupers where stimulant_uu like 'T%'
        union 
        select distinct stimulant_i from CDC_DOSE_groupers where stimulant_i like 'T%'
      ) THEN 'Stimulants'
      --WHEN diagnosis LIKE 'T4369%' THEN 'Opiods' 
      WHEN diagnosis in (
        select distinct all_opioid_uu from CDC_DOSE_groupers where all_opioid_uu like 'T%'
        union 
        select distinct all_opioid_i from CDC_DOSE_groupers where all_opioid_i like 'T%'
      ) THEN 'Opiods'
      WHEN diagnosis LIKE 'T402X%' THEN 'All drugs' 
    END as diagnosis,
    is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    --AND diagnosis IN   ('T402X1A','T402X2A','T402X4A','T401X1A','T401X2A','T401X4A','T405X1A','T405X2A','T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A')
    AND diagnosis in (
      select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu like 'T%'
      union 
      select distinct heroin_i from CDC_DOSE_groupers where heroin_i like 'T%'
      union
      select distinct all_opioid_uu from CDC_DOSE_groupers where all_opioid_uu like 'T%'
      union 
      select distinct all_opioid_i from CDC_DOSE_groupers where all_opioid_i like 'T%'
      union
      select distinct stimulant_uu from CDC_DOSE_groupers where stimulant_uu like 'T%'
      union 
      select distinct stimulant_i from CDC_DOSE_groupers where stimulant_i like 'T%'
    )
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;


--select analgesics_uu from dbo.CDC_DOSE_groupers;
--select narc_uu from dbo.CDC_DOSE_groupers;

-- missing columns, what I assume they meant
-- analgesics_uu, algesics_uu and algesics_i
-- analgesics_i, algesics_i
-- narc_uu, rc_uu and rc_i
-- narc_i, rc_i
-- narc_synth_uu, rc_synth_uu
-- narc_synth_i, rc_synth_i
-- narc_synth_other_uu, rc_synth_other_uu
-- narc_synth_other_i, rc_synth_other_i
-- narc_unspec_uu, rc_unspec_uu
-- narc_unspec_i, rc_unspec_i
-- narc_other_uu, rc_other_uu
-- narc_other_i, rc_other_i


-- the CDC_dose_grouper_table also has meth_icd_10data, benzos, and homeless, which are not listed in
-- Jame's all_drugs query.  Should any of these be included?



--CREATE VIEW dbo.dose_heroin WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_heroin WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT distinct record_id, 'Heroin' as diagnosis, is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    AND diagnosis in (
      select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu like 'T%'
      union 
      select distinct heroin_i from CDC_DOSE_groupers where heroin_i like 'T%'
    )
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;
-- 214


--CREATE VIEW dbo.dose_opioid WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_opioid WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id,'Opiods' as diagnosis, is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    --AND diagnosis IN   ('T402X1A','T402X2A','T402X4A','T401X1A','T401X2A','T401X4A','T405X1A','T405X2A','T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A')
    AND diagnosis in (
      -- I need the like 'T%' to omit nulls and NAs and whatever else they might unexpectedly stick in there
      -- this limits the results to actual codes
      select distinct all_opioid_uu from CDC_DOSE_groupers where all_opioid_uu like 'T%'
      union 
      select distinct all_opioid_i from CDC_DOSE_groupers where all_opioid_i like 'T%'
    )
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;
-- 880


--CREATE VIEW dbo.dose_stimulant WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_stimulant WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id, 'Stimulants' as diagnosis, is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
      -- I need the like 'T%' to omit nulls and NAs and whatever else they might unexpectedly stick in there
      -- this limits the results to actual codes
    AND diagnosis in (
      select distinct stimulant_uu from CDC_DOSE_groupers where stimulant_uu like 'T%'
      union 
      select distinct stimulant_i from CDC_DOSE_groupers where stimulant_i like 'T%'
    )
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;
-- 397


--CREATE VIEW dbo.dose_data WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_data WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id, 'All drugs' as diagnosis, is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    --AND diagnosis IN   ('T402X1A','T402X2A','T402X4A','T401X1A','T401X2A','T401X4A','T405X1A','T405X2A','T405X4A','T43602A' ,'T43601A','T43612A' ,'T43604A','T43622A' ,'T43611A','T43632A' ,'T43614A','T43642A','T43621A','T43692A' ,'T43624A', 'T43631A', 'T43634A', 'T43641A', 'T43644A', 'T43691A', 'T43694A')
    AND diagnosis in (
      select distinct heroin_uu from CDC_DOSE_groupers where heroin_uu like 'T%'
      union 
      select distinct heroin_i from CDC_DOSE_groupers where heroin_i like 'T%'
      union
      select distinct all_opioid_uu from CDC_DOSE_groupers where all_opioid_uu like 'T%'
      union 
      select distinct all_opioid_i from CDC_DOSE_groupers where all_opioid_i like 'T%'
      union
      select distinct stimulant_uu from CDC_DOSE_groupers where stimulant_uu like 'T%'
      union 
      select distinct stimulant_i from CDC_DOSE_groupers where stimulant_i like 'T%'
    )
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;

--drop view dbo.dose_temp;

--CREATE VIEW dbo.dose_temp WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_temp WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id, diagnosis, is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
) as diag_translated
WHERE diagnosis IS NOT NULL
    AND diagnosis != 'NA'
    AND diagnosis not in (select distinct homeless from dbo.CDC_DOSE_groupers where homeless is not null)
GROUP BY record_id, diagnosis;


select distinct meth_icd10data from dbo.CDC_DOSE_groupers;
select distinct benzos from dbo.CDC_DOSE_groupers;
select distinct homeless from dbo.CDC_DOSE_groupers;

select distinct * from dbo.dose_data where diagnosis = 'T424X1A';

--select count (*) from dbo.dose_temp;
--select distinct diagnosis from dbo.dose_temp;
--select count(distinct diagnosis) from dbo.dose_temp where diagnosis not in (select distinct homeless from dbo.CDC_DOSE_groupers where homeless is not null);
--select count(distinct diagnosis) from dbo.dose_temp where diagnosis not in ('Z590','Z5900','Z5902','Z5901','Z59811','Z5981');

select count (*) from dbo.dose_data;

select distinct skeletal_resp_i from dbo.CDC_DOSE_groupers; 

/*
-- query to get specific codes.   Used to prove there are non-drug items in the dataset
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id, diagnosis, is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    AND diagnosis like 'G%'
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;
*/


select distinct year, has_psychotic  from dbo.discharge_data_view;
select distinct year  from dbo.discharge_data_view where has_psychotic = 1;

select sum(total_calls) from dbo.cares_calls_clean;
-- 52,138

select * from dbo.cares_calls_clean;

select distinct count(*) from dbo.dose_data;
select * from dbo.dose_data;

select distinct stimulant_uu from dbo.CDC_DOSE_groupers where stimulant_uu like 'T%';
select distinct heroin_uu from dbo.CDC_DOSE_groupers where heroin_uu like 'T%';

--CREATE VIEW dbo.dose_data WITH SCHEMABINDING AS
--ALTER VIEW dbo.dose_data WITH SCHEMABINDING AS
SELECT DISTINCT record_id, diagnosis, SUM(is_primary) as is_primary
FROM (
    SELECT record_id,
    CASE 
      --Heroin
      WHEN diagnosis in (
        select distinct heroin_uu from dbo.CDC_DOSE_groupers where heroin_uu like 'T%'
        union 
        select distinct heroin_i from dbo.CDC_DOSE_groupers where heroin_i like 'T%'
      ) THEN 'Heroin' 
      --Stimulants
      WHEN diagnosis in (
        select distinct stimulant_uu from dbo.CDC_DOSE_groupers where stimulant_uu like 'T%'
        union 
        select distinct stimulant_i from dbo.CDC_DOSE_groupers where stimulant_i like 'T%'
      ) THEN 'Stimulants'
      --Opioids
      WHEN diagnosis in (
        select distinct all_opioid_uu from dbo.CDC_DOSE_groupers where all_opioid_uu like 'T%'
        union 
        select distinct all_opioid_i from dbo.CDC_DOSE_groupers where all_opioid_i like 'T%'
      ) THEN 'Opioids'
      --All drugs
      ELSE 'All drugs' 
    END as diagnosis,
    is_primary
    FROM (
        SELECT distinct 
            record_id,
            dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
        SELECT 
        DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2018 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2019 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2020 AS DX
        UNION ALL
          SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, DX.dx_25
          FROM dbo.Outpatient_DX_2021 AS DX
      ) as Outpatient_DX
    ) as diagnosis
    CROSS APPLY (
        VALUES
        (dx_1, 1),
        (dx_2, 0),
        (dx_3, 0),
        (dx_4, 0),
        (dx_5, 0),
        (dx_6, 0),
        (dx_7, 0),
        (dx_8, 0),
        (dx_9, 0),
        (dx_10, 0),
        (dx_11, 0),
        (dx_12, 0),
        (dx_13, 0),
        (dx_14, 0),
        (dx_15, 0),
        (dx_16, 0),
        (dx_17, 0),
        (dx_18, 0),
        (dx_19, 0),
        (dx_20, 0),
        (dx_21, 0),
        (dx_22, 0),
        (dx_23, 0),
        (dx_24, 0),
        (dx_25, 0)
    ) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL
    AND diagnosis like 'T%'
) as diag_translated
WHERE diagnosis IS NOT NULL
GROUP BY record_id, diagnosis;


select * from dbo.sudors_data_view_diagnosis;

select * from dbo.sudors_data_view_diagnosis where diagnosis = 'Cocaine';
-- 8 results

select * from 
  dbo.sudors_data_view_diagnosis as di
  inner join dbo.sudors_data_view_demographics de
    on di.Incident_ID = de.incident_id
where diagnosis = 'Cocaine';
-- 7 results, 3 in 2020, 4 in 2021

select * from INFORMATION_SCHEMA.TABLES 
where TABLE_NAME like 'import.tedsa_concatyears';

select count(distinct date) from dbo.cares_calls_clean;

select count(*) from dbo.cares_calls_clean;

select * from dbo.cares_calls_clean;

select sum(total_calls) from dbo.cares_calls_clean where date like '2022-09-%';
-- 11042

select count(*) from import.tedsa_concatyears;
-- 23,248

select * from import.tedsa_concatyears;

select distinct AgeAtAdmission from import.tedsa_concatyears;

-- limit options:
-- 1:
-- select TOP 10 <table names>


-- Number of individuals receiving treatment
--  Filters: Year, Age group (under/over 21yo), county
select TOP 10
  t.Caseid,
  t.YearOfAdmission,
  t.AgeAtAdmission
FROM
  import.tedsa_concatyears t;

--ORDER BY t.YearOfAdmission
--OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY;



select distinct CensusStateFipsCode from  import.tedsa_concatyears;
-- Hawaii

-- find all tables/views that have a column fitting the pattern
SELECT      COLUMN_NAME AS 'ColumnName'
            ,TABLE_NAME AS  'TableName'
FROM        INFORMATION_SCHEMA.COLUMNS
WHERE       COLUMN_NAME LIKE '%zip%'
ORDER BY    TableName
            ,ColumnName;
-- InjuryZip, sudors_hi25apr22

SELECT      COLUMN_NAME AS 'ColumnName'
            ,TABLE_NAME AS  'TableName'
FROM        INFORMATION_SCHEMA.COLUMNS
WHERE       COLUMN_NAME LIKE '%city%'
ORDER BY    TableName
            ,ColumnName;

-----------------------------------------
-- TEDS-A/WITS
            
select count(*) from dbo.WITS_Client_Diagnosis;
-- 370,575
select count(*) from dbo.WITS_Payor_Adjudication;
-- 2,338,203

select count(distinct unique_client_number)
from dbo.WITS_Client_Diagnosis;
-- 87,790

select count(distinct unique_client_number)
from dbo.WITS_Payor_Adjudication;
-- 68,388

select * 
from dbo.WITS_Client_Diagnosis
ORDER BY unique_client_number
OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY;

select distinct geo_description from dbo.WITS_Payor_Adjudication;

select * 
from dbo.WITS_Payor_Adjudication
ORDER BY unique_client_number
OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY;

-- time series of 1, 2, and 3 substances

select count (distinct primary_diagnosis_description)
from dbo.WITS_Client_Diagnosis;
-- 465

select distinct 
  primary_diagnosis_description
from dbo.WITS_Client_Diagnosis;

-- combine client, diagnosis, and county
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_description,
  a.geo_description
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number;
-- 84,665

-- same as previous query, but added timestamp.  Note explosion of results
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_description,
  a.geo_description,
  d.created_timestamp
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number;
-- 327,912

-- changed created_timestamp to adjucated_date
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_description,
  a.geo_description,
  a.adjudicated_date
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number;
-- 662,315

-- changed adjucated_date to start_date
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_description,
  a.geo_description,
  a.start_date
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number;
-- 2,914,741

-- changed start_date to program_enroll_date
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_description,
  a.geo_description,
  a.program_enroll_date
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number;
-- 224,676

/* 
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_icd_code,
  d.primary_diagnosis_description,
  d.secondary_diagnosis_icd_code,
  d.secondary_diagnosis_description,
  d.tertiary_diagnosis_icd_code,
  d.tertiary_diagnosis_description,
  d.source_client_activity_type,
  a.geo_description,
  a.program_enroll_date
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number;
*/
-- 543,126
-- took 3m 46s to run, don't run this again

-- added source_client_activity_type = admission criteria
select distinct 
  d.unique_client_number,
  d.primary_diagnosis_icd_code,
  d.primary_diagnosis_description,
  a.geo_description,
  a.program_enroll_date
from 
  dbo.WITS_Client_Diagnosis d
  inner join dbo.WITS_Payor_Adjudication a 
    on d.unique_client_number = a.unique_client_number
  where d.source_client_activity_type = 'Admission';
-- 205,311


select distinct program_enroll_date from dbo.WITS_Payor_Adjudication order by program_enroll_date;
select distinct source_client_activity_type from dbo.WITS_Client_Diagnosis;
select distinct primary_diagnosis_icd_code from dbo.WITS_Client_Diagnosis order by primary_diagnosis_icd_code;

select * from dbo.WITS_Client_Diagnosis where primary_diagnosis_icd_code = '304.40' order by created_timestamp;

-- get all diagnosis types with the word 'opioid'
select distinct primary_diagnosis_icd_code, primary_diagnosis_description from dbo.WITS_Client_Diagnosis where primary_diagnosis_description like '%opioid%';
-- 30
select distinct primary_diagnosis_description from dbo.WITS_Client_Diagnosis where primary_diagnosis_description like '%heroin%';
-- 0
select distinct primary_diagnosis_description from dbo.WITS_Client_Diagnosis where primary_diagnosis_description like '%stimulant%';
-- 39

select distinct primary_diagnosis_description from dbo.WITS_Client_Diagnosis;

-- attempting to use codes we used in substance views and convert to icd9 to get heroin codes
select distinct heroin_uu from dbo.CDC_DOSE_groupers where heroin_uu like 'T%';
-- heroin codes in icd10: T401X1A, T401X4A
-- converted to icd9: 965.01, E850.0
select * from dbo.WITS_Client_Diagnosis
where primary_diagnosis_icd_code = '965.01'
or primary_diagnosis_icd_code = 'E850.0'
order by created_timestamp;
-- zippo.  So much for conversion.

/*
talk to Sean:
1.) which date?  program_enroll_date, start_date, adjucated_date, or created_timestamp?
    using program_enroll_date for now.
2.) WITS data is using codes that changed after 2015.  ex: 304.40  Need to do two separate filters?  Not sure yet.
    http://www.icd9data.com/2015/Volume1/290-319/300-316/304/304.40.htm
    Some records are using icd9 and others are using icd10.  I need a list from 
    them as to which codes they want to use, 
    or I can filter on anything with 'opioid', etc. in the description (but there's no heroin)
3.) Filtering out everything that's not an 'admission' given they wanted teds-A.  Ok?
4.) Do they want all three diagnoses, or just primary?
*/


--select count(*) from dbo.discharge_data_view_diagnosis;
--select distinct geo_description from dbo.WITS_Payor_Adjudication;

show create view dbo.discharge_data_view_demographics;
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

ALTER VIEW dbo.teds_data_view AS
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

select diagnosis, count(record_id) from dose_data where diagnosis != 'Opioids" and record_id =
(select record_id from dose_data where diagnosis = 'Opioids');



DECLARE @TargetDrug NVARCHAR(100) = 'Heroin';

SELECT 
    t1.diagnosis, 
    COUNT(DISTINCT t1.record_id) AS [count]
FROM 
    dose_data t1
INNER JOIN 
    dose_data t2 ON t1.record_id = t2.record_id
WHERE 
    t2.diagnosis = @TargetDrug       -- Filters T2 to only find patients who had the target drug
    AND t1.diagnosis <> @TargetDrug  -- Filters T1 to exclude the target drug itself from the list
GROUP BY 
    t1.diagnosis
ORDER BY 
    [count] DESC;

SELECT COUNT(*) FROM dose_data WHERE record_id IS NULL; -- 0
SELECT COUNT(*) FROM dbo.dose_data; -- 11,157
select count(distinct record_id) from dose_data; --8,370