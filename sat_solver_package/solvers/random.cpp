// 10. DPLL with Random Variable Selection
#include "../include/base_solver.h"
#include <iostream>
#include <vector>
#include <random>

class RandomSolver : public BaseSolver {
private:
    mt19937 rng;
    
protected:
    int chooseVariable() override {
        vector<int> unassigned;
        for (int var = 1; var <= formula.num_vars; var++) {
            if (assignment.find(var) == assignment.end()) {
                unassigned.push_back(var);
            }
        }
        
        if (unassigned.empty()) return -1;
        
        uniform_int_distribution<int> dist(0, unassigned.size() - 1);
        return unassigned[dist(rng)];
    }
    
public:
    RandomSolver(const CNFFormula& f, int timeout = 60) 
        : BaseSolver(f, timeout), rng(42) {}  // Fixed seed for reproducibility
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    RandomSolver solver(formula, 60);
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
