import random
import sys

class WalkSATSolver:
    def __init__(self):
        self.clauses = []        # List of lists: [[1, -2, 3], ...]
        self.n_vars = 0          # Total number of variables
        self.occurrence_map = {} # Map: variable -> [list of clause indices]
    
    def load_dimacs(self, filename):
        """Parses a standard DIMACS .cnf file."""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('c'):
                        continue
                    if line.startswith('p'):
                        parts = line.split()
                        self.n_vars = int(parts[2])
                        self._init_occurrence_map()
                        continue
                    
                    # Read clauses (end with 0)
                    parts = [int(x) for x in line.split() if x != '0']
                    if parts:
                        self.clauses.append(parts)
                        clause_idx = len(self.clauses) - 1
                        for lit in parts:
                            self.occurrence_map[abs(lit)].append(clause_idx)
                            
            print(f"Loaded: {self.n_vars} variables, {len(self.clauses)} clauses.")
            
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            sys.exit(1)

    def load_from_list(self, clauses, n_vars):
        """Loads a problem directly from a list (useful for testing)."""
        self.clauses = clauses
        self.n_vars = n_vars
        self._init_occurrence_map()
        for idx, clause in enumerate(self.clauses):
            for lit in clause:
                self.occurrence_map[abs(lit)].append(idx)

    def _init_occurrence_map(self):
        """Initializes the mapping of variables to clauses for fast lookup."""
        self.occurrence_map = {i: [] for i in range(1, self.n_vars + 1)}

    def _evaluate_clause(self, clause, assignment):
        """Returns True if the clause is satisfied by the assignment."""
        for lit in clause:
            # lit is > 0: True if assignment[lit] is True
            # lit is < 0: True if assignment[abs(lit)] is False
            val = assignment[abs(lit)]
            if lit > 0 and val:
                return True
            if lit < 0 and not val:
                return True
        return False

    def _calculate_break_count(self, target_var, assignment):
        """
        Calculates 'break count': The number of clauses that are CURRENTLY 
        satisfied but will become UNSATISFIED if we flip target_var.
        """
        break_count = 0
        
        # Only check clauses that actually contain this variable
        relevant_clauses_indices = self.occurrence_map[target_var]
        
        for clause_idx in relevant_clauses_indices:
            clause = self.clauses[clause_idx]
            
            # Check if this clause is CURRENTLY satisfied
            is_satisfied = self._evaluate_clause(clause, assignment)
            
            if is_satisfied:
                # If we flip target_var, does it become unsatisfied?
                # Temporarily flip the variable in our mind (or copy)
                current_val = assignment[target_var]
                assignment[target_var] = not current_val # Flip
                
                if not self._evaluate_clause(clause, assignment):
                    break_count += 1
                
                assignment[target_var] = current_val # Flip back
                
        return break_count

    def solve(self, max_flips=10000, max_tries=10, p=0.5):
        """
        The main WalkSAT Algorithm.
        :param max_flips: Max changes before restarting.
        :param max_tries: How many fresh restarts to try.
        :param p: Probability of making a random move (noise).
        """
        print(f"Starting WalkSAT (Max Flips: {max_flips}, Noise p: {p})...")

        for try_num in range(max_tries):
            # 1. Start with a random assignment
            # (1-indexed map: 1->True, 2->False...)
            assignment = {i: random.choice([True, False]) for i in range(1, self.n_vars + 1)}
            
            for flip in range(max_flips):
                # 2. Find all unsatisfied clauses
                unsatisfied_indices = []
                for idx, clause in enumerate(self.clauses):
                    if not self._evaluate_clause(clause, assignment):
                        unsatisfied_indices.append(idx)
                
                # SUCCESS CHECK: If no unsatisfied clauses, we found a solution!
                if not unsatisfied_indices:
                    print(f"\nSolution found on Try {try_num+1}, Flip {flip}!")
                    return assignment

                # 3. Pick a random unsatisfied clause
                target_clause_idx = random.choice(unsatisfied_indices)
                target_clause = self.clauses[target_clause_idx]

                # 4. Choose which variable to flip
                # Logic: With probability p, random pick. Else, greedy pick.
                
                if random.random() < p:
                    # Random Walk: Pick any variable from the clause
                    var_to_flip = abs(random.choice(target_clause))
                else:
                    # Greedy Step: Pick variable with minimum 'break count'
                    best_var = None
                    min_break = float('inf')
                    
                    candidates = [abs(lit) for lit in target_clause]
                    
                    for var in candidates:
                        bk = self._calculate_break_count(var, assignment)
                        if bk < min_break:
                            min_break = bk
                            best_var = var
                        elif bk == min_break:
                            # Tie-breaking: random choice usually helps avoid loops
                            if random.random() < 0.5:
                                best_var = var
                    
                    var_to_flip = best_var

                # 5. Flip the variable
                assignment[var_to_flip] = not assignment[var_to_flip]
                
        print("\nFailure: Max flips reached without finding a solution.")
        return None

# ==========================================
#  DEMO / COMMAND LINE INTERFACE
# ==========================================
if __name__ == "__main__":
    solver = WalkSATSolver()

    # CASE 1: If a filename is provided, load it (PROFESSIONAL MODE)
    # Usage: python walksat.py my_problem.cnf
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"--- Loading file: {filename} ---")
        solver.load_dimacs(filename)
        solution = solver.solve(max_flips=100000, max_tries=10, p=0.57)
        
        if solution:
            print("SATISFIABLE")
            # Optional: print variable assignments nicely
            # print(solution)
        else:
            print("UNSATISFIABLE (or timed out)")

    # CASE 2: No file provided, run hardcoded demo (BACKUP / TEST MODE)
    else:
        print("--- No file provided. Running Hardcoded Demo ---")
        print("Usage to load file: python walksat.py <filename.cnf>")
        
        # (A or B) AND (!A or B) AND (!B or C)
        demo_clauses = [[1, 2], [-1, 2], [-2, 3]]
        n_vars = 3
        
        solver.load_from_list(demo_clauses, n_vars)
        solution = solver.solve(max_flips=100, max_tries=5, p=0.5)
        
        if solution:
            print("Assignment:", solution)
            print(f"Is variable 2 True? {solution[2]}")