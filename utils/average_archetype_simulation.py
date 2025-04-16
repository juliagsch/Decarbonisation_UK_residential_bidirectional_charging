import pandas as pd
# uncomment l.15 if there is no EV to add FF car emissions, comment l14
# Load the simulation results CSV
df = pd.read_csv("./data/simulation_results/household_simulation_results_evpv.csv")

# Define the conversion rates
pounds_per_kwh = 0.35  # Default electricity cost in pounds
gCO2_per_kwh = 162     # Default grid carbon intensity in gCO2/kWh

# Calculate Grid Emissions based on scenario:

# SCENARIO 1: With EV (default)
# Only consider grid emissions as EV charging is included in grid import
df['Grid Emissions'] = df['Grid Import'] * gCO2_per_kwh / 1000 

# SCENARIO 2: No EV
# Uncomment the line below when running no-EV scenarios
# This adds 406 kgCO2 to account for annual emissions from fossil fuel car
# df['Grid Emissions'] = df['Grid Import'] * gCO2_per_kwh / 1000 + 406

# Calculate additional columns
df['Grid Cost'] = df['Grid Import'] * pounds_per_kwh


# Group by the necessary columns and calculate the mean for each group
results = df.groupby(['Archetype', 'CAH Type', 'Operation', 'Solar']).mean().reset_index()

# Round all values to the nearest integer
results = results.round(0)

# Cast to int to remove any trailing .0 after rounding
results['Grid Import'] = results['Grid Import'].astype(int)
results['Total Load'] = results['Total Load'].astype(int)
results['Total Cost'] = results['Total Cost'].astype(int)
results['Grid Cost'] = results['Grid Cost'].astype(int)
results['Grid Emissions'] = results['Grid Emissions'].astype(int)
# Compute Grid Independence
results['Independence'] = 100 - (results['Grid Import'] / results['Total Load']) * 100

# Round Independence to an integer
results['Independence'] = results['Independence'].round(0).astype(int)
results = results[['Archetype', 'CAH Type', 'Operation', 'Solar', 'Grid Import', 'Total Load', 'Total Cost', 'Grid Cost', 'Grid Emissions', 'Independence']]


# Save the averaged results to a new CSV file
results.to_csv('./data/simulation_results/averaged_simulation_results.csv', index=False)
