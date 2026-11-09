"""
Compiler Exception Definitions.
"""

class CompileError(Exception):
    """Exception raised during algorithmic code parsing or compilation."""
    def __init__(self, message: str, line_num: int = None, column: int = None):
        super().__init__(message)
        self.message = message
        self.line_num = line_num
        self.column = column

    def __str__(self):
        if self.line_num is not None:
            return f"Ligne {self.line_num}: {self.message}"
        return self.message
