import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

folderpath_original = r"/home/arturo/Dokumente/MikeCharlie/Results/Original/data"
columnNames = ["Success Chance", "Cost"]
markers = {"URC": "^", "URC Mod": "o", "Baseline": "X"}

def pareto_front(data):
    pareto_data = []
    for x, y in data:
        if not is_dominated(x, y, pareto_data):
            pareto_data.append((x, y))
    return pareto_data


def is_dominated(x, y, data):
    for other_x, other_y in data:
        if other_x >= x and other_y <= y:
            return True
    return False


def plot_pareto_front(m=10, replication=0, ptype="URC", header=True, file_path=None):
    data = []
    filename = ''
    if file_path:
        pass
    else:
        file_path = f'Applications/EvoChecker-master/data/ROBOT{m}_REP{replication}/NSGAII/'
    
    for f_name in os.listdir(file_path):
        if "Front" in f_name:
            filename = f_name
    with open(file_path + filename, 'r') as file:
        if header:
            next(file)  # Skip the header row
        for line in file:
            x, y = map(float, line.strip().split('\t'))
            data.append((x, y))

    pareto_data = pd.DataFrame(pareto_front(data), columns=columnNames, index=None)

    data = []
    with open(f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE/Front', 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split('	'))
            data.append((x, y))

    baseline_data = pd.DataFrame(pareto_front(data[:20]), columns=columnNames, index=None)

    pareto_data["Type"] = ptype
    baseline_data["Type"] = "Baseline"
    df = pd.concat([pareto_data,baseline_data], ignore_index=True)

    return df

def build_scatterplot(m, replication, ptype):
    df = plot_pareto_front(m,replication, ptype=ptype)

    plt.figure(figsize=(8, 6))
    
    sns.scatterplot(data=df, x=columnNames[0], y=columnNames[1], style="Type", markers=markers, hue="Type")

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}'
    plt.title(output_filename)
    plt.xlim(1, 0.2)
    plt.ylim(0, 200)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/compare/' + output_filename + '.pdf')
    plt.close()

def build_lineplot(m, replication, ptype):
    df = plot_pareto_front(m,replication, ptype=ptype)

    plt.figure(figsize=(8, 6))
    sns.relplot(
    data=df, kind="line",
    x=columnNames[0], y=columnNames[1], hue="Type", style="Type", markers=markers,
    dashes=False,)

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}_lines'
    plt.title("Results after modification")
    plt.xlim(1, 0.6)
    plt.ylim(0, 70)
    #plt.legend()
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the plot as an image file
    plt.savefig('plots/compare/' + output_filename + '.pdf')
    plt.close()


def build_lineplot_compare(m, replication, output_filename=None):
    df = plot_pareto_front(m, replication, ptype="URC Mod")
    df_original = plot_pareto_front(ptype="URC", file_path=f"{folderpath_original}/ROBOT{m}_REP{replication}/NSGAII/")
    #df.loc[df["Type"] == "URC", "Type"] = "URC Mod"  # New Values with modified EvoChecker

    df = pd.concat([df, df_original], ignore_index=True)  # Add new and old values together
    df.drop_duplicates(inplace=True)

    plt.figure(figsize=(8, 6))

    # Use lineplot instead of relplot for more customization options
    sns.lineplot(
        data=df,
        x=columnNames[0],
        y=columnNames[1],
        hue="Type",
        style="Type",
        markers=markers,
        dashes=False,
        alpha=0.7,  # Adjust transparency level here
        markersize=4 
    )

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}_lines_compare'
    plt.title("Comparison between results after modification")
    plt.xlim(0.9, 0.6)
    plt.ylim(10, 70)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/compare/' + output_filename + '.pdf')
    plt.close()


build_scatterplot(10,0, "URC Mod")
build_lineplot(10,0, "URC Mod")
build_lineplot_compare(10,0)