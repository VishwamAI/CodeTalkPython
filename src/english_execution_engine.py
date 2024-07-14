import re
import ast
from typing import Any, Dict, List, Union

class EnglishExecutionEngine:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, callable] = {}

    def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """Parse English instructions into executable operations."""
        # Variable declaration
        if match := re.match(r"Create a variable named '(\w+)' with value (.+)", instruction):
            return {
                'operation': 'variable_declaration',
                'name': match.group(1),
                'value': self._parse_value(match.group(2))
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

        # Conditional
        elif match := re.match(r"If '(\w+)' is (greater than|less than|equal to) (\d+), set '(\w+)' to (\d+), otherwise set '(\w+)' to (\d+)", instruction):
            return {
                'operation': 'conditional',
                'condition_var': match.group(1),
                'comparison': match.group(2),
                'comparison_value': int(match.group(3)),
                'true_var': match.group(4),
                'true_value': int(match.group(5)),
                'false_var': match.group(6),
                'false_value': int(match.group(7))
            }

        # Loop
        elif match := re.match(r"For (\w+) from (\d+) to (\d+), add '(\w+)' to '(\w+)'", instruction):
            return {
                'operation': 'loop',
                'loop_var': match.group(1),
                'start': int(match.group(2)),
                'end': int(match.group(3)),
                'add_var': match.group(4),
                'result_var': match.group(5)
            }

        # Function definition
        elif match := re.match(r"Define a function named '(\w+)' that takes '(\w+)' and '(\w+)' as parameters and returns '(\w+)' (plus|minus|times|divided by) '(\w+)'", instruction):
            return {
                'operation': 'function_definition',
                'name': match.group(1),
                'param1': match.group(2),
                'param2': match.group(3),
                'return_var1': match.group(4),
                'operation': match.group(5),
                'return_var2': match.group(6)
            }

        # Function call
        elif match := re.match(r"Set '(\w+)' to the result of calling '(\w+)' with (\d+) and (\d+)", instruction):
            return {
                'operation': 'function_call',
                'result_var': match.group(1),
                'function_name': match.group(2),
                'arg1': int(match.group(3)),
                'arg2': int(match.group(4))
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

        if operation == 'variable_declaration':
            return self.handle_variable_declaration(parsed_instruction['name'], parsed_instruction['value'])
        elif operation == 'arithmetic':
            return self.handle_arithmetic_operation(
                parsed_instruction['result_var'],
                parsed_instruction['operand1'],
                parsed_instruction['operation_type'],
                parsed_instruction['operand2']
            )
        elif operation == 'conditional':
            return self.handle_conditional(
                parsed_instruction['condition_var'],
                parsed_instruction['comparison'],
                parsed_instruction['comparison_value'],
                parsed_instruction['true_var'],
                parsed_instruction['true_value'],
                parsed_instruction['false_var'],
                parsed_instruction['false_value']
            )
        elif operation == 'loop':
            return self.handle_loop(
                parsed_instruction['loop_var'],
                parsed_instruction['start'],
                parsed_instruction['end'],
                parsed_instruction['add_var'],
                parsed_instruction['result_var']
            )
        elif operation == 'function_definition':
            return self.handle_function_definition(
                parsed_instruction['name'],
                parsed_instruction['param1'],
                parsed_instruction['param2'],
                parsed_instruction['return_var1'],
                parsed_instruction['operation'],
                parsed_instruction['return_var2']
            )
        elif operation == 'function_call':
            return self.handle_function_call(
                parsed_instruction['result_var'],
                parsed_instruction['function_name'],
                parsed_instruction['arg1'],
                parsed_instruction['arg2']
            )
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def handle_variable_declaration(self, name: str, value: Any) -> None:
        """Handle variable creation and assignment."""
        try:
            # Evaluate the value if it's a string representation of a Python expression
            if isinstance(value, str):
                value = eval(value, {}, self.variables)
            self.variables[name] = value
            print(f"Variable '{name}' has been assigned the value: {value}")
        except Exception as e:
            print(f"Error in variable declaration: {str(e)}")

    def handle_conditional(self, condition_var: str, comparison: str, comparison_value: int,
                           true_var: str, true_value: int, false_var: str, false_value: int) -> None:
        """Handle conditional statements."""
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

            if result:
                self.variables[true_var] = true_value
                print(f"Condition is True. Set '{true_var}' to {true_value}")
            else:
                self.variables[false_var] = false_value
                print(f"Condition is False. Set '{false_var}' to {false_value}")
        except Exception as e:
            print(f"Error in conditional execution: {str(e)}")

    def handle_loop(self, loop_var: str, start: int, end: int, add_var: str, result_var: str) -> None:
        """Handle loop structures."""
        try:
            if result_var not in self.variables:
                self.variables[result_var] = 0

            for i in range(start, end + 1):
                self.variables[loop_var] = i
                add_value = self.variables.get(add_var)
                if add_value is None:
                    raise ValueError(f"Variable '{add_var}' is not defined.")
                self.variables[result_var] += add_value
                print(f"Loop iteration {i}: Added {add_value} to {result_var}. New value: {self.variables[result_var]}")

            print(f"Loop completed. Final value of {result_var}: {self.variables[result_var]}")
        except Exception as e:
            print(f"Error in loop execution: {str(e)}")

    def handle_function_definition(self, name: str, param1: str, param2: str,
                                   return_var1: str, operation: str, return_var2: str) -> None:
        """Define functions based on English instructions."""
        try:
            def function(a, b):
                self.variables[param1] = a
                self.variables[param2] = b
                if operation == 'plus':
                    result = self.variables[return_var1] + self.variables[return_var2]
                elif operation == 'minus':
                    result = self.variables[return_var1] - self.variables[return_var2]
                elif operation == 'times':
                    result = self.variables[return_var1] * self.variables[return_var2]
                elif operation == 'divided by':
                    if self.variables[return_var2] == 0:
                        raise ValueError("Division by zero")
                    result = self.variables[return_var1] / self.variables[return_var2]
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                return result

            self.functions[name] = function
            print(f"Function '{name}' has been defined.")
        except Exception as e:
            print(f"Error in function definition: {str(e)}")

    def handle_function_call(self, result_var: str, function_name: str, arg1: int, arg2: int) -> Any:
        """Execute function calls."""
        try:
            if function_name not in self.functions:
                raise ValueError(f"Function '{function_name}' is not defined.")

            result = self.functions[function_name](arg1, arg2)
            self.variables[result_var] = result
            print(f"Function '{function_name}' called with arguments: {arg1}, {arg2}")
            print(f"Result stored in '{result_var}': {result}")
            return result
        except Exception as e:
            print(f"Error in function call: {str(e)}")
            return None

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

    def handle_list_operation(self, operation: str, list_name: str, item: Any = None) -> None:
        """Perform list operations (create, append, remove)."""
        # TODO: Implement list operation logic
        pass

    def handle_dictionary_operation(self, operation: str, dict_name: str, key: Any = None, value: Any = None) -> None:
        """Perform dictionary operations."""
        # TODO: Implement dictionary operation logic
        pass

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