-- How common each sleep disorder is, with average sleep and health measures for each group.
SELECT
    sleep_disorder,
    COUNT(*)                                            AS people,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS share_pct,
    ROUND(AVG(sleep_hours), 2)      AS avg_sleep_hours,
    ROUND(AVG(sleep_quality), 2)    AS avg_sleep_quality,
    ROUND(AVG(stress_level), 2)     AS avg_stress,
    ROUND(AVG(activity_minutes), 1) AS avg_activity_minutes,
    ROUND(AVG(daily_steps), 0)      AS avg_daily_steps,
    ROUND(AVG(heart_rate), 1)       AS avg_heart_rate,
    ROUND(AVG(bp_systolic), 1)      AS avg_bp_systolic,
    ROUND(AVG(age), 1)              AS avg_age
FROM people
GROUP BY sleep_disorder
ORDER BY people DESC;
