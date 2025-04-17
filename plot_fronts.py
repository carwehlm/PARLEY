import os
import matplotlib.pyplot as plt


def pareto_front(data):
    pareto_data = []
    for x, y in data:
        if not is_dominated(x, y, pareto_data, data):
            pareto_data.append((x, y))
    return pareto_data


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


def plot_pareto_front(m=10, replication=0, header=True):
    file_path = f'Applications/EvoChecker-master/data/ROBOT{m}_REP{replication}_PLUS/NSGAII/'
    x_values_pp, y_values_pp = __get_data(file_path, header)

    file_path = f'Applications/EvoChecker-master/data/ROBOT{m}_REP{replication}/NSGAII/'
    x_values_p, y_values_p = __get_data(file_path, header)
    
    filepath = f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE'
    x_values_b, y_values_b = __get_data(filepath, header=False, split='	')
    x_values_b = x_values_b[:10]
    y_values_b = y_values_b[:10]

    plt.figure(figsize=(8, 6))


    # Add blue dots for Parley
    plt.scatter(x_values_p, y_values_p, facecolors='none', edgecolors='green', marker='o', label='PARLEY')
    # Add red crosses for the baseline
    plt.scatter(x_values_b, y_values_b, color='red', marker='x', label='Baseline')
    # Add green pluses for Parley
    plt.scatter(x_values_pp, y_values_pp, color='blue', marker='+', label='PARLEY+')


    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}'
    plt.title(output_filename)
    plt.xlim(1, 0.2)
    plt.ylim(0, 200)
    plt.legend()
    plt.grid(True)

    # Save the plot as an image file
    plt.savefig('plots/fronts/' + output_filename + '.pdf')
    plt.close()


def plot_pareto_front_for_robot(m=10, replication=2, ref_point=(0.7, 80), header=True):
    plt.rcParams.update({'font.size': 15})

    file_path = f'Applications/EvoChecker-master/data/ROBOT{m}_REP{replication}_PLUS/NSGAII/'
    x_values_pp, y_values_pp = __get_data(file_path, header)

    file_path = f'Applications/EvoChecker-master/data/ROBOT{m}_REP{replication}/NSGAII/'
    x_values_p, y_values_p = __get_data(file_path, header)

    filepath = f'Applications/EvoChecker-master/data/ROBOT{m}_BASELINE'
    x_values_b, y_values_b = __get_data(filepath, header=False, split='	')
    x_values_b = x_values_b[:10]
    y_values_b = y_values_b[:10]

    plt.figure(figsize=(10, 6))

    # Add red crosses for the baseline
    plt.scatter(x_values_b, y_values_b, color='red', marker='x', label='Baseline')
    # Add blue dots for Parley
    plt.scatter(x_values_p, y_values_p, facecolors='none', edgecolors='green', marker='o', label='PARLEY')
    # Add green pluses for Parley
    plt.scatter(x_values_pp, y_values_pp, color='blue', marker='+', label='PARLEY+')

    # Plot dashed lines at the ref_point (x=probability, y=cost)
    plt.axvline(ref_point[0], color='gray', linestyle='--', label='Minimum Allowed Success Probability')
    plt.axhline(ref_point[1], color='gray', linestyle='--', label='Maximum Allowed Cost')

    # Shading only below ref_point on the x-axis (left side)
    plt.fill_betweenx([0, ref_point[1]], x1=0.2, x2=ref_point[0], color='gray', alpha=0.2)  # Left side

    # Shading only above ref_point on the y-axis (top side)
    plt.fill_between([1, 0.2], y1=ref_point[1], y2=200, color='gray', alpha=0.2)  # Top side

    # Highlight maximum x-values whose y-value is below the ref point
    def highlight_max_below_ref(x_values, y_values, color, label):
        # Filter data points below the reference point in y
        below_ref_points = [(x, y) for x, y in zip(x_values, y_values) if y <= ref_point[1]]
        if below_ref_points:
            # Find the maximum x-value among them
            max_x_point = max(below_ref_points, key=lambda point: point[0])
            # Plot the max point with a special marker and label
            plt.scatter(max_x_point[0], max_x_point[1], color=color, s=100, marker='D',
                        label=f'Chosen policy with {label}')  # Custom label here

    # Highlight the best points for each approach
    highlight_max_below_ref(x_values_b, y_values_b, 'red', 'Baseline')
    highlight_max_below_ref(x_values_p, y_values_p, 'green', 'PARLEY')
    highlight_max_below_ref(x_values_pp, y_values_pp, 'blue', 'PARLEY+')

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = f'robot{m}_rep{replication}'
    plt.xlim(1, 0.5)
    plt.ylim(0, 120)
    plt.legend()  # Moves the legend to a custom location

    plt.grid(True)
    # plt.show()
    # Save the plot as an image file
    plt.savefig('front.pdf', bbox_inches='tight')
    plt.close()


def plot_pareto_front_for_gazebo(ref_point=(0.2, 30), header=True):
    plt.rcParams.update({'font.size': 16})
    file_path = f'Applications/EvoChecker-master/data/gazebo/PARLEY+/'
    x_values_pp, y_values_pp = __get_data(file_path, header)

    file_path = f'Applications/EvoChecker-master/data/gazebo/PARLEY/'
    x_values_p, y_values_p = __get_data(file_path, header)

    file_path = f'Applications/EvoChecker-master/data/gazebo/baseline/'
    x_values_b, y_values_b = __get_data(file_path, header)
    x_values_b = x_values_b[:5]
    y_values_b = y_values_b[:5]

    plt.figure(figsize=(8, 6))

    # Add red crosses for the baseline
    plt.scatter(x_values_b, y_values_b, color='red', marker='x', label='Baseline')
    # Add blue dots for Parley
    plt.scatter(x_values_p, y_values_p, facecolors='none', edgecolors='green', marker='o', label='PARLEY')
    # Add green pluses for Parley
    plt.scatter(x_values_pp, y_values_pp, color='blue', marker='+', label='PARLEY+')

    # Plot dashed lines at the ref_point (x=probability, y=cost)
    plt.axvline(ref_point[0], color='gray', linestyle='--', label='Minimum Probability')
    plt.axhline(ref_point[1], color='gray', linestyle='--', label='Maximum Available Cost')

    # Shading only below ref_point on the x-axis (left side)
    plt.fill_betweenx([0, ref_point[1]], x1=0, x2=ref_point[0], color='gray', alpha=0.2)  # Left side

    # Shading only above ref_point on the y-axis (top side)
    plt.fill_between([1, 0], y1=ref_point[1], y2=200, color='gray', alpha=0.2)  # Top side

    # Highlight maximum x-values whose y-value is below the ref point
    def highlight_max_below_ref(x_values, y_values, color, label):
        # Filter data points below the reference point in y
        below_ref_points = [(x, y) for x, y in zip(x_values, y_values) if y <= ref_point[1]]
        if below_ref_points:
            # Find the maximum x-value among them
            max_x_point = max(below_ref_points, key=lambda point: point[0])
            # Plot the max point with a special marker and label
            plt.scatter(max_x_point[0], max_x_point[1], color=color, s=100, marker='D',
                        label=f'Chosen policy with {label}')  # Custom label here

    # Highlight the best points for each approach
    highlight_max_below_ref(x_values_b, y_values_b, 'red', 'Baseline')
    highlight_max_below_ref(x_values_p, y_values_p, 'green', 'PARLEY')
    highlight_max_below_ref(x_values_pp, y_values_pp, 'blue', 'PARLEY+')

    plt.xlabel('Probability of mission success')
    plt.ylabel('Cost')
    output_filename = 'gazebo'
    plt.xlim(0.3, 0)
    plt.ylim(0, 50)
    plt.legend()  # Moves the legend to a custom location

    plt.grid(True)
    # plt.show()
    # Save the plot as an image file
    plt.savefig('front_gazebo.pdf', bbox_inches='tight')
    plt.close()



def plot_pareto_front_for_tas(ref_point=(10, 75), header=True):
    plt.rcParams.update({'font.size': 16})

    file_path = f'Applications/EvoChecker-master/data/TAS/PARLEY+/'
    x_values_pp, y_values_pp = __get_data(file_path, header)

    file_path = f'Applications/EvoChecker-master/data/TAS/PARLEY/'
    x_values_p, y_values_p = __get_data(file_path, header)

    file_path = f'Applications/EvoChecker-master/data/TAS/baseline/'
    x_values_b, y_values_b = __get_data(file_path, header)
    x_values_b = x_values_b[:10]
    y_values_b = y_values_b[:10]

    plt.figure(figsize=(8, 6))

    # Add red crosses for the baseline
    plt.scatter(x_values_b, y_values_b, color='red', marker='x', label='Baseline')
    # Add blue dots for Parley
    plt.scatter(x_values_p, y_values_p, facecolors='none', edgecolors='green', marker='o', label='PARLEY')
    # Add green pluses for Parley
    plt.scatter(x_values_pp, y_values_pp, color='blue', marker='+', label='PARLEY+')

    # Plot dashed lines at the ref_point (x=probability, y=cost)
    plt.axvline(ref_point[0], color='gray', linestyle='--', label='Minimum Correct Alarms')
    plt.axhline(ref_point[1], color='gray', linestyle='--', label='Maximum Available Cost')

    # Shading only below ref_point on the x-axis (left side)
    plt.fill_betweenx([0, ref_point[1]], x1=0, x2=ref_point[0], color='gray', alpha=0.2)  # Left side

    # Shading only above ref_point on the y-axis (top side)
    plt.fill_between([20, 0], y1=ref_point[1], y2=200, color='gray', alpha=0.2)  # Top side

    # Highlight maximum x-values whose y-value is below the ref point
    def highlight_max_below_ref(x_values, y_values, color, label):
        # Filter data points below the reference point in y
        below_ref_points = [(x, y) for x, y in zip(x_values, y_values) if y <= ref_point[1]]
        if below_ref_points:
            # Find the maximum x-value among them
            max_x_point = max(below_ref_points, key=lambda point: point[0])
            # Plot the max point with a special marker and label
            plt.scatter(max_x_point[0], max_x_point[1], color=color, s=100, marker='D',
                        label=f'Chosen policy with {label}')  # Custom label here

    # Highlight the best points for each approach
    highlight_max_below_ref(x_values_b, y_values_b, 'red', 'Baseline')
    highlight_max_below_ref(x_values_p, y_values_p, 'green', 'PARLEY')
    highlight_max_below_ref(x_values_pp, y_values_pp, 'blue', 'PARLEY+')

    plt.xlabel('Correct Alarms')
    plt.ylabel('Cost')
    output_filename = 'TAS'
    plt.xlim(15, 0)
    plt.ylim(0, 180)
    plt.legend()  # Moves the legend to a custom location

    plt.grid(True)
    # plt.show()
    # Save the plot as an image file
    plt.savefig('front_tas.pdf', bbox_inches='tight')
    plt.close()


def __get_data(file_path, header, split='\t'):
    data = []
    for f_name in os.listdir(file_path):
        if "Front" in f_name:
            filename = f_name
    with open(file_path + '/' + filename, 'r') as file:
        if header:
            next(file)  # Skip the header row
        for line in file:
            x, y = map(float, line.strip().split(split))
            data.append((x, y))
    pareto_data = pareto_front(data)
    x_values = [x for x, y in pareto_data]
    y_values = [y for x, y in pareto_data]
    return x_values, y_values


# plot_pareto_front()
# plot_pareto_front_for_robot()
# plot_pareto_front_for_gazebo()
# plot_pareto_front_for_tas()
