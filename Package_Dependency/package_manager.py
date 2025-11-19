import sys
import json
import argparse

# ==============================================================================
# INTEGRATION SECTION: CONNECTING TO YOUR dpll_basic.py
# ==============================================================================
try:
    # We import the specific function 'dpll' from your file 'dpll_basic'
    from dpll_basic import dpll
except ImportError:
    print("\n⚠️  IMPORT ERROR: Could not find 'dpll_basic.py'.")
    print("    Make sure the file is named exactly 'dpll_basic.py'")
    sys.exit(1)

# We create a wrapper class so the Package Manager treats it like an object
class SolverAdapter:
    def solve(self, clauses, n_vars):
        """
        Adapts the package manager's call style to your dpll function.
        """
        # Your dpll function takes (clauses, assignment_dict)
        # We pass an empty dict {} as the starting assignment
        return dpll(clauses, {})

# ==============================================================================
# PACKAGE MANAGER LOGIC
# ==============================================================================

class PackageProblemEncoder:
    def __init__(self):
        self.package_to_id = {}  
        self.id_to_package = {}  
        self.clauses = []        
        self.counter = 1         

    def get_id(self, package_name):
        if package_name not in self.package_to_id:
            self.package_to_id[package_name] = self.counter
            self.id_to_package[self.counter] = package_name
            self.counter += 1
        return self.package_to_id[package_name]

    def add_dependency(self, pkg, depends_on):
        """ A -> B  ===  (!A or B) """
        p_id = self.get_id(pkg)
        d_id = self.get_id(depends_on)
        self.clauses.append([-p_id, d_id])

    def add_conflict(self, pkg1, pkg2):
        """ !(A and B) === (!A or !B) """
        p1 = self.get_id(pkg1)
        p2 = self.get_id(pkg2)
        self.clauses.append([-p1, -p2])

    def load_repository(self, json_file):
        """Parses a JSON file to build the dependency graph."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            print(f"Loading repository from '{json_file}'...")

            # 1. Load Dependencies
            deps = data.get("dependencies", {})
            for pkg, required_list in deps.items():
                for req in required_list:
                    self.add_dependency(pkg, req)
            
            # 2. Load Explicit Conflicts
            conflicts = data.get("conflicts", [])
            for pair in conflicts:
                if len(pair) == 2:
                    self.add_conflict(pair[0], pair[1])

            # 3. Load Version Constraints (At-Most-One)
            versions = data.get("versions", [])
            for v_group in versions:
                for i in range(len(v_group)):
                    for j in range(i + 1, len(v_group)):
                        self.add_conflict(v_group[i], v_group[j])
            
            print(f"Repository loaded. ({self.counter-1} packages identified)")
            
        except FileNotFoundError:
            print(f"Error: File '{json_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from '{json_file}'.")
            sys.exit(1)

    def solve_install_request(self, target_packages):
        """
        Attempts to install MULTIPLE packages simultaneously.
        Example: target_packages = ["VideoPlayer", "Codecs-v2"]
        """
        print(f"\n--- Processing Request: Install {target_packages} ---")
        
        # Create a copy of the clauses for this specific run
        current_clauses = [c[:] for c in self.clauses]
        
        # Add a UNIT CLAUSE for every package the user requested
        # This forces the solver to try and make ALL of them True
        for pkg in target_packages:
            # Ensure package exists in our ID map
            if pkg not in self.package_to_id:
                _ = self.get_id(pkg)
            
            pkg_id = self.get_id(pkg)
            current_clauses.append([pkg_id])
        
        n_vars = self.counter - 1
        
        # --- CALL DPLL SOLVER ---
        solver = SolverAdapter()
        result = solver.solve(current_clauses, n_vars)
        
        if result is not None:
            print("✅ Plan Approved. Packages to install:")
            installed = []
            for var_id, is_true in result.items():
                if is_true:
                    name = self.id_to_package.get(var_id, f"Unknown-{var_id}")
                    installed.append(name)
            installed.sort()
            print(", ".join(installed))
            return True
        else:
            print(f"❌ Error: Cannot install {target_packages} due to conflicts.")
            return False
# ==========================================
# COMMAND LINE INTERFACE (CLI)
# ==========================================
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="SAT-Based Package Manager")
        parser.add_argument("repo_file", help="Path to the repository.json file")
        # Change: nargs='+' allows 1 or more package names
        parser.add_argument("install_pkgs", nargs='+', help="Names of packages to install")
        args = parser.parse_args()
        
        pm = PackageProblemEncoder()
        pm.load_repository(args.repo_file)
        # Pass the LIST of packages to the updated function
        pm.solve_install_request(args.install_pkgs)
        
    