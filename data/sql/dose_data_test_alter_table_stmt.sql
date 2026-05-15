ALTER VIEW [dbo].[dose_data_test]
AS
WITH 
-- 1. DEFINE DRUG CODE GROUPS (Clean Base Tables)
-- omit _i values as the indicate intentional overdoses (suicide or assault).  _uu is for unintentional.
Stimulants AS (
    SELECT [stimulant_uu] AS Code FROM CDC_DOSE_Groupers 
	UNION SELECT meth_icd10data FROM CDC_DOSE_Groupers
	UNION SELECT [cocaine_uu] FROM CDC_DOSE_Groupers
), 
Opioids AS (
    SELECT [all_opioid_uu] AS Code FROM CDC_DOSE_Groupers 
    UNION SELECT [fentanyl_uu] FROM CDC_DOSE_Groupers
), 
Cocaine AS (
    SELECT [cocaine_uu] AS Code FROM CDC_DOSE_Groupers
), 
Methamphetamine AS (
    SELECT meth_icd10data AS Code FROM CDC_DOSE_Groupers
	UNION SELECT [amphetam_uu] FROM CDC_DOSE_Groupers
), 
Fentanyl AS (
    SELECT [fentanyl_uu] AS Code FROM CDC_DOSE_Groupers
), 
Heroin AS (
    SELECT [heroin_uu] AS Code FROM CDC_DOSE_Groupers
), 
Benzodiazepine AS (
    SELECT benzos AS Code FROM CDC_DOSE_Groupers
), 
AllDrugs AS (
	SELECT [antibiotics_uu] AS Code FROM CDC_DOSE_Groupers
    UNION SELECT [antiparasitics_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [hormones_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [analgesics_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [anesthetics_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [antiepileptic_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [psychotropic_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [autoneuro_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [hematologic_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [cardio_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [gastro_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [skeletal_resp_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [skin_dental_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [diuretics_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [all_opioid_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [opium_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [opioid_oth_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [methadone_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_synth_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [fentanyl_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [tramadol_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_synth_other_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_unspec_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_other_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [heroin_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [stimulant_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [cocaine_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [psycho_unspec_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [caffeine_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [amphetam_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [methylphen_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [ecstasy_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [psychostim_oth_uu] FROM CDC_DOSE_Groupers
    UNION SELECT [meth_icd10data] FROM CDC_DOSE_Groupers
    UNION SELECT [benzos] FROM CDC_DOSE_Groupers
    UNION SELECT [xylazine] FROM CDC_DOSE_Groupers
),

-- 2. MASTER DATA SOURCE: UNION & UNPIVOT ALL YEARS ONCE
All_Admissions_Unpivoted AS (
    SELECT record_id, diagnosis_code
    FROM (
        SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
        FROM (
              SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
    UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
        ) AS UnifiedData
    ) AS SourceTable
    CROSS APPLY (
        VALUES (dx_1), (dx_2), (dx_3), (dx_4), (dx_5), (dx_6), (dx_7), (dx_8), (dx_9), (dx_10), 
               (dx_11), (dx_12), (dx_13), (dx_14), (dx_15), (dx_16), (dx_17), (dx_18), (dx_19), (dx_20), 
               (dx_21), (dx_22), (dx_23), (dx_24), (dx_25)
    ) Unpivoted (diagnosis_code)
    WHERE diagnosis_code IS NOT NULL AND diagnosis_code LIKE 'T%' 
)

-- 3. FINAL SELECTION: MATCH UNPIVOTED DATA TO CLEAN DRUG GROUPS
SELECT DISTINCT record_id, 'Stimulants' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Stimulants WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'Opioids' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Opioids WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'Cocaine' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Cocaine WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'Methamphetamine' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Methamphetamine WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'Fentanyl' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Fentanyl WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'Heroin' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Heroin WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'Benzodiazepine' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM Benzodiazepine WHERE Code IS NOT NULL)

UNION ALL

SELECT DISTINCT record_id, 'All Drugs' AS diagnosis 
FROM All_Admissions_Unpivoted 
WHERE diagnosis_code IN (SELECT Code FROM AllDrugs WHERE Code IS NOT NULL);
GO