#ifndef BASE_SOLVER_H
#define BASE_SOLVER_H

#include "cnf_parser.h"
#include <map>
#include <set>
#include <chrono>
#include <algorithm>
#include <sys/resource.h>
#include <unistd.h>

using namespace std;

struct SolverStats {
    double time_seconds;
    int max_recursion_depth;
    long memory_kb;
    int num_decisions;
    int num_backtracks;
    bool satisfiable;
    int timeout;  // 0 = no timeout, 1 = timeout
};

class BaseSolver {
protected:
    CNFFormula formula;
    map<int, bool> assignment;
    SolverStats stats;
    int current_depth;
    chrono::time_point<chrono::high_resolution_clock> start_time;
    int timeout_seconds;
    
    // Track peak memory
    long getPeakMemoryKB() {
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        #ifdef __APPLE__
            return usage.ru_maxrss / 1024;  // macOS reports in bytes
        #else
            return usage.ru_maxrss;  // Linux reports in KB
        #endif
    }
    
    bool isTimeout() {
        auto now = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::seconds>(now - start_time);
        return duration.count() >= timeout_seconds;
    }
    
    // Check if a clause is satisfied under current assignment
    bool isClauseSatisfied(const vector<int>& clause) {
        for (int lit : clause) {
            int var = abs(lit);
            if (assignment.find(var) != assignment.end()) {
                bool val = assignment[var];
                if ((lit > 0 && val) || (lit < 0 && !val)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    // Check if a clause is conflicting under current assignment
    bool isClauseConflict(const vector<int>& clause) {
        for (int lit : clause) {
            int var = abs(lit);
            if (assignment.find(var) == assignment.end()) {
                return false;  // Still has unassigned literal
            }
            bool val = assignment[var];
            if ((lit > 0 && val) || (lit < 0 && !val)) {
                return false;  // At least one literal is true
            }
        }
        return true;  // All literals are false
    }
    
    // Get unassigned literals in a clause
    vector<int> getUnassignedLiterals(const vector<int>& clause) {
        vector<int> unassigned;
        for (int lit : clause) {
            int var = abs(lit);
            if (assignment.find(var) == assignment.end()) {
                unassigned.push_back(lit);
            }
        }
        return unassigned;
    }
    
    // Unit propagation
    bool unitPropagate() {
        bool propagated = true;
        while (propagated) {
            propagated = false;
            for (const auto& clause : formula.clauses) {
                if (isClauseSatisfied(clause)) continue;
                
                vector<int> unassigned = getUnassignedLiterals(clause);
                
                if (unassigned.empty()) {
                    // Conflict
                    return false;
                }
                
                if (unassigned.size() == 1) {
                    // Unit clause
                    int lit = unassigned[0];
                    int var = abs(lit);
                    assignment[var] = (lit > 0);
                    propagated = true;
                }
            }
        }
        return true;
    }
    
    // Check if all clauses are satisfied
    bool allClausesSatisfied() {
        for (const auto& clause : formula.clauses) {
            if (!isClauseSatisfied(clause)) {
                return false;
            }
        }
        return true;
    }
    
    // Virtual function for variable selection (to be overridden)
    virtual int chooseVariable() = 0;
    
    // Main DPLL algorithm
    bool dpll(int depth) {
        current_depth = depth;
        if (depth > stats.max_recursion_depth) {
            stats.max_recursion_depth = depth;
        }
        
        if (isTimeout()) {
            stats.timeout = 1;
            return false;
        }
        
        // Unit propagation
        if (!unitPropagate()) {
            stats.num_backtracks++;
            return false;
        }
        
        // Check if satisfied
        if (allClausesSatisfied()) {
            return true;
        }
        
        // Choose variable
        int var = chooseVariable();
        if (var == -1) {
            // No variable to choose but not satisfied
            stats.num_backtracks++;
            return false;
        }
        
        stats.num_decisions++;
        
        // Try true
        map<int, bool> saved_assignment = assignment;
        assignment[var] = true;
        
        if (dpll(depth + 1)) {
            return true;
        }
        
        // Backtrack and try false
        assignment = saved_assignment;
        assignment[var] = false;
        
        if (dpll(depth + 1)) {
            return true;
        }
        
        // Backtrack
        assignment = saved_assignment;
        stats.num_backtracks++;
        return false;
    }
    
public:
    BaseSolver(const CNFFormula& f, int timeout = 60) 
        : formula(f), current_depth(0), timeout_seconds(timeout) {
        stats.time_seconds = 0;
        stats.max_recursion_depth = 0;
        stats.memory_kb = 0;
        stats.num_decisions = 0;
        stats.num_backtracks = 0;
        stats.satisfiable = false;
        stats.timeout = 0;
    }
    
    virtual ~BaseSolver() {}
    
    SolverStats solve() {
        start_time = chrono::high_resolution_clock::now();
        
        stats.satisfiable = dpll(0);
        
        auto end_time = chrono::high_resolution_clock::now();
        chrono::duration<double> duration = end_time - start_time;
        stats.time_seconds = duration.count();
        stats.memory_kb = getPeakMemoryKB();
        
        return stats;
    }
    
    map<int, bool> getAssignment() {
        return assignment;
    }
};

#endif // BASE_SOLVER_H
