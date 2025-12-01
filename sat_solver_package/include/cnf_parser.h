#ifndef CNF_PARSER_H
#define CNF_PARSER_H

#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>

using namespace std;

struct CNFFormula {
    int num_vars;
    int num_clauses;
    vector<vector<int>> clauses;
};

class CNFParser {
public:
    static CNFFormula parse(const string& filename) {
        CNFFormula formula;
        ifstream file(filename);
        
        if (!file.is_open()) {
            cerr << "Error: Cannot open file " << filename << endl;
            return formula;
        }
        
        string line;
        while (getline(file, line)) {
            if (line.empty()) continue;
            
            // Skip comments
            if (line[0] == 'c') continue;
            
            // Parse problem line
            if (line[0] == 'p') {
                istringstream iss(line);
                string p, cnf;
                iss >> p >> cnf >> formula.num_vars >> formula.num_clauses;
                continue;
            }
            
            // Parse clause
            istringstream iss(line);
            vector<int> clause;
            int lit;
            while (iss >> lit) {
                if (lit == 0) break;
                clause.push_back(lit);
            }
            if (!clause.empty()) {
                formula.clauses.push_back(clause);
            }
        }
        
        file.close();
        return formula;
    }
};

#endif // CNF_PARSER_H
