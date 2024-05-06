import os, shutil

import create_maps
import prism_model_generator
import umc_synthesis
import prism_caller
import run_evochecker
import evaluation
import plot_fronts, baseline_generator

max_replications = 10
max_maps = 12
data_folder_path = 'Applications/EvoChecker-master/data'
evo_folder_path = "Applications/EvoChecker-master"

def cleanup():
    print("Start Cleanup")

    #Deleting the previouly created solutions in data. Avoids older solutions being wrongly used in plots and/or evaluation.
    rep_folders = [os.path.join(data_folder_path,folder) for folder in os.listdir(data_folder_path) if "REP" in folder]
    rep_folders.sort()

    for folder in rep_folders:
        print(f"Removing Folder {folder}")
        shutil.rmtree(folder)

    #Deleting numerous files created during the runtime of the programm. Avoids cluttering. Its a crude solution. If some .txt files should remain, please remove from list.
    runtime_files = [os.path.join(evo_folder_path,file) for file in os.listdir(evo_folder_path) if ".properties" in file or ".txt" in file]
    runtime_files.remove(f"{evo_folder_path}/config.properties")
    runtime_files.sort()

    for file in runtime_files:
        print(f"Removing File {file}")
        os.remove(file)

    print("Finish Cleanup")
        
def set_baseline(i):
    print("Start Set Baseline Generation")
    baseline_generator.generateSet(f"{data_folder_path}/ROBOT{i}_BASELINE/Set")
    print("Finish Set Baseline Generation")

def maps():
    create_maps.create_90_maps()


def models(i):
    print("Start models")
    prism_model_generator.generate_model(i)
    infile = f'Applications/EvoChecker-master/models/model_{i}.prism'
    outfile = f'Applications/EvoChecker-master/models/model_{i}_umc.prism'
    # TODO umc_synthesis.manipulate_prism_model is currently broken
    umc_synthesis.manipulate_prism_model(infile, outfile, before_actions=['east', 'west', 'north', 'south'],
                                         after_actions=['check'])
    print("Finish models")


def baseline(i):
    baseline_file = f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE/Front'
    infile = f'Applications/EvoChecker-master/models/model_{i}.prism'
    os.makedirs(f'Applications/EvoChecker-master/data/ROBOT{i}_BASELINE', exist_ok=True)
    with open(baseline_file, 'w') as b_file:
        for period in range(1, 11):
            b_file.write(prism_caller.compute_baseline(infile, period))
            if period < 10:
                b_file.write('\n')
            print('finished baseline map {0}, value {1}'.format(str(i), str(period)))


def evo_checker(i):
    # invoke EvoChecker
    print("Start EvoChecker")
    run_evochecker.run(i, max_replications)
    print("Finish EvoChecker")


def fronts(i):
    print("Start fronts")
    for period in range(max_replications):
        plot_fronts.plot_pareto_front(i, period)
    print("Finish fronts")


def main():
    print("Start main")
    cleanup()
    # maps()
    for i in range(10, max_maps):
        # models(i)
        # baseline(i)
        set_baseline(i)
        evo_checker(i)
        fronts(i)
        print(f'Finished map {i}')
    
    # evaluation
    evaluation.main(max_replications, max_maps)
    
    print("Finish main")


if __name__ == '__main__':
    os.makedirs('plots/fronts', exist_ok=True)
    os.makedirs('plots/box-plots', exist_ok=True)
    main()
