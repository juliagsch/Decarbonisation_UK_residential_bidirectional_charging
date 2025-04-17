import os
import subprocess
import pandas as pd
import re
import multiprocessing
import csv


def get_house_files(archetype):
    return [f for f in os.listdir(f"./data/load/{archetype}/") if f.endswith('.txt')]


def process_simulation(args):
    archetype, house_file, wfh_type, op, solar_key, solar_file_name = args

    base_path = os.path.abspath("./data/load/")
    solar_path = os.path.abspath("./data/solar/")
    house_file_path = os.path.join(base_path, archetype, house_file)
    solar_file_path = os.path.join(solar_path, solar_file_name)

    try:
        if not os.path.exists(house_file_path):
            print(f"Missing house file: {house_file_path}")
            return None
        if not os.path.exists(solar_file_path):
            print(f"Missing solar file: {solar_file_path}")
            return None

        # command = f"./compiled_code/bin_sizing/sim 2100 480 70 225 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ./data/ev_UK/merged_ev_{wfh_type}_holiday.csv out.csv"
        command = f"./sim_load 2100 480 70 225 1 0.5 0.95 365 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} ./data/ev_UK/merged_ev_{wfh_type}_holiday.csv out.csv"
        print(command)
        result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)

        def extract(pattern):
            match = re.search(pattern, result.stdout)
            return float(match.group(1)) if match else None

        res = {
            "Archetype": archetype,
            "House number": house_file,
            "CAH Type": wfh_type.replace("T", "H"),
            "Operation": op,
            "Solar": solar_key,
            "Grid Cost": extract(r"Grid Cost: (\d+\.?\d*)"),
            "Optimal PV": extract(r"PV: (\d+\.?\d*)"),
            "Optimal Battery": extract(r"Battery: (\d+\.?\d*)"),
            "Total Cost": extract(r"Total Cost: (\d+\.?\d*)"),
            "Total Load": extract(r"Total Load: (\d+\.?\d*)"),
            "Grid Import": extract(r"Grid import: (\d+\.?\d*)")
        }
        output_csv = "sizing_test.csv"
        file_exists = os.path.isfile(output_csv)
        with open(output_csv, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=res.keys())
            if not file_exists:
                writer.writeheader()  # Only write header if file doesn't exist
            writer.writerow(res)

    except Exception as e:
        print(f"Error in {house_file_path}: {e}")
        return None


if __name__ == "__main__":
    archetypes = ["Detached", "Semi-detached", "Terraced"]
    operations = ["safe_unidirectional", "hybrid_bidirectional"]
    # operations = ["safe", "lbn", "sunlight", "soctarget", "sunlight_soctarget", "sunlight_lbn", "lbn_soctarget", "sunlight_lbn_soctarget"]
    wfh_types = ["T1", "T2", "T3"]
    solar_conditions = {"worst": "Lerwick_pv.txt", "best": "Weymouth_pv.txt"}

    output_csv = "./data/simulation_results/sizing_results.csv"
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    file_exists = os.path.isfile(output_csv)

    # Prepare all tasks
    tasks = []
    for archetype in archetypes:
        for house_file in get_house_files(archetype):
            for wfh_type in wfh_types:
                for op in operations:
                    for solar_key, solar_file in solar_conditions.items():
                        tasks.append((archetype, house_file, wfh_type, op, solar_key, solar_file))

    # num_processes = multiprocessing.cpu_count()
    num_processes = 1
    print(f"Running with {num_processes} processes...")

    # Run all simulations in parallel
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(process_simulation, tasks)

