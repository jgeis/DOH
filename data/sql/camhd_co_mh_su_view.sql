/****** Object:  View [dbo].[camhd_co_mh_su_view]    Script Date: 5/13/2026 2:53:51 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[camhd_co_mh_su_view]
AS 
select distinct
	csvt.client_id,
	csvt.date
from 
	dbo.camhd_service_view_test csvt
	inner join dbo.camhd_indicators_view civ
		on civ.client_id = csvt.client_id
		where civ.num_su >= 1 and civ.num_mh >= 1;
GO


