CREATE VIEW [dbo].[amhd_mh_services_view] AS

WITH TaggedRecords AS (
    -- Step 1: Apply your human-readable case statements and clean the data
    SELECT 
        PATID,
        date_of_service,
        Diagnosis_code,
        SMI,
        Sex,
        Race,
        
        -- Clean the Age column by replacing "Age " with a blank string
        REPLACE(Age, 'Age ', '') AS Age,
        
        County,
        
        -- Your Service Category Logic
        CASE 
            WHEN program_X_RRG_value = 'Hawaii State Hospital' THEN 'Hawaii State Hospital'
            WHEN program_X_RRG_value = 'POS' THEN 'Contracted Providers'
            ELSE 'Community Mental Health Centers' 
        END AS service_category,
        
        -- Your Co-Category Logic
        CASE 
            WHEN LEFT(Diagnosis_code, 2) = 'F1' THEN 'Substance Use'
            WHEN LEFT(Diagnosis_code, 1) = 'F' THEN 'Mental Health'
            ELSE '' 
        END AS co_category,

        -- Create a hidden flag: 1 if this specific row is Mental Health, 0 if not
        CASE 
            WHEN LEFT(Diagnosis_code, 1) = 'F' AND LEFT(Diagnosis_code, 2) <> 'F1' THEN 1 
            ELSE 0 
        END AS is_mh_row

    FROM AMHD_dates_of_service
),
WindowedRecords AS (
    -- Step 2: Look across the patient's entire day to see if they triggered the flag
    SELECT 
        *,
        -- This checks every row for the same PATID and date. 
        -- If even one row has a 1, it assigns a 1 to ALL of their rows for that day.
        MAX(is_mh_row) OVER (PARTITION BY PATID, CAST(date_of_service AS DATE)) AS day_has_mh
    FROM TaggedRecords
)

-- Step 3: Return the final dataset
SELECT 
    PATID,
    date_of_service,
    service_category,
    co_category,
    Diagnosis_code,
    SMI,
    Sex,
    Race,
    Age, 
    County
FROM WindowedRecords
-- Keep every record where the patient had at least one MH flag that day
WHERE day_has_mh = 1;
GO