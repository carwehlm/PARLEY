import run_evochecker_TAS
import urc_synthesis


def main():
    i=1
    infile = 'Applications/EvoChecker-master/models/TAS/TAS.prism'
    outfile = 'Applications/EvoChecker-master/models/TAS/TAS_umc.prism'
    popfile = 'Applications/EvoChecker-master/data/TAS/baseline/Front_'
    urc_synthesis.manipulate_prism_model(infile, outfile, baseline=False, initial_pop_file=popfile, before_actions=['setService1', 'setService2'], after_actions=['probe_s1', 'skip_probe'])
    run_evochecker_TAS.run(0, 1)

if __name__ == '__main__':
    main()