# Test script for the EnglishInterpreter system
from english_interpreter import EnglishInterpreter

def run_tests():
    interpreter = EnglishInterpreter()
    test_instructions = [
        "Create a new text file named 'testfile.txt'.",
        "List all files in the current directory.",
        "Delete the file named 'testfile.txt'."
    ]

    for instruction in test_instructions:
        print(f"Instruction: {instruction}")
        result = interpreter.main_driver(instruction)
        print(f"Result: {result}\n")

if __name__ == "__main__":
    run_tests()