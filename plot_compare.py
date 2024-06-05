import os, time
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import concurrent.futures

#Control Variables - These are used in all following functions and allow dynamic changes.
start = time.perf_counter()
folderpath_original = r"/home/arturo/Dokumente/MikeCharlie/Results/Original/data"
folderpath_compare = f"{os.getcwd()}/plots/compare"
columnNames = ["Model", "Replication", "Type", "Success Chance", "Cost", "Cost-Success ratio"]
tableColumns = ["URC Percentage", "URC Mod Percentage", "Baseline Percentage", "URC Cum. Percentage", "URC Mod Cum. Percentage", "Baseline Cum. Percentage"]
markers = {"URC": "^", "URC Mod": "o", "Baseline": "X", 
           "URC Percentage": "^", "URC Mod Percentage": "o", "Baseline Percentage": "X",
           "URC Cum. Percentage": "^", "URC Mod Cum. Percentage": "o", "Baseline Cum. Percentage": "X"}
boundary_x = (1, 0.5)
boundary_y = (0, 70)
minmax_model = (10,100)
minmax_repl = (0,10) 

palette = {
    'URC'                       : 'tab:green',
    'URC Percentage'            : 'tab:green',
    'URC Cum. Percentage'       : 'tab:green',
    'URC Mod'                   : 'tab:blue',
    'URC Mod Percentage'        : 'tab:blue',
    'URC Mod Cum. Percentage'   : 'tab:blue',
    "Baseline"                  : "tab:red"
}

#TODO Change orientation of values so best fit is on the top right
#TODO Cluster bilden

def plot_pareto_front(m:int, replication:int, ptype:str, header=True, file_path=None):
    """Used by the lineplot and lineplit compare functions to turn the front results into workable tables"""

    def pareto_front(data):
        """Helper Function of plot_pareto_front"""
        pareto_data = []
        for x, y in data:
            if not is_dominated(x, y, pareto_data):
                pareto_data.append((x, y))
        return pareto_data

    def is_dominated(x, y, data):
        """Helper Function of plot_pareto_front"""
        for other_x, other_y in data:
            if other_x >= x and other_y <= y:
                return True
        return False

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

def build_lineplot(m, replication, ptype):
    df = plot_pareto_front(m,replication, ptype=ptype)

    plt.figure(figsize=(8, 6))
    sns.lineplot(
        data=df,
        x=columnNames[3],
        y=columnNames[4],
        hue=columnNames[2],
        style=columnNames[2],
        markers=markers,
        dashes=False,
        alpha=0.7,  # Adjust transparency level here
        markersize=4,
        palette=palette 
    )

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}_lines'
    plt.title("Results after modification")
    plt.xlim(boundary_x)
    plt.ylim(boundary_y)
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the plot as an image file
    plt.savefig(f'{folderpath_compare}/fronts/{output_filename}.pdf')
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
        markersize=4,
        palette=palette 
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
    plt.savefig(f'{folderpath_compare}/fronts/{output_filename}.pdf')
    plt.close()

def plot_database(df:pd.DataFrame, output_filename:str, xlim:tuple[float,float], ylim:tuple[float,float]):
    """Function to plot database valus graphically"""

    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=df, x=columnNames[3], y=columnNames[4], style=columnNames[2], markers=markers, hue=columnNames[2], size=columnNames[5], palette=palette)
    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    plt.title(output_filename)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig(f'{folderpath_compare}/{output_filename}.pdf')
    plt.close()

def plot_table(df:pd.DataFrame, output_filename:str):
    """Function to plot table values graphically"""
    
    value_name_c = "Count"
    value_name_p = "Percentage"

    #Data Selection
    df_c = df.loc[:,df.columns[0:2]]
    df_c.reset_index(inplace=True)
    df_c = df_c.melt(columnNames[1], value_name=value_name_c, var_name=columnNames[0])

    df_p = df.loc[:,tableColumns[3:5]]
    df_p.reset_index(inplace=True)
    df_p = df_p.melt(columnNames[1], value_name=value_name_p, var_name=columnNames[0])

    #Plotting    
    plt.figure(figsize=(8, 6))
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx() # secondary y-axis

    # Use lineplot instead of relplot for more customization options
    sns.barplot(
        data=df_c,
        x=columnNames[1],
        y=value_name_c,
        hue=columnNames[0],
        alpha=0.7,  # Adjust transparency level here
        ax=ax1,
        palette=palette
    )

    sns.lineplot(
        data=df_p,
        x=columnNames[1],
        y=value_name_p,
        hue=columnNames[0],
        style=columnNames[0],
        markers=markers,
        dashes=False,
        alpha=0.7,  # Adjust transparency level here
        markersize=4,
        legend=False,
        ax=ax2,
        palette=palette
    )

    plt.xlabel('Replication')
    plt.ylabel('Cumulative Percentage')
    plt.title(output_filename)
    plt.ylim([0,105])
    plt.grid(True)      #No Idea
    ax1.legend(loc='upper left', bbox_to_anchor=(1, 0.94))      #Move legend to right corner
    ax1.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))    #Set to integers
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())     #Set the percentages
    plt.tight_layout(pad=2.0)   # Use tight_layout to automatically adjust the padding

    # Save the plot as an image file
    plt.savefig(f'{folderpath_compare}/{output_filename}.pdf')
    plt.close()

def build_database():
    """Creates a Database containing all available Results"""
    print("Creating Database")
    master = pd.DataFrame(columns=columnNames)
    for model in range(minmax_model[0], minmax_model[1]):
        for rep in range(minmax_repl[0], minmax_repl[1]):    
            print(f"Working on ROBOT{model}_REP{rep}")
            df = plot_pareto_front(model, rep, ptype="URC Mod")
            df_original = plot_pareto_front(model, rep, ptype="URC", file_path=f"{folderpath_original}/ROBOT{model}_REP{rep}/NSGAII/")
            master = pd.concat([master, df, df_original], ignore_index=True)  # Add new and old values together
    
    master.drop_duplicates(inplace=True)
    #master[columnNames[1]] = master[columnNames[1]].astype(int) +1  #Add one to replications so it goes 1 to 10
    #master[columnNames[1]] = master[columnNames[1]].astype("category")

    print("Database Created")
    return master

def filter_database(master:pd.DataFrame, excelExport = True):
    """Filters the Database on the highest values for success, lowest for cost and highest ratio. Return three dataframes and 3 summary tables and writes to cwd/plots."""

    #So this groups on the type column after baseline, URC, URC Mod and then get the most successful, lowest cost and best ratio replication for each model
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

    #Build tables summarizing the previous results, with min, max, median, average
    #This table counts the replication in which the value, in this case highsuccess, was found. This way we can compare between types at which stage the algorithm reached its optimum
    def build_tables(master:pd.DataFrame):
        master = master.astype({columnNames[1] : "category"})
        table_URC = master.loc[master[columnNames[2]]=="URC"].groupby(columnNames[1])[columnNames[2]].count().rename("URC")
        table_URCmod = master.loc[master[columnNames[2]]=="URC Mod"].groupby(columnNames[1])[columnNames[2]].count().rename("URC Mod")
        table_baseline = master.loc[master[columnNames[2]]=="Baseline"].groupby(columnNames[1])[columnNames[2]].count().rename("Baseline")
        
        table = pd.DataFrame([table_URC, table_URCmod, table_baseline])
        table = table.transpose()
        total_count = table["URC"].sum()
        table[tableColumns[0]] = round(table["URC"] /total_count * 100, 2)
        table[tableColumns[1]] = round(table["URC Mod"] /total_count * 100, 2)
        table[tableColumns[2]] = round(table["Baseline"] /total_count * 100, 2)
        table[tableColumns[3]] = table[tableColumns[0]].cumsum()
        table[tableColumns[4]] = table[tableColumns[1]].cumsum()
        table[tableColumns[5]] = table[tableColumns[2]].cumsum()

        return table

    table_highsucess    = build_tables(master_highsuccess)
    table_lowcost       = build_tables(master_lowcost)
    table_bestratio     = build_tables(master_bestratio)

    if excelExport:
        with pd.ExcelWriter(f"{folderpath_compare}/database.xlsx", mode='w') as writer:     #In order to append onto an existing file an ExcelWrite Object is needed
            master.to_excel(writer, sheet_name="master")
            master_highsuccess.to_excel(writer, sheet_name="highsuccess")
            master_lowcost.to_excel(writer, sheet_name="lowcost")
            master_bestratio.to_excel(writer, sheet_name="bestratio")
            table_highsucess.to_excel(writer, sheet_name="t_highsuccess")
            table_lowcost.to_excel(writer, sheet_name="t_lowcost")
            table_bestratio.to_excel(writer, sheet_name="t_bestratio")
    
    #Export to Latex
    tableColumns_Tex = ["URC", "URC Mod", tableColumns[0], tableColumns[1]]
    table_highsucess.loc[:,tableColumns_Tex].to_latex(f"{folderpath_compare}/t_highsuccess.tex", float_format=r"%.2f")
    table_lowcost.loc[:,tableColumns_Tex].to_latex(f"{folderpath_compare}/t_lowcost.tex", float_format=r"%.2f")
    table_bestratio.loc[:,tableColumns_Tex].to_latex(f"{folderpath_compare}/t_bestratio.tex", float_format=r"%.2f")

    return master_highsuccess, master_lowcost, master_bestratio, table_highsucess, table_lowcost, table_bestratio

### --- ### --- ### --- Modeling Database--- ### --- ### --- ###
master = build_database()
df_highsuccess, df_lowcost, df_bestratio, t_highsuccess, t_lowcost, t_bestratio = filter_database(master)
plot_database(df_highsuccess, "High Success", (1, 0.7), (40, 90))
plot_database(df_lowcost, "Low Cost",(1,0.5), (10,40))
plot_database(df_bestratio, "Best Ratio",(1,0.5), (10,40))
plot_table(t_highsuccess, "Table High Success")
plot_table(t_lowcost, "Table Low Cost")
plot_table(t_bestratio, "Table Best Ratio")

### --- ### --- ### --- Modeling Fronts --- ### --- ### --- ###
tasks = [(model, rep) for model in range(minmax_model[0], minmax_model[1]) for rep in range(minmax_repl[0], minmax_repl[1])]

def process_lineplots(args):
    model, rep = args
    print(f"Working on lineplots for ROBOT{model}_REP{rep}")
    build_lineplot(model, rep, "URC Mod")
    build_lineplot_compare(model, rep)

#Backup
for model, rep in tasks:
    process_lineplots((model, rep))

# #Multithread
# with concurrent.futures.ProcessPoolExecutor() as executor:    
#    executor.map(process_lineplots, tasks)


### TIME ###
finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} second(s)')