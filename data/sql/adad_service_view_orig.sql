/****** Object:  View [dbo].[adad_service_view]    Script Date: 4/28/2026 11:31:29 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[adad_service_view] AS

WITH date_expand AS (
    SELECT unique_client_number as client_id, geo_description as county, modality_type_description as modality, start_date as date, end_date
    FROM WITS_Payor_Adjudication
    UNION ALL
    SELECT client_id, county, modality, DATEADD(day, 1, date) as date, end_date
        FROM date_expand
    WHERE date < end_date
)
SELECT client_id, county, modality, date
FROM date_expand;
GO


