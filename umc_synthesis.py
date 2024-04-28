import re
import os
import shutil


def manipulate_prism_model(input_path, output_path, possible_decisions=[0, 3], decision_variables=[],
                           before_actions=[], after_actions=[], controller=None):
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise ValueError("Input and output files cannot be the same.")

    shutil.copyfile(input_path, output_path)

    variables, beliefs = get_variables(input_path, decision_variables)

    add_transition_to_module(output_path, beliefs)
    if controller is None:
        add_periodic_controller(output_path, possible_decisions, variables)
    else:
        controller(output_path, possible_decisions, variables)
    add_turn(output_path, before_actions, after_actions)


def get_variables(prism_model_path, decision_variables):
    # get all constants
    constants_pattern = re.compile(r'const\s+int\s+(\w+)\s*=\s*(\d+);')
    constants = {}

    with open(prism_model_path, 'r') as prism_model_file:
        # Process the file line by line
        for line in prism_model_file:
            # Match constants in each line
            matches = constants_pattern.finditer(line)
            for match in matches:
                constants[match.group(1)] = int(match.group(2))

    pattern = re.compile(r'(\w+)\s*:\s*\[(\w+)\.\.(\w+)\]\s*init\s*(\w+);')
    _vars = []
    _bel = []

    with open(prism_model_path, 'r') as prism_model_file:
        # Process the file line by line again
        for line in prism_model_file:
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


def add_transition_to_module(file_path, beliefs, module_name='Knowledge'):
    # figure out what the transition should look like
    new_transition = '  [update] true ->'
    for identifier in beliefs:
        new_transition += ' ({0}\'={1}) &'.format(identifier, identifier[:-3])
    # remove the last '&'
    new_transition = new_transition[:-2]
    new_transition += ';'

    # Identify the position of the module declaration
    module_declaration_pattern = re.compile(fr'module {module_name}\s*([\s\S]*?)endmodule')
    module_start_pattern = re.compile(fr'module\s+{module_name}\s+')
    module_end_pattern = re.compile(fr'endmodule')
    # Read the file line by line
    file = open(file_path, 'r')
    lines = file.readlines()
    file.seek(0)

    # Search for the module declaration
    inside_module = False
    added = False
    i = 0
    for line in file:
        # for i, line in enumerate(lines):
        if module_start_pattern.search(line):
            # We found the start of the module
            inside_module = True
        elif inside_module and module_end_pattern.search(line):
            # We found the end of the module
            # Insert the new transition before the end of the module
            lines.insert(i, f"{new_transition}\n")
            inside_module = False
            added = True
            break
        i += 1
    file.close()
    if not added:
        print(f"Module '{module_name}' not found in the model.")
    else:
        # Write the updated lines back to the file
        file = open(file_path, 'w')
        file.writelines(lines)
        file.close()


def add_periodic_controller(file_path, possible_decisions, variables,):
    # write decision variables
    combinations = generate_combinations_list(variables)
    __add_controller_prefix(file_path, possible_decisions, combinations, variables)
    with open(file_path, 'a') as file:
        file.write('  step : [1..{0}] init 1;\n'.format(str(possible_decisions[1])))
    transitions = ['no_update', 'update']
    decisions = ['step<decision', 'step>=decision']
    changes = ['(step\'=step+1)', '(step\'=1)']
    __add_specific_controller(file_path, transitions, decisions, changes, combinations, variables)


def add_static_controller(file_path, possible_decisions, variables):
    # write decision variables
    combinations = generate_combinations_list(variables)
    possible_decisions = [0, 1]
    __add_controller_prefix(file_path, possible_decisions, combinations, variables)
    transitions = ['no_update', 'update']
    decisions = ['zero=decision', 'one=decision']
    changes = ['true', 'true']
    __add_specific_controller(file_path, transitions, decisions, changes, combinations, variables)


def __add_specific_controller(file_path, transitions, decisions, changes, combinations, variables):
    with open(file_path, 'a') as file:
        for transition, decision, change in zip(transitions, decisions, changes):
            for combination in combinations:
                new_line = '  [{0}] ({1}'.format(transition, decision)
                for var in range(0, len(variables)):
                    new_line += '_' + str(combination[var])
                new_line += ')'
                for var in range(0, len(variables)):
                    new_line += ' & ({0}={1})'.format(variables[var][0], str(combination[var]))
                new_line += ' -> {0};\n'.format(change)
                file.write(new_line)

        file.write('endmodule\n\n')


def __add_controller_prefix(file_path, possible_decisions, combinations, variables):
    # write decision variables
    with open(file_path, 'a') as file:
        for combination in combinations:
            new_line = 'evolve int decision'
            # new_line = 'const int decision'
            for var in range(0, len(variables)):
                new_line += '_' + str(combination[var])
            new_line += ' [{0}..{1}];\n'.format(str(possible_decisions[0]), str(possible_decisions[1]))
            # new_line += '=0;\n'
            file.write(new_line)
        file.write('const int zero = 0;\n')
        file.write('const int one = 1;\n')
        file.write('module UMC\n')


def add_turn(file_path, before_actions, after_actions):
    with open(file_path, 'a') as file:
        file.write('module Turn\n')
        file.write('  t : [0..2] init 0;\n')
        # actions that precede
        for action in before_actions:
            file.write('  [{0}] (t=0) -> (t\'=1);\n'.format(action))
        file.write('\n')
        file.write('  [no_update] (t=1) -> (t\'=2);\n')
        file.write('  [update] (t=1) -> (t\'=2);\n')
        file.write('\n')
        for action in after_actions:
            file.write('  [{0}] (t=2) -> (t\'=0);\n'.format(action))
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
