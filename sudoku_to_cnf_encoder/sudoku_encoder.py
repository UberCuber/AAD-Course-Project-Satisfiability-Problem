"""
Sudoku to CNF Encoder

This module encodes a Sudoku puzzle into Conjunctive Normal Form (CNF).
The CNF can then be solved by a SAT solver like the CDCL solver.

Variable Encoding:
- For a 9x9 Sudoku, variables are numbered 1 to 729
- Variable i_j_k represents: "cell (i,j) contains digit k"
- i, j range from 0 to 8 (row, column)
- k ranges from 1 to 9 (digit)
- Variable number = 81*(i*9 + j) + k

The CNF ensures:
1. Each cell contains exactly one digit
2. Each row contains each digit exactly once
3. Each column contains each digit exactly once
4. Each 3x3 box contains each digit exactly once
"""

from typing import List, Set, Tuple


class SudokuToCNF:
    """Encodes a Sudoku puzzle to CNF format."""
    
    def __init__(self, size: int = 9, box_size: int = 3):
        """
        Initialize the encoder.
        
        Args:
            size: The size of the Sudoku grid (default 9x9)
            box_size: The size of each box (default 3x3)
        """
        self.size = size
        self.box_size = box_size
        self.clauses: List[List[int]] = []
        self.var_count = size * size * size
    
    def _get_var(self, row: int, col: int, digit: int) -> int:
        """
        Get the variable number for cell(row, col) containing digit.
        
        Args:
            row: Row index (0 to size-1)
            col: Column index (0 to size-1)
            digit: Digit (1 to size)
            
        Returns:
            Variable number (1-indexed)
        """
        return (row * self.size * self.size) + (col * self.size) + digit
    
    def _add_clause(self, clause: List[int]) -> None:
        """Add a clause to the CNF."""
        self.clauses.append(clause)
    
    def _add_at_least_one(self, variables: List[int]) -> None:
        """Add constraint: at least one of the variables must be true."""
        self._add_clause(variables)
    
    def _add_at_most_one(self, variables: List[int]) -> None:
        """Add constraint: at most one of the variables can be true (using Tseitin)."""
        # For each pair of variables, add clause: NOT v1 OR NOT v2
        # Negative literals represent negation: -v means NOT v
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                # Create clause with negative literals: ~variables[i] OR ~variables[j]
                clause = []
                for k in [i, j]:
                    # Negate the literal by making it negative
                    clause.append(-variables[k])
                self._add_clause(clause)
    
    def _add_exactly_one(self, variables: List[int]) -> None:
        """Add constraint: exactly one of the variables must be true."""
        self._add_at_least_one(variables)
        self._add_at_most_one(variables)
    
    def encode_sudoku(self, sudoku: List[List[int]]) -> Tuple[List[List[int]], int]:
        """
        Encode a Sudoku puzzle to CNF.
        
        Args:
            sudoku: 9x9 grid where 0 represents empty cells
            
        Returns:
            Tuple of (clauses, num_variables)
        """
        self.clauses = []
        
        # Rule 1: Each cell contains at least one digit
        for i in range(self.size):
            for j in range(self.size):
                vars_in_cell = [
                    self._get_var(i, j, k) for k in range(1, self.size + 1)
                ]
                self._add_at_least_one(vars_in_cell)
        
        # Rule 2: Each cell contains at most one digit
        for i in range(self.size):
            for j in range(self.size):
                vars_in_cell = [
                    self._get_var(i, j, k) for k in range(1, self.size + 1)
                ]
                self._add_at_most_one(vars_in_cell)
        
        # Rule 3: Each row contains each digit exactly once
        for i in range(self.size):
            for k in range(1, self.size + 1):
                vars_in_row = [
                    self._get_var(i, j, k) for j in range(self.size)
                ]
                self._add_exactly_one(vars_in_row)
        
        # Rule 4: Each column contains each digit exactly once
        for j in range(self.size):
            for k in range(1, self.size + 1):
                vars_in_col = [
                    self._get_var(i, j, k) for i in range(self.size)
                ]
                self._add_exactly_one(vars_in_col)
        
        # Rule 5: Each 3x3 box contains each digit exactly once
        for box_row in range(0, self.size, self.box_size):
            for box_col in range(0, self.size, self.box_size):
                for k in range(1, self.size + 1):
                    vars_in_box = []
                    for i in range(box_row, box_row + self.box_size):
                        for j in range(box_col, box_col + self.box_size):
                            vars_in_box.append(self._get_var(i, j, k))
                    self._add_exactly_one(vars_in_box)
        
        # Rule 6: Add given clues
        for i in range(self.size):
            for j in range(self.size):
                if sudoku[i][j] != 0:
                    digit = sudoku[i][j]
                    # Cell (i,j) must contain digit
                    self._add_clause([self._get_var(i, j, digit)])
                    # Cell (i,j) must not contain any other digit
                    for k in range(1, self.size + 1):
                        if k != digit:
                            self._add_clause([-self._get_var(i, j, k)])
        
        return self.clauses, self.var_count
    
    def decode_solution(self, assignment: List[int]) -> List[List[int]]:
        """
        Decode a SAT solver assignment back to a Sudoku grid.
        
        Args:
            assignment: List where assignment[i] > 0 if variable i+1 is true
            
        Returns:
            9x9 grid with solved Sudoku
        """
        grid = [[0] * self.size for _ in range(self.size)]
        
        for i in range(self.size):
            for j in range(self.size):
                for k in range(1, self.size + 1):
                    var_num = self._get_var(i, j, k)
                    # assignment is 0-indexed, var_num is 1-indexed
                    if var_num <= len(assignment) and assignment[var_num - 1] > 0:
                        grid[i][j] = k
                        break
        
        return grid
    
    def print_clauses(self) -> None:
        """Print the CNF clauses in a readable format."""
        print(f"CNF with {len(self.clauses)} clauses and {self.var_count} variables:")
        for i, clause in enumerate(self.clauses, 1):
            print(f"Clause {i}: {clause}")
