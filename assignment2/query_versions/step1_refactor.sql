explain analyze
WITH mental_health AS (
    SELECT
        Country,
        Gender,
        AVG(Mental_Health_Score) AS average_mental_health
    FROM students
    GROUP BY Country, Gender
),
affected_students AS (
    SELECT
        Country,
        Gender,
        COUNT(*) AS affected_students
    FROM students
    WHERE Affects_Academic_Performance = 'Yes'
    GROUP BY Country, Gender
),
filtered_students AS (
    SELECT * FROM students
    WHERE Addicted_Score > 6 AND Sleep_Hours_Per_Night < 7
)
SELECT
  s.Country,
  s.Gender,
  AVG(s.Avg_Daily_Usage_Hours) AS avg_usage_hours,
  COALESCE(afs.affected_students, 0) AS affected_students,
  mh.average_mental_health
FROM filtered_students s
LEFT JOIN affected_students afs ON afs.Country = s.Country AND afs.Gender = s.Gender
LEFT JOIN mental_health mh ON mh.Country = s.Country AND mh.Gender = s.Gender
GROUP BY s.Country, s.Gender, afs.affected_students, mh.average_mental_health
ORDER BY avg_usage_hours DESC;

-- Converted subselects into CTEs --