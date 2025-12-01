"""
Basic DPLL SAT Solver Implementation

This module implements the Davis-Putnam-Logemann-Loveland (DPLL) algorithm
for solving Boolean Satisfiability (SAT) problems in Conjunctive Normal Form (CNF).

This is a baseline implementation with NO heuristics or optimizations:
- Pure chronological backtracking
- Simple first-unassigned variable selection
- Basic clause simplification

Algorithm:
    1. Simplify clauses based on current partial assignment
    2. If unsatisfiable -> backtrack
    3. If all clauses satisfied -> return SAT
    4. Choose next unassigned variable (no heuristic)
    5. Try assigning True, recurse
    6. If fails, try False, recurse
    7. If both fail -> backtrack

Author: Advanced Algorithm Design Course Project
Date: December 2025
Complexity: Exponential worst-case O(2^n) where n = number of variables
"""

from cnf_parser import CNFFormula
from typing import Dict, List, Set, Tuple, Optional


class SolverStats:
    """
    Statistics tracker for solver performance metrics.
    
    Attributes:
        decisions (int): Number of branching decisions (variable assignments)
        backtracks (int): Number of backtrack operations due to conflicts
        unit_propagations (int): Number of unit clause propagations
        pure_eliminations (int): Number of pure literal eliminations
        learned_clauses (int): Number of conflict clauses learned (CDCL only)
        restarts (int): Number of solver restarts (CDCL only)
    """
    
    def __init__(self):
        self.decisions = 0
        self.backtracks = 0
        self.unit_propagations = 0
        self.pure_eliminations = 0
        self.learned_clauses = 0
        self.restarts = 0
    
    def __str__(self):
        return (f"Decisions: {self.decisions}, "
                f"Backtracks: {self.backtracks}, "
                f"Unit Props: {self.unit_propagations}, "
                f"Pure Elims: {self.pure_eliminations}, "
                f"Learned: {self.learned_clauses}, "
                f"Restarts: {self.restarts}")


class DPLLSolver:
    """
    Basic DPLL SAT Solver with chronological backtracking.
    
    This class implements the core DPLL algorithm without any heuristics
    or optimizations. It serves as a baseline for comparing more sophisticated
    solvers (VSIDS, CDCL, etc.).
    
    Attributes:
        formula (CNFFormula): The CNF formula to solve
        assignment (Dict[int, bool]): Current partial assignment (var -> True/False)
        stats (SolverStats): Performance metrics tracker
    
    Time Complexity:
        Worst-case: O(2^n) where n = number of variables
        Best-case: O(n) if formula is trivially satisfiable
    
    Space Complexity:
        O(n * m) where n = variables, m = clauses (for storing formula)
    
    Example:
        >>> from cnf_parser import CNFParser
        >>> formula = CNFParser.parse('instance.cnf')
        >>> solver = DPLLSolver(formula)
        >>> sat, assignment = solver.solve()
        >>> if sat:
        ...     print(f"SAT with assignment: {assignment}")
        ... else:
        ...     print("UNSAT")
    """
    
    def __init__(self, formula):
        self.formula = formula
        self.assignment = {}  # var -> True/False
        self.stats = SolverStats()
    
    def solve(self):
        """
        Solve the SAT problem
        
        Returns:
            (satisfiable: bool, assignment: dict or None)
        """
        result = self._dpll(self.formula.clauses[:], set())
        
        if result:
            return True, self.assignment
        else:
            return False, None
    
    def _dpll(self, clauses, assigned_vars):
        """
        Core DPLL algorithm
        
        Args:
            clauses: Current clause list
            assigned_vars: Set of assigned variable numbers
        
        Returns:
            True if satisfiable, False otherwise
        """
        # Simplify clauses based on current assignment
        clauses, status = self._simplify_clauses(clauses)
        
        if status == "UNSAT":
            self.stats.backtracks += 1
            return False
        
        if status == "SAT":
            return True
        
        # Choose a variable (no heuristic, just pick first unassigned)
        var = self._choose_variable(assigned_vars)
        if var is None:
            return True  # All variables assigned and no conflict
        
        self.stats.decisions += 1
        
        # Try assigning True
        self.assignment[var] = True
        assigned_vars.add(var)
        
        if self._dpll(clauses[:], assigned_vars):
            return True
        
        # Backtrack: try False
        self.assignment[var] = False
        
        if self._dpll(clauses[:], assigned_vars):
            return True
        
        # Both failed, backtrack
        del self.assignment[var]
        assigned_vars.remove(var)
        
        return False
    
    def _simplify_clauses(self, clauses):
        """
        Simplify clauses based on current assignment
        
        Returns:
            (simplified_clauses, status)
            status: "CONTINUE", "SAT", or "UNSAT"
        """
        simplified = []
        
        for clause in clauses:
            new_clause = []
            satisfied = False
            
            for lit in clause:
                var = abs(lit)
                
                if var in self.assignment:
                    # Check if this literal is satisfied
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        satisfied = True
                        break
                    # Otherwise, this literal is false, skip it
                else:
                    new_clause.append(lit)
            
            if not satisfied:
                if not new_clause:
                    # Empty clause - UNSAT
                    return [], "UNSAT"
                simplified.append(new_clause)
        
        if not simplified:
            # All clauses satisfied
            return [], "SAT"
        
        return simplified, "CONTINUE"
    
    def _choose_variable(self, assigned_vars):
        """
        Choose next variable to assign (no heuristic)
        Just picks the first unassigned variable
        """
        for var in range(1, self.formula.num_vars + 1):
            if var not in assigned_vars:
                return var
        return None
    
    def get_stats(self):
        """Return solver statistics"""
        return self.stats


def solve_sat_basic(formula):
    """
    Convenience function to solve SAT with basic DPLL
    
    Returns:
        (satisfiable, assignment, stats)
    """
    solver = DPLLSolver(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()


if __name__ == "__main__":
    # Test with simple formula
    from cnf_parser import CNFFormula
    
    # (x1 ∨ x2) ∧ (¬x1 ∨ x3) ∧ (¬x2 ∨ ¬x3)
    clauses = [[1, 2], [-1, 3], [-2, -3]]
    formula = CNFFormula(3, clauses)
    
    sat, assignment, stats = solve_sat_basic(formula)
    
    print(f"Satisfiable: {sat}")
    print(f"Assignment: {assignment}")
    print(f"Stats: {stats}")
