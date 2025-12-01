#!/bin/bash
#
# SAT Solver Benchmark Automation Script
# This script builds all solvers, runs benchmarks on UF20/UF50/UF100, and generates all plots
#

set -e  # Exit on error

echo "======================================"
echo "  SAT Solver Benchmark Automation"
echo "======================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
TIMEOUT=180
NUM_INSTANCES=200

echo "[1/6] Building C++ solvers..."
cd solvers
make clean
make all
cd ..
echo "  ✓ C++ solvers built successfully"
echo ""

echo "[2/6] Creating results directory..."
mkdir -p results/plots/individual_time
mkdir -p results/plots/individual_memory
mkdir -p results/plots/advanced
echo "  ✓ Results directories created"
echo ""

echo "[3/6] Running UF20 benchmark (200 instances, timeout ${TIMEOUT}s)..."
python3 benchmarking/benchmark.py datasets/uf20 results/uf20_benchmark.csv ${TIMEOUT}
echo "  ✓ UF20 benchmark complete"
echo ""

echo "[4/6] Running UF50 benchmark (200 instances, timeout ${TIMEOUT}s)..."
python3 benchmarking/benchmark.py datasets/uf50 results/uf50_benchmark.csv ${TIMEOUT}
echo "  ✓ UF50 benchmark complete"
echo ""

echo "[5/6] Running UF100 benchmark (200 instances, timeout ${TIMEOUT}s)..."
python3 benchmarking/benchmark.py datasets/uf100 results/uf100_benchmark.csv ${TIMEOUT}
echo "  ✓ UF100 benchmark complete"
echo ""

echo "[6/6] Generating all plots..."
echo "  - Core comparative plots (8 plots)..."
python3 plotting/generate_plots.py
echo "  - Individual solver plots (22 plots)..."
python3 plotting/generate_individual_plots.py
echo "  - Advanced analytical plots (10 plots)..."
python3 plotting/generate_advanced_plots.py
echo "  ✓ All plots generated"
echo ""

echo "======================================"
echo "  Benchmark Complete!"
echo "======================================"
echo ""
echo "Results location:"
echo "  - CSV data: results/*.csv"
echo "  - Plots: results/plots/"
echo ""
echo "Summary statistics:"
wc -l results/*.csv
echo ""
echo "Plot inventory:"
echo "  Core plots: $(ls results/plots/*.png 2>/dev/null | wc -l)"
echo "  Individual time: $(ls results/plots/individual_time/*.png 2>/dev/null | wc -l)"
echo "  Individual memory: $(ls results/plots/individual_memory/*.png 2>/dev/null | wc -l)"
echo "  Advanced: $(ls results/plots/advanced/*.png 2>/dev/null | wc -l)"
echo ""
echo "Total execution time: ${SECONDS}s"
