-- Sleep duration and quality at each stress level.
SELECT stress_level,
       COUNT(*)                       AS people,
       ROUND(AVG(sleep_hours), 2)     AS avg_sleep_hours,
       ROUND(AVG(sleep_quality), 2)   AS avg_sleep_quality,
       ROUND(100.0 * AVG(sleep_disorder <> 'None'), 1) AS any_disorder_pct
FROM people
GROUP BY stress_level
ORDER BY stress_level;
