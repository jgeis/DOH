/****** Object:  View [dbo].[dose_data_test]    Script Date: 3/4/2026 2:22:10 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


create view [dbo].[dose_data_test] as 

with stimulants as 

(Select   [stimulant_uu]  
 FROM CDC_DOSE_Groupers UNION 



select [stimulant_i] 
 FROM CDC_DOSE_Groupers 
         ),


 Opioids as (
    Select   [all_opioid_uu]  
 FROM CDC_DOSE_Groupers UNION 



select [all_opioid_i]  
 FROM CDC_DOSE_Groupers 
        ),


Heroin as (  Select   [heroin_uu]  
 FROM CDC_DOSE_Groupers UNION 

select [heroin_i]  
 FROM CDC_DOSE_Groupers 
       ),


 AllDrugs as (
SELECT [antibiotics_uu]  FROM CDC_DOSE_Groupers UNION
      Select [antibiotics_i]FROM CDC_DOSE_Groupers UNION
      Select [antiparasitics_uu]FROM CDC_DOSE_Groupers UNION
      Select [antiparasitics_i]FROM CDC_DOSE_Groupers UNION
      Select [hormones_uu]FROM CDC_DOSE_Groupers UNION
      Select [hormones_i]FROM CDC_DOSE_Groupers UNION
      Select [anesthetics_uu]FROM CDC_DOSE_Groupers UNION
      Select [anesthetics_i]FROM CDC_DOSE_Groupers UNION
      Select [antiepileptic_uu]FROM CDC_DOSE_Groupers UNION
      Select [antiepileptic_i]FROM CDC_DOSE_Groupers UNION
      Select [psychotropic_uu]FROM CDC_DOSE_Groupers UNION
      Select [psychotropic_i]FROM CDC_DOSE_Groupers UNION
      Select [autoneuro_uu]FROM CDC_DOSE_Groupers UNION
      Select [autoneuro_i]FROM CDC_DOSE_Groupers UNION
      Select [hematologic_uu]FROM CDC_DOSE_Groupers UNION
      Select [hematologic_i]FROM CDC_DOSE_Groupers UNION
      Select [cardio_uu]FROM CDC_DOSE_Groupers UNION
      Select [cardio_i]FROM CDC_DOSE_Groupers UNION
      Select [gastro_uu]FROM CDC_DOSE_Groupers UNION
      Select [gastro_i]FROM CDC_DOSE_Groupers UNION
      Select [skeletal_resp_uu]FROM CDC_DOSE_Groupers UNION
      Select [skeletal_resp_i]FROM CDC_DOSE_Groupers UNION
      Select [skin_dental_uu]FROM CDC_DOSE_Groupers UNION
      Select [skin_dental_i]FROM CDC_DOSE_Groupers UNION
      Select [diuretics_uu]FROM CDC_DOSE_Groupers UNION
      Select [diuretics_i]FROM CDC_DOSE_Groupers UNION
      Select [all_opioid_uu]FROM CDC_DOSE_Groupers UNION
      Select [all_opioid_i]FROM CDC_DOSE_Groupers UNION
      Select [opium_uu]FROM CDC_DOSE_Groupers UNION
      Select [opium_i]FROM CDC_DOSE_Groupers UNION
      Select [opioid_oth_uu]FROM CDC_DOSE_Groupers UNION
      Select [opioid_oth_i]FROM CDC_DOSE_Groupers UNION
      Select [methadone_uu]FROM CDC_DOSE_Groupers UNION
      Select [methadone_i]FROM CDC_DOSE_Groupers UNION
      Select [fentanyl_uu]FROM CDC_DOSE_Groupers UNION
      Select [fentanyl_i]FROM CDC_DOSE_Groupers UNION
      Select [tramadol_uu]FROM CDC_DOSE_Groupers UNION
      Select [tramadol_i]FROM CDC_DOSE_Groupers UNION
      Select [heroin_uu]FROM CDC_DOSE_Groupers UNION
      Select [heroin_i]FROM CDC_DOSE_Groupers UNION
      Select [stimulant_uu]FROM CDC_DOSE_Groupers UNION
      Select [stimulant_i]FROM CDC_DOSE_Groupers UNION
      Select [cocaine_uu]FROM CDC_DOSE_Groupers UNION
      Select [cocaine_i]FROM CDC_DOSE_Groupers UNION
      Select [psycho_unspec_uu]FROM CDC_DOSE_Groupers UNION
      Select [psycho_unspec_i]FROM CDC_DOSE_Groupers UNION
      Select [caffeine_uu]FROM CDC_DOSE_Groupers UNION
      Select [caffeine_i]FROM CDC_DOSE_Groupers UNION
      Select [amphetam_uu]FROM CDC_DOSE_Groupers UNION
      Select [amphetam_i]FROM CDC_DOSE_Groupers UNION
      Select [methylphen_uu]FROM CDC_DOSE_Groupers UNION
      Select [methylphen_i]FROM CDC_DOSE_Groupers UNION
      Select [ecstasy_uu]FROM CDC_DOSE_Groupers UNION
      Select [ecstasy_i]FROM CDC_DOSE_Groupers UNION
      Select [psychostim_oth_uu]FROM CDC_DOSE_Groupers UNION
      Select [psychostim_oth_i] 
	           FROM CDC_DOSE_Groupers ),



dose_data as (SELECT DISTINCT record_id, diagnosis
FROM   (SELECT record_id, CASE WHEN diagnosis in (select * from stimulants where stimulant_uu is not null) then 'Stimulants' end as diagnosis
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
										 ) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%' ) AS diag_translated
WHERE diagnosis = 'Stimulants'

UNION

SELECT DISTINCT record_id,  diagnosis
FROM   (SELECT record_id, CASE WHEN diagnosis in (select * from Opioids where all_opioid_uu is not null) then 'Opioids' end as diagnosis
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
										 ) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%' ) AS diag_translated
WHERE diagnosis = 'Opioids'

UNION

	
	
	

	 SELECT DISTINCT record_id, diagnosis
FROM   (SELECT record_id, CASE WHEN diagnosis in (select * from Heroin where heroin_uu is not null) then 'Heroin' end as diagnosis
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
										 ) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%' ) AS diag_translated
WHERE diagnosis = 'Heroin'



 UNION

	
	
	

	 SELECT DISTINCT record_id, diagnosis
FROM   (SELECT record_id,  CASE WHEN diagnosis in (select * from AllDrugs) then 'All Drugs' end as diagnosis
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
										 ) AS Outpatient_DX) AS diagnosis CROSS APPLY(VALUES (dx_1, 1), (dx_2, 0), (dx_3, 0), (dx_4, 0), (dx_5, 0), (dx_6, 0), (dx_7, 0), (dx_8, 0), (dx_9, 0), (dx_10, 0), (dx_11, 0), (dx_12, 0), (dx_13, 0), (dx_14, 0), (dx_15, 0), (dx_16, 0), (dx_17, 0), 
                           (dx_18, 0), (dx_19, 0), (dx_20, 0), (dx_21, 0), (dx_22, 0), (dx_23, 0), (dx_24, 0), (dx_25, 0)) diag_expanded(diagnosis, is_primary)
WHERE diagnosis IS NOT NULL AND diagnosis LIKE 'T%' ) AS diag_translated
WHERE diagnosis = 'All Drugs')



select * from dose_data ;
GO


