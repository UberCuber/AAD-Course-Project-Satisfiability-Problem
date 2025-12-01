"""
CNF Parser and Formula representation
Handles DIMACS CNF format parsing
"""

class CNFFormula:
    """Represents a CNF formula"""
    
    def __init__(self, num_vars, clauses):
        self.num_vars = num_vars
        self.clauses = clauses  # List of lists, each inner list is a clause
        self.num_clauses = len(clauses)
    
    def __str__(self):
        return f"CNF Formula: {self.num_vars} variables, {self.num_clauses} clauses"
    
    def copy(self):
        """Deep copy of the formula"""
        return CNFFormula(self.num_vars, [clause[:] for clause in self.clauses])


def parse_dimacs_cnf(filename):
    """
    Parse a DIMACS CNF file
    
    Format:
    c comments
    p cnf <num_vars> <num_clauses>
    clause lines (space-separated literals, ending with 0)
    
    Returns:
        CNFFormula object
    """
    clauses = []
    num_vars = 0
    num_clauses = 0
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('c'):
                continue
            
            # Problem line
            if line.startswith('p'):
                parts = line.split()
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
                continue
            
            # Clause line
            literals = [int(x) for x in line.split() if int(x) != 0]
            if literals:
                clauses.append(literals)
    
    return CNFFormula(num_vars, clauses)


def parse_cnf_string(cnf_string):
    """
    Parse CNF from a string (for programmatic formula creation)
    
    Format: "[[1, -2], [2, 3], [-1, -3]]"
    Each sublist is a clause
    """
    import ast
    clauses = ast.literal_eval(cnf_string)
    
    # Find number of variables
    num_vars = 0
    for clause in clauses:
        for lit in clause:
            num_vars = max(num_vars, abs(lit))
    
    return CNFFormula(num_vars, clauses)


def write_dimacs_cnf(formula, filename):
    """Write a CNF formula to DIMACS format"""
    with open(filename, 'w') as f:
        f.write(f"p cnf {formula.num_vars} {formula.num_clauses}\n")
        for clause in formula.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
