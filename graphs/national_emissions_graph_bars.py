import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load your data
df = pd.read_csv("data/simulation_results/national_level/emissions_all_scenarios.csv")  # Replace with actual path if needed

household_numbers = {
    'Terraced': 6417000,
    'S-Detached': 5810000,
    'Detached': 4137000
}

# Clean columns and values
df.columns = df.columns.str.strip()
df["Scenario"] = df["Scenario"].str.strip()
df["Operation"] = df["Operation"].str.strip()
df["Solar"] = df["Solar"].str.strip()

for archetype in household_numbers:
    df.loc[df["Archetype"] == archetype, "Emissions (kg CO2)"] *= household_numbers[archetype]

group_cols = [col for col in df.columns if col not in ["Archetype", "Emissions (kg CO2)"]]
df = df.groupby(group_cols, as_index=False)["Emissions (kg CO2)"].sum()

print(df)
# Filter and extract base case
base = df[df["Scenario"] == "W"]
base_lookup = base.set_index(["Solar"])["Emissions (kg CO2)"].to_dict()

# Compute % reduction from base case
df["Base"] = df.apply(lambda row: base_lookup[(row["Solar"])], axis=1)
df["Reduction (%)"] = 100 * (df["Base"] - df["Emissions (kg CO2)"]) / df["Base"]

# Drop the W rows (base case)
df = df[df["Scenario"] != "W"]

# Drop the bidirectional rows in cases without EV
df = df[~(~df["Scenario"].str.contains("E") & (df["Operation"] == "bi"))]

# Label each scenario
df["ScenarioLabel"] = np.where(
    df["Scenario"].str.contains("E"),
    df["Scenario"] + " (" + df["Operation"] + ")",
    df["Scenario"]
)
print(df)
# Group by scenario and solar condition, average across archetypes
grouped = df.groupby(["ScenarioLabel", "Solar"])["Reduction (%)"].agg(["mean", "min", "max"]).reset_index()
print(grouped)
# Separate best and worst
pivot_best = grouped[grouped["Solar"] == "best"]
pivot_worst = grouped[grouped["Solar"] == "worst"]

# Merge to get span
merged = pd.merge(pivot_best, pivot_worst, on="ScenarioLabel", suffixes=("_best", "_worst"))

# Final plot data
plot_df = pd.DataFrame({
    "Scenario": merged["ScenarioLabel"],
    "Mean Reduction (%)": (merged["mean_best"] + merged["mean_worst"]) / 2,
    "Min Reduction (%)": merged[["min_best", "min_worst"]].min(axis=1),
    "Max Reduction (%)": merged[["max_best", "max_worst"]].max(axis=1)
})

# Sort for better visualization
plot_df = plot_df.sort_values(by="Mean Reduction (%)", ascending=True)

print(plot_df)
# Plot
plt.figure(figsize=(14, 6))
sns.barplot(data=plot_df, x="Scenario", y="Mean Reduction (%)", palette="viridis")

# Add error bars
plt.errorbar(x=range(len(plot_df)),
             y=plot_df["Mean Reduction (%)"],
             yerr=[
                 plot_df["Mean Reduction (%)"] - plot_df["Min Reduction (%)"],
                 plot_df["Max Reduction (%)"] - plot_df["Mean Reduction (%)"]
             ],
             fmt='none', c='black', capsize=5)

plt.xticks(rotation=45, ha="right")
plt.ylabel("CO₂ Reduction (%)")
plt.title("Average Emission Reduction by Scenario")
plt.tight_layout()
plt.savefig("./graphs/out/national_scenarios_percentage_bar.png")
plt.show()
