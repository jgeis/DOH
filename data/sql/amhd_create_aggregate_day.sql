-- ==========================================
-- 1. Create the Physical Reporting Table
-- ==========================================
CREATE TABLE [dbo].[amhd_aggregate_day_reporting] (
    service_date DATE,
    service_category VARCHAR(100),
    co_category VARCHAR(100),
    County VARCHAR(100),
    total_service_encounters INT,
    unique_patients INT
);
GO 

-- ==========================================
-- 2. Add the Clustered Index for Performance
-- ==========================================
CREATE CLUSTERED INDEX CIX_amhd_aggregate_day 
ON [dbo].[amhd_aggregate_day_reporting](service_date, service_category, County);
GO 

-- ==========================================
-- 3. Create the Stored Procedure
-- ==========================================
CREATE PROCEDURE [dbo].[Refresh_AMHD_Aggregate_Day]
AS
BEGIN
    SET NOCOUNT ON;

    -- Wipe the table clean
    TRUNCATE TABLE [dbo].[amhd_aggregate_day_reporting];

    -- Repopulate the table with fresh data
    INSERT INTO [dbo].[amhd_aggregate_day_reporting] (
        service_date,
        service_category,
        co_category,
        County,
        total_service_encounters,
        unique_patients
    )
    SELECT 
        CAST(date_of_service AS date) AS service_date,
        service_category,
        co_category,
        County,
        COUNT(*) AS total_service_encounters,
        COUNT(DISTINCT PATID) AS unique_patients
    FROM [dbo].[AMHD_mh_services_view]
    GROUP BY 
        CAST(date_of_service AS date),
        service_category,
        co_category,
        County;
    
END;
GO