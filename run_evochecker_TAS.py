import os
from multiprocessing import Pool, cpu_count


def run_task(args):
    os.chdir('Applications/EvoChecker-master')
    os.environ['LD_LIBRARY_PATH'] = "libs/runtime"
    i, rep = args
    path = "./{0}_{1}.properties".format(str(i), str(rep))
    open(path, "w").close()
    with open(path, 'a') as f:
        f.write("PROBLEM = TAS\n")
        f.write("       MODEL_TEMPLATE_FILE = models/TAS/TAS_umc.prism\n")
        f.write("       PROPERTIES_FILE = models/TAS.pctl\n")
        f.write("       ALGORITHM = NSGAII\n")
        f.write("       POPULATION_SIZE = 100\n")
        f.write("       MAX_EVALUATIONS = 4000\n")
        f.write("       PROCESSORS = 1\n")
        f.write("       PLOT_PARETO_FRONT = false\n")
        f.write("       VERBOSE = true\n")
        f.write("       LOAD_SEED = true\n")
        f.write("       SEED_FILE = data/TAS/baseline/Front_\n")

    os.system('java -jar ./target/EvoChecker-1.1.0.jar ' + path)


def run(map_, replications):
    # Number of parallel processes
    num_processes = cpu_count()

    # available maps
    rep_values = range(replications)  # 10 replications

    # Create a list of tuples with all combinations of i and rep
    tasks = [(map_, rep) for rep in rep_values]

    with Pool(num_processes) as pool:
        pool.map(run_task, tasks)
