# SAT Solver Benchmark Package

A comprehensive benchmarking and analysis package for Boolean Satisfiability (SAT) solvers, featuring 10+ solver variants from basic DPLL to state-of-the-art CDCL with extensive visualization.

## 📋 Repository Requirements Compliance

This repository meets all course requirements:

✅ **README.md**: Comprehensive guide for compilation, dependencies, and execution  
✅ **Well-Commented Code**: All C++ and Python files include detailed comments  
✅ **Test/Benchmarking Harness**: Complete benchmarking scripts (`benchmark.py`, `run_full_benchmark.sh`)  
✅ **Docstrings**: All Python functions have type-annotated docstrings  
✅ **Modularized Code**: Each algorithm in separate file with helper utilities  

**See [COMPLIANCE.md](COMPLIANCE.md) for detailed evidence of all requirements.**

## Package Structure

```
sat_solver_package/
├── datasets/              # Benchmark instances
│   ├── uf20/             # 200 instances, 20 variables, 91 clauses
│   ├── uf50/             # 200 instances, 50 variables, 218 clauses
│   └── uf100/            # 200 instances, 100 variables, 430 clauses
├── solvers/              # Solver implementations
│   ├── *.cpp             # C++ solver sources (11 variants)
│   ├── *.py              # Python DPLL implementations
│   └── Makefile          # Build configuration
├── benchmarking/         # Benchmarking utilities
│   └── benchmark.py      # Main benchmarking script
├── plotting/             # Visualization scripts
│   ├── generate_plots.py              # Core 8 comparative plots
│   ├── generate_individual_plots.py   # Per-solver time/memory
│   └── generate_advanced_plots.py     # Advanced analytical plots
├── results/              # Output directory (created on run)
│   ├── *.csv             # Benchmark data
│   └── plots/            # Generated visualizations
├── run_full_benchmark.sh # ONE-CLICK AUTOMATION SCRIPT
└── README.md             # This file
```

## Solver Variants

### C++ Implementations (Optimized with -O3)
1. **basic_dpll** - Pure chronological backtracking
2. **unit_prop** - DPLL + Unit Propagation
3. **vsids** - DPLL + VSIDS variable selection
4. **dlis** - DPLL + Dynamic Largest Individual Sum
5. **mom** - DPLL + Maximum Occurrences in Minimum clauses
6. **jw** - DPLL + Jeroslow-Wang weighting
7. **dlcs** - DPLL + Dynamic Largest Combined Sum
8. **phase_saving** - DPLL + Phase saving heuristic
9. **backjumping** - DPLL + Non-chronological backtracking
10. **random** - DPLL + Random variable selection
11. **cdcl_solver** - Full CDCL with 1-UIP, watched literals, VSIDS, restarts

### Python Implementations
- All DPLL variants (basic, unit propagation, pure literal, heuristics)
- CDCL solver with clause learning

## Quick Start

### Prerequisites
- **C++ Compiler**: g++ or clang++ with C++17 support
- **Python**: 3.9+
- **Python Libraries**: Install from requirements.txt
  ```bash
  cd sat_solver_package
  pip install -r requirements.txt
  ```
  
  Or install manually:
  ```bash
  pip install pandas numpy matplotlib seaborn psutil scipy
  ```

### One-Command Full Benchmark

Run everything (builds solvers, benchmarks 3 datasets, generates 40+ plots):

```bash
cd sat_solver_package
./run_full_benchmark.sh
```

**Expected runtime**: ~30-60 minutes depending on hardware (timeout per instance: 180s)

**Output**:
- `results/uf20_benchmark.csv` (2,200 runs)
- `results/uf50_benchmark.csv` (2,200 runs)
- `results/uf100_benchmark.csv` (2,200 runs)
- `results/plots/` (42 plots total)

## 🔧 How to Compile and Install

### Step 1: Install Dependencies

#### System Requirements
- **Operating System**: macOS, Linux, or Windows (WSL)
- **C++ Compiler**: 
  - GCC 7+ (for C++17 support)
  - Clang 5+ (alternative)
  - macOS: Install Xcode Command Line Tools
    ```bash
    xcode-select --install
    ```
- **Python**: 3.9 or higher

#### Python Dependencies

```bash
cd sat_solver_package
pip install -r requirements.txt
```

This installs:
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `matplotlib` - Plotting
- `seaborn` - Statistical visualization
- `psutil` - System monitoring
- `scipy` - Scientific computing

### Step 2: Build C++ Solvers

Navigate to the package directory and build all solvers:

```bash
cd sat_solver_package
make -C solvers all
```

Or use the Makefile in the root directory:

```bash
cd sat_solver_package
make all
```

**What this does:**
- Compiles 11 C++ solver variants
- Creates `build/` directory
- Generates optimized binaries with `-O3` flag
- Outputs: `build/basic_dpll`, `build/vsids`, `build/cdcl_solver`, etc.

#### Build Individual Solvers

```bash
cd sat_solver_package
make -C solvers vsids      # Build only VSIDS
make -C solvers cdcl_solver # Build only CDCL
```

#### Clean and Rebuild

```bash
make -C solvers clean       # Remove all binaries
make -C solvers rebuild     # Clean + build all
```

### Step 3: Verify Installation

Test a single solver:

```bash
cd sat_solver_package
./solvers/build/vsids datasets/uf20/uf20-01.cnf
```

Expected output (comma-separated):
```
SAT,0.0012,15,0,87,23,0
# Format: result,time_seconds,max_depth,memory_kb,decisions,backtracks,timeout
```

## Manual Execution

If you prefer step-by-step control:

### 1. Build Solvers
```bash
cd solvers
make clean
make all
cd ..
```

### 2. Run Benchmarks
```bash
# Create results directory
mkdir -p results/plots/{individual_time,individual_memory,advanced}

# Benchmark UF20 (200 instances, 180s timeout)
python3 benchmarking/benchmark.py datasets/uf20 results/uf20_benchmark.csv 180

# Benchmark UF50
python3 benchmarking/benchmark.py datasets/uf50 results/uf50_benchmark.csv 180

# Benchmark UF100
python3 benchmarking/benchmark.py datasets/uf100 results/uf100_benchmark.csv 180
```

### 3. Generate Plots
```bash
# Core comparative plots (8 plots)
python3 plotting/generate_plots.py

# Individual solver plots (22 plots: 11 time + 11 memory)
python3 plotting/generate_individual_plots.py

# Advanced analytical plots (10 plots)
python3 plotting/generate_advanced_plots.py
```

## Generated Visualizations

### Core Plots (8)
1. **01_time_per_heuristic.png** - Time across datasets per solver
2. **02_memory_per_heuristic.png** - Memory usage per solver (excludes CDCL)
3. **03_time_comparison_per_dataset.png** - Median runtime bars per dataset
4. **04_memory_comparison_per_dataset.png** - Memory usage bars
5. **05_decisions_scatter.png** - Decisions vs time scatter
6. **06_time_decisions_correlation.png** - Correlation analysis
7. **07_speedup_relative_to_baseline.png** - Speedup vs basic DPLL
8. **08_success_rate.png** - Success rate (non-timeout) per solver

### Individual Plots (22)
- 11 time progression plots (one per solver)
- 11 memory progression plots (one per solver, CDCL excluded)

### Advanced Plots (10)
- A01: Backtrack efficiency
- A02: Decision quality
- A03: Scalability curves
- A04: Performance distribution (violin)
- A05: Solver heatmap
- A06: Efficiency frontier
- A07: Variance analysis
- A08: Correlation matrix
- A09: Winner distribution
- A10: Performance percentiles

## Metrics Collected

### Primary
- **time_seconds** - Wall-clock runtime
- **memory_kb** - Peak resident set size (Python solvers)
- **result** - SAT/UNSAT determination
- **timeout** - Boolean flag (180s limit)

### Algorithmic
- **num_decisions** - Branching decisions
- **num_backtracks** - Conflict-induced reversals
- **recursion_depth** - Maximum search depth (DPLL)

### CDCL-specific
- **learned_clauses** - Number of clauses added
- **restarts** - Number of search resets

## Datasets

**Source**: SATLIB Uniform Random 3-SAT (phase transition instances)

- **UF20**: 20 variables, 91 clauses, clause/variable ratio ≈ 4.26
- **UF50**: 50 variables, 218 clauses
- **UF100**: 100 variables, 430 clauses

**Sampling**: 200 instances randomly selected per dataset

**Total benchmark runs**: 6,600 (200 instances × 3 datasets × 11 solvers)

## Configuration

Edit `run_full_benchmark.sh` to adjust:
- `TIMEOUT` - Per-instance timeout (default: 180s)
- `NUM_INSTANCES` - Instances per dataset (change sampling in datasets/)

## Expected Results

### Typical Performance Hierarchy (UF100)
1. **CDCL** - Fastest, most robust (~0.0007s median)
2. **VSIDS / MOM / JW** - Strong heuristic DPLL (~0.001-0.003s)
3. **Unit Prop** - Solid baseline (~0.005s)
4. **Basic DPLL** - Slowest (~2s+)

### Speedup vs Basic DPLL
- CDCL: ~2,000-3,000×
- Unit Propagation: ~4,000× (due to shallow search)
- Heuristic variants: ~1,000-2,000×

### Success Rates
- CDCL, VSIDS, MOM, JW, Unit Prop: 100% (no timeouts)
- Backjumping (without learning): High failure rate (~89%)

## Troubleshooting

### Build Errors
- Ensure C++17 support: `g++ --version` (need gcc 7+ or clang 5+)
- macOS: Install Xcode Command Line Tools: `xcode-select --install`

### Python Errors
- Missing libraries: `pip install pandas numpy matplotlib seaborn`
- Encoding issues: Ensure Python 3.9+

### Slow Benchmarks
- Reduce timeout: Edit `TIMEOUT` in `run_full_benchmark.sh`
- Sample fewer instances: Replace datasets with smaller subsets

### Missing Plots
- Check `results/plots/` permissions
- Verify all CSV files generated: `ls -lh results/*.csv`
- Re-run plotting scripts individually

## Citation

If you use this benchmark package in research, please cite:

```
SAT Solver Heuristic Analysis Package
Analysis of Variable Selection and Learning in Boolean Satisfiability
Datasets: SATLIB UF20/UF50/UF100
Year: 2025
```

## License

This package is for educational and research purposes. Solver implementations reference classic SAT literature algorithms.

## Contact

For questions or issues, refer to the original project repository or course materials.

---

**Last Updated**: December 2025  
**Version**: 1.0  
**Total Lines of Code**: ~5,000 (solvers + benchmarking + plotting)
