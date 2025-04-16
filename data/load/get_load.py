import os
import pandas as pd

def compute_average_from_csv_folder(folder_path):
    total_sum = 0
    num_files = 0
    
    # Iterate through all CSV files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"): 
            file_path = os.path.join(folder_path, file_name)
            
            with open(file_path, 'r') as file:
                values = [float(line.strip()) for line in file if line.strip()]
                total_sum += sum(values)
                num_files += 1
    
    overall_average = total_sum / num_files
    print(num_files)
    return overall_average

gCO2_per_kwh = 162
cost_per_kwh = 0.35

for archetype in ['Terraced', 'Semi-detached', 'Detached']:
    average = compute_average_from_csv_folder(f"./data/load/{archetype}/" )
    print(f'Average load for {archetype}: {average}')
    print(f'Average cost for {archetype}: {average*cost_per_kwh}')
    print(f'Average emissions for {archetype}: {average * gCO2_per_kwh / 1000 + 406}')
print("Overall Average:", average)