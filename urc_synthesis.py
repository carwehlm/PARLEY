import os
import re
import shutil


def manipulate_prism_model(input_path, output_path, possible_decisions=[1, 10], decision_variables=[],
                           before_actions=['east', 'west', 'north', 'south'], after_actions=['update', 'skip_update'], module_name='Knowledge', baseline=False, initial_pop_file='Set'):
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise ValueError("Input and output files cannot be the same.")

    shutil.copyfile(input_path, output_path)

    variables, estimates = get_variables(input_path, decision_variables)

    remove_counter_from_module(output_path)

    add_controller(output_path, estimates, variables, possible_decisions, baseline, initial_pop_file)

    add_turn(output_path, before_actions, after_actions)


def get_variables(prism_model_path, decision_variables):
    # get all int constants
    int_constants_pattern = re.compile(r'const\s+int\s+(\w+)\s*=\s*(-?\s*\d+)\s*;')
    int_constants = {}

    with open(prism_model_path, 'r') as prism_model_file:
        # Process the file line by line
        for line in prism_model_file:
            # Match constants in each line
            matches = int_constants_pattern.finditer(line)
            for match in matches:
                int_constants[match.group(1)] = int(match.group(2).replace(" ", ""))

    int_variable_declaration_pattern = re.compile(
        r'(\w+)\s*:\s*\[(-?\s*\w+)\s*\.\.\s*(-?\s*\w+)\]\s*init\s*(-?\s*\w+)\s*;')
    _vars = []
    _bel = []

    with open(prism_model_path, 'r') as prism_model_file:
        # Process the file line by line again
        for line in prism_model_file:
            # Match variables in each line
            matches = int_variable_declaration_pattern.finditer(line)
            for match in matches:
                if match.group(1)[-3:] == 'hat':
                    _bel.append(match.group(1))
                elif match.group(1) not in decision_variables:
                    continue
                lower_limit = __get_limit(match.group(2).replace(" ", ""), int_constants)
                upper_limit = __get_limit(match.group(3).replace(" ", ""), int_constants)
                _vars.append([match.group(1), lower_limit, upper_limit])

    return _vars, _bel


def __get_limit(string, constants):
    if not string.lstrip("-").isdigit():
        return constants[string]
    else:
        return int(string)


def remove_counter_from_module(output_path):
    pattern = re.compile(r"^\s*const\s+int\s+c\d*\s*=\s*\d+\s*;")
    with open(output_path, 'r') as file:
        lines = file.readlines()

    # Filter out lines that match the regex pattern
    new_lines = [line for line in lines if not pattern.match(line)]

    # Write the modified content back to the file
    with open(output_path, 'w') as file:
        file.writelines(new_lines)


def add_controller(file_path, estimates, variables, possible_decisions, baseline, initial_pop_file):
    combinations = generate_combinations_list(variables)
    __add_controller_prefix(file_path, possible_decisions, combinations, variables, baseline)
    with open(file_path, 'a') as file:
        file.write('  c : [1..10] init decision_0_0;\n')

        for combination in combinations:
            # combination describes a tuple of values, e.g., for ^x and ^y, such as (0, 0)
            new_line = '  [URC] 1=1'
            for c, estimate in zip(combination, estimates):
                # estimate describes the variable's name
                new_line += f' & {estimate}={c}'
            new_line += ' -> (c\'=decision'
            for c in combination:
                new_line += f'_{c}'
            new_line += ');\n'
            file.write(new_line)
        file.write('endmodule\n')

    __generate_initial_population(initial_pop_file, possible_decisions, combinations)


def __add_controller_prefix(file_path, possible_decisions, combinations, variables, baseline):
    # write decision variables
    with open(file_path, 'a') as file:
        for combination in combinations:
            if baseline:
                new_line = 'const int decision'
            else:
                new_line = 'evolve int decision'
            for var in range(0, len(variables)):
                new_line += '_' + str(combination[var])
            if baseline:
                new_line += '=1;'
            else:
                new_line += f' [{possible_decisions[0]}..{possible_decisions[1]}];'
            file.write('\n' + new_line)
        file.write('\nmodule URC\n')


def add_turn(file_path, before_actions, after_actions):
    with open(file_path, 'a') as file:
        file.write('module Turn\n')
        file.write('  t : [0..2] init 0;\n')
        # actions that precede
        for action in before_actions:
            file.write(f'  [{action}] (t=0) -> (t\'=1);\n')
        file.write('\n')
        file.write('  [URC] (t=1) -> (t\'=2);\n')
        file.write('\n')
        for action in after_actions:
            file.write(f'  [{action}] (t=2) -> (t\'=0);\n')
        if len(after_actions) == 0:
            file.write('  [] (t=2) -> (t\'=0);\n')
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


def __generate_initial_population(file_path, possible_decisions, combinations):
    # write decision variables
    with open(file_path, 'w') as file:
        for c in range(possible_decisions[0], possible_decisions[1]):
            new_line = ''
            for _ in range(len(combinations)):
                new_line += f'{c} '
            file.write(new_line + '\n')
