import json
import os

import create_maps
import evaluation
import prism_model_generator
import prism_caller
import run_evochecker
import plot_fronts
import urc_synthesis

max_replications = 10


def maps():
    create_maps.create_90_maps()


def models(i):
    prism_model_generator.generate_model(i)
    infile = f'Applications/EvoChecker-master/models/model_{i}.prism'
    outfile = f'Applications/EvoChecker-master/models/model_{i}_umc.prism'
    os.makedirs(f'Applications/EvoChecker-master/data/ROBOT{i}', exist_ok=True)
    popfile = f'Applications/EvoChecker-master/data/ROBOT{i}/Front'
    urc_synthesis.manipulate_prism_model(infile, outfile, baseline=False, initial_pop_file=popfile)


def baseline(i):
    baseline_file = f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE/Front'
    # baseline_file = f'Applications/EvoChecker-master/data/TAS/baseline/Front'
    infile = f'Applications/EvoChecker-master/models/model_{i}.prism'
    # infile = f'Applications/EvoChecker-master/models/TAS/TAS.prism'
    os.makedirs(f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE', exist_ok=True)
    with open(baseline_file, 'w') as b_file:
        for period in range(1, 11):
            b_file.write(prism_caller.compute_baseline(infile, period))
            if period < 10:
                b_file.write('\n')
            print('finished baseline map {0}, value {1}'.format(str(i), str(period)))


def evo_checker(i):
    # invoke EvoChecker
    run_evochecker.run(i, max_replications)


def fronts(i):
    for period in range(max_replications):
        plot_fronts.plot_pareto_front(i, period)


def __modify_properties():
    try:
        with open('input.json', 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {"startX": 0, "startY": 0, "targetX": 9, "targetY": 9, "p": 0.01, "updates": [5], "map_file": "map.csv"}
    # Modify targetX and targetY to be equal to i
    data["targetX"] = 9
    data["targetY"] = 9
    # Write the modified data back to the JSON file
    with open('input.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    __modify_properties()
    maps()
    for i in range(10, 12):
        models(i)
        baseline(i)
        evo_checker(i)
        fronts(i)
        print(f'Finished map {i}')
    # evaluation
    evaluation.main()


if __name__ == '__main__':
    os.makedirs('plots/fronts', exist_ok=True)
    os.makedirs('plots/box-plots', exist_ok=True)
    main()
