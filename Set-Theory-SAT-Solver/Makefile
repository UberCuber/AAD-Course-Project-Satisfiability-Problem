# Makefile for Set-Based SAT Solver (C++)

CXX = g++
CXXFLAGS = -std=c++14 -O3
TARGET = set_solver
SOURCE = set_based_sat_solver.cpp

# Windows specific
ifeq ($(OS),Windows_NT)
    RM = del /Q
    TARGET_EXT = .exe
else
    RM = rm -f
    TARGET_EXT =
endif

all: $(TARGET)

$(TARGET): $(SOURCE)
$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) $(SOURCE) -o $(TARGET)$(TARGET_EXT)

debug: CXXFLAGS = -std=c++14 -g
debug: $(TARGET)
clean:
	$(RM) $(TARGET)$(TARGET_EXT)

run: $(TARGET)
	./$(TARGET)$(TARGET_EXT)

.PHONY: all debug clean run
