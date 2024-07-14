import logging

class OutputGenerator:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_output(self, execution_result):
        try:
            if isinstance(execution_result, dict):
                if 'error' in execution_result:
                    return self._format_error_message(execution_result['error'])
                elif 'success' in execution_result:
                    return f"Operation successful: {execution_result['success']}"
                elif 'data' in execution_result:
                    if isinstance(execution_result['data'], list):
                        return self._format_file_list(execution_result['data'])
                    else:
                        return f"Result: {execution_result['data']}"
            else:
                return f"Unexpected result: {execution_result}"
        except Exception as e:
            self.logger.error(f"Error generating output: {str(e)}")
            return "An error occurred while generating the output."

    def _format_file_list(self, file_list):
        if not file_list:
            return "No files found."
        formatted_list = "\n".join(f"- {file}" for file in file_list)
        return f"Files found:\n{formatted_list}"

    def _format_error_message(self, error):
        return f"Error: {error}"