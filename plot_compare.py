import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
#import openpyxl as pyxl

#Control Variables - These are used in all following functions and allow dynamic changes.
folderpath_original = r"/home/arturo/Dokumente/MikeCharlie/Results/Original/data"
columnNames = ["Model", "Replication", "Type", "Success Chance", "Cost", "Cost-Success ratio"]
markers = {"URC": "^", "URC Mod": "o", "Baseline": "X"}
boundary_x = (1, 0.5)
boundary_y = (0, 70)
minmax_model = (10,51)
minmax_repl = (0,10) 

#TODO Change orientation of values so best fit is on the top right
#TODO Cluster bilden

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

def plot_pareto_front(m:int, replication:int, ptype:str, header=True, file_path=None):
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

    pareto_data = pd.DataFrame(pareto_front(data), columns=columnNames[3:5], index=None)

    data = []
    with open(f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE/Front', 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split('	'))
            data.append((x, y))

    baseline_data = pd.DataFrame(pareto_front(data[:20]), columns=columnNames[3:5], index=None)

    #Assign the type column to each dataframe
    pareto_data[columnNames[2]] = ptype
    baseline_data[columnNames[2]] = "Baseline"
    df = pd.concat([pareto_data,baseline_data], ignore_index=True)

    #Assign Model and Replication value to df and cost-success ratio
    df[columnNames[0]] = str(m)
    df[columnNames[1]] = str(replication)
    df[columnNames[5]] = (df[columnNames[3]] / df[columnNames[4]]).round(4)

    return df

def build_scatterplot(m, replication, ptype):
    df = plot_pareto_front(m,replication, ptype=ptype)

    plt.figure(figsize=(8, 6))
    
    sns.scatterplot(data=df, x=columnNames[3], y=columnNames[4], style=columnNames[2], markers=markers, hue=columnNames[2])

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
    x=columnNames[3], y=columnNames[4], hue=columnNames[2], style=columnNames[2], markers=markers,
    dashes=False,)

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}_lines'
    plt.title("Results after modification")
    plt.xlim(boundary_x)
    plt.ylim(boundary_y)
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the plot as an image file
    plt.savefig('plots/compare/' + output_filename + '.pdf')
    plt.close()

def build_lineplot_compare(m, replication, output_filename=None):
    df = plot_pareto_front(m, replication, ptype="URC Mod")
    df_original = plot_pareto_front(m, replication, ptype="URC", file_path=f"{folderpath_original}/ROBOT{m}_REP{replication}/NSGAII/")

    df = pd.concat([df, df_original], ignore_index=True)  # Add new and old values together
    df.drop_duplicates(inplace=True)

    plt.figure(figsize=(8, 6))

    # Use lineplot instead of relplot for more customization options
    sns.lineplot(
        data=df,
        x=columnNames[3],
        y=columnNames[4],
        hue=columnNames[2],
        style=columnNames[2],
        markers=markers,
        dashes=False,
        alpha=0.7,  # Adjust transparency level here
        markersize=4 
    )

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}_lines_compare'
    plt.title("Comparison between results after modification")
    plt.xlim(boundary_x)
    plt.ylim(boundary_y)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/compare/' + output_filename + '.pdf')
    plt.close()

def plot_database(df:pd.DataFrame):
    """Function to plot database valus graphically"""

    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=df, x=columnNames[3], y=columnNames[4], style=columnNames[2], markers=markers, hue=columnNames[2], size=columnNames[5])
    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'Database Plot'
    plt.title(output_filename)
    plt.xlim((1, 0.7))
    plt.ylim((40, 90))
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/compare/' + output_filename + '.pdf')
    plt.close()


def build_database():
    """Creates a Databse containing all available Results"""
    print("Creating Database")
    master = pd.DataFrame(columns=columnNames)
    for model in range(minmax_model[0], minmax_model[1]):
        for rep in range(minmax_repl[0], minmax_repl[1]):    
            print(f"Working on ROBOT{model}_REP{rep}")
            df = plot_pareto_front(model, rep, ptype="URC Mod")
            df_original = plot_pareto_front(model, rep, ptype="URC", file_path=f"{folderpath_original}/ROBOT{model}_REP{rep}/NSGAII/")
            master = pd.concat([master, df, df_original], ignore_index=True)  # Add new and old values together
    
    master.drop_duplicates(inplace=True)
    
    print("Database Created")
    return master

def filter_database(master:pd.DataFrame, excelExport = True):
    """Filters the Database on the highest values for success, lowest for cost abd highest ratio. Return three dataframes and writed to cwd."""

    master_highsuccess  = pd.DataFrame(columns=columnNames)
    master_lowcost      = pd.DataFrame(columns=columnNames)
    master_bestratio    = pd.DataFrame(columns=columnNames)
    for model in range(minmax_model[0], minmax_model[1]):
        df = master.loc[master[columnNames[0]] == str(model)]
        df = df.groupby(columnNames[2], as_index=False)
        df_highsuccess  = df.apply(lambda x: x.loc[x[columnNames[3]].idxmax()])
        df_lowcost      = df.apply(lambda x: x.loc[x[columnNames[4]].idxmin()])
        df_bestratio    = df.apply(lambda x: x.loc[x[columnNames[5]].idxmax()])

        master_highsuccess = pd.concat([master_highsuccess,df_highsuccess], ignore_index=True)
        master_lowcost = pd.concat([master_lowcost,df_lowcost], ignore_index=True)
        master_bestratio = pd.concat([master_bestratio,df_bestratio], ignore_index=True)

    if excelExport:
        with pd.ExcelWriter(f"{os.getcwd()}/database.xlsx", mode='w') as writer:     #In order to append onto an existing file an ExcelWrite Object is needed
            master_highsuccess.to_excel(writer, sheet_name="highsuccess")
            master_lowcost.to_excel(writer, sheet_name="lowcost")
            master_bestratio.to_excel(writer, sheet_name="bestratio")

    return master_highsuccess, master_lowcost, master_bestratio

master = build_database()
df_1, df_2, df_3 = filter_database(master)
plot_database(df_1)

for model in range(minmax_model[0], minmax_model[1]):
    for rep in range(minmax_repl[0], minmax_repl[1]):
        print(f"Working on ROBOT{model}_REP{rep}")
        build_lineplot(model,rep, "URC Mod")
        build_lineplot_compare(model,rep)