"""
This module defines advanced database operations that can be executed through English instructions.
It simulates complex database functionalities without actually connecting to a database system.
"""

from typing import Dict, List, Any

class AdvancedDatabaseOperations:
    def __init__(self):
        self.simulated_database: Dict[str, List[Dict[str, Any]]] = {}

    def execute_complex_query(self, instruction: str) -> str:
        words = instruction.lower().split()
        if "select" in words and "from" in words:
            table = words[words.index("from") + 1]
            if table in self.simulated_database:
                # Simulate query execution
                return f"Executed query on table {table}: {self.simulated_database[table]}"
            else:
                return f"Table {table} not found"
        return "Invalid query instruction"

    def perform_transaction(self, instruction: str) -> str:
        words = instruction.lower().split()
        if "begin transaction" in instruction.lower():
            return "Transaction started"
        elif "commit" in words:
            return "Transaction committed"
        elif "rollback" in words:
            return "Transaction rolled back"
        else:
            return "Invalid transaction instruction"

    def create_index(self, instruction: str) -> str:
        words = instruction.lower().split()
        if "create index" in instruction.lower() and "on" in words:
            table = words[words.index("on") + 1]
            column = words[words.index("on") + 2]
            if table in self.simulated_database:
                return f"Index created on {table}.{column}"
            else:
                return f"Table {table} not found"
        return "Invalid index creation instruction"

    def join_tables(self, instruction: str) -> str:
        words = instruction.lower().split()
        if "join" in words:
            table1 = words[words.index("join") - 1]
            table2 = words[words.index("join") + 1]
            if table1 in self.simulated_database and table2 in self.simulated_database:
                return f"Joined tables {table1} and {table2}"
            else:
                return "One or both tables not found"
        return "Invalid join instruction"

    def aggregate_data(self, instruction: str) -> str:
        words = instruction.lower().split()
        if any(agg in words for agg in ["sum", "avg", "count", "min", "max"]):
            agg_func = next(agg for agg in ["sum", "avg", "count", "min", "max"] if agg in words)
            if "from" in words:
                table = words[words.index("from") + 1]
                if table in self.simulated_database:
                    return f"Aggregated data from {table} using {agg_func}"
                else:
                    return f"Table {table} not found"
        return "Invalid aggregation instruction"