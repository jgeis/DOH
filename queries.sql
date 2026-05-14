-- name: load_discharge_data_view_diag_su
WITH dx AS (
  SELECT DISTINCT record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT
  dx.record_id,
  dx.substance,
  m.county, 
  m.city, 
  m.zip, 
  m.hawaii_residency,
  m.age_group, 
  m.sex, 
  m.race_ethnicity,
  m.year
FROM dx
JOIN discharge_data_view_demographics_test m ON m.record_id = dx.record_id;


-- name: load_polysubstance_data
WITH
dx_union AS (
  SELECT DISTINCT record_id, TRIM(diagnosis) AS substance
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
),
poly_ids AS (
  -- polysubstance = ≥2 distinct substances
  SELECT record_id
  FROM dx_union
  GROUP BY record_id
  HAVING COUNT(DISTINCT substance) >= 2
)
SELECT
  u.record_id,
  u.substance,
  m.county, m.city, m.zip, m.hawaii_residency,
  m.age_group, m.sex, m.race_ethnicity,
  CAST(m.year AS INTEGER) AS year
FROM dx_union AS u
JOIN poly_ids AS p
  ON p.record_id = u.record_id
JOIN discharge_data_view_demographics_test AS m
  ON m.record_id = u.record_id
WHERE
  LOWER(COALESCE(NULLIF(TRIM(m.age_group), ''), 'unknown')) <> 'unknown';  -- drop Unknown/blank ages


-- name: load_sud_primary_mh_secondary_v2
WITH
sud_union AS (
  SELECT DISTINCT record_id, TRIM(diagnosis) AS sud_substance, '' AS sud_pos
  FROM discharge_data_view_diag_su
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
),
mh_union AS (
  SELECT record_id, TRIM(diagnosis) AS mh_dx, '' AS mh_pos
  FROM discharge_data_view_diag_mh
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
),
co AS (
  SELECT s.record_id, s.sud_substance, m.mh_dx
  FROM sud_union s
  JOIN mh_union m ON m.record_id = s.record_id
)
SELECT
  co.record_id,
  co.sud_substance                    AS su_diagnosis,
  co.mh_dx                            AS mh_diagnosis,
  d.county, d.city, d.zip, d.hawaii_residency,
  d.age_group, d.sex, d.race_ethnicity,
  CAST(d.year AS INTEGER)    AS year
FROM co
JOIN discharge_data_view_demographics_test d ON d.record_id = co.record_id
WHERE LOWER(COALESCE(NULLIF(TRIM(d.age_group), ''), 'unknown')) <> 'unknown'; -- removed hardcoded year filter


-- name: load_dose_data
WITH dx AS (
  SELECT DISTINCT record_id, TRIM(diagnosis) AS substance
  FROM dose_data
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT
  dx.record_id,
  dx.substance,
  m.county,
  m.city,
  m.zip,
  m.hawaii_residency,
  m.age_group,
  m.sex,
  m.race_ethnicity,
  m.year
FROM dx
JOIN discharge_data_view_demographics_test m ON m.record_id = dx.record_id;


-- name: load_sudors_data_view_diag_su$
WITH dx AS (
  SELECT DISTINCT incident_id, TRIM(diagnosis) AS substance
  FROM sudors_data_view_diag_su$
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
)
SELECT
  dx.incident_id,
  dx.substance,
  m.homeless,
  m.sex, 
  m.age_cat, 
  m.race_ethnicity,
  m.year
FROM dx
JOIN sudors_data_view_demographics$ m ON m.incident_id = dx.incident_id;


-- name: load_sudors_polysubstance_data
WITH
dx_union AS (
  SELECT DISTINCT incident_id, TRIM(diagnosis) AS substance
  FROM sudors_data_view_diag_su$
  WHERE diagnosis IS NOT NULL AND TRIM(diagnosis) <> ''
),
poly_ids AS (
  -- polysubstance = ≥2 distinct substances
  SELECT incident_id
  FROM dx_union
  GROUP BY incident_id
  HAVING COUNT(DISTINCT substance) >= 2
)
SELECT
  u.incident_id,
  u.substance,
  m.homeless,
  m.sex,
  m.age_cat,
  m.race_ethnicity,
  CAST(m.year AS INTEGER) AS year
FROM dx_union AS u
JOIN poly_ids AS p
  ON p.incident_id = u.incident_id
JOIN sudors_data_view_demographics$ AS m
  ON m.incident_id = u.incident_id
WHERE
  LOWER(COALESCE(NULLIF(TRIM(m.age_cat), ''), 'unknown')) <> 'unknown';  -- drop Unknown/blank ages


-- name: load_wonder_overview
SELECT
  CAST(year AS INTEGER) AS year,
  county,
  CAST(deaths AS INTEGER) AS deaths
FROM wonder_overview
WHERE year IS NOT NULL;


-- name: load_wonder_substance
SELECT
  CAST(year AS INTEGER) AS year,
  county,
  substance,
  CAST(deaths AS INTEGER) AS deaths
FROM wonder_substance
WHERE year IS NOT NULL;


-- name: load_wonder_race
SELECT
  CAST(year AS INTEGER) AS year,
  county,
  race,
  CAST(deaths AS INTEGER) AS deaths
FROM wonder_race
WHERE year IS NOT NULL;


-- name: load_wonder_age_group
SELECT
  CAST(year AS INTEGER) AS year,
  county,
  age_group,
  CAST(deaths AS INTEGER) AS deaths,
  precedence
FROM wonder_age_group
WHERE year IS NOT NULL;


-- name: load_wonder_gender
SELECT
  CAST(year AS INTEGER) AS year,
  county,
  gender,
  CAST(deaths AS INTEGER) AS deaths
FROM wonder_gender
WHERE year IS NOT NULL;


-- name: load_cares_calls
SELECT
  Date as day,
  phone as origin_of_call,
  CAST(total_calls AS INTEGER) AS count_of_users
FROM cares_calls_volume_view
WHERE Date IS NOT NULL;


-- name: load_discharge_data_view_diagnosis
WITH dx_union AS (
 SELECT DISTINCT
   record_id,
   TRIM(diagnosis) AS diagnosis,
   diagnosis_type,
   is_primary
 FROM discharge_data_view_diagnosis
 WHERE diagnosis IS NOT NULL
   AND TRIM(diagnosis) <> ''
),
co_ids AS (
 SELECT record_id
 FROM dx_union
 GROUP BY record_id
)
SELECT
 u.record_id,
 u.diagnosis,
 u.diagnosis_type,
 u.is_primary,
 m.county,
 m.city,
 m.zip,
 m.hawaii_residency,
 m.age_group,
 m.sex,
 m.race_ethnicity,
 CAST(m.year AS INTEGER) AS year
FROM dx_union u
JOIN co_ids c
 ON c.record_id = u.record_id
JOIN discharge_data_view_demographics_test m
 ON m.record_id = u.record_id
WHERE LOWER(COALESCE(NULLIF(TRIM(m.age_group), ''), 'unknown')) <> 'unknown';


-- name: load_crisis_mobile_outreach
WITH CrisisMobileOutreach AS (
    -- Step 1: Filter the dates and map the names
    SELECT 
        PATID,
        CASE 
            WHEN CMOReferralTo_Value IN ('Castle ER', 'Other ER', 'Queens ER') THEN 'Emergency Rooms'
            WHEN CMOReferralTo_Value = 'BHCC' THEN 'Behavioral Health Crisis Center'
            WHEN CMOReferralTo_Value = 'CSM' THEN 'Crisis Support Management'
            WHEN CMOReferralTo_Value = 'Family / Friends' THEN 'Parents/Family/Friends'
            WHEN CMOReferralTo_Value IN ('LCRS', 'Stabilization Bed') THEN 'Licensed Crisis Residential Services and Stabilization Beds'
            ELSE CMOReferralTo_Value 
        END AS referral_destination
    FROM AMHD_Crisis_Mobile_Outreach
    -- DATEADD subtracts 6 months from today's date
    WHERE DispatchDate >= DATEADD(month, -6, CAST(GETDATE() AS DATE))
),
GroupedCounts AS (
    -- Step 2: Get the distinct counts per destination
    SELECT 
        referral_destination,
        COUNT(DISTINCT PATID) AS ct
    FROM CrisisMobileOutreach
    GROUP BY referral_destination
)
-- Step 3: Calculate the final percentage
SELECT 
    referral_destination,
    ct,
    ROUND((ct * 100.0) / SUM(ct) OVER (), 2) AS percentage
FROM GroupedCounts
ORDER BY ct DESC;


-- name: crisis-bed-occupancy
SELECT 
    FORMAT(DispatchDate, 'yyyy-MM') AS dispatch_month, 
    program_county_value, 
    COUNT(DISTINCT PATID) AS bed_ct 
FROM AMHD_Crisis_Mobile_Outreach 
WHERE CMOReferralTo_Value = 'LCRS' 
  AND DispatchDate >= DATEADD(month, -12, CAST(GETDATE() AS DATE)) 
GROUP BY 
    FORMAT(DispatchDate, 'yyyy-MM'), 
    program_county_value 
ORDER BY 
    dispatch_month ASC, 
    program_county_value ASC;


-- name: load_adad_clients_served
SELECT
  client_id,
  county,
  modality,
  [date] AS service_date
FROM adad_service_view
WHERE [date] IS NOT NULL;


-- name: load_adad_cooccurring
select 
  sv.client_id, 
  sv.county, 
  sv.modality, 
  sv.date, 
  iv.num_su, 
  iv.num_mh, 
  iv.su_primary, 
  iv.mh_primary
from adad_service_view as sv
inner join adad_indicators_view iv 
on 
  sv.client_id = iv.client_id
  and iv.num_mh >= 1
  and iv.num_su >= 1;


-- name: load_amhd_year
SELECT 
  service_year,
  service_category,
  co_category,
  County,
  total_service_encounters,
  unique_patients
FROM amhd_aggregate_year_reporting;

-- name: load_amhd_month
SELECT 
  service_month_date,
  service_category,
  co_category,
  County,
  total_service_encounters,
  unique_patients
FROM amhd_aggregate_month_reporting;

-- name: load_amhd_day
SELECT 
  service_date,
  service_category,
  co_category,
  County,
  total_service_encounters,
  unique_patients
FROM amhd_aggregate_day_reporting;

-- Calendar Year Total Query
-- name: load_amhd_consumers_total
SELECT
  COUNT(DISTINCT PATID) AS total_consumers
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters};

-- Calendar Year Query
-- name: load_amhd_consumers_by_year
SELECT 
  {year_expr} AS year,
  COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {year_expr}
ORDER BY year DESC;

-- Calendar Year + County Query
-- name: load_amhd_consumers_by_year_and_county
SELECT
  {year_expr} AS year,
  {county_expr} AS county,
  COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {year_expr}, {county_expr}
ORDER BY year DESC, county;

-- Month Query
-- name: load_amhd_consumers_by_month
SELECT
  {month_period_expr} AS period_date,
  COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {month_period_expr}
ORDER BY period_date;

-- Month + County Query
-- name: load_amhd_consumers_by_month_and_county
SELECT
  {month_period_expr} AS period_date,
  {county_expr} AS county,
  COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {month_period_expr}, {county_expr}
ORDER BY period_date, county;

-- Service Category Query
-- name: load_amhd_consumers_by_service_category
SELECT 
  {service_category_expr} AS service_category,
  COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {service_category_expr}
ORDER BY consumer_count DESC;

-- Date & County Query
-- name: load_amhd_consumers_by_date_and_county
SELECT 
  {day_period_expr} AS service_date,
  {county_expr} AS county,
    COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {day_period_expr}, {county_expr}
ORDER BY service_date, county;

-- Date Only Query
-- name: load_amhd_consumers_by_date
SELECT 
  {day_period_expr} AS service_date,
    COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {day_period_expr}
ORDER BY service_date;

-- County Consumer Count Query
-- name: load_amhd_consumers_by_county
SELECT 
  {county_expr} AS county,
    COUNT(DISTINCT PATID) AS consumer_count
FROM amhd_dashboard_fact
WHERE 1=1
{where_filters}
GROUP BY {county_expr}
ORDER BY county;

-- name: load_camhd_clients_served
SELECT
  client_id,
  [date] AS service_date
FROM camhd_service_view_test
WHERE [date] IS NOT NULL;

-- name: load_camhd_cooccurring
SELECT
  client_id,
  date AS service_date
FROM camhd_co_mh_su_view
WHERE date IS NOT NULL;