import unittest
from src.english_execution_engine import EnglishExecutionEngine

class TestEnglishExecutionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EnglishExecutionEngine()

    def test_variable_declaration(self):
        instruction = "Create a variable named 'x' with value 5"
        parsed_instruction = self.engine.parse_instruction(instruction)
        self.engine.execute_instruction(parsed_instruction)
        self.assertEqual(self.engine.variables['x'], 5)

    def test_arithmetic_operations(self):
        instructions = [
            "Create a variable named 'a' with value 10",
            "Create a variable named 'b' with value 3",
            "Set 'c' to 'a' plus 'b'"
        ]
        for instruction in instructions:
            parsed_instruction = self.engine.parse_instruction(instruction)
            self.engine.execute_instruction(parsed_instruction)
        self.assertEqual(self.engine.variables['c'], 13)

    def test_conditional(self):
        instructions = [
            "Create a variable named 'x' with value 5",
            "If 'x' is greater than 3, set 'y' to 1, otherwise set 'y' to 0"
        ]
        for instruction in instructions:
            parsed_instruction = self.engine.parse_instruction(instruction)
            self.engine.execute_instruction(parsed_instruction)
        self.assertEqual(self.engine.variables['y'], 1)

    def test_loop(self):
        instructions = [
            "Create a variable named 'sum' with value 0",
            "For i from 1 to 5, add 'i' to 'sum'"
        ]
        for instruction in instructions:
            parsed_instruction = self.engine.parse_instruction(instruction)
            self.engine.execute_instruction(parsed_instruction)
        self.assertEqual(self.engine.variables['sum'], 15)

    def test_function_definition_and_call(self):
        instructions = [
            "Define a function named 'add' that takes 'a' and 'b' as parameters and returns 'a' plus 'b'",
            "Set 'result' to the result of calling 'add' with 3 and 4"
        ]
        for instruction in instructions:
            parsed_instruction = self.engine.parse_instruction(instruction)
            self.engine.execute_instruction(parsed_instruction)
        self.assertEqual(self.engine.variables['result'], 7)

if __name__ == '__main__':
    unittest.main()