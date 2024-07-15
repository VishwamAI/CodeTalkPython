import re
import ast
from typing import Any, Dict, List, Union

class EnglishExecutionEngine:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, callable] = {}

    def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """Parse English instructions into executable operations."""
        # Variable management
        if match := re.match(r"(Create|Set|Get|Delete) (?:a )?variable (?:named )?'(\w+)'(?: (?:with|to) value (.+))?", instruction):
            return {
                'operation': 'variable_management',
                'action': match.group(1).lower(),
                'name': match.group(2),
                'value': self._parse_value(match.group(3)) if match.group(3) else None
            }

        # Arithmetic operation
        elif match := re.match(r"Set '(\w+)' to '(\w+)' (plus|minus|times|divided by) '(\w+)'", instruction):
            return {
                'operation': 'arithmetic',
                'result_var': match.group(1),
                'operand1': match.group(2),
                'operation_type': match.group(3),
                'operand2': match.group(4)
            }

        # Control structures
        elif match := re.match(r"(If|While) '(\w+)' is (greater than|less than|equal to) (\d+), (.*?)(?:, otherwise (.*))?$", instruction):
            return {
                'operation': 'control_structure',
                'type': match.group(1).lower(),
                'condition_var': match.group(2),
                'comparison': match.group(3),
                'comparison_value': int(match.group(4)),
                'true_action': self.parse_instruction(match.group(5)),
                'false_action': self.parse_instruction(match.group(6)) if match.group(6) else None
            }

        # Loop
        elif match := re.match(r"For (\w+) from (\d+) to (\d+), (.*)", instruction):
            return {
                'operation': 'loop',
                'loop_var': match.group(1),
                'start': int(match.group(2)),
                'end': int(match.group(3)),
                'action': self.parse_instruction(match.group(4))
            }

        # Function management
        elif match := re.match(r"(Define|Call) (?:a )?function (?:named )?'(\w+)'(?: that takes (.*?) as parameters)?(?: and returns (.*?))?$", instruction):
            if match.group(1) == 'Define':
                return {
                    'operation': 'function_definition',
                    'name': match.group(2),
                    'parameters': [param.strip() for param in match.group(3).split(',')] if match.group(3) else [],
                    'return_expression': match.group(4)
                }
            else:
                return {
                    'operation': 'function_call',
                    'name': match.group(2),
                    'arguments': [self._parse_value(arg.strip()) for arg in match.group(3).split(',')] if match.group(3) else []
                }

        # List operations
        elif match := re.match(r"(Create|Append to|Remove from|Get from) list '(\w+)'(?: (with|item|at index) (.+))?", instruction):
            return {
                'operation': 'list_operation',
                'list_operation': match.group(1).lower(),
                'list_name': match.group(2),
                'item' if match.group(1).lower() in ['append', 'remove'] else 'index': self._parse_value(match.group(4)) if match.group(4) else None
            }

        # Dictionary operations
        elif match := re.match(r"(Create|Set|Get|Remove) (?:from )?dictionary '(\w+)'(?: (?:with key|key) '(.+)'(?: (?:and|to) value '(.+)')?)?", instruction):
            return {
                'operation': 'dictionary_operation',
                'dict_operation': match.group(1).lower(),
                'dict_name': match.group(2),
                'key': self._parse_value(match.group(3)) if match.group(3) else None,
                'value': self._parse_value(match.group(4)) if match.group(4) else None
            }

        # File operations
        elif match := re.match(r"(Open|Close|Read|Write|Append to) file '(.+)'(?: with (content|mode) '(.+)')?", instruction):
            return {
                'operation': 'file_operation',
                'file_operation': match.group(1).lower(),
                'filename': match.group(2),
                'content' if match.group(3) == 'content' else 'mode': match.group(4) if match.group(4) else None
            }

        # Process management
        elif match := re.match(r"(Start|Stop|Restart) process '(.+)'", instruction):
            return {
                'operation': 'process_management',
                'action': match.group(1).lower(),
                'process_name': match.group(2)
            }

        # Network operations
        elif match := re.match(r"(GET|POST|PUT|DELETE) request to '(.+)'(?: with data '(.+)')?", instruction):
            return {
                'operation': 'network_operation',
                'method': match.group(1),
                'url': match.group(2),
                'data': self._parse_value(match.group(3)) if match.group(3) else None
            }

        # System-level operations
        elif match := re.match(r"Execute system command '(.+)'", instruction):
            return {
                'operation': 'system_operation',
                'command': match.group(1)
            }

        else:
            raise ValueError(f"Unrecognized instruction: {instruction}")

    def _parse_value(self, value_str: str) -> Any:
        """Parse a string value into the appropriate Python type."""
        try:
            return ast.literal_eval(value_str)
        except:
            return value_str  # If it's not a literal, return it as a string

    def execute_instruction(self, parsed_instruction: Dict[str, Any]) -> Any:
        """Execute the parsed instructions."""
        operation = parsed_instruction['operation']

        if operation == 'variable_management':
            return self.handle_variable_management(
                parsed_instruction['action'],
                parsed_instruction['name'],
                parsed_instruction.get('value')
            )
        elif operation == 'arithmetic':
            return self.handle_arithmetic_operation(
                parsed_instruction['result_var'],
                parsed_instruction['operand1'],
                parsed_instruction['operation_type'],
                parsed_instruction['operand2']
            )
        elif operation == 'control_structure':
            return self.handle_control_structure(
                parsed_instruction['type'],
                parsed_instruction['condition_var'],
                parsed_instruction['comparison'],
                parsed_instruction['comparison_value'],
                parsed_instruction['true_action'],
                parsed_instruction.get('false_action')
            )
        elif operation == 'loop':
            return self.handle_loop(
                parsed_instruction['loop_var'],
                parsed_instruction['start'],
                parsed_instruction['end'],
                parsed_instruction['action']
            )
        elif operation == 'function_definition':
            return self.handle_function_definition(
                parsed_instruction['name'],
                parsed_instruction['parameters'],
                parsed_instruction['return_expression']
            )
        elif operation == 'function_call':
            return self.handle_function_call(
                parsed_instruction['name'],
                parsed_instruction['arguments']
            )
        elif operation == 'list_operation':
            return self.handle_list_operation(
                parsed_instruction['list_operation'],
                parsed_instruction['list_name'],
                parsed_instruction.get('item'),
                parsed_instruction.get('index')
            )
        elif operation == 'dictionary_operation':
            return self.handle_dictionary_operation(
                parsed_instruction['dict_operation'],
                parsed_instruction['dict_name'],
                parsed_instruction.get('key'),
                parsed_instruction.get('value')
            )
        elif operation == 'file_operation':
            return self.handle_file_operation(
                parsed_instruction['file_operation'],
                parsed_instruction['filename'],
                parsed_instruction.get('content'),
                parsed_instruction.get('mode')
            )
        elif operation == 'process_management':
            return self.handle_process_management(
                parsed_instruction['action'],
                parsed_instruction['process_name']
            )
        elif operation == 'network_operation':
            return self.handle_network_operation(
                parsed_instruction['method'],
                parsed_instruction['url'],
                parsed_instruction.get('data')
            )
        elif operation == 'system_operation':
            return self.handle_system_operation(
                parsed_instruction['command']
            )
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def handle_variable_management(self, action: str, name: str, value: Any = None) -> None:
        """Handle variable creation, assignment, retrieval, and deletion."""
        try:
            if action == 'create' or action == 'set':
                if isinstance(value, str):
                    value = eval(value, {}, self.variables)
                self.variables[name] = value
                print(f"Variable '{name}' has been assigned the value: {value}")
            elif action == 'get':
                if name not in self.variables:
                    raise ValueError(f"Variable '{name}' is not defined.")
                print(f"Value of variable '{name}': {self.variables[name]}")
                return self.variables[name]
            elif action == 'delete':
                if name not in self.variables:
                    raise ValueError(f"Variable '{name}' is not defined.")
                del self.variables[name]
                print(f"Variable '{name}' has been deleted.")
            else:
                raise ValueError(f"Unknown variable management action: {action}")
        except Exception as e:
            print(f"Error in variable management: {str(e)}")

    def handle_control_structure(self, structure_type: str, condition_var: str, comparison: str,
                                 comparison_value: int, true_action: Dict[str, Any],
                                 false_action: Optional[Dict[str, Any]] = None) -> None:
        """Handle control structures (if/else, while)."""
        try:
            condition_result = self.variables.get(condition_var)
            if condition_result is None:
                raise ValueError(f"Variable '{condition_var}' is not defined.")

            if comparison == 'greater than':
                result = condition_result > comparison_value
            elif comparison == 'less than':
                result = condition_result < comparison_value
            elif comparison == 'equal to':
                result = condition_result == comparison_value
            else:
                raise ValueError(f"Unknown comparison: {comparison}")

            if structure_type == 'if':
                if result:
                    self.execute_instruction(true_action)
                elif false_action:
                    self.execute_instruction(false_action)
            elif structure_type == 'while':
                while result:
                    self.execute_instruction(true_action)
                    condition_result = self.variables.get(condition_var)
                    result = eval(f"{condition_result} {comparison} {comparison_value}")
            else:
                raise ValueError(f"Unknown control structure type: {structure_type}")
        except Exception as e:
            print(f"Error in control structure execution: {str(e)}")

    def handle_loop(self, loop_var: str, start: int, end: int, action: Dict[str, Any]) -> None:
        """Handle loop structures."""
        try:
            for i in range(start, end + 1):
                self.variables[loop_var] = i
                self.execute_instruction(action)
            print(f"Loop completed. Final value of {loop_var}: {self.variables[loop_var]}")
        except Exception as e:
            print(f"Error in loop execution: {str(e)}")

    def handle_function_definition(self, name: str, parameters: List[str], return_expression: str) -> None:
        """Define functions based on English instructions."""
        try:
            def function(*args):
                if len(args) != len(parameters):
                    raise ValueError(f"Expected {len(parameters)} arguments, got {len(args)}")
                for param, arg in zip(parameters, args):
                    self.variables[param] = arg
                return eval(return_expression, {}, self.variables)

            self.functions[name] = function
            print(f"Function '{name}' has been defined with parameters: {', '.join(parameters)}")
        except Exception as e:
            print(f"Error in function definition: {str(e)}")

    def handle_function_call(self, name: str, arguments: List[Any]) -> Any:
        """Execute function calls."""
        try:
            if name not in self.functions:
                raise ValueError(f"Function '{name}' is not defined.")

            result = self.functions[name](*arguments)
            print(f"Function '{name}' called with arguments: {', '.join(map(str, arguments))}")
            print(f"Result: {result}")
            return result
        except Exception as e:
            print(f"Error in function call: {str(e)}")
            return None

    def handle_list_operation(self, operation: str, list_name: str, item: Any = None, index: int = None) -> Any:
        """Handle list operations (create, append, remove, get)."""
        try:
            if operation == "create":
                self.variables[list_name] = []
                print(f"Created a new list '{list_name}'")
            elif operation == "append":
                if list_name not in self.variables:
                    raise ValueError(f"List '{list_name}' does not exist")
                self.variables[list_name].append(item)
                print(f"Appended {item} to list '{list_name}'")
            elif operation == "remove":
                if list_name not in self.variables:
                    raise ValueError(f"List '{list_name}' does not exist")
                self.variables[list_name].remove(item)
                print(f"Removed {item} from list '{list_name}'")
            elif operation == "get":
                if list_name not in self.variables:
                    raise ValueError(f"List '{list_name}' does not exist")
                if index is None:
                    raise ValueError("Index is required for 'get' operation")
                return self.variables[list_name][index]
            else:
                raise ValueError(f"Unknown list operation: {operation}")
        except Exception as e:
            print(f"Error in list operation: {str(e)}")

    def handle_dictionary_operation(self, operation: str, dict_name: str, key: Any = None, value: Any = None) -> Any:
        """Handle dictionary operations (create, set, get, remove)."""
        try:
            if operation == "create":
                self.variables[dict_name] = {}
                print(f"Created a new dictionary '{dict_name}'")
            elif operation == "set":
                if dict_name not in self.variables:
                    raise ValueError(f"Dictionary '{dict_name}' does not exist")
                self.variables[dict_name][key] = value
                print(f"Set key '{key}' to value '{value}' in dictionary '{dict_name}'")
            elif operation == "get":
                if dict_name not in self.variables:
                    raise ValueError(f"Dictionary '{dict_name}' does not exist")
                if key not in self.variables[dict_name]:
                    raise KeyError(f"Key '{key}' not found in dictionary '{dict_name}'")
                return self.variables[dict_name][key]
            elif operation == "remove":
                if dict_name not in self.variables:
                    raise ValueError(f"Dictionary '{dict_name}' does not exist")
                if key not in self.variables[dict_name]:
                    raise KeyError(f"Key '{key}' not found in dictionary '{dict_name}'")
                del self.variables[dict_name][key]
                print(f"Removed key '{key}' from dictionary '{dict_name}'")
            else:
                raise ValueError(f"Unknown dictionary operation: {operation}")
        except Exception as e:
            print(f"Error in dictionary operation: {str(e)}")

    def handle_file_operation(self, operation: str, filename: str, content: str = None, mode: str = 'r') -> Any:
        """Handle file operations (open, close, read, write, append)."""
        try:
            if operation == "open":
                self.variables[filename] = open(filename, mode)
                print(f"Opened file '{filename}' in mode '{mode}'")
            elif operation == "close":
                if filename not in self.variables or not hasattr(self.variables[filename], 'close'):
                    raise ValueError(f"No open file object found for '{filename}'")
                self.variables[filename].close()
                del self.variables[filename]
                print(f"Closed file '{filename}'")
            elif operation == "read":
                if filename not in self.variables or not hasattr(self.variables[filename], 'read'):
                    raise ValueError(f"No open file object found for '{filename}'")
                content = self.variables[filename].read()
                print(f"Read content from file '{filename}'")
                return content
            elif operation in ["write", "append"]:
                if filename not in self.variables or not hasattr(self.variables[filename], 'write'):
                    raise ValueError(f"No open file object found for '{filename}'")
                self.variables[filename].write(content)
                print(f"{'Wrote' if operation == 'write' else 'Appended'} content to file '{filename}'")
            else:
                raise ValueError(f"Unknown file operation: {operation}")
        except Exception as e:
            print(f"Error in file operation: {str(e)}")

    def handle_process_management(self, action: str, process_name: str) -> None:
        """Handle process management operations (start, stop, restart)."""
        try:
            import psutil
            if action == "start":
                # This is a simplified version. In reality, you'd need more information to start a process.
                print(f"Starting process '{process_name}'")
                # os.system(f"start {process_name}")  # This is Windows-specific
            elif action in ["stop", "restart"]:
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == process_name:
                        if action == "stop":
                            proc.terminate()
                            print(f"Stopped process '{process_name}'")
                        else:  # restart
                            proc.terminate()
                            proc.wait()
                            # Again, this is simplified. You'd need the full command to restart.
                            print(f"Restarted process '{process_name}'")
                        break
                else:
                    print(f"No process named '{process_name}' found")
            else:
                raise ValueError(f"Unknown process management action: {action}")
        except Exception as e:
            print(f"Error in process management: {str(e)}")

    def handle_network_operation(self, method: str, url: str, data: Any = None) -> Any:
        """Handle network operations (GET, POST, PUT, DELETE requests)."""
        try:
            import requests
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                raise ValueError(f"Unknown HTTP method: {method}")

            print(f"Performed {method} request to {url}")
            return response.json()
        except Exception as e:
            print(f"Error in network operation: {str(e)}")

    def handle_system_operation(self, command: str) -> str:
        """Handle system-level operations (execute system commands)."""
        try:
            import subprocess
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"Executed system command: {command}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing system command: {e}")
            return e.output
        except Exception as e:
            print(f"Error in system operation: {str(e)}")
    def handle_arithmetic_operation(self, result_var: str, operand1: str, operation_type: str, operand2: str) -> None:
        """Perform basic arithmetic operations."""
        try:
            value1 = self.variables.get(operand1)
            value2 = self.variables.get(operand2)

            if value1 is None or value2 is None:
                raise ValueError(f"One or both operands are not defined: {operand1}, {operand2}")

            if operation_type == 'plus':
                result = value1 + value2
            elif operation_type == 'minus':
                result = value1 - value2
            elif operation_type == 'times':
                result = value1 * value2
            elif operation_type == 'divided by':
                if value2 == 0:
                    raise ValueError("Division by zero")
                result = value1 / value2
            else:
                raise ValueError(f"Unknown arithmetic operation: {operation_type}")

            self.variables[result_var] = result
            print(f"Result of {operand1} {operation_type} {operand2}: {result}")
            print(f"Stored result in variable '{result_var}'")
        except Exception as e:
            print(f"Error in arithmetic operation: {str(e)}")

    def handle_list_operation(self, operation: str, list_name: str, item: Any = None, index: int = None) -> Any:
        """Perform list operations (create, append, remove, get)."""
        try:
            if operation == "create":
                self.variables[list_name] = []
                print(f"Created a new list '{list_name}'")
            elif operation == "append":
                if list_name not in self.variables:
                    raise ValueError(f"List '{list_name}' does not exist")
                self.variables[list_name].append(item)
                print(f"Appended {item} to list '{list_name}'")
            elif operation == "remove":
                if list_name not in self.variables:
                    raise ValueError(f"List '{list_name}' does not exist")
                self.variables[list_name].remove(item)
                print(f"Removed {item} from list '{list_name}'")
            elif operation == "get":
                if list_name not in self.variables:
                    raise ValueError(f"List '{list_name}' does not exist")
                if index is None:
                    raise ValueError("Index is required for 'get' operation")
                return self.variables[list_name][index]
            else:
                raise ValueError(f"Unknown list operation: {operation}")
        except Exception as e:
            print(f"Error in list operation: {str(e)}")

    def handle_dictionary_operation(self, operation: str, dict_name: str, key: Any = None, value: Any = None) -> Any:
        """Perform dictionary operations (create, set, get, remove)."""
        try:
            if operation == "create":
                self.variables[dict_name] = {}
                print(f"Created a new dictionary '{dict_name}'")
            elif operation == "set":
                if dict_name not in self.variables:
                    raise ValueError(f"Dictionary '{dict_name}' does not exist")
                self.variables[dict_name][key] = value
                print(f"Set key '{key}' to value '{value}' in dictionary '{dict_name}'")
            elif operation == "get":
                if dict_name not in self.variables:
                    raise ValueError(f"Dictionary '{dict_name}' does not exist")
                if key not in self.variables[dict_name]:
                    raise KeyError(f"Key '{key}' not found in dictionary '{dict_name}'")
                return self.variables[dict_name][key]
            elif operation == "remove":
                if dict_name not in self.variables:
                    raise ValueError(f"Dictionary '{dict_name}' does not exist")
                if key not in self.variables[dict_name]:
                    raise KeyError(f"Key '{key}' not found in dictionary '{dict_name}'")
                del self.variables[dict_name][key]
                print(f"Removed key '{key}' from dictionary '{dict_name}'")
            else:
                raise ValueError(f"Unknown dictionary operation: {operation}")
        except Exception as e:
            print(f"Error in dictionary operation: {str(e)}")

    def handle_input_output(self, operation: str, value: Any = None) -> Any:
        """Handle user input and output operations."""
        if operation == "input":
            return input(value)
        elif operation == "output":
            print(value)
        else:
            raise ValueError(f"Unknown input/output operation: {operation}")

def main():
    engine = EnglishExecutionEngine()
    # TODO: Add example usage of the EnglishExecutionEngine

if __name__ == "__main__":
    main()