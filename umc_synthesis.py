import re
import os

# flag to depict if UMC or baseline should be generated
baseline = False


def manipulate_prism_model(input_path, output_path, possible_decisions=[1, 10], decision_variables=[],
                           before_actions=[], after_actions=[]):
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise ValueError("Input and output files cannot be the same.")

    out = open(output_path, 'w')
    out.close()

    # Open the input file
    with open(input_path, 'r') as input_file:
        # Open the output file
        with open(output_path, 'a+') as output_file:
            # Process the file line by line
            for line in input_file:
                if 'const int c = ' not in line:
                    # Copy the line to the output file
                    output_file.write(line)

            # Reset the file pointer to the beginning
            input_file.seek(0)
            output_file.seek(0)

            # Call the methods with the output file
            variables, beliefs = get_variables(input_file, decision_variables)
            combinations = generate_combinations_list(variables)

            add_umc(output_file, combinations, variables, possible_decisions, before_actions, after_actions)


def get_variables(file, decision_variables):
    # get all constants
    constants_pattern = re.compile(r'const\s+int\s+(\w+)\s*=\s*(\d+);')
    constants = {}

    # Process the file line by line
    for line in file:
        # Match constants in each line
        matches = constants_pattern.finditer(line)
        for match in matches:
            constants[match.group(1)] = int(match.group(2))

    pattern = re.compile(r'(\w+)\s*:\s*\[(\w+)\.\.(\w+)\]\s*init\s*(\w+);')
    _vars = []
    _bel = []

    # Reset the file pointer to the beginning
    file.seek(0)

    # Process the file line by line again
    for line in file:
        # Match variables in each line
        matches = pattern.finditer(line)
        for match in matches:
            if match.group(1)[-3:] == 'hat':
                _bel.append(match.group(1))
            elif match.group(1) not in decision_variables:
                continue
            lower_limit = __get_limit(match.group(2), constants)
            upper_limit = __get_limit(match.group(3), constants)
            _vars.append([match.group(1), lower_limit, upper_limit])

    return _vars, _bel


def __get_limit(string, constants):
    if not str.isnumeric(string):
        return constants[string]
    else:
        return int(string)


def add_umc(file, combinations, variables, possible_decisions, before_actions, after_actions):
    for combination in combinations:
        if baseline:
            new_line = 'const int decision'
        else:
            new_line = 'evolve int decision'

        for var in range(0, len(variables)):
            new_line += '_' + str(combination[var])
        if baseline:
            new_line += '=0;\n'
        else:
            new_line += ' [{0}..{1}];\n'.format(str(possible_decisions[0]), str(possible_decisions[1]))

        file.write(new_line)
    file.write('module UMC\n')
    file.write('  turn : [1..3] init 1;\n')
    # actions that precede
    for action in before_actions:
        file.write('  [{0}] (t=1) -> (t\'=2);\n'.format(action))
    file.write('\n')
    for combination in combinations:
        file.write('  [] (t=2) -> (c\'=decision_{0}_{1}) & (t\'=3);\n'.format(
            str(possible_decisions[0]), str(possible_decisions[1])
        ))
    file.write('\n')
    for action in after_actions:
        file.write('  [{0}] (t=3) -> (t\'=1);\n'.format(action))
    if len(after_actions) == 0:
        file.write('  [] (t=3) -> (t\'=1);\n')
    file.write('endmodule\n')


def generate_combinations_list(variables):
    result = []

    def generate_combinations_recursive(current_combination, remaining_variables):
        if not remaining_variables:
            result.append(tuple(current_combination))
            return

        current_variable = remaining_variables[0]
        for value in range(current_variable[1], current_variable[2] + 1):
            generate_combinations_recursive(
                current_combination + [value],
                remaining_variables[1:]
            )

    generate_combinations_recursive([], variables)
    return result
