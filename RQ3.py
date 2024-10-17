import statistics
import subprocess
import re

import create_maps
import prism_model_generator
import prism_caller
import json

import urc_synthesis

reps = 10

def main():
    # Initialize result lists for times, states, and transitions
    result_times = [[] for _ in range(4)]
    result_states = [[] for _ in range(4)]
    result_transitions = [[] for _ in range(4)]

    # Run experiments and collect results
    for _ in range(reps):
        create_maps.create_4_maps()
        for i in range(0, len(create_maps.sizes)):
            print(f'Starting with map {i}')
            __modify_properties(i)
            prism_model_generator.generate_model(i)
            infilename = f'Applications/EvoChecker-master/models/model_{i}.prism'
            outfilename = f'Applications/EvoChecker-master/models/model_{i}_.prism'
            urc_synthesis.manipulate_prism_model(infilename, outfilename, baseline=True)
            times, states, transitions = __prism_caller(outfilename)

            # Extend result lists with the new results
            result_times[i].extend(times)
            result_states[i].extend(states)
            result_transitions[i].extend(transitions)

    # Calculate mean and std dev for each metric
    stats_times = [__calc_mean_stddev(times) for times in result_times]
    stats_states = [__calc_mean_stddev(states) for states in result_states]
    stats_transitions = [__calc_mean_stddev(transitions) for transitions in result_transitions]

    # Print the results
    print('Model checking took (mean, standard deviation) in s')
    for i, stats in enumerate(stats_times):
        print(f'{stats} for size {create_maps.sizes[i]}')

    print('\nStates (mean, standard deviation)')
    for i, stats in enumerate(stats_states):
        print(f'{stats} for size {create_maps.sizes[i]}')

    print('\nTransitions (mean, standard deviation)')
    for i, stats in enumerate(stats_transitions):
        print(f'{stats} for size {create_maps.sizes[i]}')


def __modify_properties(i):
    try:
        with open('input.json', 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {"startX": 0, "startY": 0, "targetX": create_maps.sizes[i]-1, "targetY": create_maps.sizes[i]-1, "p": 0.01, "updates": [5], "map_file": "map.csv"}
    # Modify targetX and targetY to be equal to i
    data["targetX"] = create_maps.sizes[i]-1
    data["targetY"] = create_maps.sizes[i]-1
    # Write the modified data back to the JSON file
    with open('input.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

def __prism_caller(file_name):
    command = prism_caller.command.replace('out.prism', file_name)
    checking_times = []
    states = []
    transitions = []

    for prop in prism_caller.properties:
        try:
            result = subprocess.run(
                command + prop,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                shell=True,  # Use shell for command execution
                universal_newlines=True,  # Return output as text (str)
            )
            # Check if the command was successful (return code 0)
            if result.returncode == 0:
                # Capture standard output and standard error
                stdout = result.stdout

                # Print or process the captured output as needed
                # Find and print the line that starts with "Result:"
                lines = stdout.splitlines()
                for line in lines:
                    if line.startswith("Time for model checking:"):
                        # Regular expression to match the floating-point number in the line
                        match = re.search(r'Time for model checking:\s*([\d.]+)\s*seconds', line)
                        checking_times.append(match.group(1))
                    elif line.startswith('States:'):
                        match = re.search(r'States:\s+(\d+)', line)
                        states.append(match.group(1))
                    elif line.startswith('Transitions:'):
                        match = re.search(r'Transitions:\s+(\d+)', line)
                        transitions.append(match.group(1))
            else:
                print(f"Command failed with return code {result.returncode}")
                print(result.stdout)
                print(result.stderr)
        except Exception as e:
            print(f"An error occurred: {e}")

    return [checking_times, states, transitions]


def __calc_mean_stddev(times):
    # Convert the list of string times to floats
    float_times = [float(time) for time in times]

    # Calculate mean and standard deviation
    if len(float_times) > 1:  # Standard deviation requires at least 2 data points
        mean_val = statistics.mean(float_times)
        stdev_val = statistics.stdev(float_times)
        return [round(mean_val, 3), round(stdev_val, 3)]
    else:
        mean_val = statistics.mean(float_times)
        return [round(mean_val, 3), None]  # Return None for std dev if there's not enough data


if __name__ == '__main__':
    main()
