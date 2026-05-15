--Alaska Native (Aleut, Eskimo)' into 'Alaska Native (Aleut, Eskimo, Indian).'

select count(*) from dbo.teds_a_data_view;

--SELECT dbo.teds_a_data_view, [VIEW_DEFINITION]
--FROM [YOUR_DATABASE].[INFORMATION_SCHEMA].[VIEWS]

SELECT OBJECT_DEFINITION (OBJECT_ID(N'dbo.teds_a_data_view')); 

--CREATE VIEW 
--dbo.teds_a_data_view AS    
--select distinct    
--	Caseid,    
--	AgeAtAdmission,    
--	YearOfAdmission,    
--	Gender,    
--	SubstanceUsePrimary,    
--	SubstanceUseSecondary,    
--	SubstanceUseTertiary,    
--CASE 
--	WHEN SubstanceUsePrimary = '' Then 0    
--	WHEN SubstanceUseSecondary = '' THEN 1    
--	WHEN SubstanceUseTertiary = '' THEN 2    
--	Else 3    
--END as num_substances    
--from dbo.TEDS_A; 

------------------------------------------------------------------------------------------
------------Changing 'Asian or Pacific Islander' to 'Missing' for records > 2005 ---------
------------------------------------------------------------------------------------------

select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where RACE = 'Asian or Pacific Islander' and YearOfAdmission > 2005;
--2006	1870215	Asian Or Pacific Islander
--2006	1762451	Asian Or Pacific Islander
--2006	1690322	Asian Or Pacific Islander
--2006	1682738	Asian Or Pacific Islander
--2006	1771364	Asian Or Pacific Islander
--2006	1609837	Asian Or Pacific Islander
--2006	1530227	Asian Or Pacific Islander
--2006	1919946	Asian Or Pacific Islander
--2006	1955926	Asian Or Pacific Islander
--2008	1974337	Asian Or Pacific Islander
--2008	1681856	Asian Or Pacific Islander
--2008	1775090	Asian Or Pacific Islander
--2011	1529450	Asian Or Pacific Islander
--2011	1708468	Asian Or Pacific Islander
--2012	1564685	Asian Or Pacific Islander
--2012	1460237	Asian Or Pacific Islander

select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where YearOfAdmission > 2005 and Caseid IN (1870215, 1762451, 1690322, 1682738, 1771364, 1609837, 1530227, 1919946, 1955926, 1974337, 1681856, 1775090, 1529450, 1708468, 1564685, 1460237);
-- this was intended to make sure I was about to change only the correct records, it proved I was not.
-- used the next query to show what was going wrong

select Caseid, count(Caseid) from dbo.TEDS_A group by Caseid having count(*) > 1;
-- turns out the same Caseid can appear more than once

-- the above resulted in this new test, which shows only the correct records
select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where 
	(YearOfAdmission = 2006	and Caseid = 1870215 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1762451 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1690322 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1682738 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1771364 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1609837 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1530227 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1919946 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1955926 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2008 and Caseid = 1974337 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2008 and Caseid = 1681856 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2008 and Caseid = 1775090 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2011 and Caseid = 1529450 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2011 and Caseid = 1708468 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2012 and Caseid = 1564685 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2012 and Caseid = 1460237 and RACE = 'Asian Or Pacific Islander');

-- get the correct wording of the 'Missing' records
select distinct RACE from dbo.TEDS_A;
-- 'Missing/Unknown/Not Collected/Invalid'

-- the actual update, an edit of the preceeding query
update dbo.TEDS_A set RACE = 'Missing/Unknown/Not Collected/Invalid' where 
	(YearOfAdmission = 2006	and Caseid = 1870215 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1762451 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1690322 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1682738 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1771364 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1609837 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1530227 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1919946 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2006 and Caseid = 1955926 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2008 and Caseid = 1974337 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2008 and Caseid = 1681856 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2008 and Caseid = 1775090 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2011 and Caseid = 1529450 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2011 and Caseid = 1708468 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2012 and Caseid = 1564685 and RACE = 'Asian Or Pacific Islander')
	or (YearOfAdmission = 2012 and Caseid = 1460237 and RACE = 'Asian Or Pacific Islander');

-- verify
select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where 
	(YearOfAdmission = 2006	and Caseid = 1870215)
	or (YearOfAdmission = 2006 and Caseid = 1762451)
	or (YearOfAdmission = 2006 and Caseid = 1690322)
	or (YearOfAdmission = 2006 and Caseid = 1682738)
	or (YearOfAdmission = 2006 and Caseid = 1771364)
	or (YearOfAdmission = 2006 and Caseid = 1609837)
	or (YearOfAdmission = 2006 and Caseid = 1530227)
	or (YearOfAdmission = 2006 and Caseid = 1919946)
	or (YearOfAdmission = 2006 and Caseid = 1955926)
	or (YearOfAdmission = 2008 and Caseid = 1974337)
	or (YearOfAdmission = 2008 and Caseid = 1681856)
	or (YearOfAdmission = 2008 and Caseid = 1775090)
	or (YearOfAdmission = 2011 and Caseid = 1529450)
	or (YearOfAdmission = 2011 and Caseid = 1708468)
	or (YearOfAdmission = 2012 and Caseid = 1564685)
	or (YearOfAdmission = 2012 and Caseid = 1460237);
-- 16 rows affected 

------------------------------------------------------------------------------------------
-- Change 'Alaska Native (Aleut, Eskimo)' into 'Alaska Native (Aleut, Eskimo, Indian).' for records > 2005 ---------
------------------------------------------------------------------------------------------

-- get the set of records I need to change
select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where RACE = 'Alaska Native (Aleut, Eskimo)' and YearOfAdmission > 2005;
-- 2022	1433784	Alaska Native (Aleut, Eskimo)
-- 2022	1381164	Alaska Native (Aleut, Eskimo)
-- 2022	1177993	Alaska Native (Aleut, Eskimo)

-- pre-query to make sure I am about to change only the correct records 
select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where 
	(YearOfAdmission = 2022	and Caseid = 1433784 and RACE = 'Alaska Native (Aleut, Eskimo)')
	or (YearOfAdmission = 2022 and Caseid = 1381164 and RACE = 'Alaska Native (Aleut, Eskimo)')
	or (YearOfAdmission = 2022 and Caseid = 1177993 and RACE = 'Alaska Native (Aleut, Eskimo)');

-- the actual update, an edit of the immediately preceeding query
update dbo.TEDS_A set RACE = 'Alaska Native (Aleut, Eskimo, Indian)' where 
	(YearOfAdmission = 2022	and Caseid = 1433784 and RACE = 'Alaska Native (Aleut, Eskimo)')
	or (YearOfAdmission = 2022 and Caseid = 1381164 and RACE = 'Alaska Native (Aleut, Eskimo)')
	or (YearOfAdmission = 2022 and Caseid = 1177993 and RACE = 'Alaska Native (Aleut, Eskimo)');
-- 3 rows affected

-- verify
select YearOfAdmission, Caseid, RACE from dbo.TEDS_A where 
	(YearOfAdmission = 2022	and Caseid = 1433784)
	or (YearOfAdmission = 2022 and Caseid = 1381164)
	or (YearOfAdmission = 2022 and Caseid = 1177993);

-- another verification
select distinct RACE from dbo.TEDS_A;


------------------------------------------------------------------------------------------
-- TEDS_D: Change 'Alaska Native (Aleut, Eskimo)' into 'Alaska Native (Aleut, Eskimo, Indian).' for records > 2005 ---------
------------------------------------------------------------------------------------------
-- get the set of records I need to change
select YearOfDischarge, Caseid, RACE from dbo.TEDS_D where RACE = 'Alaska Native (Aleut, Eskimo)' and YearOfDischarge > 2005;
--2022	1523174	Alaska Native (Aleut, Eskimo)
--2022	1468127	Alaska Native (Aleut, Eskimo)
--2022	1237550	Alaska Native (Aleut, Eskimo)
--2022	1499281	Alaska Native (Aleut, Eskimo)
--2022	1522843	Alaska Native (Aleut, Eskimo)
--2022	1338623	Alaska Native (Aleut, Eskimo)
--2022	1210584	Alaska Native (Aleut, Eskimo)
--2022	1524439	Alaska Native (Aleut, Eskimo)
--2022	1457874	Alaska Native (Aleut, Eskimo)
--2022	1198977	Alaska Native (Aleut, Eskimo)

-- pre-query to make sure I am about to change only the correct records 
select YearOfDischarge, Caseid, RACE from dbo.TEDS_D where 
	YearOfDischarge = 2022 
	and RACE = 'Alaska Native (Aleut, Eskimo)'
  	and (Caseid = 1523174
	or Caseid = 1468127
	or Caseid = 1237550
	or Caseid = 1499281
	or Caseid = 1522843
	or Caseid = 1338623
	or Caseid = 1210584
	or Caseid = 1524439
	or Caseid = 1457874
	or Caseid = 1198977);

-- the actual update, an edit of the immediately preceeding query
update dbo.TEDS_D set RACE = 'Alaska Native (Aleut, Eskimo, Indian)' where 
	YearOfDischarge = 2022 
	and RACE = 'Alaska Native (Aleut, Eskimo)'
  	and (Caseid = 1523174
	or Caseid = 1468127
	or Caseid = 1237550
	or Caseid = 1499281
	or Caseid = 1522843
	or Caseid = 1338623
	or Caseid = 1210584
	or Caseid = 1524439
	or Caseid = 1457874
	or Caseid = 1198977);
-- 10 rows affected

-- verify
select YearOfDischarge, Caseid, RACE from dbo.TEDS_D where RACE = 'Alaska Native (Aleut, Eskimo)' and YearOfDischarge > 2005;

-- another verification
select distinct RACE from dbo.TEDS_D;

select distinct YearOfAdmission, count(YearOfAdmission) from dbo.TEDS_A where SubstanceUsePrimary = 'Over-The-Counter Medications' group by YearOfAdmission;

