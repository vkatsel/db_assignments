use assignment2;

CREATE INDEX filtered_stds_idx ON students (Affects_Academic_Performance, Addicted_Score, Sleep_Hours_Per_Night);

explain analyze
WITH filtered_students AS (
    SELECT
        Country,
        Gender,
        COUNT(*) AS affected_students,
        AVG(Mental_Health_Score) AS average_mental_health,
        AVG(Avg_Daily_Usage_Hours) AS avg_usage_hours
    FROM students FORCE INDEX (filtered_stds_idx)
    WHERE Affects_Academic_Performance = 'Yes' AND Addicted_Score > 6 AND Sleep_Hours_Per_Night < 7
    GROUP BY Country, Gender
)
SELECT
  Country,
  Gender,
  affected_students,
  avg_usage_hours,
  average_mental_health
FROM filtered_students
ORDER BY avg_usage_hours DESC;

-- Added index for CTE --

