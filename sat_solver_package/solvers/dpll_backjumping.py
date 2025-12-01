"""
DPLL with Backjumping (Non-Chronological Backtracking)
"""

from dpll_heuristics import DPLL_VSIDS
from collections import deque


class DPLL_Backjumping(DPLL_VSIDS):
    """
    DPLL with Backjumping (Non-Chronological Backtracking)
    
    Instead of backtracking one level at a time,
    jump directly to the decision level that caused the conflict
    """
    
    def __init__(self, formula):
        super().__init__(formula)
        self.decision_level = 0
        self.var_decision_level = {}  # var -> decision level when assigned
        self.trail = []  # Stack of (var, value, decision_level)
    
    def solve(self):
        """Solve with backjumping using iterative approach"""
        self.decision_level = 0
        self.var_decision_level = {}
        self.trail = []
        
        # Iterative DPLL with backjumping
        while True:
            # Unit propagation
            conflict = self._unit_propagate_iterative()
            
            if conflict:
                # Conflict occurred
                self.stats.backtracks += 1
                
                if self.decision_level == 0:
                    # Top-level conflict, UNSAT
                    return False, None
                
                # Analyze conflict and backjump
                backjump_level = self._analyze_conflict_simple()
                self._backjump_to_level(backjump_level)
                continue
            
            # Check if all variables assigned (SAT)
            if len(self.assignment) == self.formula.num_vars:
                # Verify solution
                if self._is_satisfied():
                    return True, self.assignment
            
            # Choose variable
            var = self._choose_variable(set(self.var_decision_level.keys()))
            if var is None:
                # No more variables, check if satisfied
                if self._is_satisfied():
                    return True, self.assignment
                else:
                    # Should not happen, but handle it
                    if self.decision_level == 0:
                        return False, None
                    self.stats.backtracks += 1
                    self._backjump_to_level(self.decision_level - 1)
                    continue
            
            # Make decision
            self.decision_level += 1
            self.stats.decisions += 1
            
            # Try True first (could use polarity heuristic)
            self.assignment[var] = True
            self.var_decision_level[var] = self.decision_level
            self.trail.append((var, True, self.decision_level, 'decision'))
    
    def _is_satisfied(self):
        """Check if current assignment satisfies all clauses"""
        for clause in self.formula.clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        satisfied = True
                        break
            if not satisfied:
                return False
        return True
    
    def _unit_propagate_iterative(self):
        """
        Iterative unit propagation
        Returns True if conflict, False otherwise
        """
        changed = True
        
        while changed:
            changed = False
            
            for clause in self.formula.clauses:
                unassigned = []
                satisfied = False
                all_false = True
                
                for lit in clause:
                    var = abs(lit)
                    
                    if var in self.assignment:
                        if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                            satisfied = True
                            all_false = False
                            break
                        # Literal is false, but clause might not be all false yet
                    else:
                        unassigned.append(lit)
                        all_false = False
                
                if satisfied:
                    continue
                
                # Check if all literals are false (conflict)
                if not unassigned:
                    # Need to verify all literals are actually false
                    truly_all_false = True
                    for lit in clause:
                        var = abs(lit)
                        if var not in self.assignment:
                            truly_all_false = False
                            break
                        if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                            truly_all_false = False
                            break
                    
                    if truly_all_false:
                        return True  # Conflict
                
                # Unit clause
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    
                    if var not in self.var_decision_level:
                        self.assignment[var] = (lit > 0)
                        self.var_decision_level[var] = self.decision_level
                        self.trail.append((var, lit > 0, self.decision_level, 'unit_prop'))
                        changed = True
                        self.stats.unit_propagations += 1
        
        return False  # No conflict
    
    def _analyze_conflict_simple(self):
        """
        Simplified conflict analysis for backjumping
        Returns the decision level to backjump to
        """
        # Find conflicting clause variables and their levels
        conflict_levels = set()
        
        for clause in self.formula.clauses:
            all_false = True
            clause_levels = []
            
            for lit in clause:
                var = abs(lit)
                
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        all_false = False
                        break
                else:
                    all_false = False
                    break
                
                if var in self.var_decision_level:
                    clause_levels.append(self.var_decision_level[var])
            
            if all_false and clause_levels:
                conflict_levels.update(clause_levels)
        
        if not conflict_levels:
            # No clear conflict, backtrack one level
            return max(0, self.decision_level - 1)
        
        # Backjump to second-highest level (skip current level)
        sorted_levels = sorted(conflict_levels, reverse=True)
        
        # Find highest level below current
        for level in sorted_levels:
            if level < self.decision_level:
                return level
        
        # If all at current level, go to previous
        return max(0, self.decision_level - 1)
    
    def _backjump_to_level(self, level):
        """Backjump to specified decision level"""
        # Remove all assignments after this level
        while self.trail and self.trail[-1][2] > level:
            var, _, _, _ = self.trail.pop()
            if var in self.assignment:
                del self.assignment[var]
            if var in self.var_decision_level:
                del self.var_decision_level[var]
        
        self.decision_level = level


def solve_sat_backjumping(formula):
    """Solve SAT with backjumping"""
    solver = DPLL_Backjumping(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()
