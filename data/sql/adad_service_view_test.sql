CREATE VIEW [dbo].[adad_service_view_test] AS

-- 1. Create a lightning-fast list of numbers from 0 to 10,000 without recursion
WITH E1(N) AS (SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1 UNION ALL SELECT 1), -- 10 rows
E2(N) AS (SELECT 1 FROM E1 a, E1 b), -- 100 rows
E4(N) AS (SELECT 1 FROM E2 a, E2 b), -- 10,000 rows
Tally(N) AS (
    SELECT TOP (10000) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 FROM E4
)
-- 2. Join your table to the numbers, expanding the dates
SELECT 
    w.unique_client_number AS client_id, 
    w.geo_description AS county, 
    w.modality_type_description AS modality, 
    DATEADD(day, t.N, w.start_date) AS date
FROM WITS_Payor_Adjudication w
JOIN Tally t 
    -- This acts as your loop. It grabs numbers 0 through X, where X is the difference in days.
    ON t.N <= DATEDIFF(day, w.start_date, w.end_date);
GO