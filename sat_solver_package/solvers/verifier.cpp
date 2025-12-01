#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>

// ==========================================
// Assignment Parser (Simple JSON)
// ==========================================
// Parses format: {"1": true, "2": false, ...}
std::unordered_map<int, bool> parse_assignment_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open assignment file.");
    }

    std::unordered_map<int, bool> assignment;
    std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());

    // Simple parsing strategy: 
    // Replace struct characters '{', '}', '"', ',', ':' with spaces
    // Then read key-value pairs as streams
    for (char &c : content) {
        if (c == '{' || c == '}' || c == '"' || c == ',' || c == ':') {
            c = ' ';
        }
    }

    std::stringstream ss(content);
    std::string key_str, val_str;
    
    // Read pairs
    while (ss >> key_str >> val_str) {
        try {
            int var = std::stoi(key_str);
            bool val = (val_str == "true");
            assignment[var] = val;
        } catch (...) {
            continue; // Skip malformed tokens if any
        }
    }
    
    return assignment;
}

// ==========================================
// Validity Checker
// ==========================================
bool check_validity(const std::string& input_file_name, std::unordered_map<int, bool>& assgn_dict) {
    std::ifstream input_file(input_file_name);
    if (!input_file.is_open()) {
        std::cerr << "Error: Could not open input CNF file." << std::endl;
        return false;
    }

    std::string line;
    while (std::getline(input_file, line)) {
        // Remove trailing whitespace
        while (!line.empty() && std::isspace(line.back())) line.pop_back();
        if (line.empty()) continue;

        std::stringstream ss(line);
        std::string first_word;
        ss >> first_word;

        // Ignore comments and header
        if (first_word == "c" || first_word == "p" || first_word == "%") {
            continue;
        }

        // It's a clause. Parse literals.
        // We need to reset stringstream to the beginning or handle first_word as a number
        std::vector<int> clause;
        
        // Check if first_word was actually a number (part of clause)
        try {
            clause.push_back(std::stoi(first_word));
        } catch (...) {
            continue; // Should not happen in valid DIMACS
        }

        int lit;
        while (ss >> lit) {
            clause.push_back(lit);
        }

        // Remove the trailing 0 if present
        if (!clause.empty() && clause.back() == 0) {
            clause.pop_back();
        }

        // Check if clause is satisfied
        bool clause_sat = false;
        for (int l : clause) {
            int var = std::abs(l);
            bool is_neg = (l < 0);

            // Check if variable exists in assignment
            if (assgn_dict.find(var) == assgn_dict.end()) {
                // If a variable is not in the assignment file, the solver didn't assign it.
                // In strict SAT, unassigned variables might effectively be "don't cares",
                // but if a clause relies ONLY on unassigned vars, it's not satisfied.
                // We treat missing vars as not satisfying the literal here.
                continue; 
            }

            bool val = assgn_dict[var];
            
            // Logic: 
            // If literal is -x, satisfied if val is False.
            // If literal is x, satisfied if val is True.
            if ((is_neg && !val) || (!is_neg && val)) {
                clause_sat = true;
                break; // Clause satisfied, move to next clause
            }
        }

        if (!clause_sat) {
            // Found a clause that is NOT satisfied
            return false;
        }
    }

    return true;
}

// ==========================================
// Main
// ==========================================
int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "Usage: ./verifier <inputfile> <assignmentfile>" << std::endl;
        return 1;
    }

    std::string input_file_name = argv[1];
    std::string assgn_file_name = argv[2];

    try {
        // 1. Load Assignment
        std::unordered_map<int, bool> assgn_dict = parse_assignment_file(assgn_file_name);

        // 2. Check Validity
        bool is_correct = check_validity(input_file_name, assgn_dict);

        // 3. Print Result
        if (is_correct) {
            std::cout << "YES!! The assignment is valid." << std::endl;
        } else {
            std::cout << "NO!! The assignment is not valid." << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}