# English Language Patterns for Database Operations

# This file defines English language patterns for database operations that will be used by the EnglishExecutionEngine
# to recognize and execute database-related instructions without generating intermediate SQL code.

# The patterns are designed to be flexible enough to handle variations in natural language input
# while still capturing the essential intent of the database operation.

# SELECT operations
select_patterns = [
    "Show me all {table}",
    "List all {table}",
    "Display all {table}",
    "Retrieve all {table}",
    "Get all {table}",
]

# INSERT operations
insert_patterns = [
    "Add a new {table} with {attributes}",
    "Create a new {table} entry with {attributes}",
    "Insert a {table} with {attributes}",
    "Add {attributes} to {table}",
]

# UPDATE operations
update_patterns = [
    "Update {table} {identifier} {attribute} to {value}",
    "Change {table} {identifier} {attribute} to {value}",
    "Modify {table} {identifier} {attribute} to {value}",
    "Set {table} {identifier} {attribute} to {value}",
]

# DELETE operations
delete_patterns = [
    "Remove {table} {identifier}",
    "Delete {table} {identifier}",
    "Erase {table} {identifier}",
]

# These patterns will be used to map English instructions to internal database actions.
# The EnglishExecutionEngine will process these patterns to perform the corresponding
# database operations without generating or displaying any intermediate SQL code.

# Example usage:
# "Show me all users" -> SELECT operation on the users table
# "Add a new user with name John Doe and email john@example.com" -> INSERT operation
# "Update user with id 5 email to newemail@example.com" -> UPDATE operation
# "Remove user with id 10" -> DELETE operation