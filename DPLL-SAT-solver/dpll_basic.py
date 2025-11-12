# dpll_basic.py
# Basic DPLL SAT Solver (with unit propagation, pure literal elimination)
# + instrumentation: performance counters & timing

import time
from typing import List, Dict, Optional, Tuple

# ------------------- GLOBAL COUNTERS -------------------
stats = {
    "calls": 0,
    "unit_props": 0,
    "pure_literals": 0,
    "backtracks": 0
}

# ------------------- DIMACS PARSER -------------------
def parse_dimacs(file_path: str) -> Tuple[List[List[int]], int]:
    clauses = []
    num_vars = 0
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith('c') or line == "" or line.startswith('%') or line.startswith('0'):
                continue
            if line.startswith('p'):
                parts = line.split()
                num_vars = int(parts[2])
            else:
                literals = [int(x) for x in line.split() if x != '0']
                if literals:
                    clauses.append(literals)
    return clauses, num_vars

# ------------------- UNIT PROPAGATION -------------------
def unit_propagate(clauses: List[List[int]], assignment: Dict[int, bool]) -> Tuple[List[List[int]], Dict[int, bool]]:
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        if not unit_clauses:
            break
        
        for uc in unit_clauses:
            lit = uc[0]
            stats["unit_props"] += 1
            val = (lit > 0)
            var = abs(lit)
            
            # Check for conflict
            if var in assignment and assignment[var] != val:
                return [[]], assignment  # conflict
            
            if var not in assignment:  # Only assign if not already assigned
                assignment[var] = val
                changed = True
                
                # Simplify clauses
                new_clauses = []
                for clause in clauses:
                    if lit in clause:
                        continue  # clause satisfied, skip it
                    elif -lit in clause:
                        new_clause = [l for l in clause if l != -lit]
                        if not new_clause:  # empty clause = conflict
                            return [[]], assignment
                        new_clauses.append(new_clause)
                    else:
                        new_clauses.append(clause[:])  # copy clause
                clauses = new_clauses
                break  # restart the loop after modification
    
    return clauses, assignment

# ------------------- PURE LITERAL ELIMINATION -------------------
def pure_literal_elimination(clauses: List[List[int]], assignment: Dict[int, bool]) -> Tuple[List[List[int]], Dict[int, bool]]:
    if not clauses:
        return clauses, assignment
        
    all_literals = {lit for clause in clauses for lit in clause}
    pure_literals = [lit for lit in all_literals if -lit not in all_literals]
    
    for lit in pure_literals:
        var = abs(lit)
        if var not in assignment:  # Only assign if not already assigned
            stats["pure_literals"] += 1
            assignment[var] = (lit > 0)
            # Remove clauses containing this literal
            clauses = [c for c in clauses if lit not in c]
    
    return clauses, assignment

# ------------------- DPLL CORE -------------------
def dpll(clauses: List[List[int]], assignment: Dict[int, bool]) -> Optional[Dict[int, bool]]:
    stats["calls"] += 1
    
    # Unit propagation
    clauses, assignment = unit_propagate(clauses, assignment)
    if [] in clauses:
        stats["backtracks"] += 1
        return None
    if not clauses:
        return assignment
    
    # Pure literal elimination
    clauses, assignment = pure_literal_elimination(clauses, assignment)
    if [] in clauses:
        stats["backtracks"] += 1
        return None
    if not clauses:
        return assignment
    
    # Choose variable (simple heuristic: first unassigned)
    all_vars = {abs(lit) for clause in clauses for lit in clause}
    unassigned = [v for v in all_vars if v not in assignment]
    if not unassigned:
        return assignment
    
    # Better heuristic: choose variable that appears in most clauses
    var_counts = {}
    for var in unassigned:
        var_counts[var] = sum(1 for clause in clauses if var in clause or -var in clause)
    var = max(unassigned, key=lambda v: var_counts.get(v, 0))
    
    # Try both assignments
    for val in [True, False]:
        new_assignment = assignment.copy()
        new_assignment[var] = val
        
        # Apply assignment to clauses
        new_clauses = []
        conflict = False
        
        for clause in clauses:
            pos_lit = var if val else -var
            neg_lit = -var if val else var
            
            if pos_lit in clause:
                continue  # clause satisfied
            elif neg_lit in clause:
                new_clause = [l for l in clause if l != neg_lit]
                if not new_clause:  # empty clause
                    conflict = True
                    break
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause[:])  # copy clause
        
        if not conflict:
            result = dpll(new_clauses, new_assignment)
            if result is not None:
                return result
    
    stats["backtracks"] += 1
    return None

# ------------------- SOLVER WRAPPER -------------------
def solve_cnf(clauses: List[List[int]]):
    global stats
    stats = {k: 0 for k in stats}  # reset
    
    start = time.time()
    result = dpll(clauses, {})
    end = time.time()
    
    print("\n===== DPLL Solver Results =====")
    if result is None:
        print("Result: UNSATISFIABLE")
    else:
        print("Result: SATISFIABLE")
        print("Assignment:", result)
    print("--------------------------------")
    print(f"Recursive Calls: {stats['calls']}")
    print(f"Unit Propagations: {stats['unit_props']}")
    print(f"Pure Literals Used: {stats['pure_literals']}")
    print(f"Backtracks: {stats['backtracks']}")
    print(f"Time Taken: {end - start:.6f} sec")
    print("================================\n")

if __name__ == "__main__":
    # Example 1: SAT
    clauses = [[1, 2], [-1, 2], [1, -2]]
    solve_cnf(clauses)
    
    # Example 2: UNSAT  
    clauses = [[1], [-1]]
    solve_cnf(clauses)
