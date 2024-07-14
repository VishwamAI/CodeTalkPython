import os
import shutil
import logging
import subprocess
import sys
import psutil
import requests
import re
from typing import Dict, Any

class ExecutionEngine:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def execute(self, intent_data):
        intent = intent_data.get('primary_intent')
        entities = intent_data.get('relevant_entities', {})
        entities['instruction'] = intent_data.get('original_instruction', '')

        intent_map = {
            'create_file': self._create_file,
            'delete_file': self._delete_file,
            'list_files': self._list_files,
            'update_file': self._update_file,
            'execute_code': self._execute_code,
            'execute_system_command': self._execute_system_command,
            'install_package': self._install_package,
            'search_file': self._search_file,
            'move_file': self._move_file,
            'copy_file': self._copy_file,
            'manage_process': self._manage_process,
            'network_operation': self._network_operation,
            'manage_variable': self._manage_variable,
            'control_flow': self._process_english_instruction,
            'function_operation': self._process_english_instruction,
            'io_operation': self._process_english_instruction,
            'data_structure_operation': self._process_english_instruction,
            'algorithm_execution': self._process_english_instruction
        }

        if intent in intent_map:
            return intent_map[intent](entities)
        else:
            return f"I'm sorry, I don't know how to perform the action: {intent}. Please check your instruction and try again."

    def _create_file(self, entities):
        filename = entities.get('filename')
        if not filename:
            return "I'm sorry, I need a filename to create a file."

        try:
            with open(filename, 'w') as f:
                pass
            self.logger.info(f"File '{filename}' created successfully.")
            return f"I've created a new file named '{filename}' for you."
        except IOError as e:
            self.logger.error(f"Error creating file '{filename}': {str(e)}")
            return f"I'm sorry, I couldn't create the file '{filename}'. There was an error: {str(e)}"

    def _delete_file(self, entities):
        filename = entities.get('filename')
        if not filename:
            return "I'm sorry, I need a filename to delete a file."

        try:
            os.remove(filename)
            self.logger.info(f"File '{filename}' deleted successfully.")
            return f"I've deleted the file named '{filename}' for you."
        except FileNotFoundError:
            self.logger.warning(f"File '{filename}' not found for deletion.")
            return f"I'm sorry, I couldn't find a file named '{filename}' to delete."
        except PermissionError:
            self.logger.error(f"Permission denied when trying to delete '{filename}'.")
            return f"I'm sorry, I don't have permission to delete the file '{filename}'."
        except Exception as e:
            self.logger.error(f"Error deleting file '{filename}': {str(e)}")
            return f"I'm sorry, I couldn't delete the file '{filename}'. There was an error: {str(e)}"

    def _list_files(self, entities):
        directory = entities.get('directory', '.')

        try:
            files = os.listdir(directory)
            self.logger.info(f"Listed files in directory '{directory}'.")
            if files:
                file_list = "\n".join(files)
                return f"Here are the files in the directory '{directory}':\n{file_list}"
            else:
                return f"The directory '{directory}' is empty."
        except FileNotFoundError:
            self.logger.warning(f"Directory '{directory}' not found.")
            return f"I'm sorry, I couldn't find the directory '{directory}'."
        except PermissionError:
            self.logger.error(f"Permission denied when trying to list files in '{directory}'.")
            return f"I'm sorry, I don't have permission to list files in the directory '{directory}'."
        except Exception as e:
            self.logger.error(f"Error listing files in directory '{directory}': {str(e)}")
            return f"I'm sorry, I couldn't list the files in the directory '{directory}'. There was an error: {str(e)}"

    def _update_file(self, entities):
        filename = entities.get('filename')
        content = entities.get('content')
        if not filename or content is None:
            return "I'm sorry, I need both a filename and content to update a file."

        try:
            with open(filename, 'w') as f:
                f.write(content)
            self.logger.info(f"File '{filename}' updated successfully.")
            return f"I've updated the file '{filename}' with the new content."
        except FileNotFoundError:
            self.logger.warning(f"File '{filename}' not found for updating.")
            return f"I'm sorry, I couldn't find a file named '{filename}' to update."
        except PermissionError:
            self.logger.error(f"Permission denied when trying to update '{filename}'.")
            return f"I'm sorry, I don't have permission to update the file '{filename}'."
        except Exception as e:
            self.logger.error(f"Error updating file '{filename}': {str(e)}")
            return f"I'm sorry, I couldn't update the file '{filename}'. There was an error: {str(e)}"

    def _execute_code(self, entities):
        code = entities.get('code')
        if not code:
            return "I'm sorry, I need code to execute."

        return self._execute_python(code)

    def _execute_python(self, code):
        try:
            result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"Python code executed successfully. Output:\n{result.stdout}"
            else:
                return f"Python code execution failed. Error:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Python code execution timed out."
        except Exception as e:
            self.logger.error(f"Error executing Python code: {str(e)}")
            return f"I'm sorry, I couldn't execute the Python code. There was an error: {str(e)}"

    def _execute_system_command(self, entities):
        command = entities.get('command')
        if not command:
            return "I'm sorry, I need a command to execute."

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"Command executed successfully. Output:\n{result.stdout}"
            else:
                return f"Command execution failed. Error:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Command execution timed out."
        except Exception as e:
            self.logger.error(f"Error executing system command: {str(e)}")
            return f"I'm sorry, I couldn't execute the system command. There was an error: {str(e)}"

    def _install_package(self, entities):
        package_name = entities.get('package_name')
        if not package_name:
            return "I'm sorry, I need a package name to install."

        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], capture_output=True, text=True, check=True)
            self.logger.info(f"Successfully installed {package_name} for Python.")
            return f"Successfully installed {package_name} for Python."
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install {package_name} for Python. Error: {e.stderr}")
            return f"Failed to install {package_name} for Python. Error:\n{e.stderr}"
        except Exception as e:
            self.logger.error(f"Error installing Python package: {str(e)}")
            return f"I'm sorry, I couldn't install the Python package. There was an error: {str(e)}"

    def _search_file(self, entities):
        filename = entities.get('filename')
        search_term = entities.get('search_term')
        if not filename or not search_term:
            return "I'm sorry, I need both a filename and a search term to search within a file."

        try:
            with open(filename, 'r') as file:
                content = file.read()
                if search_term in content:
                    return f"The search term '{search_term}' was found in the file '{filename}'."
                else:
                    return f"The search term '{search_term}' was not found in the file '{filename}'."
        except FileNotFoundError:
            return f"I'm sorry, I couldn't find the file '{filename}'."
        except Exception as e:
            self.logger.error(f"Error searching file '{filename}': {str(e)}")
            return f"I'm sorry, I couldn't search the file '{filename}'. There was an error: {str(e)}"

    def _move_file(self, entities):
        source = entities.get('source')
        destination = entities.get('destination')
        if not source or not destination:
            return "I'm sorry, I need both a source and destination to move a file."

        try:
            shutil.move(source, destination)
            return f"Successfully moved file from '{source}' to '{destination}'."
        except FileNotFoundError:
            return f"I'm sorry, I couldn't find the file '{source}'."
        except Exception as e:
            self.logger.error(f"Error moving file from '{source}' to '{destination}': {str(e)}")
            return f"I'm sorry, I couldn't move the file. There was an error: {str(e)}"

    def _copy_file(self, entities):
        source = entities.get('source')
        destination = entities.get('destination')
        if not source or not destination:
            return "I'm sorry, I need both a source and destination to copy a file."

        try:
            shutil.copy2(source, destination)
            return f"Successfully copied file from '{source}' to '{destination}'."
        except FileNotFoundError:
            return f"I'm sorry, I couldn't find the file '{source}'."
        except Exception as e:
            self.logger.error(f"Error copying file from '{source}' to '{destination}': {str(e)}")
            return f"I'm sorry, I couldn't copy the file. There was an error: {str(e)}"

    def _manage_process(self, entities):
        action = entities.get('action')
        process_name = entities.get('process_name')
        if not action or not process_name:
            return "I'm sorry, I need both an action and a process name to manage a process."

        try:
            if action == 'start':
                subprocess.Popen(process_name)
                return f"Started process '{process_name}'."
            elif action == 'stop':
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == process_name:
                        proc.terminate()
                return f"Stopped process '{process_name}'."
            elif action == 'list':
                processes = [p.info['name'] for p in psutil.process_iter(['name'])]
                return f"Running processes:\n{', '.join(processes)}"
            else:
                return f"Unknown action '{action}'. Supported actions are 'start', 'stop', and 'list'."
        except Exception as e:
            self.logger.error(f"Error managing process '{process_name}': {str(e)}")
            return f"I'm sorry, I couldn't manage the process. There was an error: {str(e)}"

    def _network_operation(self, entities):
        operation = entities.get('operation')
        url = entities.get('url')
        if not operation or not url:
            return "I'm sorry, I need both an operation and a URL to perform a network operation."

        try:
            if operation == 'get':
                response = requests.get(url)
                return f"GET request to {url} returned status code {response.status_code}"
            elif operation == 'post':
                data = entities.get('data', {})
                response = requests.post(url, json=data)
                return f"POST request to {url} returned status code {response.status_code}"
            else:
                return f"Unknown operation '{operation}'. Supported operations are 'get' and 'post'."
        except Exception as e:
            self.logger.error(f"Error performing network operation: {str(e)}")
            return f"I'm sorry, I couldn't perform the network operation. There was an error: {str(e)}"

    def _manage_variable(self, entities):
        action = entities.get('action')
        variable_name = entities.get('variable_name')
        if not action or not variable_name:
            return "I'm sorry, I need both an action and a variable name to manage a variable."

        try:
            if action == 'set':
                value = entities.get('value')
                if value is None:
                    return "I'm sorry, I need a value to set the variable."
                setattr(self, variable_name, value)
                return f"Set variable '{variable_name}' to '{value}'."
            elif action == 'get':
                if hasattr(self, variable_name):
                    value = getattr(self, variable_name)
                    return f"The value of variable '{variable_name}' is '{value}'."
                else:
                    return f"Variable '{variable_name}' is not set."
            elif action == 'delete':
                if hasattr(self, variable_name):
                    delattr(self, variable_name)
                    return f"Deleted variable '{variable_name}'."
                else:
                    return f"Variable '{variable_name}' does not exist."
            else:
                return f"Unknown action '{action}'. Supported actions are 'set', 'get', and 'delete'."
        except Exception as e:
            self.logger.error(f"Error managing variable '{variable_name}': {str(e)}")
            return f"I'm sorry, I couldn't manage the variable. There was an error: {str(e)}"

    def _process_english_instruction(self, entities):
        from nltk import word_tokenize, pos_tag
        from nltk.chunk import ne_chunk

        instruction = entities.get('instruction', '')
        intent = entities.get('primary_intent', '')

        # Use NLTK for basic NLP processing
        tokens = word_tokenize(instruction)
        pos_tags = pos_tag(tokens)
        named_entities = ne_chunk(pos_tags)

        # Extract relevant information based on the intent
        if intent == 'control_flow':
            return self._process_control_flow(instruction, named_entities)
        elif intent == 'function_operation':
            return self._process_function_operation(instruction, named_entities)
        elif intent == 'io_operation':
            return self._process_io_operation(instruction, named_entities)
        elif intent == 'data_structure_operation':
            return self._process_data_structure_operation(instruction, named_entities)
        elif intent == 'algorithm_execution':
            return self._process_algorithm_execution(instruction, named_entities)
        else:
            return f"I'm sorry, I don't know how to process this type of instruction: {intent}"

    def _process_control_flow(self, instruction):
        # Parse the instruction to identify control flow elements
        if "if" in instruction.lower():
            condition, action = self._parse_if_statement(instruction)
            if self._evaluate_condition(condition):
                return self._execute_action(action)
        elif "while" in instruction.lower():
            condition, action = self._parse_while_loop(instruction)
            result = []
            while self._evaluate_condition(condition):
                result.append(self._execute_action(action))
            return "\n".join(result)
        elif "for" in instruction.lower():
            iterable, action = self._parse_for_loop(instruction)
            result = []
            for item in iterable:
                result.append(self._execute_action(action, item))
            return "\n".join(result)
        else:
            return f"Unable to process control flow instruction: {instruction}"

    def _parse_if_statement(self, instruction):
        # Simple parsing, can be improved with NLP
        parts = instruction.split("then")
        condition = parts[0].replace("if", "").strip()
        action = parts[1].strip()
        return condition, action

    def _parse_while_loop(self, instruction):
        # Simple parsing, can be improved with NLP
        parts = instruction.split("do")
        condition = parts[0].replace("while", "").strip()
        action = parts[1].strip()
        return condition, action

    def _parse_for_loop(self, instruction):
        # Simple parsing, can be improved with NLP
        parts = instruction.split("do")
        iterable = parts[0].split("in")[1].strip()
        action = parts[1].strip()
        return eval(iterable), action

    def _evaluate_condition(self, condition):
        # This is a simplified evaluation. In a real system, you'd need more robust parsing and safe evaluation
        try:
            return eval(condition)
        except:
            return False

    def _execute_action(self, action, item=None):
        # This is a simplified execution. In a real system, you'd need more robust parsing and safe execution
        if item:
            action = action.replace("item", str(item))
        try:
            return str(eval(action))
        except:
            return f"Unable to execute action: {action}"

    def _process_function_operation(self, instruction):
        # Parse the instruction to identify function-related operations
        if "define" in instruction.lower():
            # Handle function definition
            function_name = self._extract_function_name(instruction)
            parameters = self._extract_parameters(instruction)
            body = self._extract_function_body(instruction)

            # Create and store the function
            exec(f"def {function_name}({', '.join(parameters)}):\n{body}")
            setattr(self, function_name, locals()[function_name])

            return f"Function '{function_name}' has been defined."

        elif "call" in instruction.lower():
            # Handle function call
            function_name = self._extract_function_name(instruction)
            arguments = self._extract_arguments(instruction)

            if hasattr(self, function_name):
                func = getattr(self, function_name)
                result = func(*arguments)
                return f"Function '{function_name}' called. Result: {result}"
            else:
                return f"Function '{function_name}' is not defined."

        else:
            return f"Unable to process function operation: {instruction}"

    def _extract_function_name(self, instruction):
        # Extract function name from instruction (implement NLP logic here)
        # For simplicity, let's assume the function name is the first word after "define" or "call"
        words = instruction.split()
        idx = words.index("define") if "define" in words else words.index("call")
        return words[idx + 1]

    def _extract_parameters(self, instruction):
        # Extract parameters from instruction (implement NLP logic here)
        # For simplicity, let's assume parameters are comma-separated words in parentheses
        start = instruction.find("(") + 1
        end = instruction.find(")")
        return [param.strip() for param in instruction[start:end].split(",") if param.strip()]

    def _extract_function_body(self, instruction):
        # Extract function body from instruction (implement NLP logic here)
        # For simplicity, let's assume the body is everything after ":" or "do"
        body_start = instruction.find(":") + 1 if ":" in instruction else instruction.find("do") + 2
        return instruction[body_start:].strip()

    def _extract_arguments(self, instruction):
        # Extract arguments for function call (implement NLP logic here)
        # For simplicity, let's assume arguments are comma-separated words in parentheses
        start = instruction.find("(") + 1
        end = instruction.find(")")
        return [arg.strip() for arg in instruction[start:end].split(",") if arg.strip()]

    def _process_io_operation(self, instruction):
        # Implement input/output operations
        if "read" in instruction.lower():
            filename = re.search(r'read\s+(?:from\s+)?(\w+\.?\w*)', instruction, re.IGNORECASE)
            if filename:
                try:
                    with open(filename.group(1), 'r') as file:
                        content = file.read()
                    return f"Content of {filename.group(1)}:\n{content}"
                except FileNotFoundError:
                    return f"File {filename.group(1)} not found."
                except Exception as e:
                    return f"Error reading file: {str(e)}"
            else:
                return "Please specify a file to read from."
        elif "write" in instruction.lower():
            match = re.search(r'write\s+"(.+)"\s+to\s+(\w+\.?\w*)', instruction, re.IGNORECASE)
            if match:
                content, filename = match.groups()
                try:
                    with open(filename, 'w') as file:
                        file.write(content)
                    return f"Successfully wrote to {filename}."
                except Exception as e:
                    return f"Error writing to file: {str(e)}"
            else:
                return "Please specify content and a file to write to."
        else:
            return f"Unsupported I/O operation in instruction: {instruction}"

    def _process_data_structure_operation(self, instruction):
        # Parse the instruction to identify the data structure and operation
        words = instruction.lower().split()
        data_structure = None
        operation = None

        # Identify data structure
        if 'list' in words:
            data_structure = 'list'
        elif 'dictionary' in words or 'dict' in words:
            data_structure = 'dict'
        elif 'set' in words:
            data_structure = 'set'
        elif 'tuple' in words:
            data_structure = 'tuple'

        # Identify operation
        if 'create' in words or 'make' in words:
            operation = 'create'
        elif 'add' in words or 'insert' in words:
            operation = 'add'
        elif 'remove' in words or 'delete' in words:
            operation = 'remove'
        elif 'update' in words or 'change' in words:
            operation = 'update'
        elif 'get' in words or 'retrieve' in words:
            operation = 'get'

        if not data_structure or not operation:
            return f"I'm sorry, I couldn't understand the data structure or operation in: {instruction}"

        # Perform the operation (simplified example)
        if data_structure == 'list':
            if operation == 'create':
                self.current_list = []
                return "Created a new empty list."
            elif operation == 'add':
                item = next((word for word in words if word.isalnum() and word not in ['add', 'to', 'list']), None)
                if item:
                    self.current_list.append(item)
                    return f"Added '{item}' to the list."
                else:
                    return "I'm sorry, I couldn't identify what to add to the list."
            # Implement other operations for list

        # Implement operations for other data structures

        return f"Performed {operation} operation on {data_structure}."

    def _process_algorithm_execution(self, instruction):
        # Parse the instruction to identify the algorithm and its parameters
        algorithm, params = self._parse_algorithm_instruction(instruction)

        # Execute the identified algorithm
        if algorithm == "sort":
            return self._execute_sort_algorithm(params)
        elif algorithm == "search":
            return self._execute_search_algorithm(params)
        elif algorithm == "graph":
            return self._execute_graph_algorithm(params)
        else:
            return f"I'm sorry, I don't know how to execute the algorithm: {algorithm}"

    def _parse_algorithm_instruction(self, instruction):
        # Use NLP techniques to parse the instruction and extract algorithm and parameters
        # This is a simplified example; in practice, use more sophisticated NLP tools
        words = instruction.lower().split()
        algorithm = next((word for word in words if word in ["sort", "search", "graph"]), None)
        params = [word for word in words if word not in ["execute", "run", "perform", algorithm]]
        return algorithm, params

    def _execute_sort_algorithm(self, params):
        # Implement sorting logic based on params
        return f"Executed sorting algorithm with parameters: {params}"

    def _execute_search_algorithm(self, params):
        # Implement search logic based on params
        return f"Executed search algorithm with parameters: {params}"

    def _execute_graph_algorithm(self, params):
        # Implement graph algorithm logic based on params
        return f"Executed graph algorithm with parameters: {params}"