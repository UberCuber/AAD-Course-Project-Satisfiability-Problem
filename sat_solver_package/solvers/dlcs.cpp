// 7. DPLL with DLCS Heuristic (Dynamic Largest Combined Sum)
#include "../include/base_solver.h"
#include <iostream>
#include <map>

class DLCSSolver : public BaseSolver {
protected:
    int chooseVariable() override {
        map<int, int> var_count;
        
        // Count both positive and negative occurrences combined
        for (const auto& clause : formula.clauses) {
            if (isClauseSatisfied(clause)) continue;
            
            vector<int> unassigned = getUnassignedLiterals(clause);
            for (int lit : unassigned) {
                int var = abs(lit);
                var_count[var]++;
            }
        }
        
        if (var_count.empty()) {
            for (int var = 1; var <= formula.num_vars; var++) {
                if (assignment.find(var) == assignment.end()) {
                    return var;
                }
            }
            return -1;
        }
        
        // Return variable with max combined count
        int best_var = -1;
        int best_count = 0;
        for (const auto& p : var_count) {
            if (p.second > best_count) {
                best_count = p.second;
                best_var = p.first;
            }
        }
        
        return best_var;
    }
    
public:
    DLCSSolver(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {}
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    DLCSSolver solver(formula, 60);
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
