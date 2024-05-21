import os
from multiprocessing import Pool, cpu_count
import subprocess

def run_task(args):
    i, rep = args
    path = f"./{i}_{rep}.properties"
    open(path, "w").close()
    with open(path, 'a') as f:
        f.write(f"PROBLEM = ROBOT{i}_REP{rep}\n")
        f.write(f"MODEL_TEMPLATE_FILE = models/model_{i}_umc.prism\n")
        f.write("PROPERTIES_FILE = robot.pctl\n")
        f.write("ALGORITHM = NSGAII\n")
        f.write("POPULATION_SIZE = 100\n")
        f.write("MAX_EVALUATIONS = 4000\n")
        f.write("PROCESSORS = 16\n")
        f.write("PLOT_PARETO_FRONT = false\n")
        f.write("VERBOSE = false\n")
        f.write("LOAD_SEED = true\n")
        f.write(f"SEED_FILE = data/ROBOT{i}_BASELINE/Set\n")
        f.write(f"INIT_PORT = 5{i}{rep}\n")
    # Note: The Overhead means that a higher processor count will take longer to start but will finish faster.For a pop size 100, max_eval 100, a  processor count 8 is recommended.

    os.system('java -jar ./target/EvoChecker-1.1.0.jar ' + path)


def run(map_, replications):
    old_cwd = os.getcwd()
    os.chdir(f'{old_cwd}/Applications/EvoChecker-master')       #We need to change to CWD for the .jar to find itself at home
    os.environ['LD_LIBRARY_PATH'] = "libs/runtime"

    # available maps
    rep_values = range(replications)  # 10 replications

    # Create a list of tuples with all combinations of i and rep
    tasks = [(map_, rep) for rep in rep_values]

    for task in tasks:
        run_task(task)  #The Parallelization is being taking care by the java itself, not the python. 

    os.chdir(old_cwd)       #We revert back to the original CWD for the .py to find itself at home (Yes I know there are better ways to do this.)