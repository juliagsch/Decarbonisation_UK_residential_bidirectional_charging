import pandas as pd
# uncomment l.15 if there is no EV to add FF car emissions, comment l14
# Load the simulation results CSV
type = "noevnopv"
df = pd.read_csv(f"./data/simulation_results/household_simulation_results_{type}.csv")

# Define the conversion rates
pounds_per_kwh = 0.35  # Default electricity cost in pounds
gCO2_per_kwh = 162     # Default grid carbon intensity in gCO2/kWh
gCO2_per_km_petrol = 132 # Default carbon emissions per km driven with a petrol car. Source: https://www.nimblefins.co.uk/average-co2-emissions-car-uk

# Calculate Grid Emissions based on scenario:

# SCENARIO 1: With EV (default)
# Only consider grid emissions as EV charging is included in grid import
# df['Grid Emissions'] = df['Grid Import'] * gCO2_per_kwh / 1000 

# SCENARIO 2: No EV
# Uncomment the lines below when running no-EV scenarios
df['Grid Emissions'] = df['Grid Import'] * gCO2_per_kwh / 1000 
df_T1 = pd.read_csv("./data/ev_UK/merged_ev_T1_holiday.csv")
km_H1 = df_T1['Distance (km)'].sum()
df_T2 = pd.read_csv("./data/ev_UK/merged_ev_T2_holiday.csv")
km_H2 = df_T2['Distance (km)'].sum()
df_T3 = pd.read_csv("./data/ev_UK/merged_ev_T3_holiday.csv")
km_H3 = df_T3['Distance (km)'].sum()
df.loc[df['CAH Type'] == 'H1', 'Grid Emissions'] += km_H1 * gCO2_per_km_petrol / 1000
df.loc[df['CAH Type'] == 'H2', 'Grid Emissions'] += km_H2 * gCO2_per_km_petrol / 1000
df.loc[df['CAH Type'] == 'H3', 'Grid Emissions'] += km_H3 * gCO2_per_km_petrol / 1000

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
results.to_csv(f'./data/simulation_results/averaged_simulation_results_{type}.csv', index=False)
