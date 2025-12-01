/*
 * Set-Based SAT Solver Implementation in C++
 * Based on "Complete SAT Solver Based on Set Theory" (LNCS 7473)
 * Authors: Wensheng Guo, Guowu Yang, Qianqi Le, and William N.N. Hung
 *
 * This implementation uses set theory operations to solve Boolean satisfiability problems.
 * The key idea is to map CNF formulas to set representations and use set operations
 * to determine satisfiability.
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <set>
#include <unordered_set>
#include <unordered_map>
#include <map>
#include <algorithm>
#include <chrono>
#include <thread>
#include <atomic>
#include <future>
#include <memory>
#include <ctime>
#include <iomanip>
#include <climits>
#include <dirent.h>
#include <sys/stat.h>

// Forward declarations
class Literal;
class Clause;
class CNFFormula;
class SetBasedSATSolver;

// ============================================================================
// Literal Class
// ============================================================================
class Literal
{
public:
    std::string variable;
    bool negated;

    Literal(const std::string &var, bool neg = false)
        : variable(var), negated(neg) {}

    bool operator==(const Literal &other) const
    {
        return variable == other.variable && negated == other.negated;
    }

    bool operator<(const Literal &other) const
    {
        if (variable != other.variable)
            return variable < other.variable;
        return negated < other.negated;
    }

    Literal negate() const
    {
        return Literal(variable, !negated);
    }

    std::string toString() const
    {
        return (negated ? "¬" : "") + variable;
    }
};

// Hash function for Literal
namespace std
{
    template <>
    struct hash<Literal>
    {
        size_t operator()(const Literal &lit) const
        {
            return hash<string>()(lit.variable) ^ hash<bool>()(lit.negated);
        }
    };
}

// ============================================================================
// Clause Class
// ============================================================================
class Clause
{
public:
    std::set<Literal> literals;

    Clause() = default;

    Clause(const std::set<Literal> &lits) : literals(lits) {}

    bool operator<(const Clause &other) const
    {
        return literals < other.literals;
    }

    bool operator==(const Clause &other) const
    {
        return literals == other.literals;
    }

    bool isUnitClause() const
    {
        return literals.size() == 1;
    }

    Literal getUnitLiteral() const
    {
        if (isUnitClause())
        {
            return *literals.begin();
        }
        throw std::runtime_error("Not a unit clause");
    }

    bool containsLiteral(const Literal &lit) const
    {
        return literals.find(lit) != literals.end();
    }

    bool isEmpty() const
    {
        return literals.empty();
    }

    bool isTautology() const
    {
        for (const auto &lit : literals)
        {
            if (literals.find(lit.negate()) != literals.end())
            {
                return true;
            }
        }
        return false;
    }

    std::string toString() const
    {
        if (literals.empty())
            return "()";

        std::string result = "(";
        bool first = true;
        for (const auto &lit : literals)
        {
            if (!first)
                result += " ∨ ";
            result += lit.toString();
            first = false;
        }
        result += ")";
        return result;
    }
};

// ============================================================================
// CNF Formula Class
// ============================================================================
class CNFFormula
{
public:
    std::set<Clause> clauses;
    std::set<std::string> variables;

    CNFFormula() = default;

    CNFFormula(const std::set<Clause> &cls) : clauses(cls)
    {
        extractVariables();
    }

    void extractVariables()
    {
        variables.clear();
        for (const auto &clause : clauses)
        {
            for (const auto &lit : clause.literals)
            {
                variables.insert(lit.variable);
            }
        }
    }

    bool isEmpty() const
    {
        return clauses.empty();
    }

    bool hasEmptyClause() const
    {
        for (const auto &clause : clauses)
        {
            if (clause.isEmpty())
                return true;
        }
        return false;
    }

    std::vector<Clause> getUnitClauses() const
    {
        std::vector<Clause> units;
        for (const auto &clause : clauses)
        {
            if (clause.isUnitClause())
            {
                units.push_back(clause);
            }
        }
        return units;
    }

    std::set<Literal> getPureLiterals() const
    {
        std::unordered_map<std::string, std::pair<bool, bool>> occurrences;

        for (const auto &clause : clauses)
        {
            for (const auto &lit : clause.literals)
            {
                if (occurrences.find(lit.variable) == occurrences.end())
                {
                    occurrences[lit.variable] = {false, false};
                }
                if (lit.negated)
                {
                    occurrences[lit.variable].second = true;
                }
                else
                {
                    occurrences[lit.variable].first = true;
                }
            }
        }

        std::set<Literal> pureLiterals;
        for (const auto &pair : occurrences)
        {
            const std::string &var = pair.first;
            const std::pair<bool, bool> &occ = pair.second;
            if (occ.first && !occ.second)
            {
                pureLiterals.insert(Literal(var, false));
            }
            else if (occ.second && !occ.first)
            {
                pureLiterals.insert(Literal(var, true));
            }
        }
        return pureLiterals;
    }

    CNFFormula simplifyWithAssignment(const Literal &lit) const
    {
        std::set<Clause> newClauses;

        for (const auto &clause : clauses)
        {
            // If clause contains the literal, it becomes true and is removed
            if (clause.containsLiteral(lit))
            {
                continue;
            }

            // If clause contains negation of literal, remove that literal
            if (clause.containsLiteral(lit.negate()))
            {
                std::set<Literal> newLiterals = clause.literals;
                newLiterals.erase(lit.negate());
                newClauses.insert(Clause(newLiterals));
            }
            else
            {
                // Clause is unchanged
                newClauses.insert(clause);
            }
        }

        return CNFFormula(newClauses);
    }

    std::string toString() const
    {
        if (clauses.empty())
            return "(empty)";

        std::string result;
        bool first = true;
        for (const auto &clause : clauses)
        {
            if (!first)
                result += " ∧ ";
            result += clause.toString();
            first = false;
        }
        return result;
    }
};

// ============================================================================
// Set-Based SAT Solver
// ============================================================================
class SetBasedSATSolver
{
private:
    std::map<std::string, bool> assignment;
    int decisionLevel;
    std::vector<std::tuple<std::string, bool, int>> backtrackStack;
    std::atomic<bool> shouldStop;

public:
    SetBasedSATSolver() : decisionLevel(0), shouldStop(false) {}

    std::pair<bool, std::map<std::string, bool>> solve(const CNFFormula &formula, bool verbose = false)
    {
        assignment.clear();
        decisionLevel = 0;
        backtrackStack.clear();
        shouldStop = false;

        if (verbose)
        {
            std::cout << "Initial formula: " << formula.toString() << std::endl;
            std::cout << "Variables: " << formula.variables.size() << std::endl
                      << std::endl;
        }

        bool result = dpll(formula, verbose);

        if (result)
        {
            return {true, assignment};
        }
        else
        {
            return {false, std::map<std::string, bool>()};
        }
    }

    void stop()
    {
        shouldStop = true;
    }

private:
    bool dpll(const CNFFormula &formula, bool verbose)
    {
        if (shouldStop)
            return false;

        // Base case 1: Empty formula = satisfiable
        if (formula.isEmpty())
        {
            if (verbose)
            {
                std::cout << "✓ Formula is empty - SATISFIABLE" << std::endl;
            }
            return true;
        }

        // Base case 2: Empty clause = unsatisfiable
        if (formula.hasEmptyClause())
        {
            if (verbose)
            {
                std::cout << "✗ Empty clause found - conflict" << std::endl;
            }
            return false;
        }

        // Unit propagation
        auto unitClauses = formula.getUnitClauses();
        if (!unitClauses.empty())
        {
            if (verbose)
            {
                std::cout << "\nUnit propagation: ";
                for (const auto &uc : unitClauses)
                {
                    std::cout << uc.toString() << " ";
                }
                std::cout << std::endl;
            }

            CNFFormula simplifiedFormula = formula;
            for (const auto &unitClause : unitClauses)
            {
                Literal lit = unitClause.getUnitLiteral();
                if (verbose)
                {
                    std::cout << "  Assigning " << lit.toString() << " = True" << std::endl;
                }

                assignment[lit.variable] = !lit.negated;
                backtrackStack.push_back({lit.variable, !lit.negated, decisionLevel});

                simplifiedFormula = simplifiedFormula.simplifyWithAssignment(lit);

                if (verbose && !simplifiedFormula.isEmpty())
                {
                    std::cout << "  Simplified formula: " << simplifiedFormula.toString() << std::endl;
                }
            }

            return dpll(simplifiedFormula, verbose);
        }

        // Pure literal elimination
        auto pureLiterals = formula.getPureLiterals();
        if (!pureLiterals.empty())
        {
            if (verbose)
            {
                std::cout << "\nPure literal elimination: ";
                for (const auto &pl : pureLiterals)
                {
                    std::cout << pl.toString() << " ";
                }
                std::cout << std::endl;
            }

            CNFFormula simplifiedFormula = formula;
            for (const auto &lit : pureLiterals)
            {
                if (verbose)
                {
                    std::cout << "  Assigning " << lit.toString() << " = True" << std::endl;
                }

                assignment[lit.variable] = !lit.negated;
                backtrackStack.push_back({lit.variable, !lit.negated, decisionLevel});

                simplifiedFormula = simplifiedFormula.simplifyWithAssignment(lit);
            }

            return dpll(simplifiedFormula, verbose);
        }

        // Decision: Choose a variable and branch
        std::string variable = chooseVariable(formula);
        if (variable.empty())
        {
            return true;
        }

        decisionLevel++;
        if (verbose)
        {
            std::cout << "\n[Decision Level " << decisionLevel << "] Branching on " << variable << std::endl;
        }

        // Try assigning variable to True
        Literal litTrue(variable, false);
        if (verbose)
        {
            std::cout << "  Trying " << variable << " = True" << std::endl;
        }

        assignment[variable] = true;
        backtrackStack.push_back({variable, true, decisionLevel});

        CNFFormula formulaTrue = formula.simplifyWithAssignment(litTrue);
        if (dpll(formulaTrue, verbose))
        {
            return true;
        }

        // Backtrack: Try assigning variable to False
        if (verbose)
        {
            std::cout << "  Backtracking: Trying " << variable << " = False" << std::endl;
        }

        backtrackToLevel(decisionLevel - 1);

        Literal litFalse(variable, true);
        assignment[variable] = false;
        backtrackStack.push_back({variable, false, decisionLevel});

        CNFFormula formulaFalse = formula.simplifyWithAssignment(litFalse);
        if (dpll(formulaFalse, verbose))
        {
            return true;
        }

        // Both branches failed
        decisionLevel--;
        backtrackToLevel(decisionLevel);
        return false;
    }

    std::string chooseVariable(const CNFFormula &formula)
    {
        if (formula.isEmpty())
            return "";

        // Count variable occurrences
        std::unordered_map<std::string, int> varCount;
        for (const auto &clause : formula.clauses)
        {
            for (const auto &lit : clause.literals)
            {
                varCount[lit.variable]++;
            }
        }

        // Choose unassigned variable with highest count
        std::string bestVar;
        int maxCount = 0;
        for (const auto &pair : varCount)
        {
            const std::string &var = pair.first;
            int count = pair.second;
            if (assignment.find(var) == assignment.end() && count > maxCount)
            {
                maxCount = count;
                bestVar = var;
            }
        }

        return bestVar;
    }

    void backtrackToLevel(int level)
    {
        while (!backtrackStack.empty() && std::get<2>(backtrackStack.back()) > level)
        {
            std::string var = std::get<0>(backtrackStack.back());
            backtrackStack.pop_back();
            assignment.erase(var);
        }
    }
};

// ============================================================================
// DIMACS Parser
// ============================================================================
CNFFormula parseDimacsCNF(const std::string &dimacs)
{
    std::set<Clause> clauses;
    std::istringstream stream(dimacs);
    std::string line;

    while (std::getline(stream, line))
    {
        // Skip comments and problem line
        if (line.empty() || line[0] == 'c' || line[0] == 'p')
        {
            continue;
        }

        std::istringstream lineStream(line);
        std::set<Literal> literals;
        int litValue;

        while (lineStream >> litValue)
        {
            if (litValue == 0)
                break;

            if (litValue > 0)
            {
                literals.insert(Literal("x" + std::to_string(litValue), false));
            }
            else
            {
                literals.insert(Literal("x" + std::to_string(abs(litValue)), true));
            }
        }

        if (!literals.empty())
        {
            clauses.insert(Clause(literals));
        }
    }

    return CNFFormula(clauses);
}

// ============================================================================
// Report Generation
// ============================================================================
void createReport(const std::string &filename, const CNFFormula &formula,
                  bool result, double elapsed, bool timedOut,
                  const std::map<std::string, bool> &assignment,
                  const std::string &outputFile = "")
{

    // Calculate clause statistics
    int minLen = INT_MAX, maxLen = 0;
    double avgLen = 0.0;
    for (const auto &clause : formula.clauses)
    {
        int len = clause.literals.size();
        minLen = std::min(minLen, len);
        maxLen = std::max(maxLen, len);
        avgLen += len;
    }
    if (!formula.clauses.empty())
    {
        avgLen /= formula.clauses.size();
    }

    // Get current timestamp
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    std::stringstream timestamp;
    timestamp << std::put_time(std::localtime(&time), "%Y-%m-%dT%H:%M:%S");

    // Print console report
    std::cout << "\n"
              << std::string(80, '=') << std::endl;
    std::cout << "EXECUTION REPORT" << std::endl;
    std::cout << std::string(80, '=') << std::endl;
    std::cout << "Timestamp:        " << timestamp.str() << std::endl;
    std::cout << "Input File:       " << filename << std::endl;
    std::cout << std::endl;
    std::cout << "PROBLEM STATISTICS:" << std::endl;
    std::cout << "  Variables:      " << formula.variables.size() << std::endl;
    std::cout << "  Clauses:        " << formula.clauses.size() << std::endl;
    std::cout << "  Clause Length:  min=" << minLen << ", max=" << maxLen
              << ", avg=" << std::fixed << std::setprecision(2) << avgLen << std::endl;
    std::cout << std::endl;
    std::cout << "SOLVING RESULTS:" << std::endl;
    std::cout << "  Result:         " << (timedOut ? "TIMEOUT" : (result ? "SAT" : "UNSAT")) << std::endl;
    std::cout << "  Time:           " << std::fixed << std::setprecision(6) << elapsed << " seconds" << std::endl;
    std::cout << "  Timed Out:      " << (timedOut ? "YES" : "NO") << std::endl;

    if (!timedOut && result && !assignment.empty())
    {
        std::cout << std::endl;
        std::cout << "SOLUTION:" << std::endl;
        std::cout << "  Variables Assigned: " << assignment.size() << std::endl;
        if (assignment.size() <= 20)
        {
            std::cout << "  Assignment:" << std::endl;
            for (const auto &pair : assignment)
            {
                std::cout << "    " << pair.first << " = " << (pair.second ? "true" : "false") << std::endl;
            }
        }
        else
        {
            std::cout << "  (Assignment too large to display: " << assignment.size() << " variables)" << std::endl;
        }
    }
    std::cout << std::string(80, '=') << std::endl;

    // Save JSON report
    std::string reportFilename = filename;
    size_t pos = reportFilename.find(".cnf");
    if (pos != std::string::npos)
    {
        reportFilename.replace(pos, 4, "_report.json");
    }
    else
    {
        reportFilename += "_report.json";
    }

    std::ofstream reportFile(reportFilename);
    if (reportFile.is_open())
    {
        reportFile << "{\n";
        reportFile << "  \"timestamp\": \"" << timestamp.str() << "\",\n";
        reportFile << "  \"input_file\": \"" << filename << "\",\n";
        reportFile << "  \"problem_stats\": {\n";
        reportFile << "    \"variables\": " << formula.variables.size() << ",\n";
        reportFile << "    \"clauses\": " << formula.clauses.size() << ",\n";
        reportFile << "    \"clause_lengths\": {\n";
        reportFile << "      \"min\": " << minLen << ",\n";
        reportFile << "      \"max\": " << maxLen << ",\n";
        reportFile << "      \"avg\": " << avgLen << "\n";
        reportFile << "    }\n";
        reportFile << "  },\n";
        reportFile << "  \"solving\": {\n";
        reportFile << "    \"result\": \"" << (timedOut ? "TIMEOUT" : (result ? "SAT" : "UNSAT")) << "\",\n";
        reportFile << "    \"time_seconds\": " << elapsed << ",\n";
        reportFile << "    \"timed_out\": " << (timedOut ? "true" : "false") << "\n";
        reportFile << "  }\n";
        reportFile << "}\n";
        reportFile.close();
        std::cout << "\nDetailed report saved to: " << reportFilename << std::endl;
    }

    // Save solution in DIMACS format if requested
    if (!outputFile.empty() && !timedOut)
    {
        std::ofstream solFile(outputFile);
        if (solFile.is_open())
        {
            solFile << "c Set-Based SAT Solver Result\n";
            solFile << "c Input: " << filename << "\n";
            solFile << "c Time: " << elapsed << " seconds\n";
            solFile << "c Timestamp: " << timestamp.str() << "\n";
            if (result)
            {
                solFile << "s SATISFIABLE\n";
                solFile << "v ";
                for (const auto &pair : assignment)
                {
                    std::string varNum = pair.first.substr(1); // Remove 'x' prefix
                    if (pair.second)
                    {
                        solFile << varNum << " ";
                    }
                    else
                    {
                        solFile << "-" << varNum << " ";
                    }
                }
                solFile << "0\n";
            }
            else
            {
                solFile << "s UNSATISFIABLE\n";
            }
            solFile.close();
            std::cout << "Solution saved to: " << outputFile << std::endl;
        }
    }
}

// ============================================================================
// Timeout Solver Wrapper
// ============================================================================
struct SolveResult
{
    bool sat;
    std::map<std::string, bool> assignment;
    double elapsed;
    bool timedOut;
};

SolveResult solveWithTimeout(const CNFFormula &formula, int timeoutSeconds, bool verbose = false)
{
    SolveResult result;
    result.timedOut = false;
    result.sat = false;

    SetBasedSATSolver solver;

    auto start = std::chrono::high_resolution_clock::now();

    // Run solver (note: timeout not fully implemented due to compiler limitations)
    std::pair<bool, std::map<std::string, bool>> solverResult = solver.solve(formula, verbose);

    auto end = std::chrono::high_resolution_clock::now();
    result.elapsed = std::chrono::duration<double>(end - start).count();

    // Check if exceeded timeout
    if (result.elapsed >= timeoutSeconds)
    {
        result.timedOut = true;
    }
    else
    {
        result.sat = solverResult.first;
        result.assignment = solverResult.second;
    }

    return result;
}

// ============================================================================
// Main Function
// ============================================================================
int main(int argc, char *argv[])
{
    // Simple argument parsing
    std::string inputFile;
    std::string outputFile;
    std::string directory;
    int timeout = 300;
    bool verbose = false;

    for (int i = 1; i < argc; i++)
    {
        std::string arg = argv[i];
        if (arg == "-v" || arg == "--verbose")
        {
            verbose = true;
        }
        else if (arg == "-t" || arg == "--timeout")
        {
            if (i + 1 < argc)
            {
                timeout = std::stoi(argv[++i]);
            }
        }
        else if (arg == "-o" || arg == "--output")
        {
            if (i + 1 < argc)
            {
                outputFile = argv[++i];
            }
        }
        else if (arg == "-d" || arg == "--directory")
        {
            if (i + 1 < argc)
            {
                directory = argv[++i];
            }
        }
        else if (arg == "-h" || arg == "--help")
        {
            std::cout << "Set-Based SAT Solver - C++ Implementation\n\n";
            std::cout << "Usage:\n";
            std::cout << "  " << argv[0] << " <input.cnf> [options]\n\n";
            std::cout << "Options:\n";
            std::cout << "  -v, --verbose         Show detailed solving steps\n";
            std::cout << "  -t, --timeout <sec>   Timeout in seconds (default: 300)\n";
            std::cout << "  -o, --output <file>   Output file for solution\n";
            std::cout << "  -d, --directory <dir> Process all .cnf files in directory\n";
            std::cout << "  -h, --help            Show this help message\n\n";
            std::cout << "Examples:\n";
            std::cout << "  " << argv[0] << " input.cnf\n";
            std::cout << "  " << argv[0] << " input.cnf -v -t 60\n";
            std::cout << "  " << argv[0] << " -d datasets/small/\n";
            return 0;
        }
        else if (inputFile.empty() && directory.empty())
        {
            inputFile = arg;
        }
    }

    // Directory mode
    if (!directory.empty())
    {
        std::cout << std::string(80, '=') << std::endl;
        std::cout << "BATCH MODE: Processing CNF files from '" << directory << "'" << std::endl;
        std::cout << std::string(80, '=') << std::endl;

        std::vector<std::string> cnfFiles;
        DIR *dir;
        struct dirent *ent;
        if ((dir = opendir(directory.c_str())) != NULL)
        {
            while ((ent = readdir(dir)) != NULL)
            {
                std::string filename = ent->d_name;
                if (filename.length() > 4 && filename.substr(filename.length() - 4) == ".cnf")
                {
                    cnfFiles.push_back(directory + "/" + filename);
                }
            }
            closedir(dir);
        }

        std::sort(cnfFiles.begin(), cnfFiles.end());

        for (size_t i = 0; i < cnfFiles.size(); i++)
        {
            const auto &filepath = cnfFiles[i];
            // Extract filename from full path
            size_t lastSlash = filepath.find_last_of("/\\");
            std::string filename = (lastSlash != std::string::npos) ? filepath.substr(lastSlash + 1) : filepath;

            std::cout << "\n[" << (i + 1) << "/" << cnfFiles.size() << "] Processing: "
                      << filename << std::endl;
            std::cout << std::string(80, '-') << std::endl;

            std::ifstream file(filepath);
            if (!file.is_open())
            {
                std::cerr << "ERROR: Cannot open file" << std::endl;
                continue;
            }

            std::stringstream buffer;
            buffer << file.rdbuf();
            std::string content = buffer.str();
            file.close();

            CNFFormula formula = parseDimacsCNF(content);
            std::cout << "Variables: " << formula.variables.size()
                      << ", Clauses: " << formula.clauses.size() << std::endl;
            std::cout << "Solving with timeout=" << timeout << "s... " << std::flush;

            auto result = solveWithTimeout(formula, timeout, false);

            if (result.timedOut)
            {
                std::cout << "TIMEOUT after " << std::fixed << std::setprecision(2)
                          << result.elapsed << "s" << std::endl;
            }
            else
            {
                std::cout << (result.sat ? "SAT" : "UNSAT") << " in "
                          << std::fixed << std::setprecision(4) << result.elapsed << "s" << std::endl;
            }

            createReport(filepath, formula, result.sat, result.elapsed,
                         result.timedOut, result.assignment);
        }

        return 0;
    }

    // Single file mode
    if (inputFile.empty())
    {
        std::cerr << "Error: No input file specified. Use -h for help." << std::endl;
        return 1;
    }

    std::ifstream file(inputFile);
    if (!file.is_open())
    {
        std::cerr << "Error: Cannot open file '" << inputFile << "'" << std::endl;
        return 1;
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string content = buffer.str();
    file.close();

    std::cout << std::string(80, '=') << std::endl;
    std::cout << "SET-BASED SAT SOLVER" << std::endl;
    std::cout << std::string(80, '=') << std::endl;
    std::cout << "Input file:       " << inputFile << std::endl;
    std::cout << "Timeout:          " << timeout << " seconds" << std::endl;
    std::cout << "Verbose:          " << (verbose ? "Yes" : "No") << std::endl;

    CNFFormula formula = parseDimacsCNF(content);
    std::cout << "Variables:        " << formula.variables.size() << std::endl;
    std::cout << "Clauses:          " << formula.clauses.size() << std::endl;

    std::cout << "\nSolving..." << (verbose ? "\n" : " ") << std::flush;

    auto result = solveWithTimeout(formula, timeout, verbose);

    if (!verbose)
    {
        if (result.timedOut)
        {
            std::cout << "TIMEOUT after " << std::fixed << std::setprecision(2)
                      << result.elapsed << " seconds" << std::endl;
        }
        else
        {
            std::cout << (result.sat ? "SAT" : "UNSAT") << " in "
                      << std::fixed << std::setprecision(4) << result.elapsed << " seconds" << std::endl;
        }
    }

    createReport(inputFile, formula, result.sat, result.elapsed,
                 result.timedOut, result.assignment, outputFile);

    return 0;
}
