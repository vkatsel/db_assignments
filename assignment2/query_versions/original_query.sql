-- this query was suggested by ChatGPT --

explain analyze
SELECT
  s.Country,
  s.Gender,
  AVG(s.Avg_Daily_Usage_Hours) AS avg_usage,
  (
    SELECT AVG(Mental_Health_Score)
    FROM students sub
    WHERE sub.Country = s.Country AND sub.Gender = s.Gender
  ) AS avg_mental_health,
  (
    SELECT COUNT(*)
    FROM students sub
    WHERE sub.Country = s.Country AND sub.Gender = s.Gender AND sub.Affects_Academic_Performance = 'Yes'
  ) AS affected_students
FROM students s
WHERE s.Addicted_Score > 6 AND s.Sleep_Hours_Per_Night < 7
GROUP BY s.Country, s.Gender
ORDER BY avg_usage DESC;
