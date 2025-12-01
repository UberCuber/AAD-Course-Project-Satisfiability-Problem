#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cmath>
#include <algorithm>
#include <map>
#include <unordered_map>
#include <set>
#include <iomanip>
#include <ctime>
#include <limits>
#include <memory>

// ==========================================
// Luby Sequence Generator
// ==========================================
class LubyGenerator {
private:
    std::vector<int> l;
    int mult = 1;
    int minu = 0;

public:
    void reset() {
        l.clear();
        mult = 1;
        minu = 0;
    }

    int get_next_luby_number() {
        int size = l.size();
        int to_fill = size + 1;

        double log_val = std::log2(to_fill + 1);
        // Check if log_val is integer (epsilon check for float precision)
        if (std::abs(log_val - std::round(log_val)) < 1e-9) {
            l.push_back(mult);
            mult *= 2;
            minu = size + 1;
        } else {
            l.push_back(l[to_fill - minu - 1]);
        }
        return l[size];
    }
};

// ==========================================
// Priority Queue (Custom Heap Implementation)
// ==========================================
class PriorityQueue {
private:
    // Pair: <score, element>
    std::vector<std::pair<double, int>> heap;
    // Map element -> index in heap. -1 if not in heap.
    std::vector<int> indices; 
    int size = 0;

    void swap_nodes(int ind1, int ind2) {
        std::swap(heap[ind1], heap[ind2]);
        
        // Update indices
        int elem1 = heap[ind1].second;
        int elem2 = heap[ind2].second;
        
        // Note: Python code used 1-based logic for elements in indices array mapping
        indices[elem1] = ind1;
        indices[elem2] = ind2;
    }

    void heapify(int node_index) {
        int max_idx = node_index;
        int left_index = 2 * node_index + 1;
        int right_index = 2 * node_index + 2;

        if (left_index < size && heap[left_index].first > heap[max_idx].first) {
            max_idx = left_index;
        }

        if (right_index < size && heap[right_index].first > heap[max_idx].first) {
            max_idx = right_index;
        }

        if (max_idx != node_index) {
            swap_nodes(max_idx, node_index);
            heapify(max_idx);
        }
    }

public:
    PriorityQueue() {}

    // Initialize with scores. max_element_index is needed to size the indices vector.
    void init(const std::vector<double>& start_list, int max_element_index) {
        heap.clear();
        size = 0;
        
        // indices array needs to cover up to max_element_index
        indices.assign(max_element_index + 1, -1);

        // start_list index 0 is ignored in python code logic for variables, 
        // but let's handle 1-based indexing carefully.
        // Assuming start_list corresponds to var indices 0..N
        
        for (size_t i = 1; i < start_list.size(); ++i) {
            heap.push_back({start_list[i], (int)i});
            indices[i] = (int)heap.size() - 1;
            size++;
        }

        // Heapify from bottom up
        for (int i = (size / 2) - 1; i >= 0; --i) {
            heapify(i);
        }
    }

    int get_top() {
        if (size == 0) return -1;
        int top_element = heap[0].second;
        
        // Move last to top
        swap_nodes(0, size - 1);
        indices[heap[size - 1].second] = -1; // Mark removed
        size--;
        
        if (size > 0) heapify(0);
        
        return top_element;
    }

    void increase_update(int key, double value) {
        if (key >= (int)indices.size() || indices[key] == -1) return;

        int pos = indices[key];
        heap[pos].first += value;

        // Bubble up
        int par = pos;
        while (par != 0) {
            int temp = par;
            par = (par - 1) / 2;
            if (heap[temp].first > heap[par].first) {
                swap_nodes(temp, par);
            } else {
                break;
            }
        }
    }

    void remove(int key) {
        if (key >= (int)indices.size() || indices[key] == -1) return;

        int pos = indices[key];
        double this_node_pr = heap[pos].first;
        
        // Swap with last
        swap_nodes(pos, size - 1);
        indices[key] = -1;
        size--;

        if (pos < size) { // If we didn't just remove the last element
            double replaced_node_pr = heap[pos].first;
            
            if (replaced_node_pr > this_node_pr) {
                 // Bubble up (unlikely logic in standard heap remove, but follows python code logic)
                 // Actually, if we bring the last element to 'pos', we might need to go up OR down.
                 // Python code logic:
                 int par = pos;
                 while (par != 0) {
                     int temp = par;
                     par = (par - 1) / 2;
                     if (heap[temp].first > heap[par].first) {
                         swap_nodes(temp, par);
                     } else {
                         break;
                     }
                 }
            } else {
                heapify(pos);
            }
        }
    }

    void add(int key, double value) {
        if (size == (int)heap.size()) {
            heap.push_back({0, key});
        } else {
            heap[size] = {0, key};
        }
        
        indices[key] = size;
        size++;
        increase_update(key, value);
    }
    
    bool is_empty() const { return size == 0; }
};

// ==========================================
// Statistics
// ==========================================
struct Statistics {
    std::string _input_file = "";
    std::string _result = "";
    std::string _output_statistics_file = "";
    std::string _output_assignment_file = "";
    int _num_vars = 0;
    int _num_orig_clauses = 0;
    int _num_clauses = 0;
    int _num_learned_clauses = 0;
    int _num_decisions = 0;
    long long _num_implications = 0;
    int _restarts = 0;

    double _start_time = 0;
    double _read_time = 0;
    double _complete_time = 0;
    double _bcp_time = 0;
    double _decide_time = 0;
    double _analyze_time = 0;
    double _backtrack_time = 0;

    void print_stats() {
        std::cout << "=========================== STATISTICS ===============================" << std::endl;
        std::cout << "Solving formula from file: " << _input_file << std::endl;
        std::cout << "Vars:" << _num_vars << ", Clauses:" << _num_orig_clauses 
                  << " Stored Clauses:" << _num_clauses << std::endl;
        std::cout << "Input Reading Time: " << (_read_time - _start_time) << std::endl;
        std::cout << "-------------------------------" << std::endl;
        std::cout << "Restarts: " << _restarts << std::endl;
        std::cout << "Learned clauses: " << _num_learned_clauses << std::endl;
        std::cout << "Decisions made: " << _num_decisions << std::endl;
        std::cout << "Implications made: " << _num_implications << std::endl;
        std::cout << "Time taken: " << (_complete_time - _start_time) << std::endl;
        std::cout << "----------- Time breakup ----------------------" << std::endl;
        std::cout << "BCP Time: " << _bcp_time << std::endl;
        std::cout << "Decide Time: " << _decide_time << std::endl;
        std::cout << "Conflict Analyze Time: " << _analyze_time << std::endl;
        std::cout << "Backtrack Time: " << _backtrack_time << std::endl;
        std::cout << "-------------------------------" << std::endl;
        std::cout << "RESULT: " << _result << std::endl;
        std::cout << "Statistics stored in file: " << _output_statistics_file << std::endl;
        if (_result == "SAT") {
            std::cout << "Satisfying Assignment stored in file: " << _output_assignment_file << std::endl;
        }
        std::cout << "======================================================================" << std::endl;
    }
};

// ==========================================
// Assignment Node
// ==========================================
struct AssignedNode {
    int var;
    bool value;
    int level;
    int clause; // -1 if no clause (decision), otherwise clause index
    int index;  // Index in assignment stack

    AssignedNode(int v = -1, bool val = false, int lvl = -1, int cl = -1) 
        : var(v), value(val), level(lvl), clause(cl), index(-1) {}
    
    // Check if node is valid/assigned
    bool is_valid() const { return var != -1; }
};

// ==========================================
// SAT Solver Class
// ==========================================
class SAT {
private:
    // Core data
    int _num_clauses = 0;
    int _num_vars = 0;
    int _level = 0;
    
    // Clause DB: vector of clauses, each clause is a vector of literals
    std::vector<std::vector<int>> _clauses;
    
    // Watched literals: 
    // Literal -> List of clause IDs
    std::vector<std::vector<int>> _clauses_watched_by_l;
    
    // Clause -> Pair of literals watching it
    std::vector<std::pair<int, int>> _literals_watching_c;
    
    // Map variable -> assignment node
    // Using vector for O(1) access instead of map. Index is var.
    std::vector<AssignedNode> _variable_to_assignment_nodes;
    std::vector<bool> _is_var_assigned; // Helper to check existence quickly
    
    // Stack of assignments
    std::vector<AssignedNode> _assignment_stack;
    
    // Config
    bool _is_log;
    std::string _decider;
    std::string _restarter;
    
    // Restart params
    int _conflict_limit = 0;
    int _limit_mult = 2;
    int _conflicts_before_restart = 0;
    int _luby_base = 512;
    LubyGenerator _luby_gen;
    
    // Heuristic params
    std::vector<double> _lit_scores; // VSIDS
    std::vector<double> _var_scores; // MINISAT
    std::vector<int> _phase;         // MINISAT phase saving
    double _incr = 1.0;
    double _decay = 0.85;
    PriorityQueue _priority_queue;
    
public:
    Statistics stats;

    SAT(bool to_log, std::string decider, std::string restarter = "None") 
        : _is_log(to_log), _decider(decider), _restarter(restarter) {
        
        if (decider != "ORDERED" && decider != "VSIDS" && decider != "MINISAT")
             throw std::runtime_error("Invalid decider");
        if (restarter != "None" && restarter != "GEOMETRIC" && restarter != "LUBY")
             throw std::runtime_error("Invalid restarter");

        if (restarter == "GEOMETRIC") {
            _conflict_limit = 512;
            _limit_mult = 2;
        } else if (restarter == "LUBY") {
            _luby_gen.reset();
            _conflict_limit = _luby_base * _luby_gen.get_next_luby_number();
        }
    }

private:
    double get_wall_time() {
        struct timespec time;
        if (clock_gettime(CLOCK_MONOTONIC, &time)) {
             return 0;
        }
        return (double)time.tv_sec + (double)time.tv_nsec * .000000001;
    }

    bool is_negative_literal(int literal) {
        return literal > _num_vars;
    }

    int get_var_from_literal(int literal) {
        if (is_negative_literal(literal)) return literal - _num_vars;
        return literal;
    }

    // Returns 1 on success, 0 on UNSAT/Tautology handling
    int add_clause(std::vector<int>& clause) {
        // Remove duplicates
        std::sort(clause.begin(), clause.end());
        clause.erase(std::unique(clause.begin(), clause.end()), clause.end());

        // Check tautology
        for (size_t i = 0; i < clause.size(); ++i) {
            for (size_t j = i + 1; j < clause.size(); ++j) {
                int var1 = get_var_from_literal(clause[i]);
                int var2 = get_var_from_literal(clause[j]);
                if (var1 == var2) {
                    // One is positive, one is negative (since unique removed identicals)
                    return 1; // Tautology, ignore
                }
            }
        }

        if (clause.empty()) {
            stats._result = "UNSAT";
            return 0;
        }

        if (clause.size() == 1) {
            int lit = clause[0];
            bool value_to_set = !is_negative_literal(lit);
            int var = get_var_from_literal(lit);

            if (!_is_var_assigned[var]) {
                stats._num_implications++;
                AssignedNode node(var, value_to_set, 0, -1);
                _is_var_assigned[var] = true;
                _variable_to_assignment_nodes[var] = node;
                _assignment_stack.push_back(node);
                _variable_to_assignment_nodes[var].index = (int)_assignment_stack.size() - 1;
                
                if (_is_log) std::cout << "Implied(unary): Var:" << var << " Val:" << value_to_set << "\n";
            } else {
                if (_variable_to_assignment_nodes[var].value != value_to_set) {
                    stats._result = "UNSAT";
                    return 0;
                }
            }
            return 1;
        }

        // Process clause for DB
        std::vector<int> stored_clause;
        for (int lit : clause) {
            int var = get_var_from_literal(lit);
            int encoded_lit; // Map to internal representation
            // In input: Positive V, Negative V+N.
            // Our internal structures rely on this.
            if (is_negative_literal(lit)) encoded_lit = var + _num_vars; // Already encoded in input?
            // Wait, logic check: Input is DIMACS. -3 means neg 3.
            // Python code says: "Positive literals... 1,2,3. Negative -1 => V+1."
            // We need to ensure incoming vector `clause` is already converted to internal format
            // OR convert it here. 
            // The read_dimacs function does the conversion. So here we assume `clause` 
            // holds internal literals (1..V, V+1..2V).
            stored_clause.push_back(lit); 

            if (_decider == "VSIDS") _lit_scores[lit]++;
            if (_decider == "MINISAT") _var_scores[get_var_from_literal(lit)]++;
        }

        int clause_id = _num_clauses;
        _clauses.push_back(stored_clause);
        _num_clauses++;

        int w1 = stored_clause[0];
        int w2 = stored_clause[1];

        if ((int)_literals_watching_c.size() <= clause_id) _literals_watching_c.resize(clause_id + 1);
        _literals_watching_c[clause_id] = {w1, w2};

        // Resize watched lists if needed (literals can go up to 2*num_vars)
        if (_clauses_watched_by_l.size() <= (size_t)(2 * _num_vars + 1)) 
            _clauses_watched_by_l.resize(2 * _num_vars + 2);

        _clauses_watched_by_l[w1].push_back(clause_id);
        _clauses_watched_by_l[w2].push_back(clause_id);

        return 1;
    }

    void read_dimacs_cnf_file(std::string filename) {
        std::ifstream infile(filename);
        if (!infile.is_open()) throw std::runtime_error("Could not open file");

        std::string line;
        while (std::getline(infile, line)) {
            while (!line.empty() && std::isspace(line.back())) line.pop_back(); // rstrip
            if (line.empty()) continue;

            std::stringstream ss(line);
            std::string first_word;
            ss >> first_word;

            if (first_word == "c") continue;
            if (first_word == "%") break;
            if (first_word == "p") {
                std::string cnf_dummy;
                ss >> cnf_dummy >> _num_vars >> stats._num_orig_clauses;

                // Initialize sizes
                _variable_to_assignment_nodes.resize(_num_vars + 1);
                _is_var_assigned.assign(_num_vars + 1, false);
                _clauses_watched_by_l.resize(2 * _num_vars + 2);

                if (_decider == "VSIDS") _lit_scores.assign(2 * _num_vars + 2, 0.0);
                if (_decider == "MINISAT") {
                    _var_scores.assign(_num_vars + 1, 0.0);
                    _phase.assign(_num_vars + 1, 0); // 0 corresponds to False
                }
            } else {
                // Clause line. The first word was actually a number.
                // Reset stream to parse the first number
                std::stringstream line_ss(line);
                std::vector<int> clause;
                int lit_in;
                while (line_ss >> lit_in && lit_in != 0) {
                    // Convert DIMACS to internal format
                    if (lit_in < 0) {
                        clause.push_back(std::abs(lit_in) + _num_vars);
                    } else {
                        clause.push_back(lit_in);
                    }
                }
                if (add_clause(clause) == 0) break; // UNSAT detected
            }
        }
        infile.close();

        // Initialize Priority Queue
        if (_decider == "VSIDS") {
            _priority_queue.init(_lit_scores, 2 * _num_vars + 1);
            // Remove assigned vars
            for (const auto& node : _assignment_stack) {
                _priority_queue.remove(node.var);
                _priority_queue.remove(node.var + _num_vars);
            }
        }
        if (_decider == "MINISAT") {
            _priority_queue.init(_var_scores, _num_vars);
            _decay = 0.85;
            for (const auto& node : _assignment_stack) {
                _priority_queue.remove(node.var);
            }
        }
    }

    int decide() {
        int var = -1;
        bool value_to_set = true;

        if (_decider == "ORDERED") {
            for (int x = 1; x <= _num_vars; ++x) {
                if (!_is_var_assigned[x]) {
                    var = x;
                    break;
                }
            }
        } else if (_decider == "VSIDS") {
            int literal = _priority_queue.get_top();
            if (literal != -1) {
                var = get_var_from_literal(literal);
                bool is_neg = is_negative_literal(literal);
                value_to_set = !is_neg;
                
                if (is_neg) _priority_queue.remove(var);
                else _priority_queue.remove(var + _num_vars);
            }
        } else if (_decider == "MINISAT") {
            var = _priority_queue.get_top();
            if (var != -1) {
                value_to_set = (_phase[var] == 1);
            }
        }

        if (var == -1) return -1;

        _level++;
        AssignedNode node(var, value_to_set, _level, -1);
        _is_var_assigned[var] = true;
        _variable_to_assignment_nodes[var] = node;
        _assignment_stack.push_back(node);
        _variable_to_assignment_nodes[var].index = (int)_assignment_stack.size() - 1;
        
        stats._num_decisions++;
        if (_is_log) std::cout << "Chosen decision: Var:" << var << " Val:" << value_to_set << " Lev:" << _level << "\n";

        return var;
    }

    std::string boolean_constraint_propogation(bool is_first_time) {
        int ptr = (_assignment_stack.empty()) ? 0 : (int)_assignment_stack.size() - 1;
        if (is_first_time) ptr = 0;

        while (ptr < (int)_assignment_stack.size()) {
            AssignedNode last_node = _assignment_stack[ptr];
            int literal_falsed = (last_node.value) ? (last_node.var + _num_vars) : last_node.var;

            // Clauses watched by the falsed literal need update
            // We traverse a copy or handle iteration carefully because we modify the list
            std::vector<int>& watched_clauses = _clauses_watched_by_l[literal_falsed];
            
            // Iterate backwards to mimic Python implementation preference (end clauses are newer/conflict clauses)
            for (int i = (int)watched_clauses.size() - 1; i >= 0; --i) {
                int clause_id = watched_clauses[i];
                std::pair<int, int>& watchers = _literals_watching_c[clause_id];
                
                int other_watch = (watchers.first == literal_falsed) ? watchers.second : watchers.first;
                int other_var = get_var_from_literal(other_watch);
                bool is_neg_other = is_negative_literal(other_watch);

                // If other watcher is satisfied, skip
                if (_is_var_assigned[other_var]) {
                    bool val = _variable_to_assignment_nodes[other_var].value;
                    if ((is_neg_other && !val) || (!is_neg_other && val)) {
                        continue;
                    }
                }

                // Find new watcher
                int new_watcher = -1;
                std::vector<int>& clause = _clauses[clause_id];
                
                for (int lit : clause) {
                    if (lit != watchers.first && lit != watchers.second) {
                        int v_lit = get_var_from_literal(lit);
                        if (!_is_var_assigned[v_lit]) {
                            new_watcher = lit;
                            break;
                        } else {
                            // If implied true, use it
                            bool v_val = _variable_to_assignment_nodes[v_lit].value;
                            bool lit_neg = is_negative_literal(lit);
                            if ((lit_neg && !v_val) || (!lit_neg && v_val)) {
                                new_watcher = lit;
                                break;
                            }
                        }
                    }
                }

                if (new_watcher != -1) {
                    // Update watchers
                    if (watchers.first == literal_falsed) watchers.first = new_watcher;
                    else watchers.second = new_watcher;

                    // Update watcher lists
                    // Remove clause_id from literal_falsed list. 
                    // Optimization: swap with last and pop, but here we are iterating.
                    // Since we are iterating backwards, swapping with back might invalidate current index if not careful.
                    // The standard Swap-and-Pop idiom works if we adjust the loop index.
                    // BUT, we are iterating `watched_clauses` which belongs to `literal_falsed`.
                    // We can just overwrite the current position with the last element and pop back.
                    watched_clauses[i] = watched_clauses.back();
                    watched_clauses.pop_back();

                    _clauses_watched_by_l[new_watcher].push_back(clause_id);

                } else {
                    // No new watcher found.
                    if (!_is_var_assigned[other_var]) {
                        // Implication
                        bool val_to_set = !is_neg_other;
                        AssignedNode node(other_var, val_to_set, _level, clause_id);
                        _is_var_assigned[other_var] = true;
                        _variable_to_assignment_nodes[other_var] = node;
                        _assignment_stack.push_back(node);
                        _variable_to_assignment_nodes[other_var].index = (int)_assignment_stack.size() - 1;

                        if (_decider == "VSIDS") {
                            _priority_queue.remove(other_var);
                            _priority_queue.remove(other_var + _num_vars);
                        }
                        if (_decider == "MINISAT") {
                            _priority_queue.remove(other_var);
                            _phase[other_var] = (val_to_set ? 1 : 0);
                        }

                        stats._num_implications++;
                        if (_is_log) std::cout << "Implied decision: Var:" << other_var << " Val:" << val_to_set << "\n";
                    } else {
                        // Conflict
                        if (_restarter != "None") {
                            _conflicts_before_restart++;
                            if (_conflicts_before_restart >= _conflict_limit) {
                                stats._restarts++;
                                _conflicts_before_restart = 0;
                                if (_restarter == "GEOMETRIC") _conflict_limit *= _limit_mult;
                                if (_restarter == "LUBY") _conflict_limit = _luby_base * _luby_gen.get_next_luby_number();
                                if (_is_log) std::cout << "RESTARTING Limit: " << _conflict_limit << "\n";
                                return "RESTART";
                            }
                        }

                        AssignedNode conf_node(-1, false, _level, clause_id);
                        _assignment_stack.push_back(conf_node);
                        conf_node.index = (int)_assignment_stack.size() - 1;
                        if (_is_log) std::cout << "CONFLICT\n";
                        return "CONFLICT";
                    }
                }
            }
            ptr++;
        }
        return "NO_CONFLICT";
    }

    std::vector<int> binary_resolution(const std::vector<int>& c1, const std::vector<int>& c2, int var) {
        std::vector<int> res;
        res.reserve(c1.size() + c2.size());
        
        int pos_lit = var;
        int neg_lit = var + _num_vars;

        for (int l : c1) if (l != pos_lit && l != neg_lit) res.push_back(l);
        for (int l : c2) if (l != pos_lit && l != neg_lit) res.push_back(l);

        std::sort(res.begin(), res.end());
        res.erase(std::unique(res.begin(), res.end()), res.end());
        return res;
    }

    std::pair<int, AssignedNode> analyze_conflict() {
        AssignedNode conflict_node = _assignment_stack.back();
        _assignment_stack.pop_back();

        int conflict_level = conflict_node.level;
        std::vector<int> conflict_clause = _clauses[conflict_node.clause];

        if (conflict_level == 0) return {-1, AssignedNode()};

        AssignedNode prev_assigned_node;
        
        while (true) {
            int counter = 0;
            int max_idx = -1;
            AssignedNode cand;

            for (int lit : conflict_clause) {
                int var = get_var_from_literal(lit);
                AssignedNode& n = _variable_to_assignment_nodes[var];
                if (n.level == conflict_level) {
                    counter++;
                    if (n.index > max_idx) {
                        max_idx = n.index;
                        cand = n;
                    }
                }
            }

            if (counter == 1) {
                prev_assigned_node = cand; // This is the UIP related assignment? No, this is 1-UIP literal
                // Actually the variable is what we need to return or use.
                // Re-check logic: "return counter == 1, cand". 
                // cand is the latest assigned node at the conflict level.
                // If counter == 1, we found the 1-UIP clause.
                break;
            }

            std::vector<int>& other_clause = _clauses[cand.clause];
            conflict_clause = binary_resolution(conflict_clause, other_clause, cand.var);
        }

        if (conflict_clause.size() > 1) {
            stats._num_learned_clauses++;
            int clause_id = _num_clauses++;
            _clauses.push_back(conflict_clause);

            int w1 = conflict_clause[0];
            int w2 = conflict_clause[1];
            
            if ((int)_literals_watching_c.size() <= clause_id) _literals_watching_c.resize(clause_id + 1);
            _literals_watching_c[clause_id] = {w1, w2};
            
            _clauses_watched_by_l[w1].push_back(clause_id);
            _clauses_watched_by_l[w2].push_back(clause_id);

            // Heuristic update
            if (_decider == "VSIDS") {
                for (int l : conflict_clause) {
                    _lit_scores[l] += _incr;
                    _priority_queue.increase_update(l, _incr);
                }
                _incr += 0.75;
            }
            if (_decider == "MINISAT") {
                for (int l : conflict_clause) {
                    int v = get_var_from_literal(l);
                    _var_scores[v] += _incr;
                    _priority_queue.increase_update(v, _incr);
                }
                _incr /= _decay;
            }

            // Calculate backtrack level
            int backtrack_level = -1;
            int lit_at_conflict = -1;
            
            for (int lit : conflict_clause) {
                int var = get_var_from_literal(lit);
                AssignedNode& n = _variable_to_assignment_nodes[var];
                if (n.level == conflict_level) {
                    lit_at_conflict = lit;
                } else {
                    if (n.level > backtrack_level) backtrack_level = n.level;
                }
            }
            if (backtrack_level == -1) backtrack_level = 0; // Should not happen for size > 1 but safe

            int var_con = get_var_from_literal(lit_at_conflict);
            bool val_set = !is_negative_literal(lit_at_conflict);
            
            AssignedNode new_node(var_con, val_set, backtrack_level, clause_id);
            return {backtrack_level, new_node};
        } else {
            // Unit conflict clause
            int lit = conflict_clause[0];
            int var = get_var_from_literal(lit);
            bool val_set = !is_negative_literal(lit);
            AssignedNode new_node(var, val_set, 0, -1);
            return {0, new_node};
        }
    }

    void backtrack(int backtrack_level, AssignedNode* node_to_add) {
        _level = backtrack_level;

        while (!_assignment_stack.empty()) {
            AssignedNode& top = _assignment_stack.back();
            if (top.level <= backtrack_level) break;

            int var = top.var;
            // Unset
            if (top.is_valid()) { // Conflict nodes in stack have var=-1
                 _is_var_assigned[var] = false;
                 
                 if (_decider == "VSIDS") {
                     _priority_queue.add(var, _lit_scores[var]);
                     _priority_queue.add(var + _num_vars, _lit_scores[var + _num_vars]);
                 }
                 if (_decider == "MINISAT") {
                     _priority_queue.add(var, _var_scores[var]);
                 }
            }
            _assignment_stack.pop_back();
        }

        if (node_to_add != nullptr && node_to_add->is_valid()) {
            _is_var_assigned[node_to_add->var] = true;
            _variable_to_assignment_nodes[node_to_add->var] = *node_to_add;
            _assignment_stack.push_back(*node_to_add);
            _variable_to_assignment_nodes[node_to_add->var].index = (int)_assignment_stack.size() - 1;

            if (_decider == "VSIDS") {
                _priority_queue.remove(node_to_add->var);
                _priority_queue.remove(node_to_add->var + _num_vars);
            }
            if (_decider == "MINISAT") {
                _priority_queue.remove(node_to_add->var);
                _phase[node_to_add->var] = (node_to_add->value ? 1 : 0);
            }
            stats._num_implications++;
        }
    }

public:
    void solve(std::string cnf_filename) {
        stats._input_file = cnf_filename;
        stats._start_time = get_wall_time();

        try {
            read_dimacs_cnf_file(cnf_filename);
        } catch (const std::exception& e) {
            std::cerr << "Error reading file: " << e.what() << std::endl;
            return;
        }

        stats._read_time = get_wall_time();
        stats._num_vars = _num_vars;
        stats._num_clauses = _num_clauses;

        if (stats._result == "UNSAT") {
            stats._complete_time = get_wall_time();
            std::cout << "UNSAT" << std::endl;
        } else {
            bool first_time = true;

            while (true) {
                while (true) {
                    double t0 = get_wall_time();
                    std::string res = boolean_constraint_propogation(first_time);
                    stats._bcp_time += (get_wall_time() - t0);

                    if (res == "NO_CONFLICT") break;

                    if (res == "RESTART") {
                        backtrack(0, nullptr);
                        break;
                    }

                    first_time = false;
                    
                    t0 = get_wall_time();
                    std::pair<int, AssignedNode> analysis = analyze_conflict();
                    stats._analyze_time += (get_wall_time() - t0);

                    if (analysis.first == -1) {
                        stats._result = "UNSAT";
                        std::cout << "UNSAT" << std::endl;
                        stats._complete_time = get_wall_time();
                        goto end_solve; // Break out of all loops
                    }

                    t0 = get_wall_time();
                    backtrack(analysis.first, &analysis.second);
                    stats._backtrack_time += (get_wall_time() - t0);
                }

                if (stats._result == "UNSAT") break;
                first_time = false;

                double t0 = get_wall_time();
                int var = decide();
                stats._decide_time += (get_wall_time() - t0);

                if (var == -1) {
                    stats._result = "SAT";
                    std::cout << "SAT" << std::endl;
                    stats._complete_time = get_wall_time();
                    break;
                }
            }
        }

    end_solve:
        // Output results
        std::string base_filename = cnf_filename.substr(cnf_filename.find_last_of("/\\") + 1);
        std::string case_name = base_filename.substr(0, base_filename.find_last_of("."));
        stats._output_statistics_file = "stats_" + case_name + ".txt";

        if (stats._result == "SAT") {
            stats._output_assignment_file = "assgn_" + case_name + ".txt";
            std::ofstream out(stats._output_assignment_file);
            out << "{";
            for (int i = 1; i <= _num_vars; ++i) {
                if (_is_var_assigned[i]) {
                    out << "\"" << i << "\": " << (_variable_to_assignment_nodes[i].value ? "true" : "false");
                    if (i < _num_vars) out << ", ";
                }
            }
            out << "}";
            out.close();
        }
    }
};

// ==========================================
// Main Function
// ==========================================
int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cout << "Usage: ./solver <to_log> <decider> <restarter> <inputfile>" << std::endl;
        std::cout << "Example: ./solver False MINISAT None test/sat/bmc-1.cnf" << std::endl;
        return 1;
    }

    std::string to_log_str = argv[1];
    bool to_log = (to_log_str == "True");
    std::string decider = argv[2];
    std::string restarter = argv[3];
    std::string input_file = argv[4];

    try {
        SAT sat(to_log, decider, restarter);
        sat.solve(input_file);
        // To print stats to file/console as per python script logic
        // Redirecting cout is complex in C++, so we just print to console 
        // and file writing is handled in stats print_stats if needed, 
        // but here we just call the print method.
        // If file output is strictly required for stats, we can use freopen or fstream.
        
        std::ofstream stat_file(sat.stats._output_statistics_file);
        std::streambuf *coutbuf = std::cout.rdbuf(); // save old buf
        std::cout.rdbuf(stat_file.rdbuf()); // redirect std::cout to out.txt!
        
        sat.stats.print_stats();

        std::cout.rdbuf(coutbuf); // reset to standard output
        sat.stats.print_stats(); // Print to console as well

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}