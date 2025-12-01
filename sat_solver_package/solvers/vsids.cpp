// 3. DPLL with VSIDS Heuristic
#include "../include/base_solver.h"
#include <iostream>
#include <map>

class VSIDSSolver : public BaseSolver {
private:
    map<int, double> activity;
    double decay_factor;
    double increment;
    
    void initializeActivity() {
        increment = 1.0;
        decay_factor = 0.95;
        
        // Initialize all variables to 0
        for (int var = 1; var <= formula.num_vars; var++) {
            activity[var] = 0.0;
        }
        
        // Give initial scores based on occurrence
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
    
public:
    VSIDSSolver(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {
        initializeActivity();
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    VSIDSSolver solver(formula, 60);
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
