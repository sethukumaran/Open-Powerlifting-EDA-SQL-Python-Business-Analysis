
-- Powerlifting EDA & business analysis queries
-- SQLite-compatible

-- 1. Annual participation and performance trend
SELECT CAST(strftime('%Y', Date) AS INTEGER) AS Year,
       COUNT(DISTINCT MeetID) AS Meets,
       COUNT(*) AS LifterEntries,
       COUNT(DISTINCT Name) AS UniqueLifters,
       ROUND(AVG(TotalKg), 2) AS AvgTotalKg,
       ROUND(AVG(Wilks), 2) AS AvgWilks
FROM lifting
WHERE Date IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- 2. Federation scale and performance
SELECT Federation,
       COUNT(DISTINCT MeetID) AS Meets,
       COUNT(*) AS Entries,
       COUNT(DISTINCT Name) AS UniqueLifters,
       ROUND(AVG(TotalKg), 2) AS AvgTotalKg,
       ROUND(AVG(Wilks), 2) AS AvgWilks
FROM lifting
GROUP BY Federation
ORDER BY Entries DESC;

-- 3. Equipment mix
SELECT Equipment,
       COUNT(*) AS Entries,
       COUNT(DISTINCT Name) AS UniqueLifters,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM lifting), 2) AS SharePct,
       ROUND(AVG(TotalKg), 2) AS AvgTotalKg
FROM lifting
GROUP BY Equipment
ORDER BY Entries DESC;

-- 4. Geographic concentration
SELECT MeetCountry AS Country,
       COUNT(DISTINCT MeetID) AS Meets,
       COUNT(*) AS Entries,
       COUNT(DISTINCT Name) AS UniqueLifters
FROM lifting
GROUP BY MeetCountry
ORDER BY Meets DESC;

-- 5. Sex participation and performance
SELECT Sex,
       COUNT(*) AS Entries,
       COUNT(DISTINCT Name) AS UniqueLifters,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM lifting), 2) AS SharePct,
       ROUND(AVG(TotalKg), 2) AS AvgTotalKg,
       ROUND(AVG(Wilks), 2) AS AvgWilks
FROM lifting
GROUP BY Sex;

-- 6. Top verified complete totals
SELECT Name, Sex, Equipment, BodyweightKg,
       BestSquatKg, BestBenchKg, BestDeadliftKg,
       TotalKg, Wilks, Federation, Date
FROM lifting
WHERE TotalKg > 0
  AND BestSquatKg > 0
  AND BestBenchKg > 0
  AND BestDeadliftKg > 0
ORDER BY TotalKg DESC
LIMIT 20;

-- 7. Data quality
SELECT COUNT(*) AS Rows,
       SUM(CASE WHEN Age IS NULL THEN 1 ELSE 0 END) AS MissingAge,
       SUM(CASE WHEN BodyweightKg IS NULL THEN 1 ELSE 0 END) AS MissingBodyweight,
       SUM(CASE WHEN TotalKg IS NULL THEN 1 ELSE 0 END) AS MissingTotal,
       SUM(CASE WHEN Wilks IS NULL THEN 1 ELSE 0 END) AS MissingWilks,
       SUM(CASE WHEN BestSquatKg < 0 THEN 1 ELSE 0 END) AS NegativeBestSquat,
       SUM(CASE WHEN BestBenchKg < 0 THEN 1 ELSE 0 END) AS NegativeBestBench,
       SUM(CASE WHEN BestDeadliftKg < 0 THEN 1 ELSE 0 END) AS NegativeBestDeadlift
FROM lifting;
