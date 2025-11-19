import sys
import json
import argparse

# ==============================================================================
# INTEGRATION: IMPORT YOUR TEAM'S DPLL SOLVER
# ==============================================================================
try:
    from dpll_basic import dpll
except ImportError:
    print("⚠️ Error: Could not import 'dpll' from 'dpll_basic.py'")
    sys.exit(1)

class SolverAdapter:
    """Wrapper to make the function look like a class"""
    def solve(self, clauses, n_vars):
        return dpll(clauses, {})

# ==============================================================================
# HARDWARE VERIFICATION ENGINE
# ==============================================================================
class CircuitVerifier:
    def __init__(self):
        self.clauses = []
        self.var_count = 0
        self.gate_map = {} # Maps string names (e.g. "wire_1") to integer IDs

    def get_var_id(self, name):
        """Returns the SAT ID for a wire name, creating it if new."""
        if name not in self.gate_map:
            self.var_count += 1
            self.gate_map[name] = self.var_count
        return self.gate_map[name]

    # --- TSEITIN TRANSFORMATIONS ---
    def add_gate(self, gate_type, inputs, output):
        """Dispatch method to add gates based on string type."""
        out = self.get_var_id(output)
        ins = [self.get_var_id(n) for n in inputs]

        if gate_type == "AND":
            self._add_and(ins[0], ins[1], out)
        elif gate_type == "OR":
            self._add_or(ins[0], ins[1], out)
        elif gate_type == "NOT":
            self._add_not(ins[0], out)
        elif gate_type == "NAND":
            self._add_nand(ins[0], ins[1], out)
        elif gate_type == "XOR":
            self._add_xor(ins[0], ins[1], out)
        else:
            print(f"⚠️ Warning: Unknown gate type '{gate_type}'")

    def _add_and(self, a, b, out):
        self.clauses.append([-a, -b, out])
        self.clauses.append([a, -out])
        self.clauses.append([b, -out])

    def _add_or(self, a, b, out):
        self.clauses.append([a, b, -out])
        self.clauses.append([-a, out])
        self.clauses.append([-b, out])

    def _add_not(self, a, out):
        self.clauses.append([-a, -out])
        self.clauses.append([a, out])

    def _add_nand(self, a, b, out):
        self.clauses.append([-a, -b, -out])
        self.clauses.append([a, out])
        self.clauses.append([b, out])

    def _add_xor(self, a, b, out):
        self.clauses.append([-a, -b, -out])
        self.clauses.append([a, b, -out])
        self.clauses.append([a, -b, out])
        self.clauses.append([-a, b, out])

    def verify_json_scenario(self, json_file, scenario_name):
        """Parses JSON and builds the Miter circuit."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if scenario_name not in data:
                print(f"Error: Scenario '{scenario_name}' not found in {json_file}")
                return

            scenario = data[scenario_name]
            print(f"\n--- Scenario: {scenario_name} ---")
            print(f"Description: {scenario.get('description', '')}")

            # 1. Build the internal circuits
            for g in scenario['gates']:
                self.add_gate(g['type'], g['in'], g['out'])

            # 2. Build the Miter (XOR the two comparison outputs)
            compare_nodes = scenario['compare']
            ref_out = self.get_var_id(compare_nodes[0])
            opt_out = self.get_var_id(compare_nodes[1])
            
            miter_out = self.get_var_id("miter_final")
            self._add_xor(ref_out, opt_out, miter_out)

            # 3. Assert Difference (Unit Clause)
            self.clauses.append([miter_out])
            
            # 4. Solve
            self.run_verification(scenario['inputs'])

        except FileNotFoundError:
            print("Error: JSON file not found.")

    def run_verification(self, input_names):
        print(f"Verifying... ({self.var_count} wires, {len(self.clauses)} clauses)")
        solver = SolverAdapter()
        result = solver.solve(self.clauses, self.var_count)
        
        if result is None:
            print("\n✅ RESULT: UNSAT (Equivalent)")
            print("   Success: No input combination makes the outputs differ.")
        else:
            print("\n❌ RESULT: SAT (Not Equivalent)")
            print("   Bug Found! Counter-example inputs:")
            inputs_found = []
            for name in input_names:
                vid = self.gate_map.get(name)
                val = result.get(vid, False)
                # If result returns DIMACS list instead of dict
                if isinstance(result, list):
                    val = vid in result
                inputs_found.append(f"{name}={int(val)}")
            print(f"   {', '.join(inputs_found)}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hardware Equivalence Checker")
    parser.add_argument("json_file", help="Path to circuits.json")
    parser.add_argument("scenario", help="Name of the test case (key in JSON)")
    
    # Optional: if no args, run a default
    if len(sys.argv) == 1:
        print("Usage: python hardware_verify.py circuits.json DeMorgan_Test")
        sys.exit(1)

    args = parser.parse_args()
    
    verifier = CircuitVerifier()
    verifier.verify_json_scenario(args.json_file, args.scenario)