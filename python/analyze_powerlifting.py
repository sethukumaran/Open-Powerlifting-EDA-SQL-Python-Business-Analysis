"""
Powerlifting EDA + SQL/Python Business Analysis
Run from project root:
    python src/analyze_powerlifting.py

The script:
1) Loads data/meets.csv and data/openpowerlifting.csv
2) Performs Python EDA and data-quality checks
3) Loads both tables into SQLite
4) Executes SQL business queries from sql/analysis_queries.sql
5) Writes outputs/ and visualizations/
"""
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
VIZ = ROOT / "visualizations"
OUT.mkdir(exist_ok=True); VIZ.mkdir(exist_ok=True)

meets = pd.read_csv(DATA / "meets.csv", low_memory=False)
lifting = pd.read_csv(DATA / "openpowerlifting.csv", low_memory=False)
meets["Date"] = pd.to_datetime(meets["Date"], errors="coerce")

print("=== EDA ===")
print("Meets:", meets.shape)
print("Lifting:", lifting.shape)
print("Duplicate lifting rows:", lifting.duplicated().sum())
print("\nMissingness (%):")
print((lifting.isna().mean()*100).sort_values(ascending=False).round(2))
print("\nCategoricals:")
for c in ["Sex", "Equipment"]:
    print(c, lifting[c].value_counts(dropna=False).to_dict())

meet_map = meets.set_index("MeetID")
lifting["Year"] = lifting["MeetID"].map(meet_map["Date"].dt.year)
lifting["Federation"] = lifting["MeetID"].map(meet_map["Federation"])
lifting["MeetCountry"] = lifting["MeetID"].map(meet_map["MeetCountry"])
lifting["Date"] = lifting["MeetID"].map(meet_map["Date"])

for c in ["Age","BodyweightKg","BestSquatKg","BestBenchKg","BestDeadliftKg","TotalKg","Wilks"]:
    lifting[c] = pd.to_numeric(lifting[c], errors="coerce")

# Raw-data QA flags; negative best-lift values are retained and reported,
# rather than silently changing source data.
for c in ["BestSquatKg","BestBenchKg","BestDeadliftKg"]:
    print(f"Negative {c}:", int((lifting[c] < 0).sum()))

db = ROOT / "powerlifting_analysis.db"
con = sqlite3.connect(db)
meets.to_sql("meets", con, if_exists="replace", index=False)
lifting.to_sql("lifting", con, if_exists="replace", index=False)

sql = {
"annual_trend": """SELECT CAST(strftime('%Y', Date) Year), COUNT(DISTINCT MeetID) Meets,
COUNT(*) LifterEntries, COUNT(DISTINCT Name) UniqueLifters,
ROUND(AVG(TotalKg),2) AvgTotalKg, ROUND(AVG(Wilks),2) AvgWilks
FROM lifting WHERE Date IS NOT NULL GROUP BY 1 ORDER BY 1;""",
"equipment": """SELECT Equipment, COUNT(*) Entries, COUNT(DISTINCT Name) UniqueLifters,
ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM lifting),2) SharePct,
ROUND(AVG(TotalKg),2) AvgTotalKg FROM lifting GROUP BY Equipment ORDER BY Entries DESC;""",
"sex": """SELECT Sex, COUNT(*) Entries, COUNT(DISTINCT Name) UniqueLifters,
ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM lifting),2) SharePct,
ROUND(AVG(TotalKg),2) AvgTotalKg, ROUND(AVG(Wilks),2) AvgWilks
FROM lifting GROUP BY Sex ORDER BY Entries DESC;""",
"federation": """SELECT Federation, COUNT(DISTINCT MeetID) Meets, COUNT(*) Entries,
COUNT(DISTINCT Name) UniqueLifters, ROUND(AVG(TotalKg),2) AvgTotalKg,
ROUND(AVG(Wilks),2) AvgWilks FROM lifting GROUP BY Federation ORDER BY Entries DESC;""",
"country": """SELECT MeetCountry Country, COUNT(DISTINCT MeetID) Meets, COUNT(*) Entries,
COUNT(DISTINCT Name) UniqueLifters FROM lifting GROUP BY MeetCountry ORDER BY Meets DESC;"""
}
for name, q in sql.items():
    pd.read_sql_query(q, con).to_csv(OUT / f"{name}.csv", index=False)
con.close()
print("SQL outputs written to outputs/.")
