-- SUDORS, expected numbers
-- Year	Sex		n	
-- 2023	female	8		
-- 2023	male	247/251	
-- 2024	female	82/82		
-- 2024	male	278/278	
-----------------------			
-- Year	HAWAII	HONOLULU	KAUAI	MAUI
-- 2023	43		206			24		53
-- 2024	61		234			16		49

select year, sex, count(Incident_ID)
from dbo.sudors_data_view_demographics$ 
where year = 2023 or year = 2024
group by year, sex
order by year, sex;

--dbo.sudors_data_view_demographics$
--dbo.sudors_data_view_demographics$$
--dbo.sudors_data_view_demographics_STAGING,
--dbo.sudors_demographics

--dbo.sudors_data_view_diag_su$
--dbo.sudors_data_view_diag_su_STAGING
--dbo.sudors_data_view_diagnosis_STAGING

--dbo.sudors_data_view_indicators$
--dbo.sudors_data_view_indicators_STAGING

select * from dbo.wonder_gender where year = 2023;
select * from dbo.wonder_overview;
