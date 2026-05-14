-- ==========================================
-- 1. Create the ONE Master Dashboard Table
-- ==========================================
CREATE TABLE [dbo].[amhd_dashboard_fact] (
    PATID VARCHAR(255),
    service_date DATE,
    service_year INT,
    county VARCHAR(100),
    service_category VARCHAR(100)
);
GO

-- ==========================================
-- 2. Add an Index optimized for Date Filtering
-- ==========================================
CREATE CLUSTERED INDEX CIX_amhd_dashboard_fact 
ON [dbo].[amhd_dashboard_fact](service_date, service_year);
GO

-- ==========================================
-- 3. Create the Master Refresh Procedure
-- ==========================================
CREATE PROCEDURE [dbo].[Refresh_AMHD_Dashboard_Fact]
AS
BEGIN
    SET NOCOUNT ON;

    -- Wipe the table clean
    TRUNCATE TABLE [dbo].[amhd_dashboard_fact];

    -- Extract, clean, and deduplicate all the core dimensions at once!
    INSERT INTO [dbo].[amhd_dashboard_fact] (
        PATID,
        service_date,
        service_year,
        county,
        service_category
    )
    SELECT DISTINCT 
        PATID,
        CAST(date_of_service AS date),
        YEAR(date_of_service),
        UPPER(LTRIM(RTRIM(County))),
        LTRIM(RTRIM(service_category))
    FROM [dbo].[AMHD_mh_services_view];
    
END;
GO