-- ==========================================
-- 1. Create the Physical Reporting Table
-- ==========================================
CREATE TABLE [dbo].[amhd_aggregate_month_reporting] (
    service_month_date DATE,
    service_category VARCHAR(100),
    co_category VARCHAR(100),
    County VARCHAR(100),
    total_service_encounters INT,
    unique_patients INT
);
GO -- Ends the first batch

-- ==========================================
-- 2. Add the Clustered Index for Performance
-- ==========================================
CREATE CLUSTERED INDEX CIX_amhd_aggregate_month 
ON [dbo].[amhd_aggregate_month_reporting](service_month_date, service_category, County);
GO -- Ends the second batch

-- ==========================================
-- 3. Create the Stored Procedure
-- ==========================================
CREATE PROCEDURE [dbo].[Refresh_AMHD_Aggregate_Month]
AS
BEGIN
    SET NOCOUNT ON;

    -- Wipe the table clean
    TRUNCATE TABLE [dbo].[amhd_aggregate_month_reporting];

    -- Repopulate the table with fresh data
    INSERT INTO [dbo].[amhd_aggregate_month_reporting] (
        service_month_date,
        service_category,
        co_category,
        County,
        total_service_encounters,
        unique_patients
    )
    SELECT 
        DATEFROMPARTS(YEAR(date_of_service), MONTH(date_of_service), 1),
        service_category,
        co_category,
        County,
        COUNT(*),
        COUNT(DISTINCT PATID)
    FROM [dbo].[AMHD_mh_services_view]
    GROUP BY 
        DATEFROMPARTS(YEAR(date_of_service), MONTH(date_of_service), 1),
        service_category,
        co_category,
        County;
    
END;
GO -- Ends the final batch

