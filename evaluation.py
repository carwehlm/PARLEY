import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from deap.tools._hypervolume.pyhv import hypervolume
from scipy.stats import wilcoxon, anderson, mannwhitneyu


MAXIMUM_SPREAD_VALUE = 1.5
plt.rcParams.update({'font.size': 16})


def is_dominated(x, y, data):
    for other_x, other_y in data:
        if other_x <= x and other_y <= y:
            return True
    return False


def filter_dominated_points(data):
    non_dominated_data = []
    for x, y in data:
        if is_dominated(x, y, data):
            non_dominated_data.append((x, y))
    return non_dominated_data


def compute_spread(front_data):
    # Normalize objectives
    front_data = np.array(front_data)
    if any(np.max(front_data, axis=0) - np.min(front_data, axis=0)) == 0:
        return MAXIMUM_SPREAD_VALUE

    normalized_front = (front_data - np.min(front_data, axis=0)) / \
                       (np.max(front_data, axis=0) - np.min(front_data, axis=0))

    # Sort normalized solutions based on the first objective
    sorted_front = normalized_front[np.argsort(normalized_front[:, 0])]

    # Compute Euclidean distances between adjacent solutions
    distances = np.linalg.norm(np.diff(sorted_front, axis=0), axis=1)

    # Calculate spread as the average distance
    spread = np.mean(distances)
    # test for NaN
    if spread != spread:
        return MAXIMUM_SPREAD_VALUE
    return spread


def anderson_darling(umc, baseline):
    differences = np.array(baseline) - np.array(
        umc[0])  # Assuming you are comparing with the first repetition of UMC
    # Anderson-Darling normality test
    statistic, critical_values, significance_level = anderson(differences)
    print(f'Anderson-Darling Statistic: {statistic}')
    print(f'Critical Values: {critical_values}')
    print(f'Significance Level: {significance_level}')

    chosen_significance_level = 0.05
    if statistic < critical_values[2]:  # Index 2 corresponds to the 5% significance level
        print('The differences appear to be normally distributed.')
    else:
        print('The differences do not appear to be normally distributed.')


def perform_wilcoxon_test_against_zero(gains_data, alternative='two-sided'):
    # Perform Wilcoxon signed-rank test against zero
    gains_data = list(map(list, zip(*gains_data)))

    statistic, p_value = wilcoxon(gains_data, alternative=alternative)

    # Output Wilcoxon statistic and p-value
    # print(f'Wilcoxon Statistic: {statistic}')
    # print(f'P-Value: {p_value}')

    # Count statistically significant results
    significant_count = sum(p < 0.05 for p in p_value)

    # Check for statistical significance
    if significant_count == len(p_value):
        print('All gains are statistically different from zero.')
    elif significant_count > 0:
        print(f'{significant_count} out of {len(p_value)} gains are statistically different from zero.')
    else:
        print('There is no significant difference from zero.')


def perform_mann_whitney_u_test(data, alpha=0.05):
    """
    Perform Mann-Whitney U test against zero for each map's gain data.

    Parameters:
    - data: List of lists where each inner list represents the gain data for a map.
    - alpha: Significance level.

    Returns:
    - results: Dictionary containing the results for each map, categorizing as 'better', 'worse', or 'no difference'.
    """
    results = {'higher': 0, 'lower': 0, 'no_difference': 0}

    for map_data in data:
        statistic, p_value = mannwhitneyu(map_data, np.zeros_like(map_data), alternative='two-sided')
        mean_difference = np.mean(map_data)

        if p_value < alpha:
            if mean_difference > 0:
                results['higher'] += 1
            elif mean_difference < 0:
                results['lower'] += 1
        else:
            results['no_difference'] += 1

    return results


def create_selected_box_plots(gains_data, selected_maps, ylabel, title):
    # Extract gains for the selected maps
    gains_selected = [gains_data[i] for i in selected_maps]

    # Create a single plot for the selected gains
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=gains_selected)

    # Add a dashed line at y=0
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xticks(np.arange(0, len(selected_maps), 5))

    plt.xlabel('Map')
    plt.ylabel(ylabel)
    # plt.title(title)
    # plt.legend()  # Add legend to show the zero line
    plt.savefig(f'plots/box-plots/{ylabel}_{title[:1]}_{title[2:]}.pdf')



# Specify the paths to CSV files and the file containing expected values
fronts_dir = 'Applications/EvoChecker-master/data/'

#maps = 100

acceptable_intervals = [(0.8, 100), (0.8, 80), (0.8, 60),
                        (0.7, 100), (0.7, 80), (0.7, 60),
                        (0.6, 100), (0.6, 80), (0.6, 60)]


def main(max_replications:int, maps:int):
    print("Start evaluation main")
    for acceptable_interval in acceptable_intervals:
        ref_point = np.array(acceptable_interval)

        hv_map = []
        baseline_hv = []
        baseline_spread = []
        umc_hv = []
        umc_spread = []

        # for each map
        for m in range(10, maps):
            # first let's get the hypervolume for the baseline
            periodic = []
            with open(f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE/Front', 'r') as file:
                for line in file:
                    x, y = map(float, line.strip().split('	'))
                    if x > acceptable_interval[0] and y < acceptable_interval[1]:
                        periodic.append((1 - x, y))
            periodic = filter_dominated_points(periodic[0:20])
            if len(periodic) == 0:
                hv_periodic = 0
                baseline_spread.append(MAXIMUM_SPREAD_VALUE)
            else:
                hv_periodic = hypervolume(np.array(periodic), ref_point)
                baseline_spread.append(compute_spread(periodic))

            baseline_hv.append(hv_periodic)

            hv_rep = 0
            rep_hv = []
            rep_spread = []
            # for each replication
            for rep in range(0, max_replications):
                # Read the expected values from the external file (excluding the first line)
                pareto_data = []
                filename = ""
                for filename_ in os.listdir(fronts_dir + 'ROBOT{0}_REP{1}/NSGAII/'.format(str(m), str(rep))):
                    if "Front" in filename_:
                        filename = filename_

                with open(fronts_dir + 'ROBOT{0}_REP{1}/NSGAII/'.format(str(m), str(rep)) + filename, 'r') as f:
                    next(f)  # Skip the first line
                    for line in f:
                        values = line.strip().split('\t')
                        if len(values) >= 2 and float(values[0]) > acceptable_interval[0] and float(values[1]) < \
                                acceptable_interval[1]:
                            pareto_data.append((1 - float(values[0]), float(values[1])))

                    # Convert the pareto_data to a NumPy array
                    pareto_array = np.array(filter_dominated_points(pareto_data))
                    # Calculate the hypervolume
                    if len(pareto_array) == 0:
                        hv = 0
                        rep_spread.append(MAXIMUM_SPREAD_VALUE)
                    else:
                        # Sort the Pareto front based on the first objective (probability)
                        pareto_array = pareto_array[np.argsort(pareto_array[:, 0])]
                        hv = hypervolume(np.array(pareto_array), np.array(ref_point))
                        rep_spread.append(compute_spread(pareto_array))
                    hv_rep += hv - hv_periodic
                    rep_hv.append(hv)
            umc_spread.append(rep_spread)
            umc_hv.append(rep_hv)
            hv_map.append(hv_rep / 10)

        # Calculate differences for spread and hypervolume
        spread_gain = [[umc - baseline for umc, baseline in zip(repetition, baseline_spread)] for repetition in umc_spread]
        hv_gain = [[umc - baseline for umc, baseline in zip(repetition, baseline_hv)] for repetition in umc_hv]

        # Select the maps shown in the plots (if too many maps)
        selected_maps = range(maps-10)

        # Create box plots for spread gains
        create_selected_box_plots(spread_gain, selected_maps, 'Spread-Gains',
                                  f'{acceptable_interval[0]}-{acceptable_interval[1]}')

        # Create box plots for hypervolume gains
        create_selected_box_plots(hv_gain, selected_maps, 'Hypervolume-Gains',
                                   f'{acceptable_interval[0]}-{acceptable_interval[1]}')
        # perform_wilcoxon_test_against_zero(hv_gain, alternative='greater')
        # perform_wilcoxon_test_against_zero(spread_gain, alternative='less')

        print(perform_mann_whitney_u_test(spread_gain))
        print(perform_mann_whitney_u_test(hv_gain))

        print("Finsh evaluation main")
