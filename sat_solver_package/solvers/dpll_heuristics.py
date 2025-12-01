"""
DPLL Solvers with Various Variable Selection Heuristics
Implements: VSIDS, DLIS, MOM, JW
"""

from dpll_unit_prop import DPLLUnitPropagation
from collections import defaultdict
import math


class DPLL_VSIDS(DPLLUnitPropagation):
    """
    DPLL with VSIDS (Variable State Independent Decaying Sum)
    
    Tracks activity scores for variables based on conflict participation
    Periodically decays all scores
    """
    
    def __init__(self, formula, decay_factor=0.95):
        super().__init__(formula)
        self.activity = defaultdict(float)
        self.decay_factor = decay_factor
        self.increment = 1.0
        
        # Initialize activity for all variables
        for var in range(1, formula.num_vars + 1):
            self.activity[var] = 0.0
        
        # Give initial scores based on occurrence in clauses
        for clause in formula.clauses:
            for lit in clause:
                var = abs(lit)
                self.activity[var] += 1.0
    
    def _choose_variable(self, assigned_vars):
        """Choose variable with highest activity score"""
        best_var = None
        best_score = -1
        
        for var in range(1, self.formula.num_vars + 1):
            if var not in assigned_vars:
                if self.activity[var] > best_score:
                    best_score = self.activity[var]
                    best_var = var
        
        return best_var
    
    def _update_activity(self, conflict_vars):
        """Update activity scores after a conflict"""
        for var in conflict_vars:
            self.activity[var] += self.increment
    
    def _decay_activity(self):
        """Decay all activity scores"""
        for var in self.activity:
            self.activity[var] *= self.decay_factor
        self.increment /= self.decay_factor


class DPLL_DLIS(DPLLUnitPropagation):
    """
    DPLL with DLIS (Dynamic Largest Individual Sum)
    
    Chooses the literal that appears most frequently in unsatisfied clauses
    """
    
    def _choose_variable(self, assigned_vars):
        """Choose variable appearing most in unsatisfied clauses"""
        # Count occurrences of each literal in unsatisfied clauses
        literal_count = defaultdict(int)
        
        for clause in self.formula.clauses:
            # Check if clause is unsatisfied
            satisfied = False
            unassigned_lits = []
            
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        satisfied = True
                        break
                else:
                    unassigned_lits.append(lit)
            
            # Count literals in unsatisfied clauses
            if not satisfied:
                for lit in unassigned_lits:
                    literal_count[lit] += 1
        
        if not literal_count:
            # No unsatisfied clauses, pick any unassigned variable
            for var in range(1, self.formula.num_vars + 1):
                if var not in assigned_vars:
                    return var
            return None
        
        # Find literal with max count
        best_lit = max(literal_count.items(), key=lambda x: x[1])[0]
        return abs(best_lit)


class DPLL_MOM(DPLLUnitPropagation):
    """
    DPLL with MOM (Maximum Occurrences in Minimum clauses)
    
    Focuses on variables appearing in smallest clauses
    Similar to MRV (Minimum Remaining Values)
    """
    
    def _choose_variable(self, assigned_vars):
        """Choose variable appearing most in smallest unsatisfied clauses"""
        # Find minimum clause size
        min_size = float('inf')
        clause_sizes = []
        
        for clause in self.formula.clauses:
            # Count unassigned literals
            unassigned = []
            satisfied = False
            
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            
            if not satisfied and unassigned:
                size = len(unassigned)
                clause_sizes.append((size, unassigned))
                min_size = min(min_size, size)
        
        if not clause_sizes:
            # All clauses satisfied or no unassigned vars
            for var in range(1, self.formula.num_vars + 1):
                if var not in assigned_vars:
                    return var
            return None
        
        # Count occurrences in minimum-sized clauses
        literal_count = defaultdict(int)
        for size, lits in clause_sizes:
            if size == min_size:
                for lit in lits:
                    literal_count[abs(lit)] += 1
        
        if not literal_count:
            return None
        
        # Return variable with max count
        best_var = max(literal_count.items(), key=lambda x: x[1])[0]
        return best_var


class DPLL_JW(DPLLUnitPropagation):
    """
    DPLL with Jeroslow-Wang heuristic
    
    Weighted scoring that favors variables in shorter clauses
    Weight: 2^(-clause_length)
    """
    
    def _choose_variable(self, assigned_vars):
        """Choose variable with highest JW score"""
        scores = defaultdict(float)
        
        for clause in self.formula.clauses:
            # Count unassigned literals
            unassigned = []
            satisfied = False
            
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            
            if not satisfied and unassigned:
                # Add weight to each variable in this clause
                weight = 2.0 ** (-len(unassigned))
                for lit in unassigned:
                    var = abs(lit)
                    scores[var] += weight
        
        if not scores:
            # Pick any unassigned variable
            for var in range(1, self.formula.num_vars + 1):
                if var not in assigned_vars:
                    return var
            return None
        
        # Return variable with highest score
        best_var = max(scores.items(), key=lambda x: x[1])[0]
        return best_var


class DPLL_TwoClause(DPLLUnitPropagation):
    """
    DPLL with Two-Clause heuristic
    
    Prioritizes variables appearing in 2-literal clauses
    """
    
    def _choose_variable(self, assigned_vars):
        """Choose variable appearing in most 2-literal clauses"""
        two_clause_count = defaultdict(int)
        other_count = defaultdict(int)
        
        for clause in self.formula.clauses:
            unassigned = []
            satisfied = False
            
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            
            if not satisfied and unassigned:
                for lit in unassigned:
                    var = abs(lit)
                    if len(unassigned) == 2:
                        two_clause_count[var] += 1
                    else:
                        other_count[var] += 1
        
        # Prefer variables in 2-clauses
        if two_clause_count:
            return max(two_clause_count.items(), key=lambda x: x[1])[0]
        elif other_count:
            return max(other_count.items(), key=lambda x: x[1])[0]
        else:
            for var in range(1, self.formula.num_vars + 1):
                if var not in assigned_vars:
                    return var
            return None


# Convenience functions
def solve_sat_vsids(formula):
    """Solve SAT with VSIDS heuristic"""
    solver = DPLL_VSIDS(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()


def solve_sat_dlis(formula):
    """Solve SAT with DLIS heuristic"""
    solver = DPLL_DLIS(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()


def solve_sat_mom(formula):
    """Solve SAT with MOM heuristic"""
    solver = DPLL_MOM(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()


def solve_sat_jw(formula):
    """Solve SAT with JW heuristic"""
    solver = DPLL_JW(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()


def solve_sat_two_clause(formula):
    """Solve SAT with Two-Clause heuristic"""
    solver = DPLL_TwoClause(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()
