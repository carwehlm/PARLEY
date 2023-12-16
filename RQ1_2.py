import os

import create_maps
import prism_model_generator
import umc_synthesis
import prism_caller
import run_evochecker
import evaluation
import plot_fronts

max_replications = 10

def maps():
    create_maps.create_90_maps()


def models(i):
    prism_model_generator.generate_model(i)
    infile = f'Applications/EvoChekcer-master/models/model_{i}.prism'
    outfile = f'Applications/EvoChekcer-master/models/model_{i}_umc.prism'
    umc_synthesis.manipulate_prism_model(infile, outfile, before_actions=['east', 'west', 'north', 'south'],
                                         after_actions=['check'])


def baseline(i):
    baseline_file = f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE/Front'
    infile = f'Applications/EvoChecker-master/models/model_{i}.prism'
    if not os.path.exists(f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE'):
        os.mkdir(f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE')
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

def main():
    # maps()
    if not os.path.exists('plots/fronts'):
        os.mkdir('plots/fronts')
    for i in range(10, 11):
        # models(i)
        # baseline(i)
        # evo_checker(i)
        # fronts(i)
        print(f'Finished map {i}')
    # evaluation
    if not os.path.exists('plots/box-plots'):
        os.mkdir('plots/box-plots')
    evaluation.main()


if __name__ == '__main__':
    main()
