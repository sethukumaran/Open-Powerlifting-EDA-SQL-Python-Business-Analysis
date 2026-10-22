"""
Powerlifting EDA + SQL/Python Business Analysis
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

## Number of meets by year
annual = (
    lifting
    .groupby("Year")
    .agg(
        Meets=("MeetID", "nunique"),
        LifterEntries=("Name", "count"),
        UniqueLifters=("Name", "nunique")
    )
    .reset_index()
)
plt.figure(figsize=(12, 6))
plt.plot(
    annual["Year"],
    annual["Meets"],
    marker="o",
    linewidth=2
)
plt.title("Powerlifting Meets by Year")
plt.xlabel("Year")
plt.ylabel("Number of Meets")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(
    "visualizations/01_meets_by_year.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Unique lifters by year
plt.figure(figsize=(12, 6))

plt.plot(
    annual["Year"],
    annual["UniqueLifters"],
    marker="o",
    linewidth=2
)
plt.title("Unique Powerlifters by Year")
plt.xlabel("Year")
plt.ylabel("Unique Lifters")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    "visualizations/02_unique_lifters_by_year.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Equipment participation mix

equipment = (
    lifting["Equipment"]
    .value_counts()
    .reset_index()
)
equipment.columns = ["Equipment", "Entries"]
plt.figure(figsize=(10, 6))
plt.bar(
    equipment["Equipment"],
    equipment["Entries"]
)
plt.title("Lifter Entries by Equipment")
plt.xlabel("Equipment")
plt.ylabel("Number of Entries")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(
    "visualizations/03_equipment_mix.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Sex participation
sex = (
    lifting["Sex"]
    .value_counts()
    .reset_index()
)
sex.columns = ["Sex", "Entries"]
plt.figure(figsize=(8, 6))
plt.bar(
    sex["Sex"],
    sex["Entries"]
)
plt.title("Lifter Entries by Sex")
plt.xlabel("Sex")
plt.ylabel("Number of Entries")
plt.tight_layout()
plt.savefig(
    "visualizations/04_sex_mix.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Top 10 federations
federation = (
    lifting
    .groupby("Federation")
    .agg(
        Entries=("Name", "count"),
        UniqueLifters=("Name", "nunique"),
        Meets=("MeetID", "nunique")
    )
    .reset_index()
    .sort_values("Entries", ascending=False)
)
top_federations = federation.head(10).sort_values("Entries")
plt.figure(figsize=(10, 7))
plt.barh(
    top_federations["Federation"],
    top_federations["Entries"]
)
plt.title("Top 10 Federations by Lifter Entries")
plt.xlabel("Lifter Entries")
plt.ylabel("Federation")
plt.tight_layout()
plt.savefig(
    "visualizations/05_top_federations.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Top 10 countries by number of meets

country = (
    lifting
    .groupby("MeetCountry")
    .agg(
        Meets=("MeetID", "nunique"),
        Entries=("Name", "count"),
        UniqueLifters=("Name", "nunique")
    )
    .reset_index()
    .sort_values("Meets", ascending=False)
)
top_countries = country.head(10).sort_values("Meets")
plt.figure(figsize=(10, 7))
plt.barh(
    top_countries["MeetCountry"],
    top_countries["Meets"]
)
plt.title("Top 10 Countries by Number of Meets")
plt.xlabel("Number of Meets")
plt.ylabel("Country")
plt.tight_layout()
plt.savefig(
    "visualizations/06_top_countries.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Bodyweight vs total — performance relationship

performance = lifting[
    (lifting["BodyweightKg"] > 0) &
    (lifting["TotalKg"] > 0)
].copy()
plt.figure(figsize=(10, 7))
plt.scatter(
    performance["BodyweightKg"],
    performance["TotalKg"],
    alpha=0.15,
    s=12
)
plt.title("Bodyweight vs Powerlifting Total")
plt.xlabel("Bodyweight (kg)")
plt.ylabel("Total (kg)")
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(
    "visualizations/07_bodyweight_vs_total.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Median total by equipment
complete_lifters = lifting[
    (lifting["TotalKg"] > 0) &
    (lifting["BestSquatKg"] > 0) &
    (lifting["BestBenchKg"] > 0) &
    (lifting["BestDeadliftKg"] > 0)
].copy()
equipment_performance = (
    complete_lifters
    .groupby("Equipment")["TotalKg"]
    .median()
    .sort_values(ascending=False)
)
plt.figure(figsize=(10, 6))
plt.bar(
    equipment_performance.index,
    equipment_performance.values
)
plt.title("Median Powerlifting Total by Equipment")
plt.xlabel("Equipment")
plt.ylabel("Median Total (kg)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(
    "visualizations/08_median_total_by_equipment.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Additional visualization: total distribution

total_data = lifting[
    lifting["TotalKg"] > 0
]["TotalKg"].dropna()
plt.figure(figsize=(10, 6))
plt.hist(
    total_data,
    bins=50,
    edgecolor="black"
)
plt.title("Distribution of Powerlifting Totals")
plt.xlabel("Total (kg)")
plt.ylabel("Number of Lifter Entries")
plt.tight_layout()
plt.savefig(
    "visualizations/10_total_distribution.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Age distribution

age_data = lifting[
    (lifting["Age"] > 0) &
    (lifting["Age"] < 100)
]["Age"].dropna()
plt.figure(figsize=(10, 6))
plt.hist(
    age_data,
    bins=30,
    edgecolor="black"
)
plt.title("Age Distribution of Powerlifters")
plt.xlabel("Age")
plt.ylabel("Number of Lifter Entries")
plt.tight_layout()
plt.savefig(
    "visualizations/11_age_distribution.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Squat, bench and deadlift comparison
lift_columns = [
    "BestSquatKg",
    "BestBenchKg",
    "BestDeadliftKg"
]
median_lifts = (
    complete_lifters[lift_columns]
    .median()
)
median_lifts.index = [
    "Squat",
    "Bench",
    "Deadlift"
]
plt.figure(figsize=(9, 6))
plt.bar(
    median_lifts.index,
    median_lifts.values
)
plt.title("Median Best Lift")
plt.xlabel("Lift")
plt.ylabel("Weight (kg)")
plt.tight_layout()
plt.savefig(
    "visualizations/12_median_lifts.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

## Annual average total
annual_performance = (
    complete_lifters
    .groupby("Year")
    .agg(
        AverageTotal=("TotalKg", "mean"),
        MedianTotal=("TotalKg", "median")
    )
    .reset_index()
)
plt.figure(figsize=(12, 6))
plt.plot(
    annual_performance["Year"],
    annual_performance["AverageTotal"],
    marker="o",
    label="Average Total"
)
plt.plot(
    annual_performance["Year"],
    annual_performance["MedianTotal"],
    marker="o",
    label="Median Total"
)
plt.title("Powerlifting Performance Trend")
plt.xlabel("Year")
plt.ylabel("Total (kg)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    "visualizations/13_performance_trend.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
