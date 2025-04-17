import pandas as pd

# Load the data from the CSV file that gives OPEX for each archetype x WFH x operation x solar
# file_path = './data/simulation_results/averaged_simulation_results_evpv.csv'
file_path = './sizing.csv'
data = pd.read_csv(file_path)

# Average OPEX values computed from Faraday data for houses without EV or PV (baseline scenario)
# Was calculated by total yearly load * 0.35
# pre_conversion_opex = {
#     'Terraced': 2739.301,
#     'Semi-detached': 2904.193,
#     'Detached': 2957.12
# }

pounds_per_kwh = 0.35  # Default electricity cost in pounds

pre_conversion_opex = {
    'Terraced': 809.2498,
    'Semi-detached': 869.9464,
    'Detached': 917.3098
}
# Initialize a list to hold the results
results = []

# Iterate over each row in the dataframe to compute OPEX savings
for index, row in data.iterrows():
    archetype = row['Archetype']
    wfh_type = row['CAH Type']
    operation = row['Operation']
    solar = row['Solar']
    grid_import = row['Grid Import']
    grid_cost = row['Grid Cost']
    total_cost = row['Total Cost']

    petrol_cost = 0

    if 'H1' == wfh_type:
        petrol_cost = 1484.68
    if 'H2' == wfh_type:
        petrol_cost = 724.76
    if 'H3' == wfh_type:
        petrol_cost = 217.738
    
    # Calculate OPEX Savings
    opex_savings = pre_conversion_opex[archetype] + petrol_cost - grid_cost#(grid_import*pounds_per_kwh)
    
    # Append the results
    results.append({
        'Archetype': archetype,
        'CAH Type': wfh_type,
        'Operation': operation,
        'Solar': solar,
        'CAPEX': total_cost,
        'OPEX Savings': opex_savings
    })

# Convert the list of results into a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a CSV file
results_df.to_csv('./data/simulation_results/opex_savings_results.csv', index=False)

print("CSV file with OPEX Savings has been created.")
