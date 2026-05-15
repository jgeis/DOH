/****** Object:  View [dbo].[teds_d_data_view]    Script Date: 10/1/2024 9:39:47 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [dbo].[teds_d_data_view] AS
select distinct
  Caseid,
  AgeAtDischarge,
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
from import.TEDS_D;
GO



  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN ROUTE3 VARCHAR(80);   
  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN ROUTE2 VARCHAR(80);   
  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN ROUTE1 VARCHAR(80);   
  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN REASON VARCHAR(70);   
  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN PRIMPAY VARCHAR(100);   
  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN EDUC VARCHAR(90);   
  ALTER TABLE dbo.TEDS_D_2025_04_11 ALTER COLUMN DSMCRIT VARCHAR(80);  

  select distinct SubstanceUsePrimary from dbo.TEDS_D;

  select * from dbo.TEDS_D where SubstanceUsePrimary = 'Pcp';
 select * from dbo.teds_d_data_view where SubstanceUsePrimary = 'Pcp';

  update dbo.TEDS_D set SubstanceUsePrimary = 'PCP' where SubstanceUsePrimary = 'Pcp';
  update dbo.TEDS_D set SubstanceUseSecondary = 'PCP' where SubstanceUseSecondary = 'Pcp';
  update dbo.TEDS_D set SubstanceUseTertiary = 'PCP' where SubstanceUseTertiary = 'Pcp';
  
  
  select * from dbo.TEDS_D where SubstanceUsePrimary = '';
