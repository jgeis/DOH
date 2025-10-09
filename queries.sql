-- Hybrid: supports long or wide diagnoses table
-- name: load_main_data
WITH dx_long AS (
  -- If table is already long (record_id, substance), use it.
  SELECT record_id, TRIM(substance) AS substance
  FROM diagnoses
  WHERE substance IS NOT NULL AND TRIM(substance) <> ''
),
dx_wide AS (
  -- If table is wide (one column per substance), unpivot via UNION ALLs.
  -- If these columns don't exist, SQLite will ignore this whole CTE at parse time with error,
  -- so keep names in sync with your schema. Tweak strings if yours differ.
  SELECT record_id, 'Alcohol' AS substance
  FROM diagnoses
  WHERE COALESCE(CAST("Alcohol" AS INTEGER), 0) = 1
     OR "Alcohol" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Nicotine'
  FROM diagnoses
  WHERE COALESCE(CAST("Nicotine" AS INTEGER), 0) = 1
     OR "Nicotine" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Other Stimulant (Includes Methamphetamine)'
  FROM diagnoses
  WHERE COALESCE(CAST("Other Stimulant (Includes Methamphetamine)" AS INTEGER), 0) = 1
     OR "Other Stimulant (Includes Methamphetamine)" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Cannabis'
  FROM diagnoses
  WHERE COALESCE(CAST("Cannabis" AS INTEGER), 0) = 1
     OR "Cannabis" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Other Psychoactive Substance'
  FROM diagnoses
  WHERE COALESCE(CAST("Other Psychoactive Substance" AS INTEGER), 0) = 1
     OR "Other Psychoactive Substance" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Opioid'
  FROM diagnoses
  WHERE COALESCE(CAST("Opioid" AS INTEGER), 0) = 1
     OR "Opioid" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Cocaine'
  FROM diagnoses
  WHERE COALESCE(CAST("Cocaine" AS INTEGER), 0) = 1
     OR "Cocaine" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Sedative, Hypnotic, or Anxiolytic'
  FROM diagnoses
  WHERE COALESCE(CAST("Sedative, Hypnotic, or Anxiolytic" AS INTEGER), 0) = 1
     OR "Sedative, Hypnotic, or Anxiolytic" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Hallucinogen'
  FROM diagnoses
  WHERE COALESCE(CAST("Hallucinogen" AS INTEGER), 0) = 1
     OR "Hallucinogen" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')

  UNION ALL
  SELECT record_id, 'Inhalant'
  FROM diagnoses
  WHERE COALESCE(CAST("Inhalant" AS INTEGER), 0) = 1
     OR "Inhalant" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
),
dx AS (
  -- Use whichever exists; DISTINCT prevents duplicates if both shapes exist.
  SELECT DISTINCT record_id, substance FROM dx_long
  UNION
  SELECT DISTINCT record_id, substance FROM dx_wide
)
SELECT
  dx.record_id,
  dx.substance,
  m.county, m.region, m.zip, m.residency,
  m.age_group, m.sex, m.calendar_year
FROM dx
JOIN demographics m ON m.record_id = dx.record_id;

-- name: load_filtered_data


-- name: load_polysubstance_data
WITH
dx_long AS (
  SELECT record_id, TRIM(substance) AS substance
  FROM diagnoses
  WHERE substance IS NOT NULL AND TRIM(substance) <> ''
),
dx_wide AS (
  SELECT record_id, 'Alcohol' AS substance
    FROM diagnoses WHERE COALESCE(CAST("Alcohol" AS INTEGER), 0) = 1
       OR "Alcohol" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Nicotine'
    FROM diagnoses WHERE COALESCE(CAST("Nicotine" AS INTEGER), 0) = 1
       OR "Nicotine" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Other Stimulant (Includes Methamphetamine)'
    FROM diagnoses WHERE COALESCE(CAST("Other Stimulant (Includes Methamphetamine)" AS INTEGER), 0) = 1
       OR "Other Stimulant (Includes Methamphetamine)" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Cannabis'
    FROM diagnoses WHERE COALESCE(CAST("Cannabis" AS INTEGER), 0) = 1
       OR "Cannabis" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Other Psychoactive Substance'
    FROM diagnoses WHERE COALESCE(CAST("Other Psychoactive Substance" AS INTEGER), 0) = 1
       OR "Other Psychoactive Substance" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Opioid'
    FROM diagnoses WHERE COALESCE(CAST("Opioid" AS INTEGER), 0) = 1
       OR "Opioid" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Cocaine'
    FROM diagnoses WHERE COALESCE(CAST("Cocaine" AS INTEGER), 0) = 1
       OR "Cocaine" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Sedative, Hypnotic, or Anxiolytic'
    FROM diagnoses WHERE COALESCE(CAST("Sedative, Hypnotic, or Anxiolytic" AS INTEGER), 0) = 1
       OR "Sedative, Hypnotic, or Anxiolytic" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Hallucinogen'
    FROM diagnoses WHERE COALESCE(CAST("Hallucinogen" AS INTEGER), 0) = 1
       OR "Hallucinogen" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Inhalant'
    FROM diagnoses WHERE COALESCE(CAST("Inhalant" AS INTEGER), 0) = 1
       OR "Inhalant" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
),
dx_union AS (
  SELECT DISTINCT record_id, TRIM(substance) AS substance FROM dx_long
  UNION
  SELECT DISTINCT record_id, TRIM(substance) AS substance FROM dx_wide
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
  m.county, m.region, m.zip, m.residency,
  m.age_group, m.sex,
  CAST(m.calendar_year AS INTEGER) AS calendar_year
FROM dx_union AS u
JOIN poly_ids AS p
  ON p.record_id = u.record_id
JOIN demographics AS m
  ON m.record_id = u.record_id
WHERE
  CAST(m.calendar_year AS INTEGER) BETWEEN 2018 AND 2024
  AND LOWER(COALESCE(NULLIF(TRIM(m.age_group), ''), 'unknown')) <> 'unknown';  -- drop Unknown/blank ages




-- name: load_sud_primary_mh_secondary_v2
WITH
sud_long AS (
  SELECT record_id, TRIM(substance) AS sud_substance, '' AS sud_pos
  FROM diagnoses
  WHERE substance IS NOT NULL AND TRIM(substance) <> ''
),
sud_wide AS (
  SELECT record_id, 'Alcohol' AS sud_substance, '' AS sud_pos
    FROM diagnoses WHERE COALESCE(CAST("Alcohol" AS INTEGER), 0) = 1
       OR "Alcohol" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Nicotine', '' FROM diagnoses
    WHERE COALESCE(CAST("Nicotine" AS INTEGER), 0) = 1
       OR "Nicotine" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Other Stimulant (Includes Methamphetamine)', '' FROM diagnoses
    WHERE COALESCE(CAST("Other Stimulant (Includes Methamphetamine)" AS INTEGER), 0) = 1
       OR "Other Stimulant (Includes Methamphetamine)" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Cannabis', '' FROM diagnoses
    WHERE COALESCE(CAST("Cannabis" AS INTEGER), 0) = 1
       OR "Cannabis" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Other Psychoactive Substance', '' FROM diagnoses
    WHERE COALESCE(CAST("Other Psychoactive Substance" AS INTEGER), 0) = 1
       OR "Other Psychoactive Substance" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Opioid', '' FROM diagnoses
    WHERE COALESCE(CAST("Opioid" AS INTEGER), 0) = 1
       OR "Opioid" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Cocaine', '' FROM diagnoses
    WHERE COALESCE(CAST("Cocaine" AS INTEGER), 0) = 1
       OR "Cocaine" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Sedative, Hypnotic, or Anxiolytic', '' FROM diagnoses
    WHERE COALESCE(CAST("Sedative, Hypnotic, or Anxiolytic" AS INTEGER), 0) = 1
       OR "Sedative, Hypnotic, or Anxiolytic" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Hallucinogen', '' FROM diagnoses
    WHERE COALESCE(CAST("Hallucinogen" AS INTEGER), 0) = 1
       OR "Hallucinogen" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
  UNION ALL SELECT record_id, 'Inhalant', '' FROM diagnoses
    WHERE COALESCE(CAST("Inhalant" AS INTEGER), 0) = 1
       OR "Inhalant" IN ('1','true','True','TRUE','yes','Yes','YES','y','Y','t','T')
),
sud_union AS (
  SELECT DISTINCT record_id, sud_substance, sud_pos FROM sud_long
  UNION
  SELECT DISTINCT record_id, sud_substance, sud_pos FROM sud_wide
),
mh_union AS (
  SELECT record_id, TRIM(mh_diagnosis) AS mh_dx, '' AS mh_pos
  FROM mh_diagnoses
  WHERE mh_diagnosis IS NOT NULL AND TRIM(mh_diagnosis) <> ''
),
co AS (
  SELECT s.record_id, s.sud_substance, m.mh_dx
  FROM sud_union s
  JOIN mh_union m ON m.record_id = s.record_id
)
SELECT
  co.record_id,
  co.sud_substance                    AS substance,
  co.mh_dx                            AS mh_diagnosis,
  d.county, d.region, d.zip, d.residency,
  d.age_group, d.sex,
  CAST(d.calendar_year AS INTEGER)    AS calendar_year
FROM co
JOIN demographics d ON d.record_id = co.record_id
WHERE CAST(d.calendar_year AS INTEGER) BETWEEN 2018 AND 2024
  AND LOWER(COALESCE(NULLIF(TRIM(d.age_group), ''), 'unknown')) <> 'unknown';
