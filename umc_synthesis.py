import re
import os
import shutil


def manipulate_prism_model(input_path, output_path, possible_decisions=[0, 3], decision_variables=[],
                           before_actions=[], after_actions=[], controller=None, module_name='Knowledge'):
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise ValueError("Input and output files cannot be the same.")

    shutil.copyfile(input_path, output_path)

    variables, beliefs = get_variables(input_path, decision_variables)

    add_transition_to_module(output_path, beliefs, module_name)
    if controller is None:
        add_periodic_controller(output_path, possible_decisions, variables)
    else:
        controller(output_path, possible_decisions, variables)
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

    int_variable_declaration_pattern = re.compile(r'(\w+)\s*:\s*\[(-?\s*\w+)\s*\.\.\s*(-?\s*\w+)\]\s*init\s*(-?\s*\w+)\s*;')
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


def add_transition_to_module(file_path, beliefs, module_name='Knowledge'):
    # figure out what the transition should look like
    new_transition = '  [update] true ->'
    for identifier in beliefs:
        new_transition += f' ({identifier}\'={identifier[:-3]}) &'
    # remove the last '&'
    new_transition = new_transition[:-2]
    new_transition += ';'

    # Identify the position of the module declaration
    module_declaration_pattern = re.compile(fr'(?<=module {module_name}).*(?=endmodule)', re.DOTALL)
    file_content = ''
    with open(file_path, 'r') as file:
        file_content = file.read()
    module_content_old_match = module_declaration_pattern.search(file_content)
    if module_content_old_match is None:
        print(f"Module '{module_name}' not found in the model.")
        return  # TODO maybe throw an error
    module_content_old = module_content_old_match.group()
    # append the new transition to the module
    module_content_new = f"{module_content_old}{new_transition}\n"
    # overwrite the file with the new content
    with open(file_path, 'w') as file:
        file.write(file_content.replace(module_content_old, module_content_new))


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
