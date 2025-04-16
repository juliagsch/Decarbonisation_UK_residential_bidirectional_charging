import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import shutil
import random

input_path = "./data/load/faraday_large"
output_path = "./data/load/processed_poster"

def process_responses(input_file):
    # Load JSON file
    print(input_file)
    with open(input_file, 'r') as file:
        data = json.load(file)

    population = {
        "NoLCT": "NoLCT",
        "EV": "EV",
        "DetachedA": "Detached",
        "DetachedD": "Detached",
        "TerracedA": "Terraced",
        "TerracedD": "Terraced",
        "Semi-detachedA": "Semi-detached",
        "Semi-detachedD": "Semi-detached"
    }

    for p in population:
        os.makedirs(f"{output_path}/{population[p]}", exist_ok=True)

        # Extract results
        response = next((item for item in data["message"]["results"] if item["name"] == p), None)
        kwh = response["kwh"]

        # Write to output text file with each hourly value on a new line
        for idx, daily_trace in enumerate(kwh):
            with open(f'{output_path}/{population[p]}/{p}_{idx}.txt', 'a') as file:
                for i in range(0, len(daily_trace) - 1, 2):
                    # Get hourly values by adding half-hourly load
                    file.write(f"{float(daily_trace[i]) + float(daily_trace[i + 1])}\n")


def read_and_process_hourly(file_path, average, day = 0):
    with open(file_path, 'r') as file:
        # Read all lines and convert them to floats
        data = np.array([float(line.strip()) for line in file.readlines()])
        
    # Calculate total PV generation
    total_pv_generation = np.sum(data)
    
    # Calculate average hourly production
    if(average):
        hourly = [np.mean(data[hour::24]) for hour in range(24)]
    else:
        hourly = data[day*24:(day+1)*24]
 
    return total_pv_generation, hourly

def read_and_process_weekdays(file_path, average, week = 30):
    with open(file_path, 'r') as file:
        # Read all lines and convert them to floats
        data = np.array([float(line.strip()) for line in file.readlines()])

    if(average):
        weekday_total = [0.0 for _ in range(7)]
        for day in range(365):
            weekday_data = data[day*24:day*24+24]
            weekday_total[day%7] += np.sum(weekday_data)
    else:
        weekday_total = [0.0 for _ in range(7)]
        start_idx = week*7*24
        for day in range(7):
            weekday_total[day] = np.sum(data[start_idx:start_idx+24])
            start_idx += 24
    
    return weekday_total

def read_and_process_monthly_all(file_paths):
    monthly_averages = [0.0 for _ in range(12)]
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            # Read all lines and convert them to floats
            data = np.array([float(line.strip()) for line in file.readlines()])
            
        # Calculate total PV generation
        total_pv_generation = np.sum(data)
        
        # Assume data has 365 days, so we split it into 12 months
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        start_idx = 0
        for i, days in enumerate(days_in_month):
            end_idx = start_idx + days
            monthly_averages[i] += np.sum(data[start_idx * 24:end_idx * 24])/days  # Average over the month
            start_idx = end_idx  # Move to the next month
    
    return total_pv_generation, monthly_averages

def read_and_process_monthly(file_path):
    with open(file_path, 'r') as file:
        # Read all lines and convert them to floats
        data = np.array([float(line.strip()) for line in file.readlines()])
        
    # Calculate total PV generation
    total_pv_generation = np.sum(data)
    
    # Assume data has 365 days, so we split it into 12 months
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    monthly_averages = []
    start_idx = 0
    for days in days_in_month:
        end_idx = start_idx + days
        monthly_averages.append(np.sum(data[start_idx * 24:end_idx * 24])/days)  # Average over the month
        start_idx = end_idx  # Move to the next month
    
    return total_pv_generation, monthly_averages

def analyze_and_plot_daily(load_files, average):
    plt.figure(figsize=(10, 5))
    # load_files = random.sample(load_files, 10)
    day = random.randint(0,365)
    print("day: ", day)
    
    for load_file in load_files:
        _, hourly = read_and_process_hourly(load_file, average, day)
        # label = f"NoEV_{load_file}" if load_file < 50 else f"EV_{load_file}"
        label = load_file
        plt.plot(range(24), hourly, label=label, marker='o')
    

    plt.title('Average Hourly Load')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Average Load')
    plt.xticks(range(24), labels=[f'{hour}:00' for hour in range(24)], rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./data/load/average_daily_load.png')
    plt.show()

def analyze_and_plot_weekly(load_files, average):
    plt.figure(figsize=(12, 6))
    # load_files = random.sample(load_files, 10)
    week = random.randint(0,52)

    for load_file in load_files:
        weekly = read_and_process_weekdays(load_file, average, week)
        plt.plot(range(7), weekly, label=load_file, marker='o')
    
    plt.title('Weekly Load Average')
    plt.xlabel('Weekday')
    plt.ylabel('Load')
    plt.xticks(range(7), labels=[f'{month}' for month in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]], rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./data/load/average_weekly_load.png')
    plt.show()

def analyze_and_plot_monthly(load_files, average):
    plt.figure(figsize=(12, 6))
    # load_files = random.sample(load_files, 100)

    total = [0.0 for _ in range(12)]
    for load_file in load_files:
        _, monthly = read_and_process_monthly(load_file)
        if(not average):
            plt.plot(range(12), monthly, label=load_file, marker='o')
     
        total = np.add(total, monthly)
    
    if(average):
        plt.plot(range(12), total, label="average", marker='o')
    
    plt.title('Monthly Load')
    plt.xlabel('Month of the Year')
    plt.ylabel('Load')
    plt.xticks(range(12), labels=[f'{month}' for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]], rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./data/load/average_monthly_load.png')
    plt.show()

def get_load_files():
    files = []
    for type in ["Detached", "EV", "NoLCT", "Semi-detached", "Terraced", "Noisy"]:
        files = files + [f"{output_path}/{type}/{f}" for f in os.listdir(f"{output_path}/{type}") if f.endswith('.txt')]
    return files

if __name__ == "__main__":
    # Create output directory
    # shutil.rmtree("./data/load/processed_poster/")
    # os.makedirs('./data/load/processed_poster/', exist_ok=True)

    # # First process the raw data
    # for load_file_idx in range(365):
    #     process_responses(f'./data/load/faraday_large/day_{load_file_idx}.json')
        
    # Then analyze and plot the processed data
    # files = get_load_files()
    files = ["/Users/juliagschwind/Developer/Decarbonisation_UK_residential_bidirectional_charging-1/data/load/Detached/DetachedA_54.txt", "out_lbn.txt", "out_safe.txt", "out_sunlight.txt", "out_soctarget.txt"]
    average = False
    analyze_and_plot_daily(files, average)
    analyze_and_plot_weekly(files, average)
    analyze_and_plot_monthly(files, average)
