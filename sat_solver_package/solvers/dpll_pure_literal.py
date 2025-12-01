"""
DPLL Solver with Unit Propagation and Pure Literal Elimination
"""

from dpll_unit_prop import DPLLUnitPropagation


class DPLLPureLiteral(DPLLUnitPropagation):
    """
    DPLL with Unit Propagation and Pure Literal Elimination
    
    Pure Literal: A variable that appears only in positive (or only negative) form
    can be assigned to satisfy all clauses containing it
    """
    
    def _dpll(self, clauses, assigned_vars):
        """
        Core DPLL with unit propagation and pure literal elimination
        """
        # Apply unit propagation
        clauses, up_result = self._unit_propagate(clauses, assigned_vars)
        
        if up_result == "UNSAT":
            self.stats.backtracks += 1
            return False
        
        if up_result == "SAT":
            return True
        
        # Apply pure literal elimination
        clauses, pl_result = self._pure_literal_eliminate(clauses, assigned_vars)
        
        if pl_result == "SAT":
            return True
        
        # Simplify
        clauses, status = self._simplify_clauses(clauses)
        
        if status == "UNSAT":
            self.stats.backtracks += 1
            return False
        
        if status == "SAT":
            return True
        
        # Choose variable
        var = self._choose_variable(assigned_vars)
        if var is None:
            return True
        
        self.stats.decisions += 1
        
        # Try True
        self.assignment[var] = True
        assigned_vars.add(var)
        
        if self._dpll(clauses[:], assigned_vars.copy()):
            return True
        
        # Try False
        self.assignment[var] = False
        
        if self._dpll(clauses[:], assigned_vars.copy()):
            return True
        
        # Backtrack
        del self.assignment[var]
        assigned_vars.discard(var)
        
        return False
    
    def _pure_literal_eliminate(self, clauses, assigned_vars):
        """
        Find and assign pure literals
        
        Returns:
            (clauses, status)
        """
        # Track polarity of each variable
        polarity = {}  # var -> set of polarities (True for positive, False for negative)
        
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        clause_sat = True
                        break
            
            if clause_sat:
                continue
            
            for lit in clause:
                var = abs(lit)
                if var not in self.assignment:
                    if var not in polarity:
                        polarity[var] = set()
                    polarity[var].add(lit > 0)
        
        # Find pure literals (appear in only one polarity)
        pure_literals = []
        for var, polarities in polarity.items():
            if len(polarities) == 1:
                pure_literals.append((var, polarities.pop()))
        
        # Assign pure literals
        if pure_literals:
            for var, is_positive in pure_literals:
                if var not in assigned_vars:
                    self.assignment[var] = is_positive
                    assigned_vars.add(var)
                    self.stats.pure_eliminations += 1
            
            # Check if all clauses satisfied after pure literal elimination
            all_satisfied = True
            for clause in clauses:
                clause_satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if var in self.assignment:
                        if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                            clause_satisfied = True
                            break
                
                if not clause_satisfied:
                    all_satisfied = False
                    break
            
            if all_satisfied:
                return clauses, "SAT"
        
        return clauses, "CONTINUE"


def solve_sat_pure_literal(formula):
    """Solve SAT with unit propagation and pure literal elimination"""
    solver = DPLLPureLiteral(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()
