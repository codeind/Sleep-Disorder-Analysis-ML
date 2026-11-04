-- The most repeated profiles: identical rows apart from person_id.
SELECT profile_key, COUNT(*) AS copies, MIN(sleep_disorder) AS sleep_disorder,
       MIN(occupation) AS occupation, MIN(bmi_category) AS bmi_category
FROM people
GROUP BY profile_key
HAVING COUNT(*) > 1
ORDER BY copies DESC
LIMIT 10;
