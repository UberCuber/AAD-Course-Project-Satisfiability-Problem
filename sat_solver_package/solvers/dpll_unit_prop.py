"""
DPLL Solver with Unit Propagation
"""

from dpll_basic import DPLLSolver, SolverStats


class DPLLUnitPropagation(DPLLSolver):
    """
    DPLL with Unit Propagation heuristic
    
    Unit Propagation: If a clause has only one literal, that literal must be true
    """
    
    def _dpll(self, clauses, assigned_vars):
        """
        Core DPLL with unit propagation
        """
        # Apply unit propagation until fixpoint
        clauses, up_result = self._unit_propagate(clauses, assigned_vars)
        
        if up_result == "UNSAT":
            self.stats.backtracks += 1
            return False
        
        if up_result == "SAT":
            return True
        
        # Simplify based on assignments
        clauses, status = self._simplify_clauses(clauses)
        
        if status == "UNSAT":
            self.stats.backtracks += 1
            return False
        
        if status == "SAT":
            return True
        
        # Choose a variable
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
    
    def _unit_propagate(self, clauses, assigned_vars):
        """
        Perform unit propagation
        
        Returns:
            (clauses, status)
        """
        changed = True
        
        while changed:
            changed = False
            
            for clause in clauses:
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
                
                if satisfied:
                    continue
                
                if not unassigned:
                    # Empty clause - conflict
                    return clauses, "UNSAT"
                
                if len(unassigned) == 1:
                    # Unit clause - propagate
                    lit = unassigned[0]
                    var = abs(lit)
                    
                    if var not in assigned_vars:
                        self.assignment[var] = (lit > 0)
                        assigned_vars.add(var)
                        changed = True
                        self.stats.unit_propagations += 1
        
        # Check if all clauses satisfied
        all_satisfied = True
        for clause in clauses:
            clause_satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in self.assignment:
                    if (lit > 0 and self.assignment[var]) or (lit < 0 and not self.assignment[var]):
                        clause_satisfied = True
                        break
                else:
                    all_satisfied = False
            
            if not clause_satisfied:
                all_satisfied = False
                break
        
        if all_satisfied:
            return clauses, "SAT"
        
        return clauses, "CONTINUE"


def solve_sat_unit_prop(formula):
    """Solve SAT with unit propagation"""
    solver = DPLLUnitPropagation(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()
