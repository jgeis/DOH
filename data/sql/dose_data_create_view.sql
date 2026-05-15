/****** Object:  View [dbo].[dose_data]    Script Date: 12/31/2025 2:04:45 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[dose_data]
AS
WITH Stimulants as (SELECT [stimulant_uu]
FROM   CDC_DOSE_Groupers
UNION
SELECT [stimulant_i]
FROM   CDC_DOSE_Groupers), Opioids AS
    (SELECT [all_opioid_uu]
    FROM    CDC_DOSE_Groupers
    UNION
    SELECT [all_opioid_i]
    FROM   CDC_DOSE_Groupers), Heroin AS
    (SELECT [heroin_uu]
    FROM    CDC_DOSE_Groupers
    UNION
    SELECT [heroin_i]
    FROM   CDC_DOSE_Groupers), AllDrugs AS
    (SELECT [antibiotics_uu]
    FROM    CDC_DOSE_Groupers
    UNION
    SELECT [antibiotics_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [antiparasitics_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [antiparasitics_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [hormones_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [hormones_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [anesthetics_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [anesthetics_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [antiepileptic_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [antiepileptic_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [psychotropic_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [psychotropic_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [autoneuro_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [autoneuro_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [hematologic_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [hematologic_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [cardio_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [cardio_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [gastro_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [gastro_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [skeletal_resp_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [skeletal_resp_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [skin_dental_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [skin_dental_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [diuretics_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [diuretics_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [all_opioid_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [all_opioid_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [opium_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [opium_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [opioid_oth_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [opioid_oth_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [methadone_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [methadone_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [fentanyl_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [fentanyl_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [tramadol_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [tramadol_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [heroin_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [heroin_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [stimulant_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [stimulant_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [cocaine_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [cocaine_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [psycho_unspec_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [psycho_unspec_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [caffeine_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [caffeine_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [amphetam_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [amphetam_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [methylphen_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [methylphen_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [ecstasy_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [ecstasy_i]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [psychostim_oth_uu]
    FROM   CDC_DOSE_Groupers
    UNION
    SELECT [psychostim_oth_i]
    FROM   CDC_DOSE_Groupers), dose_data AS
    (SELECT DISTINCT record_id, diagnosis
    FROM    (SELECT record_id, CASE WHEN diagnosis IN
                                    (SELECT *
                                    FROM    stimulants
                                    WHERE stimulant_uu IS NOT NULL) THEN 'Stimulants' END AS diagnosis
                  FROM    (SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
                                FROM    (SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                            DX.dx_25
                                              FROM    dbo.Outpatient_DX_2018 AS DX
                                              UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2019 AS DX
                                              UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2020 AS DX
                                              UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2021 AS DX
                                              UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2022 AS DX
                                              UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2023 AS DX
                                              UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2024 AS DX
											   UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2025 AS DX) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                                (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
    WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%') AS diag_translated
WHERE diagnosis = 'Stimulants'
UNION
SELECT DISTINCT record_id, diagnosis
FROM   (SELECT record_id, CASE WHEN diagnosis IN
                               (SELECT *
                               FROM    Opioids
                               WHERE all_opioid_uu IS NOT NULL) THEN 'Opioids' END AS diagnosis
             FROM    (SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
                           FROM    (SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                       DX.dx_25
                                         FROM    dbo.Outpatient_DX_2018 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2019 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2020 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2021 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2022 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2023 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2024 AS DX
										    UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2025 AS DX) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%') AS diag_translated
WHERE diagnosis = 'Opioids'
UNION
SELECT DISTINCT record_id, diagnosis
FROM   (SELECT record_id, CASE WHEN diagnosis IN
                               (SELECT *
                               FROM    Heroin
                               WHERE heroin_uu IS NOT NULL) THEN 'Heroin' END AS diagnosis
             FROM    (SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
                           FROM    (SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                       DX.dx_25
                                         FROM    dbo.Outpatient_DX_2018 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2019 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2020 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2021 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2022 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2023 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2024 AS DX
										    UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2025 AS DX) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%') AS diag_translated
WHERE diagnosis = 'Heroin'
UNION
SELECT DISTINCT record_id, diagnosis
FROM   (SELECT record_id, CASE WHEN diagnosis IN
                               (SELECT *
                               FROM    AllDrugs) THEN 'All Drugs' END AS diagnosis
             FROM    (SELECT DISTINCT record_id, dx_1, dx_2, dx_3, dx_4, dx_5, dx_6, dx_7, dx_8, dx_9, dx_10, dx_11, dx_12, dx_13, dx_14, dx_15, dx_16, dx_17, dx_18, dx_19, dx_20, dx_21, dx_22, dx_23, dx_24, dx_25
                           FROM    (SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                       DX.dx_25
                                         FROM    dbo.Outpatient_DX_2018 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2019 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2020 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2021 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2022 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2023 AS DX
                                         UNION ALL
                                         SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                      DX.dx_25
                                         FROM   dbo.Outpatient_DX_2024 AS DX
										    UNION ALL
                                              SELECT DX.record_id, DX.dx_1, DX.dx_2, DX.dx_3, DX.dx_4, DX.dx_5, DX.dx_6, DX.dx_7, DX.dx_8, DX.dx_9, DX.dx_10, DX.dx_11, DX.dx_12, DX.dx_13, DX.dx_14, DX.dx_15, DX.dx_16, DX.dx_17, DX.dx_18, DX.dx_19, DX.dx_20, DX.dx_21, DX.dx_22, DX.dx_23, DX.dx_24, 
                                                           DX.dx_25
                                              FROM   dbo.Outpatient_DX_2025 AS DX) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%') AS diag_translated
WHERE diagnosis = 'All Drugs')
    SELECT *
   FROM    dose_data;
GO


