import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Load data ──────────────────────────────────────────────
df = pd.read_csv('/mnt/user-data/uploads/WA_Fn-UseC_-HR-Employee-Attrition.csv')
df.columns = df.columns.str.strip()

# ── SQLite in-memory DB ────────────────────────────────────
conn = sqlite3.connect(':memory:')
df.to_sql('employees', conn, index=False, if_exists='replace')

# ── Query runner ───────────────────────────────────────────
def run(sql):
    return pd.read_sql_query(sql, conn)

# ══════════════════════════════════════════════════════════════
# ANALYSIS
# ══════════════════════════════════════════════════════════════

# Q1: Overall attrition rate
q1 = run("""
    SELECT
        COUNT(*) AS total_employees,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate_pct
    FROM employees
""")

# Q2: Attrition by Department
q2 = run("""
    SELECT Department,
        COUNT(*) AS total,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    GROUP BY Department
    ORDER BY attrition_rate DESC
""")

# Q3: Attrition by Job Role
q3 = run("""
    SELECT JobRole,
        COUNT(*) AS total,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    GROUP BY JobRole
    ORDER BY attrition_rate DESC
""")

# Q4: Overtime impact on attrition
q4 = run("""
    SELECT OverTime,
        COUNT(*) AS total,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    GROUP BY OverTime
""")

# Q5: Salary band analysis
q5 = run("""
    SELECT
        CASE
            WHEN MonthlyIncome < 3000 THEN 'Below 3K'
            WHEN MonthlyIncome BETWEEN 3000 AND 6000 THEN '3K-6K'
            WHEN MonthlyIncome BETWEEN 6001 AND 10000 THEN '6K-10K'
            ELSE 'Above 10K'
        END AS salary_band,
        COUNT(*) AS total,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    GROUP BY salary_band
    ORDER BY attrition_rate DESC
""")

# Q6: Tenure vs attrition
q6 = run("""
    SELECT
        CASE
            WHEN YearsAtCompany <= 2 THEN '0-2 Years'
            WHEN YearsAtCompany BETWEEN 3 AND 5 THEN '3-5 Years'
            WHEN YearsAtCompany BETWEEN 6 AND 10 THEN '6-10 Years'
            ELSE '10+ Years'
        END AS tenure_band,
        COUNT(*) AS total,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    GROUP BY tenure_band
    ORDER BY attrition_rate DESC
""")

# Q7: Job satisfaction vs attrition
q7 = run("""
    SELECT JobSatisfaction,
        COUNT(*) AS total,
        SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) AS attrited,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    GROUP BY JobSatisfaction
    ORDER BY JobSatisfaction
""")

# Q8: High risk segment — young + overtime + low salary
q8 = run("""
    SELECT COUNT(*) AS high_risk_employees,
        ROUND(AVG(MonthlyIncome),2) AS avg_income,
        ROUND(SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attrition_rate
    FROM employees
    WHERE Age < 30 AND OverTime='Yes' AND MonthlyIncome < 5000
""")

# ══════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ══════════════════════════════════════════════════════════════
NAVY = '#1B2A4A'
BLUE = '#2E75B6'
LIGHT = '#A8C4E0'
RED   = '#C0392B'
GREEN = '#1A7A4A'

fig = plt.figure(figsize=(18, 20))
fig.patch.set_facecolor('#F7F9FC')

# Title
fig.text(0.5, 0.97, 'HR Employee Attrition — Business Intelligence Report',
         ha='center', va='top', fontsize=18, fontweight='bold', color=NAVY)
fig.text(0.5, 0.955, 'IBM HR Analytics Dataset  |  1,470 Employees  |  SQL + Python Analysis',
         ha='center', va='top', fontsize=11, color='#555555')

axes = []
positions = [
    (0.05, 0.72, 0.40, 0.20),
    (0.55, 0.72, 0.40, 0.20),
    (0.05, 0.46, 0.40, 0.20),
    (0.55, 0.46, 0.40, 0.20),
    (0.05, 0.20, 0.40, 0.20),
    (0.55, 0.20, 0.40, 0.20),
]
for pos in positions:
    ax = fig.add_axes(pos)
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#DDDDDD')
    axes.append(ax)

# Plot 1: Attrition by Department
ax = axes[0]
colors = [RED if x == q2['attrition_rate'].max() else BLUE for x in q2['attrition_rate']]
bars = ax.barh(q2['Department'], q2['attrition_rate'], color=colors, height=0.5)
ax.set_title('Attrition Rate by Department', fontweight='bold', color=NAVY, fontsize=11)
ax.set_xlabel('Attrition Rate (%)', fontsize=9)
for bar, val in zip(bars, q2['attrition_rate']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val}%', va='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_xlim(0, q2['attrition_rate'].max() + 8)

# Plot 2: Overtime Impact
ax = axes[1]
colors2 = [RED if v == q4['attrition_rate'].max() else GREEN for v in q4['attrition_rate']]
bars2 = ax.bar(q4['OverTime'], q4['attrition_rate'], color=colors2, width=0.4)
ax.set_title('Overtime vs Attrition Rate', fontweight='bold', color=NAVY, fontsize=11)
ax.set_ylabel('Attrition Rate (%)', fontsize=9)
for bar, val in zip(bars2, q4['attrition_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val}%', ha='center', fontsize=11, fontweight='bold', color=NAVY)
ax.set_ylim(0, q4['attrition_rate'].max() + 12)

# Plot 3: Salary Band
ax = axes[2]
order = ['Below 3K', '3K-6K', '6K-10K', 'Above 10K']
q5_sorted = q5.set_index('salary_band').reindex(order).reset_index()
bar_colors = [RED if x == q5_sorted['attrition_rate'].max() else BLUE for x in q5_sorted['attrition_rate']]
bars3 = ax.bar(q5_sorted['salary_band'], q5_sorted['attrition_rate'], color=bar_colors, width=0.5)
ax.set_title('Attrition Rate by Salary Band', fontweight='bold', color=NAVY, fontsize=11)
ax.set_ylabel('Attrition Rate (%)', fontsize=9)
for bar, val in zip(bars3, q5_sorted['attrition_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val}%', ha='center', fontsize=9, fontweight='bold', color=NAVY)
ax.set_ylim(0, q5_sorted['attrition_rate'].max() + 10)
ax.tick_params(axis='x', labelsize=8)

# Plot 4: Tenure Band
ax = axes[3]
order2 = ['0-2 Years', '3-5 Years', '6-10 Years', '10+ Years']
q6_sorted = q6.set_index('tenure_band').reindex(order2).reset_index()
bar_colors2 = [RED if x == q6_sorted['attrition_rate'].max() else BLUE for x in q6_sorted['attrition_rate']]
bars4 = ax.bar(q6_sorted['tenure_band'], q6_sorted['attrition_rate'], color=bar_colors2, width=0.5)
ax.set_title('Attrition Rate by Employee Tenure', fontweight='bold', color=NAVY, fontsize=11)
ax.set_ylabel('Attrition Rate (%)', fontsize=9)
for bar, val in zip(bars4, q6_sorted['attrition_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val}%', ha='center', fontsize=9, fontweight='bold', color=NAVY)
ax.set_ylim(0, q6_sorted['attrition_rate'].max() + 10)
ax.tick_params(axis='x', labelsize=8)

# Plot 5: Job Satisfaction
ax = axes[4]
sat_labels = {1: 'Low (1)', 2: 'Medium (2)', 3: 'High (3)', 4: 'Very High (4)'}
q7['label'] = q7['JobSatisfaction'].map(sat_labels)
bar_colors3 = [RED if x == q7['attrition_rate'].max() else BLUE for x in q7['attrition_rate']]
bars5 = ax.bar(q7['label'], q7['attrition_rate'], color=bar_colors3, width=0.5)
ax.set_title('Attrition Rate by Job Satisfaction', fontweight='bold', color=NAVY, fontsize=11)
ax.set_ylabel('Attrition Rate (%)', fontsize=9)
for bar, val in zip(bars5, q7['attrition_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val}%', ha='center', fontsize=9, fontweight='bold', color=NAVY)
ax.set_ylim(0, q7['attrition_rate'].max() + 10)
ax.tick_params(axis='x', labelsize=8)

# Plot 6: Top Job Roles by Attrition
ax = axes[5]
top5 = q3.head(5)
bar_colors4 = [RED if x == top5['attrition_rate'].max() else BLUE for x in top5['attrition_rate']]
bars6 = ax.barh(top5['JobRole'], top5['attrition_rate'], color=bar_colors4, height=0.5)
ax.set_title('Top 5 Job Roles by Attrition Rate', fontweight='bold', color=NAVY, fontsize=11)
ax.set_xlabel('Attrition Rate (%)', fontsize=9)
for bar, val in zip(bars6, top5['attrition_rate']):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val}%', va='center', fontsize=9, color=NAVY, fontweight='bold')
ax.set_xlim(0, top5['attrition_rate'].max() + 10)
ax.tick_params(axis='y', labelsize=8)

# KPI Banner
kpi_ax = fig.add_axes([0.05, 0.91, 0.90, 0.045])
kpi_ax.set_facecolor(NAVY)
kpi_ax.set_xlim(0, 1)
kpi_ax.set_ylim(0, 1)
kpi_ax.axis('off')
overall_rate = q1['attrition_rate_pct'].values[0]
attrited = q1['attrited'].values[0]
total = q1['total_employees'].values[0]
high_risk = q8['high_risk_employees'].values[0]
high_risk_rate = q8['attrition_rate'].values[0]
kpis = [
    (f"{total:,}", "Total Employees"),
    (f"{attrited}", "Attrited"),
    (f"{overall_rate}%", "Overall Attrition Rate"),
    (f"{high_risk}", "High-Risk Employees"),
    (f"{high_risk_rate}%", "High-Risk Attrition Rate"),
]
for i, (val, label) in enumerate(kpis):
    x = 0.1 + i * 0.20
    kpi_ax.text(x, 0.72, val, ha='center', va='center', fontsize=13,
                fontweight='bold', color='white')
    kpi_ax.text(x, 0.22, label, ha='center', va='center', fontsize=8, color=LIGHT)

# Footer
fig.text(0.5, 0.02, 'Analysis by Sai Akshay Jilla  |  Tools: Python (Pandas, Matplotlib, SQLite)  |  Dataset: IBM HR Analytics (Kaggle)',
         ha='center', fontsize=9, color='#888888')

plt.savefig('/mnt/user-data/outputs/HR_Attrition_Analysis.png', dpi=150, bbox_inches='tight',
            facecolor='#F7F9FC')
plt.close()

# ── Print key findings ─────────────────────────────────────
print("=" * 60)
print("PROJECT 1: HR ATTRITION SQL ANALYSIS — KEY FINDINGS")
print("=" * 60)
print(f"\nOverall Attrition Rate: {overall_rate}%")
print(f"Total Employees: {total} | Attrited: {attrited}")
print("\nDEPARTMENT ATTRITION:")
print(q2.to_string(index=False))
print("\nOVERTIME IMPACT:")
print(q4.to_string(index=False))
print("\nSALARY BAND:")
print(q5.to_string(index=False))
print("\nTENURE BAND:")
print(q6.to_string(index=False))
print("\nHIGH RISK SEGMENT (Age<30, Overtime, Income<5K):")
print(q8.to_string(index=False))
print("\nDone. Chart saved.")
