CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall

# Executable names
SOLVER = solver
VERIFIER = verifier

# Source files
SOLVER_SRC = cdcl_solver.cpp
VERIFIER_SRC = verifier.cpp

# Object files
SOLVER_OBJ = $(SOLVER_SRC:.cpp=.o)
VERIFIER_OBJ = $(VERIFIER_SRC:.cpp=.o)

all: $(SOLVER) $(VERIFIER)

$(SOLVER): $(SOLVER_OBJ)
	$(CXX) $(CXXFLAGS) -o $(SOLVER) $(SOLVER_OBJ)

$(VERIFIER): $(VERIFIER_OBJ)
	$(CXX) $(CXXFLAGS) -o $(VERIFIER) $(VERIFIER_OBJ)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(SOLVER) $(VERIFIER) *.o
