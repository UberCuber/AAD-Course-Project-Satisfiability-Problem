// 8. DPLL with VSIDS + Phase Saving
#include "../include/base_solver.h"
#include <iostream>
#include <map>

class PhaseSavingSolver : public BaseSolver {
private:
    map<int, double> activity;
    map<int, bool> saved_phase;
    double decay_factor;
    double increment;
    
    void initializeActivity() {
        increment = 1.0;
        decay_factor = 0.95;
        
        for (int var = 1; var <= formula.num_vars; var++) {
            activity[var] = 0.0;
            saved_phase[var] = false;  // Default phase
        }
        
        for (const auto& clause : formula.clauses) {
            for (int lit : clause) {
                int var = abs(lit);
                activity[var] += 1.0;
            }
        }
    }
    
protected:
    int chooseVariable() override {
        int best_var = -1;
        double best_score = -1.0;
        
        for (int var = 1; var <= formula.num_vars; var++) {
            if (assignment.find(var) == assignment.end()) {
                if (activity[var] > best_score) {
                    best_score = activity[var];
                    best_var = var;
                }
            }
        }
        
        return best_var;
    }
    
    // Override DPLL to use phase saving
    bool dpll_with_phase(int depth) {
        current_depth = depth;
        if (depth > stats.max_recursion_depth) {
            stats.max_recursion_depth = depth;
        }
        
        if (isTimeout()) {
            stats.timeout = 1;
            return false;
        }
        
        if (!unitPropagate()) {
            stats.num_backtracks++;
            return false;
        }
        
        if (allClausesSatisfied()) {
            return true;
        }
        
        int var = chooseVariable();
        if (var == -1) {
            stats.num_backtracks++;
            return false;
        }
        
        stats.num_decisions++;
        
        // Try saved phase first
        bool phase = saved_phase[var];
        map<int, bool> saved_assignment = assignment;
        assignment[var] = phase;
        
        if (dpll_with_phase(depth + 1)) {
            saved_phase[var] = phase;  // Save successful phase
            return true;
        }
        
        // Try opposite phase
        assignment = saved_assignment;
        assignment[var] = !phase;
        
        if (dpll_with_phase(depth + 1)) {
            saved_phase[var] = !phase;  // Save successful phase
            return true;
        }
        
        assignment = saved_assignment;
        stats.num_backtracks++;
        return false;
    }
    
public:
    PhaseSavingSolver(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {
        initializeActivity();
    }
    
    SolverStats solve() {
        start_time = chrono::high_resolution_clock::now();
        
        stats.satisfiable = dpll_with_phase(0);
        
        auto end_time = chrono::high_resolution_clock::now();
        chrono::duration<double> duration = end_time - start_time;
        stats.time_seconds = duration.count();
        stats.memory_kb = getPeakMemoryKB();
        
        return stats;
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    PhaseSavingSolver solver(formula, 60);
    SolverStats stats = solver.solve();
    
    cout << (stats.satisfiable ? "SAT" : "UNSAT") << ","
         << stats.time_seconds << ","
         << stats.max_recursion_depth << ","
         << stats.memory_kb << ","
         << stats.num_decisions << ","
         << stats.num_backtracks << ","
         << stats.timeout << endl;
    
    return 0;
}
