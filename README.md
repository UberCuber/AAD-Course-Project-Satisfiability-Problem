# SAT Solver Project

This repository contains a comprehensive implementation of SAT solvers, benchmarking utilities, and visualization tools. It includes various SAT solving techniques, from basic DPLL to advanced CDCL, and additional modules for hardware verification, package dependency resolution, and Sudoku solving.

---

## 📂 Project Structure

```
FINAL/
├── AAD-Course-Project-Satisfiability-Problem/
│   ├── WALKSAT/                     # WalkSAT solver and benchmarks
│   │   ├── walksat.py
│   │   └── benchmark.py
│   ├── Sudoku-solver/               # Sudoku solver using SAT
│   │   └── sudoku_solver_mrv.py
│   ├── sudoku_to_cnf_encoder/       # Sudoku to CNF encoder and result plotting
│   │   ├── sudoku_encoder.py
│   │   ├── plot_result.py
│   │   └── compare.py
│   ├── Set-Theory-SAT-Solver/       # Set theory-based SAT solver
│   │   ├── set_based_sat_solver.cpp
│   │   ├── plot_enhanced_time.py
│   │   ├── requirements.txt
│   │   └── Makefile
│   ├── sat_solver_package/          # Core SAT solvers and utilities
│   │   ├── solvers/                 # C++ and Python solvers
│   │   │   ├── *.cpp
│   │   │   ├── *.py
│   │   │   └── Makefile
│   │   ├── plotting/                # Plot generation scripts
│   │   │   ├── generate_plots.py
│   │   │   ├── generate_individual_plots.py
│   │   │   └── generate_advanced_plots.py
│   │   ├── benchmarking/            # Benchmarking utilities
│   │   │   └── benchmark.py
│   │   └── requirements.txt
│   ├── Package_Dependency/          # Package dependency resolution
│   │   ├── repository.json
│   │   └── package_manager.py
│   ├── Hardware_verification/       # Hardware equivalence checker
│   │   └── hardware_verify.py
│   ├── DPLL-SAT-solver/             # Basic DPLL SAT solver
│   │   └── dpll_basic.py
│   ├── CDCL_SAT_Solver/             # CDCL SAT solver
│   │   ├── cdcl_solver.cpp
│   │   ├── verifier.cpp
│   │   └── Makefile
│   └── README.md                    # This file
```

---

## 🛠️ Dependencies

### System Requirements
- **Operating System**: macOS, Linux, or Windows (WSL)
- **C++ Compiler**: GCC 7+ or Clang 5+ (for C++17 support)
- **Python**: 3.9 or higher

### Python Libraries
Install the required Python libraries using the following commands:

```bash
pip install -r sat_solver_package/requirements.txt
pip install -r Set-Theory-SAT-Solver/requirements.txt
```

Alternatively, install manually:
```bash
pip install pandas numpy matplotlib seaborn psutil scipy
```

---

## 🚀 How to Run

### 1. **WalkSAT Solver**
- **Files**: `WALKSAT/walksat.py`, `WALKSAT/benchmark.py`
- **Run**:
  ```bash
  python WALKSAT/walksat.py
  python WALKSAT/benchmark.py
  ```

### 2. **Sudoku Solver**
- **Files**: `Sudoku-solver/sudoku_solver_mrv.py`
- **Run**:
  ```bash
  python Sudoku-solver/sudoku_solver_mrv.py
  ```

### 3. **Sudoku to CNF Encoder**
- **Files**: `sudoku_to_cnf_encoder/sudoku_encoder.py`, `sudoku_to_cnf_encoder/plot_result.py`, `sudoku_to_cnf_encoder/compare.py`
- **Run**:
  ```bash
  python sudoku_to_cnf_encoder/sudoku_encoder.py
  python sudoku_to_cnf_encoder/plot_result.py
  python sudoku_to_cnf_encoder/compare.py
  ```

### 4. **Set Theory SAT Solver**
- **Files**: `Set-Theory-SAT-Solver/set_based_sat_solver.cpp`, `Set-Theory-SAT-Solver/plot_enhanced_time.py`
- **Build**:
  ```bash
  cd Set-Theory-SAT-Solver
  make
  ```
- **Run**:
  ```bash
  ./set_based_sat_solver
  python plot_enhanced_time.py
  ```

### 5. **SAT Solver Package**
- **Files**: `sat_solver_package/solvers/`, `sat_solver_package/plotting/`, `sat_solver_package/benchmarking/`
- **Build**:
  ```bash
  cd sat_solver_package/solvers
  make all
  ```
- **Run Benchmarks**:
  ```bash
  python sat_solver_package/benchmarking/benchmark.py <instances_dir> <output.csv> <timeout_seconds>
  ```
- **Generate Plots**:
  ```bash
  python sat_solver_package/plotting/generate_plots.py
  python sat_solver_package/plotting/generate_individual_plots.py
  python sat_solver_package/plotting/generate_advanced_plots.py
  ```

### 6. **Package Dependency Manager**
- **Files**: `Package_Dependency/package_manager.py`, `Package_Dependency/repository.json`
- **Run**:
  ```bash
  python Package_Dependency/package_manager.py Package_Dependency/repository.json <package_names>
  ```

### 7. **Hardware Verification**
- **Files**: `Hardware_verification/hardware_verify.py`
- **Run**:
  ```bash
  python Hardware_verification/hardware_verify.py <circuits.json> <scenario_name>
  ```

### 8. **DPLL SAT Solver**
- **Files**: `DPLL-SAT-solver/dpll_basic.py`
- **Run**:
  ```bash
  python DPLL-SAT-solver/dpll_basic.py
  ```

### 9. **CDCL SAT Solver**
- **Files**: `CDCL_SAT_Solver/cdcl_solver.cpp`, `CDCL_SAT_Solver/verifier.cpp`
- **Build**:
  ```bash
  cd CDCL_SAT_Solver
  make
  ```
- **Run**:
  ```bash
  ./cdcl_solver <to_log> <decider> <restarter> <inputfile>
  ./verifier <inputfile> <assignmentfile>
  ```

---

## 📊 Visualization

### Core Plots
- Time and memory usage per solver
- Decision and backtrack metrics
- Success rates and scalability analysis

### Advanced Plots
- Backtrack efficiency
- Decision quality
- Solver heatmaps
- Pareto frontiers

---

## 🧪 Testing and Benchmarking

### Run All Benchmarks
```bash
cd sat_solver_package
python benchmarking/benchmark.py datasets/uf20 results/uf20_benchmark.csv 180
python benchmarking/benchmark.py datasets/uf50 results/uf50_benchmark.csv 180
python benchmarking/benchmark.py datasets/uf100 results/uf100_benchmark.csv 180
```

### Generate All Plots
```bash
python plotting/generate_plots.py
python plotting/generate_individual_plots.py
python plotting/generate_advanced_plots.py
```

---

## 🛠️ Troubleshooting

### Build Errors
- Ensure C++17 support: `g++ --version` (GCC 7+ or Clang 5+ required)
- macOS: Install Xcode Command Line Tools: `xcode-select --install`

### Python Errors
- Missing libraries: `pip install -r requirements.txt`
- Encoding issues: Ensure Python 3.9+

---

**Last Updated**: October 2023  
**Version**: 1.1  
**Total Lines of Code**: ~6,000 (solvers + utilities + benchmarks)

--- 
Team Members
- [Mahek Desai]
- [Krrish Gupta]
- [Laveena Jain]
- [Sarah Roomi]
- [Shravan Kannan]
