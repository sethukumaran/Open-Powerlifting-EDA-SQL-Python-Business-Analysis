# Open Powerlifting — EDA, SQL & Python Business Analysis

## 1. Project objective

This project performs an end-to-end exploratory and business analysis of the OpenPowerlifting dataset using Python, pandas, matplotlib and SQLite SQL.
The analysis focuses on:
- participation and market growth
- federation and country concentration
- equipment mix
- male/female participation
- performance distributions and relationships
- top complete powerlifting totals
- data quality and analytical limitations

## 2. Dataset
Two source files are used:
- `data/meets.csv` — meet metadata
- `data/openpowerlifting.csv` — lifter-level results
Observed source size:
- **386,414 lifter-result rows**
- **8,482 meets**
- **136,687 unique lifter names**
- **60 federations**
- **45 countries**
- Date coverage: **1974-03-02 to 2018-01-28**

> Note: the dataset is historical and ends in early 2018, so this is not a current industry-market report.

## 3. Analytical workflow

### Python EDA
The Python workflow starts with:
1. shape and schema inspection
2. duplicate detection
3. missing-value profiling
4. descriptive statistics
5. categorical distributions
6. outlier/data-quality checks
7. derived fields such as year, federation and country

### SQL analysis
SQLite is used to answer business questions consistently and reproducibly. SQL queries are stored in `sql/analysis_queries.sql`.

### Visualization
Charts are generated into `visualizations/` using matplotlib.

## 4. Key business findings

### Growth and participation
- Meets increased from **264 in 2010** to **1,640 in 2017**, an approximate **29.8% CAGR** over 2010–2017.
- Lifter entries increased from **6,688 in 2010** to **108,682 in 2017**.
- The dataset therefore shows a major expansion in recorded competitive activity, especially after 2013.

### Gender participation
- Female lifter entries represented **17.4%** of entries in 2010 and **23.9%** in 2017.
- Across the full dataset, women account for **22.61%** of entries.
- This suggests meaningful growth in female participation, although the annual share is not monotonic because federation/event composition changes over time.

### Equipment mix
- Raw: **48.22%** of entries.
- Single-ply: **37.37%**.
- Wraps: **11.93%**.
- Multi-ply: **2.48%**.
- Equipment type is strongly associated with observed totals; this means raw totals should **not** be compared directly across equipment categories without segmentation.

### Geographic concentration
- **USA** is the dominant country by number of meets in this extract.
- The top countries are highly concentrated, so country-level trends should be interpreted as dataset participation/coverage rather than a complete measure of global powerlifting activity.

### Federation concentration
- **USAPL** is the largest federation by recorded lifter entries.
- Federation sizes and performance distributions vary substantially, making federation a critical segmentation dimension for benchmarking.

### Performance
- The highest complete positive total in the dataset is **1365.31 kg**.
- The highest Wilks value in the complete-positive subset is **779.38**.
- Squat, bench and deadlift are strongly correlated with total; this is expected mathematically because total is their sum, but it also confirms that complete lift-level data can be used for performance decomposition.

## 5. Data-quality findings

The dataset requires care before production KPI use:
- **545 exact duplicate rows** are present.
- Age is missing in approximately **61.92%** of rows.
- TotalKg is missing in approximately **6.00%** of rows.
- Wilks is missing in approximately **6.27%** of rows.
- Some `BestSquatKg`, `BestBenchKg` and `BestDeadliftKg` values are negative. These are retained as source-data QA flags rather than silently overwritten.
- Fourth-attempt fields are extremely sparse and should not be used as primary performance measures.

## 6. Important analytical interpretation

The strongest business signal is **rapid growth in recorded participation**, but the dataset is not a controlled panel of athletes or meets. Growth may reflect a combination of:
- actual sport participation growth
- improved data collection
- more federations contributing data
- changes in meet coverage
- changes in recording practices

Therefore, the safest business interpretation is **"growth in recorded competitive activity"**, not necessarily a causal estimate of global powerlifting growth.

## 7. Recommended business KPIs

For a recurring dashboard, track:
1. Meets per month/quarter
2. Unique lifters per period
3. New vs returning lifters
4. Female participation share
5. Entries by equipment
6. Entries and median total by federation
7. Entries and meets by country
8. Median total by sex + weight class + equipment
9. Data completeness rate
10. Top performance trends using a consistent eligibility rule

## 8. Conclusion

The analysis indicates that the recorded powerlifting ecosystem expanded dramatically during the later years of the dataset, with the sharpest increase in meets and lifter entries occurring from roughly 2013 onward. Participation is concentrated by country and federation, while equipment category materially changes observed strength totals and must be controlled for in any fair benchmarking. Female participation shows meaningful long-term growth, although yearly composition varies. From a data-engineering perspective, the dataset is valuable but requires explicit handling of duplicates, missing age/performance fields, negative best-lift values, and uneven historical coverage before being used for executive KPI reporting.
**Bottom line:** the dataset supports strong evidence of expanding recorded competitive activity and clear segmentation opportunities, but business conclusions should be framed around **recorded participation and performance patterns**, not interpreted as a complete causal picture of the global sport.
