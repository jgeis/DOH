/****** Object:  View [dbo].[teds_data_view]    Script Date: 10/1/2024 9:39:47 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [dbo].[teds_data_view] AS
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
GO


