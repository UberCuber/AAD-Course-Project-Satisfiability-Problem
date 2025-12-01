"""
CDCL SAT Solver - Conflict-Driven Clause Learning (Optimized)
State-of-the-art SAT solving with:
- Unit propagation with watched literals
- VSIDS variable selection with decay
- Non-chronological backtracking
- Conflict clause learning with 1-UIP
- Restarts with geometric sequence
- Clause deletion
"""

from dpll_heuristics import DPLL_VSIDS
from collections import defaultdict, deque


class CDCLSolver(DPLL_VSIDS):
    """
    Optimized CDCL (Conflict-Driven Clause Learning) SAT Solver
    """
    
    def __init__(self, formula, restart_interval=100, clause_deletion_threshold=1000):
        super().__init__(formula)
        self.decision_level = 0
        self.var_decision_level = {}
        self.trail = []
        self.learned_clauses = []
        self.restart_interval = restart_interval
        self.clause_deletion_threshold = clause_deletion_threshold
        self.conflicts_since_restart = 0
        self.clause_activity = {}
        self.implication_graph = {}  # var -> (reason_clause, antecedents)
        
        # Watched literals: clause_id -> [lit1, lit2]
        self.watched = defaultdict(list)
        self.watch_list = defaultdict(list)  # literal -> list of clause indices watching it
        self._initialize_watched_literals()
    
    def _initialize_watched_literals(self):
        """Initialize two-watched-literal scheme"""
        all_clauses = self.formula.clauses
        for i, clause in enumerate(all_clauses):
            if len(clause) >= 2:
                # Watch first two literals
                self.watched[i] = [clause[0], clause[1]]
                self.watch_list[clause[0]].append(i)
                self.watch_list[clause[1]].append(i)
            elif len(clause) == 1:
                # Unit clause, watch the only literal
                self.watched[i] = [clause[0]]
                self.watch_list[clause[0]].append(i)
    
    def solve(self):
        """Solve with optimized CDCL"""
        self.decision_level = 0
        self.var_decision_level = {}
        self.trail = []
        self.learned_clauses = []
        self.conflicts_since_restart = 0
        self.implication_graph = {}
        
        # Initial unit propagation
        conflict = self._unit_propagate_watched()
        if conflict is not None:
            return False, None
        
        # Main CDCL loop
        while True:
            # Check if all variables assigned (SAT)
            if len(self.assignment) == self.formula.num_vars:
                return True, self.assignment
            
            # Make decision
            var = self._choose_variable(set(self.var_decision_level.keys()))
            if var is None:
                # All variables assigned
                return True, self.assignment
            
            # Increment decision level
            self.decision_level += 1
            self.stats.decisions += 1
            
            # Choose polarity (default to True)
            value = True
            
            self.assignment[var] = value
            self.var_decision_level[var] = self.decision_level
            self.trail.append((var, value, self.decision_level, 'decision'))
            self.implication_graph[var] = (None, [])
            
            # Propagate
            while True:
                conflict_clause_idx = self._unit_propagate_watched()
                
                if conflict_clause_idx is None:
                    # No conflict, continue
                    break
                
                # Conflict occurred
                self.stats.backtracks += 1
                self.conflicts_since_restart += 1
                
                if self.decision_level == 0:
                    # Top-level conflict - UNSAT
                    return False, None
                
                # Learn from conflict
                learned_clause, backjump_level = self._analyze_conflict_1uip(conflict_clause_idx)
                
                if learned_clause and len(learned_clause) > 0:
                    # Add learned clause
                    clause_idx = len(self.formula.clauses) + len(self.learned_clauses)
                    self.learned_clauses.append(learned_clause)
                    self.stats.learned_clauses += 1
                    
                    # Initialize watched literals for learned clause
                    if len(learned_clause) >= 2:
                        self.watched[clause_idx] = [learned_clause[0], learned_clause[1]]
                        self.watch_list[learned_clause[0]].append(clause_idx)
                        self.watch_list[learned_clause[1]].append(clause_idx)
                    elif len(learned_clause) == 1:
                        self.watched[clause_idx] = [learned_clause[0]]
                        self.watch_list[learned_clause[0]].append(clause_idx)
                    
                    # Update VSIDS scores
                    for lit in learned_clause:
                        var = abs(lit)
                        self.activity[var] += self.increment
                    self._decay_activity()
                
                # Backjump
                self._backjump_to_level(backjump_level)
                
                # Check for restart
                if self.conflicts_since_restart >= self.restart_interval:
                    self._restart()
                    break
                
                # Check for clause deletion
                if len(self.learned_clauses) > self.clause_deletion_threshold:
                    self._delete_clauses()
    
    def _unit_propagate_watched(self):
        """
        Unit propagation using watched literals
        Returns clause index if conflict, None otherwise
        """
        propagate_queue = deque()
        
        # Check for initial unit clauses
        for i, clause in enumerate(self.formula.clauses + self.learned_clauses):
            if len(clause) == 1:
                lit = clause[0]
                var = abs(lit)
                if var not in self.assignment:
                    propagate_queue.append((var, lit > 0, i))
        
        while propagate_queue:
            var, value, reason_clause_idx = propagate_queue.popleft()
            
            if var in self.assignment:
                # Already assigned, check consistency
                if self.assignment[var] != value:
                    return reason_clause_idx
                continue
            
            # Assign variable
            self.assignment[var] = value
            self.var_decision_level[var] = self.decision_level
            self.trail.append((var, value, self.decision_level, 'unit_prop'))
            self.stats.unit_propagations += 1
            
            # Get reason (antecedents)
            if reason_clause_idx is not None:
                clause = self._get_clause(reason_clause_idx)
                antecedents = [abs(lit) for lit in clause if abs(lit) != var]
                self.implication_graph[var] = (reason_clause_idx, antecedents)
            
            # Update watches for clauses watching -lit (now false)
            false_lit = var if not value else -var
            
            # Process all clauses watching this literal
            clauses_to_check = list(self.watch_list[false_lit])
            
            for clause_idx in clauses_to_check:
                clause = self._get_clause(clause_idx)
                
                if clause_idx not in self.watched:
                    continue
                
                watched_lits = self.watched[clause_idx]
                
                # If this literal is not watched by this clause, skip
                if false_lit not in watched_lits:
                    continue
                
                # Try to find alternative literal to watch
                found_alternative = False
                clause_satisfied = False
                
                for lit in clause:
                    if lit in watched_lits:
                        # Already watching this
                        continue
                    
                    lit_var = abs(lit)
                    
                    # Check if literal is satisfied or unassigned
                    if lit_var not in self.assignment:
                        # Unassigned - can watch this
                        # Replace the false literal with this one
                        self.watch_list[false_lit].remove(clause_idx)
                        watched_lits.remove(false_lit)
                        watched_lits.append(lit)
                        self.watch_list[lit].append(clause_idx)
                        found_alternative = True
                        break
                    elif (lit > 0 and self.assignment[lit_var]) or (lit < 0 and not self.assignment[lit_var]):
                        # Literal is satisfied
                        clause_satisfied = True
                        break
                
                if clause_satisfied or found_alternative:
                    continue
                
                # Couldn't find alternative - check other watched literal
                other_watched = [l for l in watched_lits if l != false_lit]
                
                if not other_watched:
                    # Conflict - all literals false
                    return clause_idx
                
                other_lit = other_watched[0]
                other_var = abs(other_lit)
                
                if other_var not in self.assignment:
                    # Unit clause - propagate
                    propagate_queue.append((other_var, other_lit > 0, clause_idx))
                elif not ((other_lit > 0 and self.assignment[other_var]) or 
                         (other_lit < 0 and not self.assignment[other_var])):
                    # Other watched literal is also false - conflict
                    return clause_idx
        
        return None  # No conflict
        return None  # No conflict
    
    def _get_clause(self, clause_idx):
        """Get clause by index (from original or learned)"""
        if clause_idx < len(self.formula.clauses):
            return self.formula.clauses[clause_idx]
        else:
            learned_idx = clause_idx - len(self.formula.clauses)
            if learned_idx < len(self.learned_clauses):
                return self.learned_clauses[learned_idx]
        return []
    
    def _analyze_conflict_1uip(self, conflict_clause_idx):
        """
        Analyze conflict using 1-UIP (First Unique Implication Point) scheme
        
        Returns:
            (learned_clause, backjump_level)
        """
        if self.decision_level == 0:
            return None, -1
        
        conflict_clause = self._get_clause(conflict_clause_idx)
        
        # Start with conflict clause
        learned_lits = set(conflict_clause)
        
        # Count literals at current decision level
        current_level_count = sum(
            1 for lit in learned_lits 
            if abs(lit) in self.var_decision_level and 
            self.var_decision_level[abs(lit)] == self.decision_level
        )
        
        # Resolve until we have exactly one literal from current level (1-UIP)
        trail_idx = len(self.trail) - 1
        
        while current_level_count > 1 and trail_idx >= 0:
            var, value, level, reason_type = self.trail[trail_idx]
            trail_idx -= 1
            
            if level != self.decision_level:
                continue
            
            # Check if this variable is in the learned clause
            pos_lit = var
            neg_lit = -var
            
            if pos_lit not in learned_lits and neg_lit not in learned_lits:
                continue
            
            # Remove this literal from learned clause
            if pos_lit in learned_lits:
                learned_lits.remove(pos_lit)
            else:
                learned_lits.remove(neg_lit)
            
            current_level_count -= 1
            
            # Add reason for this assignment
            if var in self.implication_graph:
                reason_clause_idx, antecedents = self.implication_graph[var]
                if reason_clause_idx is not None:
                    reason_clause = self._get_clause(reason_clause_idx)
                    for lit in reason_clause:
                        if abs(lit) != var and lit not in learned_lits:
                            learned_lits.add(lit)
                            lit_var = abs(lit)
                            if (lit_var in self.var_decision_level and 
                                self.var_decision_level[lit_var] == self.decision_level):
                                current_level_count += 1
        
        # Find backjump level (second highest decision level)
        levels = []
        for lit in learned_lits:
            var = abs(lit)
            if var in self.var_decision_level:
                level = self.var_decision_level[var]
                if level < self.decision_level:
                    levels.append(level)
        
        if levels:
            backjump_level = max(levels)
        else:
            backjump_level = 0
        
        return list(learned_lits), backjump_level
    
    def _backjump_to_level(self, level):
        """Backjump to specified decision level"""
        # Remove all assignments after this level
        while self.trail and self.trail[-1][2] > level:
            var, _, _, _ = self.trail.pop()
            if var in self.assignment:
                del self.assignment[var]
            if var in self.var_decision_level:
                del self.var_decision_level[var]
            if var in self.implication_graph:
                del self.implication_graph[var]
        
        self.decision_level = level
    
    def _restart(self):
        """
        Restart search while keeping learned clauses
        """
        self.stats.restarts += 1
        self.conflicts_since_restart = 0
        
        # Clear all assignments
        self.assignment = {}
        self.var_decision_level = {}
        self.trail = []
        self.decision_level = 0
        self.implication_graph = {}
        
        # Increase restart interval (geometric)
        self.restart_interval = int(self.restart_interval * 1.5)
    
    def _delete_clauses(self):
        """
        Delete inactive learned clauses to prevent memory bloat
        Keep only the most active half
        """
        if len(self.learned_clauses) <= self.clause_deletion_threshold:
            return
        
        # Simple deletion: keep first half (could use activity-based deletion)
        keep_count = self.clause_deletion_threshold // 2
        
        # Clear watch lists for deleted clauses
        base_idx = len(self.formula.clauses)
        for i in range(keep_count, len(self.learned_clauses)):
            clause_idx = base_idx + i
            if clause_idx in self.watched:
                for lit in self.watched[clause_idx]:
                    if clause_idx in self.watch_list[lit]:
                        self.watch_list[lit].remove(clause_idx)
                del self.watched[clause_idx]
        
        # Keep only first half
        self.learned_clauses = self.learned_clauses[:keep_count]


def solve_sat_cdcl(formula):
    """Solve SAT with optimized CDCL"""
    solver = CDCLSolver(formula)
    sat, assignment = solver.solve()
    return sat, assignment, solver.get_stats()


if __name__ == "__main__":
    from cnf_parser import CNFFormula
    
    # Test
    clauses = [[1, 2], [-1, 3], [-2, -3], [1, -3]]
    formula = CNFFormula(3, clauses)
    
    sat, assignment, stats = solve_sat_cdcl(formula)
    print(f"SAT: {sat}")
    print(f"Assignment: {assignment}")
    print(f"Stats: {stats}")
