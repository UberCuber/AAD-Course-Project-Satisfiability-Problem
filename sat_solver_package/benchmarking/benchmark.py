#!/usr/bin/env python3
"""
SAT Solver Benchmarking Script

This script benchmarks multiple SAT solver implementations on a directory of CNF instances.
It runs each solver on each instance, measures performance metrics, and outputs results to CSV.

Author: Advanced Algorithm Design Course Project
Date: December 2025
"""

import os
import sys
import csv
import subprocess
import glob
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict

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

def run_solver(solver_path: str, cnf_file: str, timeout: int = 180) -> Tuple[str, float, int, int, int, int, int]:
    """
    Execute a single SAT solver on a CNF instance and parse its output.
    
    This function runs a compiled SAT solver binary on a CNF file with a timeout.
    It handles different command-line interfaces for CDCL vs DPLL solvers and
    parses the standardized output format.
    
    Args:
        solver_path (str): Absolute or relative path to the compiled solver binary
        cnf_file (str): Path to the CNF instance file
        timeout (int): Maximum execution time in seconds (default: 180)
    
    Returns:
        Tuple[str, float, int, int, int, int, int]: A 7-tuple containing:
            - result (str): 'SAT', 'UNSAT', 'TIMEOUT', or 'ERROR'
            - time (float): Execution time in seconds
            - depth (int): Maximum recursion depth
            - memory (int): Peak memory usage in kilobytes
            - decisions (int): Number of branching decisions made
            - backtracks (int): Number of backtrack operations
            - timeout_flag (int): 1 if timeout occurred, 0 otherwise
    
    Output Format:
        Solvers must output: SAT,time,depth,memory,decisions,backtracks,timeout
        Example: SAT,0.0012,15,0,87,23,0
    
    Raises:
        subprocess.TimeoutExpired: If execution exceeds timeout limit
        Exception: For any other runtime errors
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

def benchmark(instances_dir: str, output_csv: str, build_dir: str = 'build', timeout: int = 180) -> None:
    """
    Benchmark all compiled SAT solvers on all CNF instances in a directory.
    
    This function orchestrates the complete benchmarking process:
    1. Discovers all .cnf files in the instances directory
    2. Iterates through all solver binaries
    3. Runs each solver on each instance with timeout
    4. Writes performance metrics to a CSV file
    
    The function provides real-time progress feedback and handles missing binaries gracefully.
    
    Args:
        instances_dir (str): Directory containing .cnf instance files
        output_csv (str): Output CSV file path for benchmark results
        build_dir (str): Directory containing compiled solver binaries (default: 'build')
        timeout (int): Per-instance timeout in seconds (default: 180)
    
    Returns:
        None: Results are written to output_csv file
    
    CSV Output Format:
        Columns: instance, solver, solver_name, result, time_seconds, 
                max_recursion_depth, memory_kb, num_decisions, num_backtracks, timeout
    
    Example:
        benchmark('datasets/uf20', 'results/uf20_bench.csv', timeout=60)
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

def main() -> None:
    """
    Main entry point for the benchmarking script with command-line interface.
    
    Parses command-line arguments, validates inputs, checks for compiled solvers,
    and initiates the benchmarking process.
    
    Command-Line Usage:
        python benchmark.py <instances_dir> [output.csv] [timeout_seconds]
    
    Arguments:
        instances_dir (required): Directory containing CNF instance files
        output.csv (optional): Output CSV filename (default: benchmark_results_TIMESTAMP.csv)
        timeout_seconds (optional): Timeout per instance in seconds (default: 180)
    
    Examples:
        python benchmark.py datasets/uf20
        python benchmark.py datasets/uf50 results/uf50_bench.csv 120
        python benchmark.py ../instances output.csv 60
    
    Exit Codes:
        0: Success
        1: Error (missing directory, no solvers compiled, user cancelled)
    
    Pre-requisites:
        - Solvers must be compiled in the 'build/' directory
        - CNF files must have .cnf extension
        - Python 3.9+ with standard library
    """
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
