#!/usr/bin/env python3
"""
Benchmarking script for SAT solvers
Runs all solvers on all CNF files in a directory and outputs results to CSV
"""

import os
import sys
import csv
import subprocess
import glob
from pathlib import Path
from datetime import datetime

# Solver names
SOLVERS = [
    'basic_dpll',
    'unit_prop', 
    'vsids',
    'dlis',
    'mom',
    'jw',
    'dlcs',
    'phase_saving',
    'backjumping',
    'random',
    'cdcl_solver'
]

# Friendly names for the solvers
SOLVER_NAMES = {
    'basic_dpll': 'Basic DPLL',
    'unit_prop': 'DPLL + Unit Propagation',
    'vsids': 'DPLL + VSIDS',
    'dlis': 'DPLL + DLIS',
    'mom': 'DPLL + MOM',
    'jw': 'DPLL + JW',
    'dlcs': 'DPLL + DLCS',
    'phase_saving': 'DPLL + VSIDS + Phase Saving',
    'backjumping': 'DPLL + Backjumping',
    'random': 'DPLL + Random',
    'cdcl_solver': 'CDCL (MINISAT heuristic)'
}

def run_solver(solver_path, cnf_file, timeout=180):
    """
    Run a single solver on a CNF file
    Returns: (result, time, depth, memory, decisions, backtracks, timeout_flag)
    """
    try:
        # CDCL solver has different command line arguments
        solver_name = os.path.basename(solver_path)
        if solver_name == 'cdcl_solver':
            # CDCL format: ./cdcl_solver <to_log> <decider> <restarter> <inputfile>
            # Use False for logging, MINISAT for heuristic, None for restart
            cmd = [solver_path, 'False', 'MINISAT', 'None', cnf_file]
        else:
            # DPLL solvers: ./solver <inputfile>
            cmd = [solver_path, cnf_file]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout.strip()
        if not output:
            return ('ERROR', 0, 0, 0, 0, 0, 0)
        
        # Parse output: SAT,time,depth,memory,decisions,backtracks,timeout
        parts = output.split(',')
        if len(parts) != 7:
            return ('ERROR', 0, 0, 0, 0, 0, 0)
        
        return (
            parts[0],           # SAT/UNSAT
            float(parts[1]),    # time
            int(parts[2]),      # depth
            int(parts[3]),      # memory
            int(parts[4]),      # decisions
            int(parts[5]),      # backtracks
            int(parts[6])       # timeout flag
        )
    except subprocess.TimeoutExpired:
        return ('TIMEOUT', timeout, 0, 0, 0, 0, 1)
    except Exception as e:
        print(f"Error running {solver_path} on {cnf_file}: {e}")
        return ('ERROR', 0, 0, 0, 0, 0, 0)

def benchmark(instances_dir, output_csv, build_dir='build', timeout=180):
    """
    Run all solvers on all CNF files in instances_dir
    """
    # Get all CNF files
    cnf_files = sorted(glob.glob(os.path.join(instances_dir, '*.cnf')))
    
    if not cnf_files:
        print(f"No CNF files found in {instances_dir}")
        return
    
    print(f"Found {len(cnf_files)} CNF files")
    print(f"Running {len(SOLVERS)} solvers with {timeout}s timeout")
    print("-" * 80)
    
    # Open CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = [
            'instance',
            'solver',
            'solver_name',
            'result',
            'time_seconds',
            'max_recursion_depth',
            'memory_kb',
            'num_decisions',
            'num_backtracks',
            'timeout'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_runs = len(cnf_files) * len(SOLVERS)
        current_run = 0
        
        # Run each solver on each instance
        for cnf_file in cnf_files:
            instance_name = os.path.basename(cnf_file)
            print(f"\nInstance: {instance_name}")
            
            for solver in SOLVERS:
                current_run += 1
                solver_path = os.path.join(build_dir, solver)
                
                if not os.path.exists(solver_path):
                    print(f"  [{current_run}/{total_runs}] {solver}: MISSING BINARY")
                    continue
                
                print(f"  [{current_run}/{total_runs}] {solver}...", end=' ', flush=True)
                
                result, time, depth, memory, decisions, backtracks, timeout_flag = \
                    run_solver(solver_path, cnf_file, timeout)
                
                # Write to CSV
                writer.writerow({
                    'instance': instance_name,
                    'solver': solver,
                    'solver_name': SOLVER_NAMES[solver],
                    'result': result,
                    'time_seconds': f'{time:.6f}',
                    'max_recursion_depth': depth,
                    'memory_kb': memory,
                    'num_decisions': decisions,
                    'num_backtracks': backtracks,
                    'timeout': timeout_flag
                })
                
                # Print result
                if result == 'TIMEOUT':
                    print(f"TIMEOUT ({timeout}s)")
                elif result == 'ERROR':
                    print("ERROR")
                else:
                    print(f"{result} ({time:.4f}s, {decisions} decisions, {backtracks} backtracks)")
    
    print("\n" + "=" * 80)
    print(f"Benchmarking complete! Results saved to {output_csv}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <instances_directory> [output.csv] [timeout_seconds]")
        print("\nExample:")
        print("  python benchmark.py ../sat_solver/instances results.csv 60")
        sys.exit(1)
    
    instances_dir = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else f'benchmark_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 180
    
    if not os.path.isdir(instances_dir):
        print(f"Error: Directory '{instances_dir}' not found")
        sys.exit(1)
    
    # Check if solvers are built
    build_dir = 'build'
    if not os.path.isdir(build_dir):
        print(f"Error: Build directory '{build_dir}' not found")
        print("Please run 'make' first to compile all solvers")
        sys.exit(1)
    
    missing_solvers = []
    for solver in SOLVERS:
        solver_path = os.path.join(build_dir, solver)
        if not os.path.exists(solver_path):
            missing_solvers.append(solver)
    
    if missing_solvers:
        print("Warning: The following solvers are not compiled:")
        for solver in missing_solvers:
            print(f"  - {solver}")
        print("\nRun 'make' to compile all solvers")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    benchmark(instances_dir, output_csv, build_dir, timeout)

if __name__ == '__main__':
    main()
