# benchmark_dpll.py
# Benchmarks all .cnf files using DPLL solver
# Logs: SAT/UNSAT, metrics, avg/median/stdev times

import csv
import os
import time
import statistics
from dpll_basic import parse_dimacs, dpll, stats


def run_dpll_on_file(file_path, runs=20):
    clauses, _ = parse_dimacs(file_path)
    times = []
    for _ in range(runs):
        # Reset global stats each run
        for key in stats:
            stats[key] = 0

        start = time.perf_counter()
        result = dpll(clauses, {})
        end = time.perf_counter()

        times.append(end - start)

    avg_time = sum(times) / len(times)
    median_time = statistics.median(times)
    stdev_time = statistics.stdev(times) if len(times) > 1 else 0.0
    outcome = "SAT" if result is not None else "UNSAT"

    return {
        "file": os.path.basename(file_path),
        "recursive_calls": stats["calls"],
        "unit_props": stats["unit_props"],
        "pure_literals": stats["pure_literals"],
        "backtracks": stats["backtracks"],
        "avg_time_sec": round(avg_time, 6),
        "median_time_sec": round(median_time, 6),
        "stdev_time_sec": round(stdev_time, 6),
        "result": outcome
    }


def benchmark_folder(folder_path="dat/unsat", output_csv="dpll_results_unsat.csv"):
    os.makedirs(folder_path, exist_ok=True)
    cnf_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".cnf")])
    if not cnf_files:
        print(f"No .cnf files found in '{folder_path}'. Add test CNFs there.")
        return

    print(f"\nRunning DPLL benchmark on {len(cnf_files)} CNF files...\n")
    results = []
    for f in cnf_files:
        path = os.path.join(folder_path, f)
        print(f"→ Solving {f} ...")
        result = run_dpll_on_file(path)
        results.append(result)

    # Save results to CSV
    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Print summary
    print("\n===== Benchmark Summary =====")
    for r in results:
        print(
            f"{r['file']:22s} | {r['result']:5s} | "
            f"Calls: {r['recursive_calls']:5d} | "
            f"Backtracks: {r['backtracks']:4d} | "
            f"Avg: {r['avg_time_sec']:.6f}s | "
            f"Median: {r['median_time_sec']:.6f}s | "
            f"σ: {r['stdev_time_sec']:.6f}s"
        )
    print(f"\nResults saved to {output_csv}")
    print("=============================\n")


if __name__ == "__main__":
    benchmark_folder()
