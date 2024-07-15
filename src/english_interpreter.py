import argparse
from execution_engine import ExecutionEngine
from output_generator import OutputGenerator
from intent_recognizer import IntentRecognizer
from input_processor import InputProcessor
from langchain_community.embeddings import OllamaEmbeddings

class EnglishInterpreter:
    def __init__(self):
        self.execution_engine = ExecutionEngine()
        self.output_generator = OutputGenerator()
        self.intent_recognizer = IntentRecognizer()
        self.input_processor = InputProcessor()
        self.variables = {}  # Dictionary to store variables
        self.functions = {}  # Dictionary to store user-defined functions
        self.data_structures = {}  # Dictionary to store complex data structures
        self.algorithms = {}  # Dictionary to store implemented algorithms
        self.current_scope = {}  # Initialize current_scope
        self.embeddings = OllamaEmbeddings()  # Instantiate OllamaEmbeddings

    def main_driver(self, english_instruction=None, test_file=None):
        if test_file:
            return self.process_test_instructions(test_file)
        elif english_instruction:
            return self.process_single_instruction(english_instruction)
        else:
            raise ValueError("Either english_instruction or test_file must be provided")

    def process_single_instruction(self, english_instruction):
        intent_data = self.input_processor.process_input(english_instruction)
        context = self._get_current_context()
        recognized_intent = self.intent_recognizer.recognize_intent(intent_data, context)
        result = self._execute_instruction(recognized_intent, context)
        self._update_context(result, context)
        output = self.output_generator.generate_output(result, context)
        return {
            'output': output,
            'context': context,
            'intent': recognized_intent
        }

    def _get_current_context(self):
        return {
            'variables': self.variables,
            'functions': self.functions,
            'scope': self.current_scope
        }

    def _update_context(self, result, context):
        self.variables = context['variables']
        self.functions = context['functions']
        self.current_scope = context['scope']

    def _execute_instruction(self, recognized_intent, context):
        intent_type = recognized_intent['type']
        handlers = {
            'variable_assignment': self._handle_variable_assignment,
            'control_structure': self._handle_control_structure,
            'function_definition': self._handle_function_definition,
            'function_call': self._handle_function_call,
            'io_operation': self._handle_io_operation,
            'data_structure_operation': self._handle_data_structure_operation,
            'algorithm_execution': self._handle_algorithm_execution,
            'expression_evaluation': self._handle_expression_evaluation,
            'error_handling': self._handle_error_handling,
            'module_import': self._handle_module_import,
            'code_block': self._handle_code_block,
        }

        handler = handlers.get(intent_type, self.execution_engine.execute)
        return handler(recognized_intent, context)

    def _handle_expression_evaluation(self, intent_data, context):
        expression = intent_data.get('expression')
        try:
            result = eval(expression, {}, context['variables'])
            return {'status': 'success', 'result': result}
        except Exception as e:
            return {'status': 'error', 'message': f"Error evaluating expression: {str(e)}"}

    def _handle_error_handling(self, intent_data, context):
        try:
            action = intent_data.get('action')
            result = self._execute_instruction({'type': 'code_block', 'code': action}, context)
            return {'status': 'success', 'result': result}
        except Exception as e:
            error_handler = intent_data.get('error_handler')
            if error_handler:
                return self._execute_instruction({'type': 'code_block', 'code': error_handler}, context)
            else:
                return {'status': 'error', 'message': f"Unhandled error: {str(e)}"}

    def _handle_module_import(self, intent_data, context):
        module_name = intent_data.get('module_name')
        try:
            module = __import__(module_name)
            context['modules'][module_name] = module
            return {'status': 'success', 'message': f"Module '{module_name}' imported successfully"}
        except ImportError as e:
            return {'status': 'error', 'message': f"Error importing module '{module_name}': {str(e)}"}

    def _handle_code_block(self, intent_data, context):
        code = intent_data.get('code')
        results = []
        for instruction in code.split(';'):
            instruction = instruction.strip()
            if instruction:
                result = self.process_single_instruction(instruction, context)
                results.append(result)
        return {'status': 'success', 'results': results}

    def _handle_variable_assignment(self, intent_data):
        try:
            variable_name = intent_data.get('variable_name')
            value = intent_data.get('value')
            data_type = intent_data.get('data_type', 'auto')

            if not variable_name:
                raise ValueError("Variable name not provided")

            if value is None:
                raise ValueError("Value not provided")

            # Convert value to appropriate type based on data_type or auto-detect
            if data_type == 'auto':
                value = self._auto_convert_value(value)
            else:
                value = self._convert_value(value, data_type)

            # Handle complex assignments (e.g., list indexing, dictionary keys, nested structures)
            if '.' in variable_name or '[' in variable_name:
                self._handle_complex_assignment(variable_name, value)
            else:
                self._assign_variable(variable_name, value)

            return {
                'status': 'success',
                'message': f"Variable '{variable_name}' assigned value: {value} (type: {type(value).__name__})"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error in variable assignment: {str(e)}"
            }

    def _assign_variable(self, variable_name, value):
        # Support for nested dictionaries and lists
        parts = variable_name.split('.')
        current = self.variables
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        last_part = parts[-1]
        if '[' in last_part:
            list_name, index = last_part.split('[')
            index = int(index.rstrip(']'))
            if list_name not in current:
                current[list_name] = []
            while len(current[list_name]) <= index:
                current[list_name].append(None)
            current[list_name][index] = value
        else:
            current[last_part] = value

    def _auto_convert_value(self, value):
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    # Check for list or dict syntax
                    if value.startswith('[') and value.endswith(']'):
                        return eval(value)  # Caution: eval can be dangerous, consider safer alternatives
                    elif value.startswith('{') and value.endswith('}'):
                        return eval(value)  # Caution: eval can be dangerous, consider safer alternatives
                    return value
        return value

    def _convert_value(self, value, data_type):
        type_converters = {
            'int': int,
            'float': float,
            'bool': lambda x: x.lower() == 'true' if isinstance(x, str) else bool(x),
            'string': str,
            'list': lambda x: x if isinstance(x, list) else [x],
            'dict': lambda x: x if isinstance(x, dict) else {'value': x},
            'set': lambda x: set(x) if isinstance(x, (list, tuple)) else {x}
        }
        converter = type_converters.get(data_type.lower(), lambda x: x)
        return converter(value)

    def _handle_complex_assignment(self, variable_name, value):
        parts = variable_name.split('.')
        current = self.variables
        for part in parts[:-1]:
            if '[' in part:
                name, index = part.split('[')
                index = int(index[:-1])  # Remove closing bracket
                if name not in current:
                    current[name] = []
                while len(current[name]) <= index:
                    current[name].append({})
                current = current[name][index]
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
        last_part = parts[-1]
        if '[' in last_part:
            name, index = last_part.split('[')
            index = int(index[:-1])  # Remove closing bracket
            if name not in current:
                current[name] = []
            while len(current[name]) <= index:
                current[name].append(None)
            current[name][index] = value
        else:
            current[last_part] = value

    def _handle_control_structure(self, intent_data):
        try:
            structure_type = intent_data.get('structure_type')
            condition = intent_data.get('condition')
            action = intent_data.get('action')
            else_action = intent_data.get('else_action')

            if not structure_type or not action:
                raise ValueError("Incomplete control structure information")

            if structure_type in ['if', 'while', 'for', 'switch', 'try']:
                return self._execute_control_structure(structure_type, condition, action, else_action, intent_data)
            else:
                raise ValueError(f"Unsupported control structure: {structure_type}")

        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error in control structure execution: {str(e)}"
            }

    def _execute_control_structure(self, structure_type, condition, action, else_action, intent_data):
        if structure_type == 'if':
            return self._execute_if(condition, action, else_action)
        elif structure_type == 'while':
            return self._execute_while(condition, action)
        elif structure_type == 'for':
            return self._execute_for(condition, action, intent_data)
        elif structure_type == 'switch':
            return self._execute_switch(condition, intent_data)
        elif structure_type == 'try':
            return self._execute_try(action, else_action)

    def _execute_if(self, condition, action, else_action):
        if self._evaluate_complex_condition(condition):
            return self._execute_action(action)
        elif else_action:
            return self._execute_action(else_action)
        return {'status': 'success', 'message': "Condition not met, no action taken"}

    def _execute_while(self, condition, action):
        result = {'status': 'success', 'message': "While loop executed"}
        while self._evaluate_complex_condition(condition):
            action_result = self._execute_action(action)
            if action_result['status'] == 'error':
                return action_result
            if 'break' in action_result:
                break
            if 'continue' in action_result:
                continue
        return result

    def _execute_for(self, condition, action, intent_data):
        iterations = intent_data.get('iterations')
        iterator = intent_data.get('iterator')
        iterable = intent_data.get('iterable')

        result = {'status': 'success', 'message': "For loop executed"}
        if iterations:
            for i in range(int(iterations)):
                self.variables['_index'] = i
                action_result = self._execute_action(action)
                if action_result['status'] == 'error':
                    return action_result
                if 'break' in action_result:
                    break
                if 'continue' in action_result:
                    continue
        elif iterator and iterable:
            for i, item in enumerate(self._get_iterable(iterable)):
                self.variables[iterator] = item
                self.variables['_index'] = i
                action_result = self._execute_action(action)
                if action_result['status'] == 'error':
                    return action_result
                if 'break' in action_result:
                    break
                if 'continue' in action_result:
                    continue
        else:
            raise ValueError("Invalid 'for' loop parameters")
        return result

    def _execute_switch(self, condition, intent_data):
        cases = intent_data.get('cases', {})
        default = intent_data.get('default')

        condition_value = self._evaluate_complex_condition(condition)
        for case, action in cases.items():
            if self._evaluate_complex_condition(f"{condition_value} == {case}"):
                return self._execute_action(action)
        if default:
            return self._execute_action(default)
        return {'status': 'success', 'message': "No matching case found"}

    def _execute_try(self, try_action, except_action):
        try:
            return self._execute_action(try_action)
        except Exception as e:
            self.variables['_exception'] = str(e)
            return self._execute_action(except_action)

    def _evaluate_complex_condition(self, condition):
        try:
            return self.execution_engine.evaluate_condition(condition, self.variables)
        except Exception as e:
            raise ValueError(f"Error evaluating condition: {str(e)}")

    def _evaluate_condition(self, condition):
        try:
            return self.execution_engine.evaluate_condition(condition, self.variables)
        except Exception as e:
            return {'status': 'error', 'message': f"Error evaluating condition: {str(e)}"}

    def _execute_action(self, action):
        return self.process_single_instruction(action)

    def _get_iterable(self, iterable_name):
        if iterable_name in self.variables:
            return self.variables[iterable_name]
        else:
            raise ValueError(f"Iterable '{iterable_name}' not found")

    def _handle_function_definition(self, intent_data):
        try:
            function_name = intent_data.get('function_name')
            parameters = intent_data.get('parameters', [])
            body = intent_data.get('body')

            if not function_name or not body:
                raise ValueError("Incomplete function definition")

            if not hasattr(self, 'functions'):
                self.functions = {}

            def dynamic_function(*args, **kwargs):
                local_scope = self.variables.copy()
                for param, arg in zip(parameters, args):
                    local_scope[param] = arg
                for key, value in kwargs.items():
                    if key in parameters:
                        local_scope[key] = value
                return self._execute_function_body(body, local_scope)

            self.functions[function_name] = dynamic_function

            return {
                'status': 'success',
                'message': f"Function '{function_name}' defined successfully",
                'data': {'name': function_name, 'parameters': parameters}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error in function definition: {str(e)}"
            }

    def _execute_function_body(self, body, local_scope):
        instructions = [instr.strip() for instr in body.split(';') if instr.strip()]
        result = None
        for instruction in instructions:
            intent_data = self.input_processor.process_input(instruction)
            recognized_intent = self.intent_recognizer.recognize_intent(intent_data)
            result = self._execute_instruction(recognized_intent, context={'variables': local_scope})
            if result.get('status') == 'error':
                break
        return result

    def _handle_function_call(self, intent_data):
        try:
            function_name = intent_data.get('function_name')
            arguments = intent_data.get('arguments', [])
            keyword_arguments = intent_data.get('keyword_arguments', {})

            if function_name not in self.functions:
                raise ValueError(f"Function '{function_name}' is not defined")

            result = self.functions[function_name](*arguments, **keyword_arguments)

            return {
                'status': 'success',
                'message': f"Function '{function_name}' called successfully",
                'data': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error in function call: {str(e)}"
            }

    def _handle_return_statement(self, intent_data):
        value = intent_data.get('value')
        if value in self.variables:
            value = self.variables[value]
        return {
            'status': 'return',
            'data': value
        }

    def _handle_io_operation(self, intent_data):
        try:
            operation_type = intent_data.get('operation_type')
            target = intent_data.get('target')
            content = intent_data.get('content')

            if operation_type == 'read':
                if target.startswith('file:'):
                    with open(target[5:], 'r') as file:
                        result = file.read()
                    return {'status': 'success', 'message': f"File '{target[5:]}' read successfully", 'data': result}
                else:
                    raise ValueError("Unsupported read target")

            elif operation_type == 'write':
                if target.startswith('file:'):
                    with open(target[5:], 'w') as file:
                        file.write(content)
                    return {'status': 'success', 'message': f"Content written to file '{target[5:]}' successfully"}
                else:
                    raise ValueError("Unsupported write target")

            elif operation_type == 'display':
                print(content)
                return {'status': 'success', 'message': "Content displayed successfully"}

            elif operation_type == 'input':
                user_input = input(content)
                return {'status': 'success', 'message': "User input received", 'data': user_input}

            else:
                raise ValueError(f"Unsupported I/O operation: {operation_type}")

        except Exception as e:
            return {'status': 'error', 'message': f"Error in I/O operation: {str(e)}"}

    def _handle_data_structure_operation(self, intent_data):
        try:
            operation_type = intent_data.get('operation_type')
            structure_name = intent_data.get('structure_name')
            data = intent_data.get('data')

            if structure_name not in self.data_structures:
                self.data_structures[structure_name] = []

            if operation_type == 'create':
                self.data_structures[structure_name] = data
                return {'status': 'success', 'message': f"Data structure '{structure_name}' created successfully"}
            elif operation_type == 'add':
                self.data_structures[structure_name].append(data)
                return {'status': 'success', 'message': f"Data added to '{structure_name}' successfully"}
            elif operation_type == 'remove':
                self.data_structures[structure_name].remove(data)
                return {'status': 'success', 'message': f"Data removed from '{structure_name}' successfully"}
            elif operation_type == 'get':
                return {'status': 'success', 'message': f"Data retrieved from '{structure_name}'", 'data': self.data_structures[structure_name]}
            else:
                raise ValueError(f"Unsupported data structure operation: {operation_type}")

        except Exception as e:
            return {'status': 'error', 'message': f"Error in data structure operation: {str(e)}"}

    def _handle_algorithm_execution(self, intent_data):
        try:
            algorithm_name = intent_data.get('algorithm_name')
            input_data = intent_data.get('input_data')

            if algorithm_name == 'sort':
                result = sorted(input_data)
                return {'status': 'success', 'message': "Sorting algorithm executed successfully", 'data': result}
            elif algorithm_name == 'search':
                target = intent_data.get('target')
                result = target in input_data
                return {'status': 'success', 'message': "Search algorithm executed successfully", 'data': result}
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm_name}")

        except Exception as e:
            return {'status': 'error', 'message': f"Error in algorithm execution: {str(e)}"}

    def process_test_instructions(self, test_file):
        instructions = self.read_test_instructions(test_file)
        results = []
        for instruction in instructions:
            result = self.process_single_instruction(instruction)
            results.append((instruction, result))
        return results

    def read_test_instructions(self, file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="English Interpreter")
    parser.add_argument("--test", help="Path to test instructions file")
    args = parser.parse_args()

    interpreter = EnglishInterpreter()
    if args.test:
        results = interpreter.main_driver(test_file=args.test)
        for instruction, result in results:
            print(f"Instruction: {instruction}")
            print(f"Result: {result}")
            print("---")
    else:
        while True:
            user_input = input("Enter an instruction (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            result = interpreter.main_driver(english_instruction=user_input)
            print(f"Result: {result}")