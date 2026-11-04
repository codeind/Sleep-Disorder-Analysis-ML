-- Share of each sleep disorder within each gender, BMI category and occupation.
WITH g AS (
    SELECT 'Gender' AS dimension, gender AS grp, sleep_disorder FROM people
    UNION ALL SELECT 'BMI category', bmi_category, sleep_disorder FROM people
    UNION ALL SELECT 'Occupation', occupation, sleep_disorder FROM people
    UNION ALL SELECT 'Age group',
        CASE WHEN age < 35 THEN '27-34' WHEN age < 45 THEN '35-44' WHEN age < 55 THEN '45-54' ELSE '55-59' END,
        sleep_disorder FROM people
)
SELECT
    dimension, grp,
    COUNT(*)                                                         AS people,
    ROUND(100.0 * AVG(sleep_disorder = 'None'), 1)                   AS none_pct,
    ROUND(100.0 * AVG(sleep_disorder = 'Insomnia'), 1)               AS insomnia_pct,
    ROUND(100.0 * AVG(sleep_disorder = 'Sleep Apnea'), 1)            AS sleep_apnea_pct,
    ROUND(100.0 * AVG(sleep_disorder <> 'None'), 1)                  AS any_disorder_pct
FROM g
GROUP BY dimension, grp
ORDER BY dimension, any_disorder_pct DESC;
