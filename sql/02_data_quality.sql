-- Data quality checks and facts about the data.
SELECT 'people' AS item, COUNT(*) AS value FROM people
UNION ALL SELECT 'unique profiles', COUNT(DISTINCT profile_key) FROM people
UNION ALL SELECT 'rows that repeat an earlier profile', COUNT(*) - COUNT(DISTINCT profile_key) FROM people
UNION ALL SELECT 'systolic below diastolic (should be 0)', COUNT(*) FROM people WHERE bp_systolic <= bp_diastolic
UNION ALL SELECT 'duplicate person IDs (should be 0)', COUNT(*) - COUNT(DISTINCT person_id) FROM people;
