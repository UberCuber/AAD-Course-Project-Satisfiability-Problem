// 6. DPLL with JW Heuristic (Jeroslow-Wang)
#include "../include/base_solver.h"
#include <iostream>
#include <map>
#include <cmath>

class JWSolver : public BaseSolver {
protected:
    int chooseVariable() override {
        map<int, double> scores;
        
        // Calculate JW scores
        for (const auto& clause : formula.clauses) {
            if (isClauseSatisfied(clause)) continue;
            
            vector<int> unassigned = getUnassignedLiterals(clause);
            if (unassigned.empty()) continue;
            
            double weight = pow(2.0, -(double)unassigned.size());
            for (int lit : unassigned) {
                int var = abs(lit);
                scores[var] += weight;
            }
        }
        
        if (scores.empty()) {
            for (int var = 1; var <= formula.num_vars; var++) {
                if (assignment.find(var) == assignment.end()) {
                    return var;
                }
            }
            return -1;
        }
        
        // Return variable with highest score
        int best_var = -1;
        double best_score = -1.0;
        for (const auto& p : scores) {
            if (p.second > best_score) {
                best_score = p.second;
                best_var = p.first;
            }
        }
        
        return best_var;
    }
    
public:
    JWSolver(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {}
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <cnf_file>" << endl;
        return 1;
    }
    
    CNFFormula formula = CNFParser::parse(argv[1]);
    JWSolver solver(formula, 60);
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
