# language_templates.py

class LanguageTemplates:
    @staticmethod
    def get_template(language: str, construct: str) -> str:
        templates = {
            'python': {
                'variable_declaration': '{name} = {value}',
                'function_definition': 'def {name}({params}):\n    {body}',
                'if_statement': 'if {condition}:\n    {body}',
                'for_loop': 'for {var} in {iterable}:\n    {body}',
                'while_loop': 'while {condition}:\n    {body}',
                'class_definition': 'class {name}:\n    {body}',
            },
            'c': {
                'variable_declaration': '{type} {name} = {value};',
                'function_definition': '{return_type} {name}({params}) {{\n    {body}\n}}',
                'if_statement': 'if ({condition}) {{\n    {body}\n}}',
                'for_loop': 'for ({init}; {condition}; {increment}) {{\n    {body}\n}}',
                'while_loop': 'while ({condition}) {{\n    {body}\n}}',
                'struct_definition': 'struct {name} {{\n    {body}\n}};',
            },
            'java': {
                'variable_declaration': '{type} {name} = {value};',
                'function_definition': 'public {return_type} {name}({params}) {{\n    {body}\n}}',
                'if_statement': 'if ({condition}) {{\n    {body}\n}}',
                'for_loop': 'for ({init}; {condition}; {increment}) {{\n    {body}\n}}',
                'while_loop': 'while ({condition}) {{\n    {body}\n}}',
                'class_definition': 'public class {name} {{\n    {body}\n}}',
            },
        }
        return templates.get(language, {}).get(construct, '')

    @staticmethod
    def fill_template(template: str, **kwargs) -> str:
        kwargs.setdefault('params', [])
        return template.format(**kwargs)