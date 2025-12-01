# Set-Based SAT Solver

A pure set-theory implementation of the DPLL SAT solving algorithm using C++14.

## Quick Start

### 1. Compile

```bash
make
```

This creates `set_solver.exe` (Windows) or `set_solver` (Linux/Mac).

### 2. Run on CNF file

```bash
./set_solver.exe path/to/problem.cnf
```

### 3. Generate plots (optional)

```bash
pip install -r requirements.txt
python plot_enhanced_time.py
```

## Output

- **SAT**: Solution found (prints satisfying assignment)
- **UNSAT**: No solution exists
- **UNKNOWN**: Timeout or error

## Clean up

```bash
make clean
```
