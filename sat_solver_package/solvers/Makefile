# Makefile for SAT Solvers

CXX = g++
CXXFLAGS = -std=c++17 -O3 -Wall -I./include
BUILD_DIR = build
SOLVERS_DIR = solvers

# List of all solvers
SOLVERS = basic_dpll unit_prop vsids dlis mom jw dlcs phase_saving backjumping random cdcl

# Build all solvers
all: $(SOLVERS)

# Generic rule for building each solver
%: $(SOLVERS_DIR)/%.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/$@ $<

# Individual targets
basic_dpll: $(SOLVERS_DIR)/basic_dpll.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/basic_dpll $<

unit_prop: $(SOLVERS_DIR)/unit_prop.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/unit_prop $<

vsids: $(SOLVERS_DIR)/vsids.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/vsids $<

dlis: $(SOLVERS_DIR)/dlis.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/dlis $<

mom: $(SOLVERS_DIR)/mom.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/mom $<

jw: $(SOLVERS_DIR)/jw.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/jw $<

dlcs: $(SOLVERS_DIR)/dlcs.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/dlcs $<

phase_saving: $(SOLVERS_DIR)/phase_saving.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/phase_saving $<

backjumping: $(SOLVERS_DIR)/backjumping.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/backjumping $<

random: $(SOLVERS_DIR)/random.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/random $<

cdcl: $(SOLVERS_DIR)/cdcl.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/cdcl $<

# Verifier
verifier: verifier.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -o $(BUILD_DIR)/verifier $<

# Clean build directory
clean:
	rm -rf $(BUILD_DIR)

# Rebuild all
rebuild: clean all

.PHONY: all clean rebuild
