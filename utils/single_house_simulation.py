import subprocess
import pandas as pd
import re
import os

# Function to get paths of house files
def get_house_files():
    # Changed path to go up one level
    return [f for f in os.listdir("../data/load/") if f.endswith('.txt')]

# Base path for the files
base_path = os.path.abspath("../data/load/")
solar_path = os.path.abspath("../data/solar/")

# Archetypes and their corresponding folders (kept for compatibility)
archetypes = ["Sample"]  # Modified to use single sample instead of different archetypes
operations = ["safe_unidirectional", "hybrid_bidirectional"]
wfh_types = ["T1", "T2", "T3"]
solar_conditions = {"worst": "Lerwick_pv.txt", "best": "Weymouth_pv.txt"}

# Prepare DataFrame to collect results
results = []

# Iterate over configurations
for archetype in archetypes:
    for house_file in get_house_files():
        house_file_path = os.path.join(base_path, house_file)
        
        # Check if the house file exists
        if not os.path.exists(house_file_path):
            print(f"Error: File does not exist - {house_file_path}")
            continue  # Skip this file if it does not exist

        for wfh_type in wfh_types:
            for op in operations:
                for solar_key, solar_file_name in solar_conditions.items():
                    solar_file_path = os.path.join(solar_path, solar_file_name)
                    
                    # Check if the solar file exists
                    if not os.path.exists(solar_file_path):
                        print(f"Error: Solar file does not exist - {solar_file_path}")
                        continue  # Skip this solar file if it does not exist
                    
                    # Default: PV and EV scenario
                    #command = f"../compiled_code/bin_pv_ev/sim 2100 480 10 20 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ../data/ev_usage/merged_{wfh_type}_UK.csv 0 4"
                    
                    # For EV only (no PV) scenario
                    command = f"../compiled_code/bin_ev_only/sim 2100 480 10 20 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ../data/ev_usage/merged_{wfh_type}_UK.csv 0 4"
                    
                    # For PV only (no EV) scenario
                    #command = f"../compiled_code/bin_pv_only/sim 2100 480 10 20 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ../data/ev_usage/merged_{wfh_type}_UK.csv 0 4"
                    
                    # For PV, EV, and storage scenario
                    #command = f"../compiled_code/bin_pv_ev_storage/sim 2100 480 10 20 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ../data/ev_usage/merged_{wfh_type}_UK.csv 0 4"
                    
                    # For storage, EV, and PV scenario (alternative implementation)
                    #command = f"../compiled_code/bin_pv_ev_storage/sim 2100 480 10 20 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ../data/ev_usage/merged_{wfh_type}_UK.csv 0 4"

                    print("Executing command: " + command)
                    
                    # Execute the command
                    result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)

                    # Extract numbers from output
                    grid_import_match = re.search(r"Grid import: (\d+\.?\d*)", result.stdout)
                    total_cost_match = re.search(r"Total Cost: (\d+\.?\d*)", result.stdout)
                    
                    # Store results
                    results.append({
                        "Archetype": archetype,
                        "House number": 1,
                        "CAH Type": wfh_type.replace("T", "H"),
                        "Operation": op,
                        "Solar": solar_key,
                        "Grid Import": float(grid_import_match.group(1)) if grid_import_match else None,
                        "Total Cost": float(total_cost_match.group(1)) if total_cost_match else None
                    })

# Convert results to DataFrame and save to CSV
df_results = pd.DataFrame(results)
df_results.to_csv("../data/simulation_results/household_simulation_results.csv", index=False)
