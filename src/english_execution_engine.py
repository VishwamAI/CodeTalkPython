import re
import ast
import types
from typing import Any, Dict, List, Union, Optional
from .language_templates import LanguageTemplates

class EnglishExecutionEngine:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, callable] = {}
        self.language_templates = LanguageTemplates()
        self.current_language = 'python'  # Default language

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

        # Stack operations
        elif match := re.match(r"(Create|Push|Pop|Peek) (?:a )?stack (?:named )?'(\w+)'(?: (?:with|item) (.+))?", instruction):
            return {
                'operation': 'stack_operation',
                'stack_operation': match.group(1).lower(),
                'stack_name': match.group(2),
                'item': self._parse_value(match.group(3)) if match.group(3) else None
            }

        # Queue operations
        elif match := re.match(r"(Create|Enqueue|Dequeue|Peek) (?:a )?queue (?:named )?'(\w+)'(?: (?:with|item) (.+))?", instruction):
            return {
                'operation': 'queue_operation',
                'queue_operation': match.group(1).lower(),
                'queue_name': match.group(2),
                'item': self._parse_value(match.group(3)) if match.group(3) else None
            }

        # Class operations
        elif match := re.match(r"Create a class named (\w+)", instruction):
            return {
                'operation': 'class_operation',
                'class_operation': 'create',
                'class_name': match.group(1)
            }
        elif match := re.match(r"Add attribute (\w+) to (\w+)", instruction):
            return {
                'operation': 'class_operation',
                'class_operation': 'add_attribute',
                'class_name': match.group(2),
                'attribute_name': match.group(1)
            }
        elif match := re.match(r"Add method (\w+) to (\w+) that takes (.*) and does (.*)", instruction):
            return {
                'operation': 'class_operation',
                'class_operation': 'add_method',
                'class_name': match.group(2),
                'method_name': match.group(1),
                'parameters': [param.strip() for param in match.group(3).split(',')],
                'action': match.group(4)
            }
        # Object operations
        elif match := re.match(r"Create a (\w+) object named (\w+)", instruction):
            return {
                'operation': 'object_operation',
                'object_operation': 'create',
                'class_name': match.group(1),
                'object_name': match.group(2)
            }
        elif match := re.match(r"Set attribute '(\w+)' of '(\w+)' to '(.+)'", instruction):
            return {
                'operation': 'object_operation',
                'object_operation': 'set_attribute',
                'object_name': match.group(2),
                'attribute_name': match.group(1),
                'value': self._parse_value(match.group(3))
            }
        elif match := re.match(r"Get attribute '(\w+)' of '(\w+)'", instruction):
            return {
                'operation': 'object_operation',
                'object_operation': 'get_attribute',
                'object_name': match.group(2),
                'attribute_name': match.group(1)
            }
        elif match := re.match(r"Call method '(\w+)' of '(\w+)' with arguments (.*)", instruction):
            return {
                'operation': 'object_operation',
                'object_operation': 'call_method',
                'object_name': match.group(2),
                'method_name': match.group(1),
                'arguments': [self._parse_value(arg.strip()) for arg in match.group(3).split(',')]
            }
        # Inheritance
        elif match := re.match(r"Create class (\w+) inheriting from (\w+)", instruction):
            return {
                'operation': 'inheritance',
                'subclass_name': match.group(1),
                'superclass_name': match.group(2)
            }
        # Interface
        elif match := re.match(r"Create interface (\w+) with methods (.*)", instruction):
            return {
                'operation': 'interface',
                'interface_operation': 'create',
                'interface_name': match.group(1),
                'methods': [method.strip() for method in match.group(2).split(',')]
            }
        elif match := re.match(r"Implement interface (\w+) in class (\w+)", instruction):
            return {
                'operation': 'interface',
                'interface_operation': 'implement',
                'interface_name': match.group(1),
                'class_name': match.group(2)
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

        # Get the appropriate template
        template = self.language_templates.get_template(self.current_language, operation)

        # Fill the template with the parsed instruction data
        if template:
            code_snippet = self.language_templates.fill_template(template, **parsed_instruction)
            print(f"Generated code snippet: {code_snippet}")
            # TODO: Execute or return the code snippet as needed

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
        elif operation == 'stack_operation':
            return self.handle_stack_operation(
                parsed_instruction['stack_operation'],
                parsed_instruction['stack_name'],
                parsed_instruction.get('item')
            )
        elif operation == 'queue_operation':
            return self.handle_queue_operation(
                parsed_instruction['queue_operation'],
                parsed_instruction['queue_name'],
                parsed_instruction.get('item')
            )
        elif operation == 'class_operation':
            return self.handle_class_operation(
                parsed_instruction['class_operation'],
                parsed_instruction['class_name'],
                **{k: v for k, v in parsed_instruction.items() if k not in ['operation', 'class_operation', 'class_name']}
            )
        elif operation == 'object_operation':
            return self.handle_object_operation(
                parsed_instruction['object_operation'],
                parsed_instruction['class_name'],
                parsed_instruction['object_name'],
                **{k: v for k, v in parsed_instruction.items() if k not in ['operation', 'object_operation', 'class_name', 'object_name']}
            )
        elif operation == 'inheritance':
            return self.handle_inheritance(
                parsed_instruction['subclass_name'],
                parsed_instruction['superclass_name']
            )
        elif operation == 'interface':
            return self.handle_interface(
                parsed_instruction['interface_operation'],
                parsed_instruction['interface_name'],
                **{k: v for k, v in parsed_instruction.items() if k not in ['operation', 'interface_operation', 'interface_name']}
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
        import subprocess
        import shlex

        # List of allowed commands for security
        allowed_commands = ['ls', 'dir', 'echo', 'pwd', 'whoami', 'date', 'time', 'uptime']

        try:
            # Split the command into parts
            cmd_parts = shlex.split(command)

            # Check if the base command is in the allowed list
            if cmd_parts[0] not in allowed_commands:
                raise ValueError(f"Command '{cmd_parts[0]}' is not allowed for security reasons.")

            # Execute the command
            result = subprocess.run(cmd_parts, check=True, capture_output=True, text=True)
            print(f"Executed system command: {command}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing system command: {e}")
            return e.output
        except Exception as e:
            print(f"Error in system operation: {str(e)}")
            return str(e)

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

    def handle_stack_operation(self, operation: str, stack_name: str, item: Any = None) -> Any:
        """Handle stack operations (create, push, pop, peek)."""
        try:
            if operation == "create":
                self.variables[stack_name] = []
                print(f"Created a new stack '{stack_name}'")
            elif operation == "push":
                if stack_name not in self.variables:
                    raise ValueError(f"Stack '{stack_name}' does not exist")
                self.variables[stack_name].append(item)
                print(f"Pushed {item} onto stack '{stack_name}'")
            elif operation == "pop":
                if stack_name not in self.variables:
                    raise ValueError(f"Stack '{stack_name}' does not exist")
                if not self.variables[stack_name]:
                    raise IndexError(f"Stack '{stack_name}' is empty")
                item = self.variables[stack_name].pop()
                print(f"Popped {item} from stack '{stack_name}'")
                return item
            elif operation == "peek":
                if stack_name not in self.variables:
                    raise ValueError(f"Stack '{stack_name}' does not exist")
                if not self.variables[stack_name]:
                    raise IndexError(f"Stack '{stack_name}' is empty")
                return self.variables[stack_name][-1]
            else:
                raise ValueError(f"Unknown stack operation: {operation}")
        except Exception as e:
            print(f"Error in stack operation: {str(e)}")

    def handle_queue_operation(self, operation: str, queue_name: str, item: Any = None) -> Any:
        """Handle queue operations (create, enqueue, dequeue, peek)."""
        try:
            if operation == "create":
                self.variables[queue_name] = []
                print(f"Created a new queue '{queue_name}'")
            elif operation == "enqueue":
                if queue_name not in self.variables:
                    raise ValueError(f"Queue '{queue_name}' does not exist")
                self.variables[queue_name].append(item)
                print(f"Enqueued {item} to queue '{queue_name}'")
            elif operation == "dequeue":
                if queue_name not in self.variables:
                    raise ValueError(f"Queue '{queue_name}' does not exist")
                if not self.variables[queue_name]:
                    raise IndexError(f"Queue '{queue_name}' is empty")
                item = self.variables[queue_name].pop(0)
                print(f"Dequeued {item} from queue '{queue_name}'")
                return item
            elif operation == "peek":
                if queue_name not in self.variables:
                    raise ValueError(f"Queue '{queue_name}' does not exist")
                if not self.variables[queue_name]:
                    raise IndexError(f"Queue '{queue_name}' is empty")
                return self.variables[queue_name][0]
            else:
                raise ValueError(f"Unknown queue operation: {operation}")
        except Exception as e:
            print(f"Error in queue operation: {str(e)}")

def main():
    engine = EnglishExecutionEngine()
    # TODO: Add example usage of the EnglishExecutionEngine

if __name__ == "__main__":
    main()
def set_language(self, language: str):
    if language in ['python', 'c', 'java']:
        self.current_language = language
        print(f"Switched to {language} mode")
    else:
        raise ValueError(f"Unsupported language: {language}")

def execute_code_snippet(self, code_snippet: str, language: str) -> str:
    import subprocess
    import tempfile
    import os

    if language not in ['python', 'c', 'java']:
        raise ValueError(f"Unsupported language: {language}")

    if language == 'python':
        try:
            exec_globals = {}
            exec(code_snippet, exec_globals)
            return str(exec_globals.get('__builtins__', {}).get('_', None))
        except Exception as e:
            return f"Error executing Python code: {str(e)}"

    elif language == 'c':
        with tempfile.NamedTemporaryFile(suffix='.c', mode='w+', delete=False) as temp_file:
            temp_file.write(code_snippet)
            temp_file_path = temp_file.name

        try:
            compile_process = subprocess.run(['gcc', temp_file_path, '-o', f'{temp_file_path}.out'],
                                             capture_output=True, text=True, check=True)
            run_process = subprocess.run([f'{temp_file_path}.out'],
                                         capture_output=True, text=True, check=True)
            return run_process.stdout
        except subprocess.CalledProcessError as e:
            return f"Error compiling/running C code: {e.stderr}"
        finally:
            os.remove(temp_file_path)
            if os.path.exists(f'{temp_file_path}.out'):
                os.remove(f'{temp_file_path}.out')

    elif language == 'java':
        class_name = 'TempClass'
        full_code = f"public class {class_name} {{ public static void main(String[] args) {{ {code_snippet} }} }}"

        with tempfile.NamedTemporaryFile(suffix='.java', mode='w+', delete=False) as temp_file:
            temp_file.write(full_code)
            temp_file_path = temp_file.name

        try:
            compile_process = subprocess.run(['javac', temp_file_path],
                                             capture_output=True, text=True, check=True)
            run_process = subprocess.run(['java', '-cp', os.path.dirname(temp_file_path), class_name],
                                         capture_output=True, text=True, check=True)
            return run_process.stdout
        except subprocess.CalledProcessError as e:
            return f"Error compiling/running Java code: {e.stderr}"
        finally:
            os.remove(temp_file_path)
            class_file = f"{os.path.splitext(temp_file_path)[0]}.class"
            if os.path.exists(class_file):
                os.remove(class_file)

def handle_class_operation(self, operation: str, class_name: str, **kwargs):
    if operation == "create":
        self.variables[class_name] = type(class_name, (), {})
        print(f"Created class '{class_name}'")
    elif operation == "add_attribute":
        if class_name not in self.variables:
            raise ValueError(f"Class '{class_name}' does not exist")
        setattr(self.variables[class_name], kwargs['attribute_name'], None)
        print(f"Added attribute '{kwargs['attribute_name']}' to class '{class_name}'")
    elif operation == "add_method":
        if class_name not in self.variables:
            raise ValueError(f"Class '{class_name}' does not exist")
        method_code = f"def {kwargs['method_name']}(self, {', '.join(kwargs['parameters'])}):\n    {kwargs['action']}"
        exec(method_code)
        setattr(self.variables[class_name], kwargs['method_name'], locals()[kwargs['method_name']])
        print(f"Added method '{kwargs['method_name']}' to class '{class_name}'")
    else:
        raise ValueError(f"Unknown class operation: {operation}")

def handle_object_operation(self, operation: str, class_name: str, object_name: str, **kwargs):
    if operation == "create":
        if class_name not in self.variables:
            raise ValueError(f"Class '{class_name}' does not exist")
        self.variables[object_name] = self.variables[class_name]()
        print(f"Created object '{object_name}' of class '{class_name}'")
    elif operation == "set_attribute":
        if object_name not in self.variables:
            raise ValueError(f"Object '{object_name}' does not exist")
        setattr(self.variables[object_name], kwargs['attribute_name'], kwargs['value'])
        print(f"Set attribute '{kwargs['attribute_name']}' of '{object_name}' to {kwargs['value']}")
    elif operation == "get_attribute":
        if object_name not in self.variables:
            raise ValueError(f"Object '{object_name}' does not exist")
        return getattr(self.variables[object_name], kwargs['attribute_name'])
    elif operation == "call_method":
        if object_name not in self.variables:
            raise ValueError(f"Object '{object_name}' does not exist")
        method = getattr(self.variables[object_name], kwargs['method_name'])
        return method(*kwargs['arguments'])
    else:
        raise ValueError(f"Unknown object operation: {operation}")

def handle_inheritance(self, subclass_name: str, superclass_name: str):
    if superclass_name not in self.variables:
        raise ValueError(f"Superclass '{superclass_name}' does not exist")
    self.variables[subclass_name] = type(subclass_name, (self.variables[superclass_name],), {})
    print(f"Created subclass '{subclass_name}' inheriting from '{superclass_name}'")

def handle_interface(self, operation: str, interface_name: str, **kwargs):
    if operation == "create":
        self.variables[interface_name] = type(interface_name, (), {method: None for method in kwargs['methods']})
        print(f"Created interface '{interface_name}' with methods {', '.join(kwargs['methods'])}")
    elif operation == "implement":
        if interface_name not in self.variables:
            raise ValueError(f"Interface '{interface_name}' does not exist")
        if kwargs['class_name'] not in self.variables:
            raise ValueError(f"Class '{kwargs['class_name']}' does not exist")
        for method in self.variables[interface_name].__dict__:
            if method not in self.variables[kwargs['class_name']].__dict__:
                raise ValueError(f"Class '{kwargs['class_name']}' does not implement method '{method}' from interface '{interface_name}'")
        print(f"Class '{kwargs['class_name']}' now implements interface '{interface_name}'")
    else:
        raise ValueError(f"Unknown interface operation: {operation}")

def handle_file_management(self, operation: str, path: str, new_path: str = None, content: str = None):
    """Handle file management operations (create, delete, move, copy, read, write)."""
    import os
    import shutil

    try:
        if operation == "create":
            with open(path, 'w') as f:
                if content:
                    f.write(content)
            print(f"Created file: {path}")
        elif operation == "delete":
            os.remove(path)
            print(f"Deleted file: {path}")
        elif operation == "move":
            shutil.move(path, new_path)
            print(f"Moved file from {path} to {new_path}")
        elif operation == "copy":
            shutil.copy2(path, new_path)
            print(f"Copied file from {path} to {new_path}")
        elif operation == "read":
            with open(path, 'r') as f:
                return f.read()
        elif operation == "write":
            with open(path, 'w') as f:
                f.write(content)
            print(f"Wrote content to file: {path}")
        else:
            raise ValueError(f"Unknown file management operation: {operation}")
    except Exception as e:
        print(f"Error in file management operation: {str(e)}")
        return str(e)