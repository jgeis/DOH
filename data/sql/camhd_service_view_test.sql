/****** Object:  View [dbo].[camhd_service_view]    Script Date: 5/13/2026 2:53:51 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[camhd_service_view_test]
AS
WITH 
-- Create a massive list of numbers (up to ~65,000) very quickly
L0 AS (SELECT 1 AS c UNION ALL SELECT 1),
L1 AS (SELECT 1 AS c FROM L0 AS A CROSS JOIN L0 AS B),
L2 AS (SELECT 1 AS c FROM L1 AS A CROSS JOIN L1 AS B),
L3 AS (SELECT 1 AS c FROM L2 AS A CROSS JOIN L2 AS B),
L4 AS (SELECT 1 AS c FROM L3 AS A CROSS JOIN L3 AS B),
Numbers AS (SELECT ROW_NUMBER() OVER(ORDER BY (SELECT NULL)) - 1 AS n FROM L4),

-- Generate a clean list of dates starting from 2008
Dates AS (
    SELECT DATEADD(day, n, '2008-01-01') AS CalendarDate
    FROM Numbers
    WHERE DATEADD(day, n, '2008-01-01') <= CAST(GETDATE() AS DATE)
)

-- Simply JOIN the clients to the list of dates
SELECT 
    c.customerid AS client_id, 
    d.CalendarDate AS date
FROM dbo.CAMHD_Clients c
JOIN Dates d ON d.CalendarDate >= c.rsmhhs_startdate 
             AND d.CalendarDate <= CASE 
                                     WHEN c.rsmhhs_enddate IS NULL OR c.rsmhhs_enddate = '9999-09-09' 
                                     THEN CAST(GETDATE() AS DATE) 
                                     ELSE c.rsmhhs_enddate 
                                   END
WHERE c.rsmhhs_startdate IS NOT NULL 
  AND c.rsmhhs_startdate <> '9999-09-09';
GO


