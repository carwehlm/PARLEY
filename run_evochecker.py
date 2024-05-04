import os
from multiprocessing import Pool, cpu_count


def run_task(args):
    os.chdir('Applications/EvoChecker-master')
    os.environ['LD_LIBRARY_PATH'] = "libs/runtime"
    i, rep = args
    path = f"./{i}_{rep}.properties"
    open(path, "w").close()
    with open(path, 'a') as f:
        f.write(f"PROBLEM = ROBOT{i}_REP{rep}\n")
        f.write(f"MODEL_TEMPLATE_FILE = models/model_{i}_umc.prism\n")
        f.write("PROPERTIES_FILE = robot.pctl\n")
        f.write("ALGORITHM = NSGAII\n")
        f.write("POPULATION_SIZE = 100\n")
        f.write("MAX_EVALUATIONS = 100\n")
        f.write("PROCESSORS = 1\n")
        f.write("PLOT_PARETO_FRONT = false\n")
        f.write("VERBOSE = true\n")
        f.write("LOAD_SEED = false\n")
        f.write(f"SEED_FILE = data/ROBOT{i}_BASELINE/front\n")
        f.write(f"INIT_PORT = 5{i}{rep}\n")
    # Note: INIT_PORT doesn't have an effect https://github.com/gerasimou/EvoChecker/issues/11

    os.system('java -jar ./target/EvoChecker-1.1.0.jar ' + path)


def run(map_, replications):
    # Number of parallel processes
    num_processes = 10

    # available maps
    rep_values = range(replications)  # 10 replications

    # Create a list of tuples with all combinations of i and rep
    tasks = [(map_, rep) for rep in rep_values]

    with Pool(num_processes) as pool:
        pool.map(run_task, tasks)
