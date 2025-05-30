# Report on productivity of the queries.

## Original query analysis
```sql
-> Sort: avg_usage DESC  (actual time=27.9..28 rows=88 loops=1)
    -> Table scan on <temporary>  (actual time=27.8..27.8 rows=88 loops=1)
        -> Aggregate using temporary table  (actual time=27.8..27.8 rows=88 loops=1)
            -> Filter: ((s.Addicted_Score > 6) and (s.Sleep_Hours_Per_Night < 7))  (cost=72.2 rows=78.3) (actual time=0.406..0.984 rows=337 loops=1)
                -> Table scan on s  (cost=72.2 rows=705) (actual time=0.401..0.892 rows=705 loops=1)
-> Select #2 (subquery in projection; dependent)
    -> Aggregate: avg(sub.Mental_Health_Score)  (cost=1.76 rows=1) (actual time=0.039..0.039 rows=1 loops=337)
        -> Filter: ((sub.Country = s.Country) and (sub.Gender = s.Gender))  (cost=1.7 rows=0.653) (actual time=0.00804..0.0362 rows=15.1 loops=337)
            -> Index lookup on sub using country_idx (Country=s.Country)  (cost=1.7 rows=6.53) (actual time=0.00429..0.0305 rows=24.1 loops=337)
-> Select #3 (subquery in projection; dependent)
    -> Aggregate: count(0)  (cost=1.72 rows=1) (actual time=0.0347..0.0347 rows=1 loops=337)
        -> Filter: ((sub.Affects_Academic_Performance = 'Yes') and (sub.Country = s.Country) and (sub.Gender = s.Gender))  (cost=1.67 rows=0.419) (actual time=0.00796..0.0334 rows=13.7 loops=337)
            -> Index lookup on sub using country_idx (Country=s.Country)  (cost=1.67 rows=6.53) (actual time=0.00275..0.0275 rows=24.1 loops=337)

```

## Step 1:
Using CTEs instead of subselects, and, as a result, a great impact on actual time and complexity
```sql
-> Sort: avg_usage_hours DESC  (actual time=5.01..5.02 rows=88 loops=1)
    -> Table scan on <temporary>  (actual time=4.96..4.97 rows=88 loops=1)
        -> Aggregate using temporary table  (actual time=4.96..4.96 rows=88 loops=1)
            -> Left hash join (<hash>(mh.Gender)=<hash>(students.Gender)), (<hash>(mh.Country)=<hash>(students.Country)), extra conditions: (mh.Gender = students.Gender) and (mh.Country = students.Country)  (cost=297 rows=0) (actual time=3.34..4.38 rows=337 loops=1)
                -> Left hash join (<hash>(afs.Gender)=<hash>(students.Gender)), (<hash>(afs.Country)=<hash>(students.Country)), extra conditions: (afs.Gender = students.Gender) and (afs.Country = students.Country)  (cost=11 rows=0) (actual time=1.65..2.48 rows=337 loops=1)
                    -> Filter: ((students.Addicted_Score > 6) and (students.Sleep_Hours_Per_Night < 7))  (cost=72.2 rows=78.3) (actual time=0.0171..0.614 rows=337 loops=1)
                        -> Table scan on students  (cost=72.2 rows=705) (actual time=0.0131..0.532 rows=705 loops=1)
                    -> Hash
                        -> Table scan on afs  (cost=2.5..2.5 rows=0) (actual time=1.57..1.57 rows=90 loops=1)
                            -> Materialize CTE affected_students  (cost=0..0 rows=0) (actual time=1.57..1.57 rows=90 loops=1)
                                -> Table scan on <temporary>  (actual time=1.51..1.52 rows=90 loops=1)
                                    -> Aggregate using temporary table  (actual time=1.51..1.51 rows=90 loops=1)
                                        -> Index lookup on students using filtered_stds_idx (Affects_Academic_Performance='Yes'), with index condition: (students.Affects_Academic_Performance = 'Yes')  (cost=50.6 rows=453) (actual time=0.162..0.933 rows=453 loops=1)
                -> Hash
                    -> Table scan on mh  (cost=2.5..2.5 rows=0) (actual time=1.53..1.54 rows=132 loops=1)
                        -> Materialize CTE mental_health  (cost=0..0 rows=0) (actual time=1.53..1.53 rows=132 loops=1)
                            -> Table scan on <temporary>  (actual time=1.43..1.45 rows=132 loops=1)
                                -> Aggregate using temporary table  (actual time=1.43..1.43 rows=132 loops=1)
                                    -> Table scan on students  (cost=72.2 rows=705) (actual time=0.0209..0.503 rows=705 loops=1)
```

## Step 2:
Refactoring all CTEs into one, getting rid of multiple group bys and joins.
```sql
-> Sort: filtered_students.avg_usage_hours DESC  (cost=2.6..2.6 rows=0) (actual time=1.21..1.23 rows=88 loops=1)
    -> Table scan on filtered_students  (cost=2.5..2.5 rows=0) (actual time=1.16..1.17 rows=88 loops=1)
        -> Materialize CTE filtered_students  (cost=0..0 rows=0) (actual time=1.16..1.16 rows=88 loops=1)
            -> Table scan on <temporary>  (actual time=1.09..1.1 rows=88 loops=1)
                -> Aggregate using temporary table  (actual time=1.09..1.09 rows=88 loops=1)
                    -> Filter: ((students.Affects_Academic_Performance = 'Yes') and (students.Addicted_Score > 6) and (students.Sleep_Hours_Per_Night < 7))  (cost=72.2 rows=39.2) (actual time=0.0309..0.653 rows=337 loops=1)
                        -> Table scan on students  (cost=72.2 rows=705) (actual time=0.0271..0.537 rows=705 loops=1)
```

## Step 3:
Adding index for CTE, so that it works faster.

```sql
-> Sort: filtered_students.avg_usage_hours DESC  (cost=2.6..2.6 rows=0) (actual time=1.1..1.11 rows=88 loops=1)
    -> Table scan on filtered_students  (cost=2.5..2.5 rows=0) (actual time=1.06..1.07 rows=88 loops=1)
        -> Materialize CTE filtered_students  (cost=0..0 rows=0) (actual time=1.06..1.06 rows=88 loops=1)
            -> Table scan on <temporary>  (actual time=0.992..1 rows=88 loops=1)
                -> Aggregate using temporary table  (actual time=0.991..0.991 rows=88 loops=1)
                    -> Index range scan on students using filtered_stds_idx over (Affects_Academic_Performance = 'yes' AND 6 < Addicted_Score), with index condition: ((students.Affects_Academic_Performance = 'Yes') and (students.Addicted_Score > 6) and (students.Sleep_Hours_Per_Night < 7))  (cost=184 rows=408) (actual time=0.0255..0.583 rows=337 loops=1)
```