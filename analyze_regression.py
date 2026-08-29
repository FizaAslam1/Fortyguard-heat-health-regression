"""
analyze_regression.py
-----------------------
outputs/merged_data.csv padhta hai (jo fetch_temperatures.py ne banaya tha)
aur temperature vs outcome (energy_consumption_kwh) ka regression/correlation nikalta hai.

Chalane ka tareeqa (fetch_temperatures.py ke baad):
    python analyze_regression.py
"""

import os
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

OUTCOME_COLUMN = "heat_illness_er_rate_per_100k"  # Real CDC data: heat-illness ER visits per 100,000 ED visits (HHS region, 2023 warm season)


def main():
    df = pd.read_csv("outputs/merged_data.csv")
    df = df.dropna(subset=["temperature_c", OUTCOME_COLUMN])

    x = df["temperature_c"]
    y = df[OUTCOME_COLUMN]

    # Pearson correlation
    corr, p_value = stats.pearsonr(x, y)

    # Linear regression
    slope, intercept, r_value, p_value_reg, std_err = stats.linregress(x, y)

    r_squared = r_value ** 2

    # Result print karo
    print("=" * 55)
    print("📊 REGRESSION RESULTS: Temperature vs", OUTCOME_COLUMN)
    print("=" * 55)
    print(f"Pearson correlation (r):     {corr:.3f}")
    print(f"p-value:                     {p_value:.4f}")
    print(f"R-squared:                   {r_squared:.3f}")
    print(f"Regression equation:         y = {slope:.3f} * x + {intercept:.3f}")
    print()
    if p_value < 0.05:
        print("✅ Statistically significant relationship hai (p < 0.05)")
    else:
        print("⚠️  Relationship statistically significant NAHI hai (p >= 0.05)")

    if corr > 0:
        print(f"📈 Direction: Temperature badhne se {OUTCOME_COLUMN} bhi badhta hai (positive correlation)")
    else:
        print(f"📉 Direction: Temperature badhne se {OUTCOME_COLUMN} kam hota hai (negative correlation)")
    print("=" * 55)

    # Save text results
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/regression_result.txt", "w") as f:
        f.write(f"Pearson correlation (r): {corr:.3f}\n")
        f.write(f"p-value: {p_value:.4f}\n")
        f.write(f"R-squared: {r_squared:.3f}\n")
        f.write(f"Equation: y = {slope:.3f} * x + {intercept:.3f}\n")

    # Scatter plot + regression line
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color="crimson", label="Locations")
    line_x = pd.Series([x.min(), x.max()])
    line_y = slope * line_x + intercept
    plt.plot(line_x, line_y, color="navy", label=f"Fit line (R²={r_squared:.2f})")

    for _, row in df.iterrows():
        plt.annotate(row["location_name"], (row["temperature_c"], row[OUTCOME_COLUMN]),
                     fontsize=7, alpha=0.7)

    plt.xlabel("Temperature (°C)")
    plt.ylabel(OUTCOME_COLUMN)
    plt.title("FortyGuard Temperature vs " + OUTCOME_COLUMN)
    plt.legend()
    plt.tight_layout()
    plt.savefig("outputs/scatter_plot.png", dpi=150)
    print("\n✅ Chart save ho gaya: outputs/scatter_plot.png")
    print("✅ Text results save ho gaye: outputs/regression_result.txt")


if __name__ == "__main__":
    main()
