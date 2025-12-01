// 1. Basic DPLL - No heuristics
#include "../include/base_solver.h"
#include <iostream>

class BasicDPLL : public BaseSolver {
protected:
    int chooseVariable() override {
        // Simply choose first unassigned variable
        for (int var = 1; var <= formula.num_vars; var++) {
            if (assignment.find(var) == assignment.end()) {
                return var;
            }
        }
        return -1;
    }
    
public:
    BasicDPLL(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {}
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    BasicDPLL solver(formula, 60);
    SolverStats stats = solver.solve();
    
    // Output format: SAT,time,depth,memory,decisions,backtracks,timeout
    cout << (stats.satisfiable ? "SAT" : "UNSAT") << ","
         << stats.time_seconds << ","
         << stats.max_recursion_depth << ","
         << stats.memory_kb << ","
         << stats.num_decisions << ","
         << stats.num_backtracks << ","
         << stats.timeout << endl;
    
    return 0;
}
