--ALTER VIEW [dbo].[dose_data]
--AS
--WITH Stimulants AS (
--    SELECT [stimulant_uu] FROM CDC_DOSE_Groupers
--    UNION
--    SELECT [stimulant_i] FROM CDC_DOSE_Groupers
--), 
--Opioids AS (
--    SELECT [all_opioid_uu] FROM CDC_DOSE_Groupers
--    UNION
--    SELECT [all_opioid_i] FROM CDC_DOSE_Groupers
--), 
--Cocaine AS (
--    SELECT [cocaine_uu] FROM CDC_DOSE_Groupers
--    UNION
--    SELECT [cocaine_i] FROM CDC_DOSE_Groupers
--), 
--Methamphetamine AS (
--    SELECT meth_icd10data FROM CDC_DOSE_Groupers
--), 
--Fentanyl AS (
--    SELECT [fentanyl_uu] FROM CDC_DOSE_Groupers
--    UNION
--    SELECT [fentanyl_i] FROM CDC_DOSE_Groupers
--), 
--Heroin AS (
--    SELECT [heroin_uu] FROM CDC_DOSE_Groupers
--    UNION
--    SELECT [heroin_i] FROM CDC_DOSE_Groupers
--), 
--Benzodiazepine AS (
--    SELECT benzos FROM CDC_DOSE_Groupers
--), 
--AllDrugs AS (
--	SELECT [antibiotics_uu] FROM CDC_DOSE_Groupers UNION SELECT [antibiotics_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [antiparasitics_uu] FROM CDC_DOSE_Groupers UNION SELECT [antiparasitics_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [hormones_uu] FROM CDC_DOSE_Groupers UNION SELECT [hormones_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [analgesics_uu] FROM CDC_DOSE_Groupers UNION SELECT [analgesics_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [narc_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [anesthetics_uu] FROM CDC_DOSE_Groupers UNION SELECT [anesthetics_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [antiepileptic_uu] FROM CDC_DOSE_Groupers UNION SELECT [antiepileptic_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [psychotropic_uu] FROM CDC_DOSE_Groupers UNION SELECT [psychotropic_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [autoneuro_uu] FROM CDC_DOSE_Groupers UNION SELECT [autoneuro_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [hematologic_uu] FROM CDC_DOSE_Groupers UNION SELECT [hematologic_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [cardio_uu] FROM CDC_DOSE_Groupers UNION SELECT [cardio_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [gastro_uu] FROM CDC_DOSE_Groupers UNION SELECT [gastro_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [skeletal_resp_uu] FROM CDC_DOSE_Groupers UNION SELECT [skeletal_resp_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [skin_dental_uu] FROM CDC_DOSE_Groupers UNION SELECT [skin_dental_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [diuretics_uu] FROM CDC_DOSE_Groupers UNION SELECT [diuretics_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [all_opioid_uu] FROM CDC_DOSE_Groupers UNION SELECT [all_opioid_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [opium_uu] FROM CDC_DOSE_Groupers UNION SELECT [opium_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [opioid_oth_uu] FROM CDC_DOSE_Groupers UNION SELECT [opioid_oth_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [methadone_uu] FROM CDC_DOSE_Groupers UNION SELECT [methadone_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [narc_synth_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_synth_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [fentanyl_uu] FROM CDC_DOSE_Groupers UNION SELECT [fentanyl_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [tramadol_uu] FROM CDC_DOSE_Groupers UNION SELECT [tramadol_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [narc_synth_other_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_synth_other_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [narc_unspec_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_unspec_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [narc_other_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_other_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [heroin_uu] FROM CDC_DOSE_Groupers UNION SELECT [heroin_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [stimulant_uu] FROM CDC_DOSE_Groupers UNION SELECT [stimulant_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [cocaine_uu] FROM CDC_DOSE_Groupers UNION SELECT [cocaine_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [psycho_unspec_uu] FROM CDC_DOSE_Groupers UNION SELECT [psycho_unspec_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [caffeine_uu] FROM CDC_DOSE_Groupers UNION SELECT [caffeine_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [amphetam_uu] FROM CDC_DOSE_Groupers UNION SELECT [amphetam_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [methylphen_uu] FROM CDC_DOSE_Groupers UNION SELECT [methylphen_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [ecstasy_uu] FROM CDC_DOSE_Groupers UNION SELECT [ecstasy_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [psychostim_oth_uu] FROM CDC_DOSE_Groupers UNION SELECT [psychostim_oth_i] FROM CDC_DOSE_Groupers
--    UNION SELECT [meth_icd10data] FROM CDC_DOSE_Groupers
--    UNION SELECT [benzos] FROM CDC_DOSE_Groupers
--    UNION SELECT [homeless] FROM CDC_DOSE_Groupers
--    UNION SELECT [xylazine] FROM CDC_DOSE_Groupers
--), 
--dose_data AS (
--    -- LOGIC FOR STIMULANTS
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Stimulants WHERE stimulant_uu IS NOT NULL) THEN 'Stimulants' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Stimulants'

--    UNION

--    -- LOGIC FOR OPIOIDS
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Opioids WHERE all_opioid_uu IS NOT NULL) THEN 'Opioids' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Opioids'

--    UNION

--    -- LOGIC FOR COCAINE
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Cocaine WHERE cocaine_uu IS NOT NULL) THEN 'Cocaine' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Cocaine'

--    UNION

--    -- LOGIC FOR METH
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Methamphetamine WHERE meth_icd10data IS NOT NULL) THEN 'Methamphetamine' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Methamphetamine'

--    UNION

--    -- LOGIC FOR FENTANYL
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Fentanyl WHERE fentanyl_uu IS NOT NULL) THEN 'Fentanyl' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Fentanyl'

--    UNION

--    -- LOGIC FOR HEROIN
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Heroin WHERE heroin_uu IS NOT NULL) THEN 'Heroin' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Heroin'

--    UNION

--    -- LOGIC FOR Benzodiazepine
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM Benzodiazepine WHERE benzos IS NOT NULL) THEN 'Benzodiazepine' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'Benzodiazepine'

--    UNION

--    -- LOGIC FOR ALL DRUGS
--    SELECT DISTINCT record_id, diagnosis
--    FROM (
--        SELECT record_id, CASE WHEN diagnosis IN (SELECT * FROM AllDrugs) THEN 'All Drugs' END AS diagnosis
--        FROM (
--            SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
--            FROM (
--                SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2018
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2019
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2020
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2021
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2022
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2023
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2024
--                UNION ALL SELECT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25 FROM dbo.Outpatient_DX_2025
--            ) AS Outpatient_DX
--        ) AS diagnosis 
--        CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
--        WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%'
--    ) AS diag_translated
--    WHERE diagnosis = 'All Drugs'
--)
--SELECT * FROM dose_data;


ALTER VIEW [dbo].[dose_data]
AS
WITH 
-- 1. DEFINE DRUG CODE GROUPS
Stimulants AS (
    SELECT [stimulant_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [stimulant_i] FROM CDC_DOSE_Groupers
), 
Opioids AS (
    SELECT [all_opioid_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [all_opioid_i] FROM CDC_DOSE_Groupers
), 
Cocaine AS (
    SELECT [cocaine_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [cocaine_i] FROM CDC_DOSE_Groupers
), 
Methamphetamine AS (
    SELECT meth_icd10data AS Code FROM CDC_DOSE_Groupers
), 
Fentanyl AS (
    SELECT [fentanyl_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [fentanyl_i] FROM CDC_DOSE_Groupers
), 
Heroin AS (
    SELECT [heroin_uu] AS Code FROM CDC_DOSE_Groupers UNION SELECT [heroin_i] FROM CDC_DOSE_Groupers
), 
Benzodiazepine AS (
    SELECT benzos AS Code FROM CDC_DOSE_Groupers
), 
AllDrugs AS (
    SELECT [antibiotics_uu] FROM CDC_DOSE_Groupers UNION SELECT [antibiotics_i] FROM CDC_DOSE_Groupers
    UNION SELECT [antiparasitics_uu] FROM CDC_DOSE_Groupers UNION SELECT [antiparasitics_i] FROM CDC_DOSE_Groupers
    UNION SELECT [hormones_uu] FROM CDC_DOSE_Groupers UNION SELECT [hormones_i] FROM CDC_DOSE_Groupers
    UNION SELECT [analgesics_uu] FROM CDC_DOSE_Groupers UNION SELECT [analgesics_i] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_i] FROM CDC_DOSE_Groupers
    UNION SELECT [anesthetics_uu] FROM CDC_DOSE_Groupers UNION SELECT [anesthetics_i] FROM CDC_DOSE_Groupers
    UNION SELECT [antiepileptic_uu] FROM CDC_DOSE_Groupers UNION SELECT [antiepileptic_i] FROM CDC_DOSE_Groupers
    UNION SELECT [psychotropic_uu] FROM CDC_DOSE_Groupers UNION SELECT [psychotropic_i] FROM CDC_DOSE_Groupers
    UNION SELECT [autoneuro_uu] FROM CDC_DOSE_Groupers UNION SELECT [autoneuro_i] FROM CDC_DOSE_Groupers
    UNION SELECT [hematologic_uu] FROM CDC_DOSE_Groupers UNION SELECT [hematologic_i] FROM CDC_DOSE_Groupers
    UNION SELECT [cardio_uu] FROM CDC_DOSE_Groupers UNION SELECT [cardio_i] FROM CDC_DOSE_Groupers
    UNION SELECT [gastro_uu] FROM CDC_DOSE_Groupers UNION SELECT [gastro_i] FROM CDC_DOSE_Groupers
    UNION SELECT [skeletal_resp_uu] FROM CDC_DOSE_Groupers UNION SELECT [skeletal_resp_i] FROM CDC_DOSE_Groupers
    UNION SELECT [skin_dental_uu] FROM CDC_DOSE_Groupers UNION SELECT [skin_dental_i] FROM CDC_DOSE_Groupers
    UNION SELECT [diuretics_uu] FROM CDC_DOSE_Groupers UNION SELECT [diuretics_i] FROM CDC_DOSE_Groupers
    UNION SELECT [all_opioid_uu] FROM CDC_DOSE_Groupers UNION SELECT [all_opioid_i] FROM CDC_DOSE_Groupers
    UNION SELECT [opium_uu] FROM CDC_DOSE_Groupers UNION SELECT [opium_i] FROM CDC_DOSE_Groupers
    UNION SELECT [opioid_oth_uu] FROM CDC_DOSE_Groupers UNION SELECT [opioid_oth_i] FROM CDC_DOSE_Groupers
    UNION SELECT [methadone_uu] FROM CDC_DOSE_Groupers UNION SELECT [methadone_i] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_synth_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_synth_i] FROM CDC_DOSE_Groupers
    UNION SELECT [fentanyl_uu] FROM CDC_DOSE_Groupers UNION SELECT [fentanyl_i] FROM CDC_DOSE_Groupers
    UNION SELECT [tramadol_uu] FROM CDC_DOSE_Groupers UNION SELECT [tramadol_i] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_synth_other_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_synth_other_i] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_unspec_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_unspec_i] FROM CDC_DOSE_Groupers
    UNION SELECT [narc_other_uu] FROM CDC_DOSE_Groupers UNION SELECT [narc_other_i] FROM CDC_DOSE_Groupers
    UNION SELECT [heroin_uu] FROM CDC_DOSE_Groupers UNION SELECT [heroin_i] FROM CDC_DOSE_Groupers
    UNION SELECT [stimulant_uu] FROM CDC_DOSE_Groupers UNION SELECT [stimulant_i] FROM CDC_DOSE_Groupers
    UNION SELECT [cocaine_uu] FROM CDC_DOSE_Groupers UNION SELECT [cocaine_i] FROM CDC_DOSE_Groupers
    UNION SELECT [psycho_unspec_uu] FROM CDC_DOSE_Groupers UNION SELECT [psycho_unspec_i] FROM CDC_DOSE_Groupers
    UNION SELECT [caffeine_uu] FROM CDC_DOSE_Groupers UNION SELECT [caffeine_i] FROM CDC_DOSE_Groupers
    UNION SELECT [amphetam_uu] FROM CDC_DOSE_Groupers UNION SELECT [amphetam_i] FROM CDC_DOSE_Groupers
    UNION SELECT [methylphen_uu] FROM CDC_DOSE_Groupers UNION SELECT [methylphen_i] FROM CDC_DOSE_Groupers
    UNION SELECT [ecstasy_uu] FROM CDC_DOSE_Groupers UNION SELECT [ecstasy_i] FROM CDC_DOSE_Groupers
    UNION SELECT [psychostim_oth_uu] FROM CDC_DOSE_Groupers UNION SELECT [psychostim_oth_i] FROM CDC_DOSE_Groupers
    UNION SELECT [meth_icd10data] FROM CDC_DOSE_Groupers
    UNION SELECT [benzos] FROM CDC_DOSE_Groupers
    UNION SELECT [homeless] FROM CDC_DOSE_Groupers
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
    WHERE diagnosis_code IS NOT NULL AND diagnosis_code LIKE 'T%' -- Filter applied once here for speed
)

-- 3. FINAL SELECTION: MATCH UNPIVOTED DATA TO DRUG GROUPS
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
WHERE diagnosis_code IN (SELECT * FROM AllDrugs);
