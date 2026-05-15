SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[amhd_aggregate_year]
AS
SELECT 
    YEAR(date_of_service) AS service_year,
    service_category,
    co_category,
    County,
    COUNT(*) AS total_service_encounters,
    COUNT(DISTINCT PATID) AS unique_patients
FROM AMHD_mh_services_view
GROUP BY 
    YEAR(date_of_service),
	  service_category,
	  co_category,
	  County;
GO