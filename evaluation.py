import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from deap.tools._hypervolume.pyhv import hypervolume
from scipy.stats import wilcoxon, anderson, mannwhitneyu
import itertools

MAXIMUM_SPREAD_VALUE = 1.0
plt.rcParams.update({'font.size': 16})


def filter_dominated_points(data):
    pareto_data = []
    for x, y in data:
        if not is_dominated(x, y, pareto_data, data):
            pareto_data.append((x, y))
    return list(set(pareto_data))


def is_dominated(x, y, data1, data2):
    for other_x, other_y in data1:
        # Check if another point is better in both objectives: maximize x and minimize y
        if other_x >= x and other_y <= y:
            # Strict domination: at least one condition must be strictly better
            if other_x > x or other_y < y:
                return True
    for other_x, other_y in data2:
        # Check if another point is better in both objectives: maximize x and minimize y
        if other_x >= x and other_y <= y:
            # Strict domination: at least one condition must be strictly better
            if other_x > x or other_y < y:
                return True
    return False


def visualize_normalized_fronts(front_data, ref_point):
    # Normalize the front as described above
    min_values = np.min(front_data, axis=0)
    max_values = np.maximum(ref_point, np.max(front_data, axis=0))

    normalized_front = (front_data - min_values) / (max_values - min_values)
    plt.figure(figsize=(8, 6))
    plt.scatter(normalized_front[:, 0], normalized_front[:, 1], label='Normalized Pareto Front')

    # Mark the reference point
    normalized_ref_point = (ref_point - min_values) / (max_values - min_values)
    plt.scatter(normalized_ref_point[0], normalized_ref_point[1], color='red', marker='x', label='Reference Point')

    plt.xlabel('Normalized Probability of Mission Success')
    plt.ylabel('Normalized Cost')
    plt.legend()
    plt.grid(True)
    plt.show()


def compute_spread(front_data, ref_point):
    """
    Compute the spread (distribution of solutions) on a Pareto front.

    Args:
        front_data: List of points representing the Pareto front.
        ref_point: Reference point representing the possible end points.

    Returns:
        The spread of the Pareto front.
    """
    print(ref_point)
    for p in front_data:
        print(p)
    # Convert front data to numpy array
    front_data = np.array(front_data)

    # Check if spread can be computed (avoid division by zero)
    if any(np.max(front_data, axis=0) - np.min(front_data, axis=0)) == 0:
        return MAXIMUM_SPREAD_VALUE

    # Normalize front data and reference point using the same min and max
    min_values = np.min(ref_point, axis=0)
    max_values = np.max(ref_point, axis=0)

    min_values = np.min(front_data, axis=0)
    max_values = np.maximum(ref_point, np.max(front_data, axis=0))

    normalized_front = (front_data - min_values) / (max_values - min_values)

    # Normalize front data using ref_point as the max values
    normalized_front = front_data / ref_point
    normalized_ref_point = [1, 1]
    normalized_front = (front_data - min_values) / (max_values - min_values)
    normalized_ref_point = (ref_point - min_values) / (max_values - min_values)
    print(normalized_ref_point)
    # visualize_normalized_fronts(normalized_front, normalized_ref_point)
    # Sort normalized solutions based on the first objective (x)
    sorted_front = normalized_front[np.argsort(normalized_front[:, 0])]


    # Compute Euclidean distances between adjacent solutions
    distances = np.linalg.norm(np.diff(sorted_front, axis=0), axis=1)
    for p in sorted_front:
        print(p)
    for d in distances:
        print(d)
    d_ = np.mean(distances)  # Average distance between adjacent solutions
    print(d_)

    # Calculate d_upper: Distance from the uppermost solution to (max x from normalized ref_point, 0)
    uppermost_solution = sorted_front[0]
    d_upper_point = np.array([normalized_ref_point[0], 0])  # Use normalized max x, set y = 0
    d_upper = np.linalg.norm(uppermost_solution - d_upper_point)
    print(d_upper)

    # Calculate d_bottom: Distance from the lowermost solution to (0, max y from normalized ref_point)
    lowermost_solution = sorted_front[-1]
    d_bottom_point = np.array([0, normalized_ref_point[1]])  # Use normalized max y, set x = 0
    print(d_bottom_point)
    d_bottom = np.linalg.norm(lowermost_solution - d_bottom_point)
    print("d-bottom")
    print(d_bottom)

    # Calculate the sum of |di - d_|
    di_diff_sum = np.sum(np.abs(distances - d_))

    # Spread formula from literature
    spread = (d_upper + d_bottom + di_diff_sum) / (d_upper + d_bottom + (len(distances) * d_))
    spread = di_diff_sum / (len(distances) * d_)


    # Handle NaN case
    if spread != spread:  # NaN check
        return MAXIMUM_SPREAD_VALUE
    print(f"Spread: {spread}")
    return spread


def compute_pdi(front_data, ref_point):
    """
     Compute the PDI (distribution of solutions) on a Pareto front.

     Args:
         front_data: List of points representing the Pareto front.
         ref_point: Reference point representing the possible end points.

     Returns:
         The PDI of the Pareto front.
     """
    # Convert front data to numpy array
    front_data = np.array(front_data)

    # Check if spread can be computed (avoid division by zero)
    if any(np.max(front_data, axis=0) - np.min(front_data, axis=0)) == 0:
        return MAXIMUM_SPREAD_VALUE

    # Normalize front data and reference point using the same min and max
    min_values = np.min(front_data, axis=0)
    max_values = np.maximum(ref_point, np.max(front_data, axis=0))

    normalized_front = (front_data - min_values) / (max_values - min_values)
    normalized_ref_point = (ref_point - min_values) / (max_values - min_values)
    # visualize_normalized_fronts(normalized_front, normalized_ref_point)
    # Sort normalized solutions based on the first objective (x)
    sorted_front = normalized_front[np.argsort(normalized_front[:, 0])]

    # Compute Euclidean distances between adjacent solutions
    distances = np.linalg.norm(np.diff(sorted_front, axis=0), axis=1)
    # distances = [y for y in distances if y > 0.05]
    d_ = np.mean(distances)  # Average distance between adjacent solutions

    # Calculate d_upper: Distance from the uppermost solution to (max x from normalized ref_point, 0)
    uppermost_solution = sorted_front[0]
    d_upper_point = np.array([normalized_ref_point[0], 0])  # Use normalized max x, set y = 0
    d_upper = np.linalg.norm(uppermost_solution - d_upper_point)

    # Calculate d_bottom: Distance from the lowermost solution to (0, max y from normalized ref_point)
    lowermost_solution = sorted_front[-1]
    d_bottom_point = np.array([0, normalized_ref_point[1]])  # Use normalized max y, set x = 0
    d_bottom = np.linalg.norm(lowermost_solution - d_bottom_point)

    # Calculate the sum of |di - d_|
    di_diff_sum = np.sum(np.abs(distances - d_))

    # Spread formula from literature
    spread = (d_upper + d_bottom + di_diff_sum) / (d_upper + d_bottom + len(distances))


    # Handle NaN case
    if spread != spread:  # NaN check
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
    results = {'worse': 0, 'no_difference': 0, 'better': 0}

    for map_data in data:
        statistic, p_value = mannwhitneyu(map_data, np.zeros_like(map_data), alternative='two-sided')
        mean_difference = np.mean(map_data)

        if p_value < alpha:
            if mean_difference > 0:
                results['better'] += 1
            elif mean_difference < 0:
                results['worse'] += 1
        else:
            results['no_difference'] += 1

    return results


def create_selected_box_plots(gains_data, selected_maps=range(90), ylabel='Hypervolume', title=''):
    # Extract gains for the selected maps
    gains_selected = [gains_data[i] for i in selected_maps]

    # Create a single plot for the selected gains
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=gains_selected)

    # Add a dashed line at y=0
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xticks(np.arange(0, len(selected_maps), 5))

    # plt.ylim(-5, 15)
    # plt.ylim(-0.4,0.1)

    plt.xlabel('Map')
    plt.ylabel(ylabel)
    # plt.title(title)
    # plt.legend()  # Add legend to show the zero line
    plt.savefig(f'plots/box-plots/{ylabel}_{title[:1]}_{title[2:]}.pdf', bbox_inches='tight')
    # plt.show()

# Specify the paths to CSV files and the file containing expected values
fronts_dir = 'Applications/EvoChecker-master/data/'


def __baseline_data(acceptable_interval, m):
    used_interval = acceptable_interval.copy()
    periodic = []
    with open(f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE/Front', 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split('	'))
            if x > used_interval[0] and y < used_interval[1]:
                periodic.append((x, y))
    periodic = filter_dominated_points(periodic[:10])
    used_interval[0] = 1 - used_interval[0]
    if len(periodic) == 0:
        hv_periodic = 0
        baseline_spread = MAXIMUM_SPREAD_VALUE
        if used_interval[1] == float('inf'):
            used_interval[1] = 200
        ref_point = np.array(used_interval)
    else:
        if used_interval[1] == float('inf'):
            used_interval[1] = max(y + 1 for x, y in periodic)
        ref_point = np.array(used_interval)
        baseline_spread = compute_pdi(periodic, ref_point)
        periodic = np.array([[1 - x, y] for x, y in periodic])
        hv_periodic = hypervolume(np.array(periodic), ref_point)
    return hv_periodic, baseline_spread, ref_point


def __get_data(acceptable_interval, m, ref_point, rep):
    hv = 0
    spread = MAXIMUM_SPREAD_VALUE
    pareto_data = []
    filename = ""
    for filename_ in os.listdir(fronts_dir + f'ROBOT{m}_REP{rep}/NSGAII/'):
        if "Front" in filename_:
            filename = filename_

    with open(fronts_dir + f'ROBOT{m}_REP{rep}/NSGAII/{filename}', 'r') as f:
        next(f)  # Skip the first line

        for line in f:
            values = line.strip().split('\t')
            if len(values) >= 2 and float(values[0]) > acceptable_interval[0] and float(values[1]) < \
                    acceptable_interval[1]:
                pareto_data.append((float(values[0]), float(values[1])))

        # Convert the pareto_data to a NumPy array
        pareto_array = np.array(filter_dominated_points(pareto_data))

        # Calculate the hypervolume
        if len(pareto_array) > 0:
            # Sort the Pareto front based on the first objective (probability)
            spread = compute_pdi(pareto_array, ref_point)
            pareto_array = np.array([[1 - x, y] for x, y in pareto_array])
            pareto_array = pareto_array[np.argsort(pareto_array[:, 0])]
            hv = hypervolume(np.array(pareto_array), np.array(ref_point))
    if hv < 0:
        raise ValueError("Negative Hypervolume computed, something in the configuration is wrong!!")
    return hv, spread


def __get_diffs(data1, data2):
    """
    Calculate the point-wise difference between two lists of lists hv1 and hv2.
    Returns a list of lists containing the differences.
    """
    # Ensure both lists have the same length
    if len(data1) != len(data2):
        raise ValueError("Input lists must have the same length")

    diffs = []

    # Loop through each pair of lists from hv1 and hv2
    for data1, data2 in zip(data1, data2):
        # Check if both sublists have the same length
        if len(data1) != len(data2):
            raise ValueError("Sublists in both approaches must have the same length")

        # Calculate point-wise differences and store them
        diff = [d1 - d2 for d1, d2 in zip(data1, data2)]
        diffs.append(diff)

    return diffs


# Dynamically create count dictionaries
def initialize_counts():
    count_dict = {}

    # Create outer dictionary for each approach
    for approach1, _ in approaches:
        count_dict[approach1] = {}

        # Create inner dictionary for comparisons
        for approach2, _ in approaches:
            if approach1 != approach2:  # Avoid self-comparison
                count_dict[approach1][approach2] = {
                    'worse': 0,
                    'no_difference': 0,
                    'better': 0
                }

    return count_dict


def update_counts_from_test(counts, approach1, approach2, test_results):
    counts[approach1][approach2]['better'] += test_results['better']
    counts[approach1][approach2]['worse'] += test_results['worse']
    counts[approach1][approach2]['no_difference'] += test_results['no_difference']


def print_comparison_results(counts, title):
    """
    Print the comparison results for the given counts dictionary.

    Parameters:
    - counts: Dictionary containing count results for comparisons.
    - title: Title for the results section.
    """
    print(f"\n{title} Comparison Results:")
    for approach1, comparisons in counts.items():
        for approach2, result in comparisons.items():
            better_count = result['better']
            worse_count = result['worse']
            no_diff_count = result['no_difference']
            if better_count + worse_count + no_diff_count > 0:
                print(f"{approach1} outperformed {approach2} in {worse_count} cases.")
                print(f"{approach2} outperformed {approach1} in {better_count} cases.")
                print(
                    f"No statistical significant difference between {approach1} and {approach2} in {no_diff_count} cases.")


approaches = [('Baseline', '_Baseline/Front'), ('PARLEY', ''), ('PARLEY+', '_PLUS')]
# approaches = [('Baseline', '_Baseline/Front'), ('PARLEY+', '_PLUS')]
acceptable_boundaries = [(0.001, 0.6, 0.7, 0.8), (60, 80, 100, float('inf'))]
# acceptable_boundaries = [(0.001, 0.6), (float('inf'), 100)]
maps = 100


def main():
    acceptable_intervals = [[b1, b2] for b1 in acceptable_boundaries[0] for b2 in acceptable_boundaries[1]]
    hv_count = initialize_counts()
    spread_count = initialize_counts()

    for acceptable_interval in acceptable_intervals:
        pdi = {}
        hv = {}
        ref_points = []
        for approach, _ in approaches:
            hv[approach] = []
            pdi[approach] = []
        # for each approach
        for approach, approach_path in approaches:
            # for each map
            for m in range(10, maps):
                if approach == 'Baseline':
                    # first let's get the hypervolume and pdi for the baseline
                    hv_periodic, spread_periodic, ref_point = __baseline_data(acceptable_interval, m)
                    # Duplicate the data 10 times as lists
                    hv_data = [hv_periodic] * 10  # This duplicates the data as a list
                    spread_data = [spread_periodic] * 10  # Same for pdi
                    # Append the duplicated data to the dictionaries for this approach
                    hv[approach].append(hv_data)  # Append list of 10 duplicated entries to the 'hv' key
                    pdi[approach].append(spread_data)  # Same for pdi
                    ref_points.append(ref_point)
                else:
                    ref_point = ref_points[m - 10]
                    hv_ = []
                    spread_ = []
                    for rep in range(0, 10):
                        if approach == 'PARLEY+':
                            rep = str(rep) + '_PLUS'
                        hv_rep, spread_rep = __get_data(acceptable_interval, m, ref_point, rep)
                        hv_.append(hv_rep)
                        spread_.append(spread_rep)
                    hv[approach].append(hv_)
                    pdi[approach].append(spread_)

        # Extract the approach names (first element of each tuple)
        approach_names = [approach[0] for approach in approaches]
        print(f'Investigating following interval: min prob={acceptable_interval[0]}, max cost={acceptable_interval[1]}')
        # Iterate over all unique combinations of two approaches (excluding same pairs)
        for approach1, approach2 in itertools.combinations(approach_names, 2):
            print(f"Comparing {approach1} with {approach2}")
            print(f'Worse means that {approach1} outperforms {approach2}.')
            hv_diff = __get_diffs(hv[approach2], hv[approach1])
            # inverse here because pdi is to be minimised
            spread_diff = __get_diffs(pdi[approach1], pdi[approach2])
            print('HV: ')
            result = perform_mann_whitney_u_test(hv_diff)
            update_counts_from_test(hv_count, approach1, approach2, result)
            print(result)
            print('PDI:')
            result = perform_mann_whitney_u_test(spread_diff)
            update_counts_from_test(spread_count, approach1, approach2, result)
            print(result)
            # box plots
            if acceptable_interval[0] == 0.001:
                acc_int = '0'
            else:
                acc_int = acceptable_interval[0]
            create_selected_box_plots(hv_diff, ylabel='Hypervolume-Gains', title=f'{acc_int}-{acceptable_interval[1]}-{approach1}-{approach2}')
            spread_diff = __get_diffs(pdi[approach2], pdi[approach1])
            create_selected_box_plots(spread_diff, ylabel='PDI-Gains', title=f'{acc_int}-{acceptable_interval[1]}-{approach1}-{approach2}')

        # Calculate relative gains after all data is accumulated
        relative_gains_hv = {approach: [] for approach in ['PARLEY', 'PARLEY+']}
        relative_gains_pdi = {approach: [] for approach in ['PARLEY', 'PARLEY+']}

        for approach in ['PARLEY', 'PARLEY+']:
            for hv_baseline, hv_approach in zip(hv['Baseline'], hv[approach]):
                gains_hv = [(a - b) / b * 100 if b != 0 else 100 for a, b in zip(hv_approach, hv_baseline)]
                relative_gains_hv[approach].extend(gains_hv)

            for pdi_baseline, pdi_approach in zip(pdi['Baseline'], pdi[approach]):
                gains_pdi = [-(a - b) / b * 100 if b != 0 else -100 for a, b in zip(pdi_approach, pdi_baseline)]
                relative_gains_pdi[approach].extend(gains_pdi)

        print(f'Relative HV Gain for PARLEY: {np.mean(relative_gains_hv["PARLEY"]):.2f}%')
        print(f'Relative HV Gain for PARLEY+: {np.mean(relative_gains_hv["PARLEY+"]):.2f}%')
        print(f'Relative PDI Gain for PARLEY: {np.mean(relative_gains_pdi["PARLEY"]):.2f}%')
        print(f'Relative PDI Gain for PARLEY+: {np.mean(relative_gains_pdi["PARLEY+"]):.2f}%')

    print_comparison_results(hv_count, "HV")
    print_comparison_results(spread_count, "PDI")


# main()
# data = [[0.4, 100], [0.5, 90]]
# print(filter_dominated_points(data))
