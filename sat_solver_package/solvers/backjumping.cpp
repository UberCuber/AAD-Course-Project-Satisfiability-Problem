// 9. DPLL with Backjumping (Non-chronological backtracking)
#include "../include/base_solver.h"
#include <iostream>
#include <map>
#include <set>

class BackjumpingSolver : public BaseSolver {
private:
    map<int, set<int>> decision_level;
    int current_level;
    
    // Find conflict level
    int analyzeConflict(const vector<int>& conflict_clause) {
        int jump_level = 0;
        for (int lit : conflict_clause) {
            int var = abs(lit);
            if (assignment.find(var) != assignment.end()) {
                for (const auto& p : decision_level) {
                    if (p.second.count(var) > 0) {
                        if (p.first < current_level && p.first > jump_level) {
                            jump_level = p.first;
                        }
                    }
                }
            }
        }
        return jump_level;
    }
    
    // Find conflicting clause
    vector<int> findConflictClause() {
        for (const auto& clause : formula.clauses) {
            if (isClauseConflict(clause)) {
                return clause;
            }
        }
        return {};
    }
    
    bool dpll_backjump(int level) {
        current_level = level;
        current_depth = level;
        
        if (level > stats.max_recursion_depth) {
            stats.max_recursion_depth = level;
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
        decision_level[level].insert(var);
        
        // Try true
        map<int, bool> saved_assignment = assignment;
        assignment[var] = true;
        
        if (dpll_backjump(level + 1)) {
            return true;
        }
        
        // Check for conflict and backjump
        vector<int> conflict = findConflictClause();
        if (!conflict.empty()) {
            int jump_level = analyzeConflict(conflict);
            if (jump_level < level - 1) {
                // Backjump to earlier level
                assignment = saved_assignment;
                stats.num_backtracks++;
                return false;
            }
        }
        
        // Try false
        assignment = saved_assignment;
        assignment[var] = false;
        
        if (dpll_backjump(level + 1)) {
            return true;
        }
        
        assignment = saved_assignment;
        decision_level[level].erase(var);
        stats.num_backtracks++;
        return false;
    }
    
protected:
    int chooseVariable() override {
        for (int var = 1; var <= formula.num_vars; var++) {
            if (assignment.find(var) == assignment.end()) {
                return var;
            }
        }
        return -1;
    }
    
public:
    BackjumpingSolver(const CNFFormula& f, int timeout = 60) 
        : BaseSolver(f, timeout), current_level(0) {}
    
    SolverStats solve() {
        start_time = chrono::high_resolution_clock::now();
        
        stats.satisfiable = dpll_backjump(0);
        
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
    BackjumpingSolver solver(formula, 60);
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
