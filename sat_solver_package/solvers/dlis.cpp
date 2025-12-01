// 4. DPLL with DLIS Heuristic (Dynamic Largest Individual Sum)
#include "../include/base_solver.h"
#include <iostream>
#include <map>

class DLISSolver : public BaseSolver {
protected:
    int chooseVariable() override {
        map<int, int> literal_count;
        
        // Count occurrences in unsatisfied clauses
        for (const auto& clause : formula.clauses) {
            if (isClauseSatisfied(clause)) continue;
            
            vector<int> unassigned = getUnassignedLiterals(clause);
            for (int lit : unassigned) {
                literal_count[lit]++;
            }
        }
        
        if (literal_count.empty()) {
            // No unsatisfied clauses with unassigned vars
            for (int var = 1; var <= formula.num_vars; var++) {
                if (assignment.find(var) == assignment.end()) {
                    return var;
                }
            }
            return -1;
        }
        
        // Find literal with max count
        int best_lit = 0;
        int best_count = 0;
        for (const auto& p : literal_count) {
            if (p.second > best_count) {
                best_count = p.second;
                best_lit = p.first;
            }
        }
        
        return abs(best_lit);
    }
    
public:
    DLISSolver(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {}
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    DLISSolver solver(formula, 60);
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
