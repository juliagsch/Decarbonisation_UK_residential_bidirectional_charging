import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from CSV files
uni_best = pd.read_csv('./data/simulation_results/national_level/uni_best_all_scenarios.csv')
uni_worst = pd.read_csv('./data/simulation_results/national_level/uni_worst_all_scenarios.csv')
bi_best = pd.read_csv('./data/simulation_results/national_level/bi_best_all_scenarios.csv')
bi_worst = pd.read_csv('./data/simulation_results/national_level/bi_worst_all_scenarios.csv')

# Rename columns in all dataframes to change 'H+P = P' to 'P'
def rename_columns(df):
    df.columns = [col.replace('H+P = P', 'P') for col in df.columns]
    return df

# Apply renaming to all dataframes
uni_best = rename_columns(uni_best)
uni_worst = rename_columns(uni_worst)
bi_best = rename_columns(bi_best)
bi_worst = rename_columns(bi_worst)

# Function to convert emission values from kilotonnes to megatonnes
def convert_to_megatonnes(df):
    df.iloc[:, 1:] = df.iloc[:, 1:] / 1000
    return df

# Convert all dataframes
uni_best = convert_to_megatonnes(uni_best)
uni_worst = convert_to_megatonnes(uni_worst)
bi_best = convert_to_megatonnes(bi_best)
bi_worst = convert_to_megatonnes(bi_worst)

# Custom color palette
custom_colors = ['#88a1cf', '#ff8556', '#a4de52', '#f684c6', '#39c5a3', '#39c5a3']
highlight_color = '#79DAE8'  # Color that pops the most

# Assign specific colors to scenarios
custom_palette = {
    'H+P': custom_colors[0],
    'H+E+P': custom_colors[3],
    'H+E': custom_colors[1],
    'E+P': custom_colors[2],
    'H+P+E+S': custom_colors[4]
}

# Function to plot the graph with simplified legend and adjusted x-axis
def plot_combined_graph(uni_best, uni_worst, bi_best, bi_worst, title):
    plt.figure(figsize=(12, 6))  # Increase figure size for better clarity
    uni_scenarios = uni_best.columns[1:]  # Extract scenario names from uni_best
    bi_scenarios = bi_best.columns[1:]

    combined_scenarios = list(set(uni_scenarios)) 

    for scenario in combined_scenarios:
        color = custom_palette.get(scenario, 'grey')
        print(scenario + "----------------")

        if scenario == 'P':  # Changed from 'H+P'
            label = 'P'
            print("P")
            # Plot combined P scenario lines in a single color
            sns.lineplot(x='Conversion Rate (%)', y='P', data=uni_best,  # Changed from 'H+P'
                         color=color, marker='o', linestyle='-')
            sns.lineplot(x='Conversion Rate (%)', y='P', data=uni_worst,  # Changed from 'H+P'
                         color=color, marker='o', linestyle='--')
            plt.fill_between(x=uni_best['Conversion Rate (%)'], y1=uni_best['P'],  # Changed from 'H+P'
                             y2=uni_worst['P'], color=color, alpha=0.3)  # Changed from 'H+P'
            # Add combined label
            max_emission_best = uni_best.loc[uni_best['Conversion Rate (%)'] == uni_best['Conversion Rate (%)'].max(), 'P'].values[0]  # Changed from 'H+P'
            plt.text(105, max_emission_best, 'P', color=color, ha='left', va='center')
        else:
            if scenario in uni_scenarios:
                label = scenario
                if scenario == 'H+E+P':
                    label = 'H + E + P (Uni)'
                if scenario == 'H+E':
                    label = 'H + E (Uni)'
                if scenario == 'E+P':
                    label = 'E + P (Uni)'
                if scenario == 'E':
                    label = 'E (Uni)'
                if scenario == 'H+P+E+S':
                    label = 'H + P + E + S (Uni)'

                # Plot unidirectional best scenario lines
                sns.lineplot(x='Conversion Rate (%)', y=scenario, data=uni_best, 
                             color=color, marker='o', linestyle='-')
                # Plot unidirectional worst scenario lines
                sns.lineplot(x='Conversion Rate (%)', y=scenario, data=uni_worst, 
                             color=color, marker='o', linestyle='--')
                plt.fill_between(x=uni_best['Conversion Rate (%)'], y1=uni_best[scenario],
                                 y2=uni_worst[scenario], color=color, alpha=0.3)
                # Adding scenario labels to the right of the lines
                max_emission_best = uni_best.loc[uni_best['Conversion Rate (%)'] == uni_best['Conversion Rate (%)'].max(), scenario].values[0]
                plt.text(105, max_emission_best, label, color=color, ha='left', va='center')

            if scenario in bi_scenarios and scenario != 'H+P+E+S':
                label = scenario
                if scenario == 'H+E+P':
                    label = 'H + E + P (Bi)'
                elif scenario == 'H+E':
                    label = 'H + E (Bi)'
                if scenario == 'E+P':
                    label = 'E + P (Bi)'
                if scenario == 'E':
                    label = 'E (Bi)'

                # Plot bidirectional best scenario lines
                sns.lineplot(x='Conversion Rate (%)', y=scenario, data=bi_best, 
                             color=color, marker='o', linestyle='-')
                # Plot bidirectional worst scenario lines
                sns.lineplot(x='Conversion Rate (%)', y=scenario, data=bi_worst, 
                             color=color, marker='o', linestyle='--')
                plt.fill_between(x=bi_best['Conversion Rate (%)'], y1=bi_best[scenario],
                                 y2=bi_worst[scenario], color=color, alpha=0.3)
                # Adding scenario labels to the right of the lines
                max_emission_best = bi_best.loc[bi_best['Conversion Rate (%)'] == bi_best['Conversion Rate (%)'].max(), scenario].values[0]
                plt.text(105, max_emission_best, label, color=color, ha='left', va='center')

    #plt.title(title)
    plt.xlabel('Conversion Rate (%)')
    plt.ylabel('Total CO2 Emissions (Megatonnes)')
    plt.xlim([0, 125])  # Extend x-axis to 125 to fit labels
    plt.ylim([2, 14])  # Adjust according to your data range (2 to 14 megatonnes)
    plt.xticks(range(0, 101, 10))  # Ensure ticks are only up to 100
    plt.savefig("./graphs/out/national_scenarios.png")
    plt.show()

# Plotting the graphs for unidirectional and bidirectional cases
plot_combined_graph(uni_best, uni_worst, bi_best, bi_worst, 'Unidirectional vs Bidirectional Case: CO2 Emissions vs. Conversion Rate')
