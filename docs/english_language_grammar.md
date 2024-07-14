# English-Based Programming Language Grammar

## 1. Introduction
This document outlines the basic grammar for an English-based programming language. The purpose of this language is to allow users to write code using natural English phrases, making programming more accessible to non-technical users while maintaining the precision required for execution.

## 2. Variables and Data Types

### Declaring Variables
English: Create a variable called 'age' and set it to 25.
Python equivalent: age = 25

English: Make a list named 'fruits' containing apple, banana, and orange.
Python equivalent: fruits = ['apple', 'banana', 'orange']

### Supported Data Types
- Numbers (integers and floats)
- Strings
- Lists
- Dictionaries
- Booleans

## 3. Basic Operations

### Arithmetic Operations
English: Add 5 to the variable 'count'.
Python equivalent: count += 5

English: Multiply 'price' by 1.1 and store the result in 'new_price'.
Python equivalent: new_price = price * 1.1

### String Operations
English: Join the words "Hello" and "World" with a space between them.
Python equivalent: result = "Hello" + " " + "World"

English: Get the length of the string 'message'.
Python equivalent: length = len(message)

### List Operations
English: Add "grape" to the end of the 'fruits' list.
Python equivalent: fruits.append("grape")

English: Remove the first item from the 'queue' list.
Python equivalent: queue.pop(0)

## 4. Control Structures

### If-Else Statements
English:
If 'age' is greater than or equal to 18, then
    Set 'can_vote' to true.
Otherwise,
    Set 'can_vote' to false.

Python equivalent:
```python
if age >= 18:
    can_vote = True
else:
    can_vote = False
```

### Loops
English:
For each 'item' in the 'shopping_list',
    Print the 'item'.

Python equivalent:
```python
for item in shopping_list:
    print(item)
```

English:
While 'attempts' is less than 3,
    Ask for user input.
    Increase 'attempts' by 1.

Python equivalent:
```python
while attempts < 3:
    user_input = input("Enter your guess: ")
    attempts += 1
```

## 5. Functions

### Defining Functions
English:
Create a function called 'greet' that takes a 'name' parameter:
    Print "Hello, " followed by the 'name'.

Python equivalent:
```python
def greet(name):
    print(f"Hello, {name}")
```

### Calling Functions
English: Call the 'greet' function with the name "Alice".
Python equivalent: greet("Alice")

## 6. Input/Output

### User Input
English: Ask the user for their name and store it in 'user_name'.
Python equivalent: user_name = input("What is your name? ")

### Output
English: Display the value of 'result' to the user.
Python equivalent: print(result)

## 7. Data Structures

### Lists
English: Create a list called 'numbers' with the values 1, 2, and 3.
Python equivalent: numbers = [1, 2, 3]

### Dictionaries
English: Make a dictionary named 'person' with keys "name" set to "John" and "age" set to 30.
Python equivalent: person = {"name": "John", "age": 30}

## 8. Error Handling

English:
Try to:
    Convert 'user_input' to an integer.
If an error occurs:
    Print "Invalid input. Please enter a number."

Python equivalent:
```python
try:
    number = int(user_input)
except ValueError:
    print("Invalid input. Please enter a number.")
```

This grammar provides a foundation for expressing common programming concepts in natural English. As the language evolves, more complex structures and operations can be added to enhance its capabilities.