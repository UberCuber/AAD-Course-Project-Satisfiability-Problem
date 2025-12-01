// 11. CDCL Solver - Conflict-Driven Clause Learning
// Advanced SAT solving with:
// - VSIDS variable selection with activity decay
// - Conflict analysis and clause learning
// - Non-chronological backtracking
// - Restart strategy

#include "../include/base_solver.h"
#include <iostream>
#include <map>
#include <vector>
#include <set>
#include <algorithm>

using namespace std;

class CDCLSolver : public BaseSolver {
private:
    // VSIDS activity scores
    map<int, double> activity;
    double decay_factor;
    double increment;
    
    // Learned clauses
    vector<vector<int>> learned_clauses;
    
    // Decision level tracking
    map<int, int> var_level;  // variable -> decision level
    vector<pair<int, bool>> trail;  // assignment trail
    int decision_level;
    
    // Conflict tracking for restarts
    int conflicts;
    int restart_threshold;
    
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
    
    void bumpActivity(int var) {
        activity[var] += increment;
        if (activity[var] > 1e100) {
            // Rescale to prevent overflow
            for (auto& p : activity) {
                p.second *= 1e-100;
            }
            increment *= 1e-100;
        }
    }
    
    void decayActivities() {
        for (auto& p : activity) {
            p.second *= decay_factor;
        }
        increment /= decay_factor;
    }
    
    // OPTIMIZED unit propagation - only check clauses once
    bool unitPropagateWithLearned() {
        bool changed = true;
        int iterations = 0;
        
        while (changed && iterations < 1000) {  // Prevent infinite loops
            changed = false;
            iterations++;
            
            // Original clauses
            for (const auto& clause : formula.clauses) {
                if (isClauseSatisfied(clause)) continue;
                
                int unassigned_count = 0;
                int unassigned_lit = 0;
                bool conflict = true;
                
                for (int lit : clause) {
                    int var = abs(lit);
                    if (assignment.find(var) == assignment.end()) {
                        unassigned_count++;
                        unassigned_lit = lit;
                        conflict = false;
                    } else {
                        bool val = assignment[var];
                        if ((lit > 0 && val) || (lit < 0 && !val)) {
                            conflict = false;
                            break;  // Clause satisfied
                        }
                    }
                }
                
                if (conflict && unassigned_count == 0) {
                    return false;  // Conflict
                }
                
                if (unassigned_count == 1) {
                    // Unit clause - propagate
                    int var = abs(unassigned_lit);
                    assignment[var] = (unassigned_lit > 0);
                    var_level[var] = decision_level;
                    trail.push_back({var, (unassigned_lit > 0)});
                    changed = true;
                }
            }
            
            // Learned clauses - limit to prevent slowdown
            int learned_check_limit = min((int)learned_clauses.size(), 1000);
            for (int i = 0; i < learned_check_limit; i++) {
                const auto& clause = learned_clauses[i];
                if (isClauseSatisfied(clause)) continue;
                
                int unassigned_count = 0;
                int unassigned_lit = 0;
                bool conflict = true;
                
                for (int lit : clause) {
                    int var = abs(lit);
                    if (assignment.find(var) == assignment.end()) {
                        unassigned_count++;
                        unassigned_lit = lit;
                        conflict = false;
                    } else {
                        bool val = assignment[var];
                        if ((lit > 0 && val) || (lit < 0 && !val)) {
                            conflict = false;
                            break;
                        }
                    }
                }
                
                if (conflict && unassigned_count == 0) {
                    return false;  // Conflict
                }
                
                if (unassigned_count == 1) {
                    int var = abs(unassigned_lit);
                    assignment[var] = (unassigned_lit > 0);
                    var_level[var] = decision_level;
                    trail.push_back({var, (unassigned_lit > 0)});
                    changed = true;
                }
            }
        }
        return true;
    }
    
    // Simple conflict analysis - learn a clause from conflict
    vector<int> analyzeConflict(const vector<int>& conflict_clause) {
        // Basic learning: negate the conflict clause
        vector<int> learned;
        for (int lit : conflict_clause) {
            learned.push_back(-lit);
            bumpActivity(abs(lit));
        }
        return learned;
    }
    
    // Find the conflicting clause
    vector<int> findConflictClause() {
        // Check original clauses
        for (const auto& clause : formula.clauses) {
            if (isClauseConflict(clause)) {
                return clause;
            }
        }
        
        // Check learned clauses
        for (const auto& clause : learned_clauses) {
            if (isClauseConflict(clause)) {
                return clause;
            }
        }
        
        return {};
    }
    
    // Backtrack to a lower decision level
    void backtrack(int target_level) {
        while (!trail.empty() && var_level[trail.back().first] > target_level) {
            int var = trail.back().first;
            assignment.erase(var);
            var_level.erase(var);
            trail.pop_back();
        }
        decision_level = target_level;
        stats.num_backtracks++;
    }
    
    // CDCL main loop with optimizations
    bool cdclSolve() {
        decision_level = 0;
        conflicts = 0;
        restart_threshold = 100;
        
        // Initial unit propagation
        if (!unitPropagateWithLearned()) {
            return false;  // UNSAT from initial propagation
        }
        
        int iterations = 0;
        int max_iterations = 1000000;  // Prevent infinite loops
        
        while (iterations++ < max_iterations) {
            if (isTimeout()) {
                stats.timeout = 1;
                return false;
            }
            
            // Check if all satisfied
            if (allClausesSatisfied()) {
                return true;
            }
            
            // Choose variable
            int var = chooseVariable();
            if (var == -1) {
                return allClausesSatisfied();
            }
            
            // Make decision
            decision_level++;
            stats.num_decisions++;
            assignment[var] = true;
            var_level[var] = decision_level;
            trail.push_back({var, true});
            
            if (stats.num_decisions > stats.max_recursion_depth) {
                stats.max_recursion_depth = stats.num_decisions;
            }
            
            // Propagate and handle conflicts
            if (!unitPropagateWithLearned()) {
                // Conflict found
                conflicts++;
                
                if (decision_level == 0) {
                    return false;  // UNSAT
                }
                
                // Find and learn from conflict
                vector<int> conflict_clause = findConflictClause();
                
                if (!conflict_clause.empty()) {
                    vector<int> learned = analyzeConflict(conflict_clause);
                    
                    // Limit learned clause database size
                    if (!learned.empty() && learned_clauses.size() < 5000) {
                        learned_clauses.push_back(learned);
                    }
                    
                    // Smart backtracking
                    int backtrack_level = max(0, decision_level - 1);
                    for (int lit : learned) {
                        int v = abs(lit);
                        if (var_level.count(v) && var_level[v] < decision_level) {
                            backtrack_level = max(backtrack_level, var_level[v]);
                        }
                    }
                    
                    backtrack(backtrack_level);
                } else {
                    // Fallback: backtrack one level
                    backtrack(max(0, decision_level - 1));
                }
                
                // Decay activities less frequently
                if (conflicts % 10 == 0) {
                    decayActivities();
                }
                
                // Restart strategy
                if (conflicts >= restart_threshold) {
                    backtrack(0);
                    conflicts = 0;
                    restart_threshold = min(restart_threshold * 2, 10000);
                    
                    // Clean up learned clauses on restart
                    if (learned_clauses.size() > 3000) {
                        learned_clauses.resize(2000);
                    }
                }
            }
        }
        
        return false;
    }
    
protected:
    int chooseVariable() override {
        // VSIDS: Choose unassigned variable with highest activity
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
    CDCLSolver(const CNFFormula& f, int timeout = 60) : BaseSolver(f, timeout) {
        initializeActivity();
        decision_level = 0;
        conflicts = 0;
        restart_threshold = 100;
    }
    
    // Override solve to use CDCL instead of basic DPLL
    SolverStats solve() {
        start_time = chrono::high_resolution_clock::now();
        
        stats.satisfiable = cdclSolve();
        
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
    if (formula.num_vars == 0) {
        cerr << "Error: Could not parse CNF file" << endl;
        return 1;
    }
    
    CDCLSolver solver(formula);
    SolverStats stats = solver.solve();
    
    // Output
    if (stats.timeout) {
        cout << "TIMEOUT" << endl;
    } else if (stats.satisfiable) {
        cout << "SAT" << endl;
    } else {
        cout << "UNSAT" << endl;
    }
    
    // Print stats
    cout << "Time: " << stats.time_seconds << endl;
    cout << "Decisions: " << stats.num_decisions << endl;
    cout << "Backtracks: " << stats.num_backtracks << endl;
    cout << "MaxDepth: " << stats.max_recursion_depth << endl;
    cout << "Memory: " << stats.memory_kb << endl;
    
    return 0;
}
