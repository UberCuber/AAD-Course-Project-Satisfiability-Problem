import time
import random
import matplotlib.pyplot as plt
import numpy as np
from walksat import WalkSATSolver

# --- EXPERIMENTAL CONFIGURATION ---
# Adjusted to balance statistical significance with runtime [cite: 43]
TRIALS_PER_POINT = 20       # Sufficient sample size for student projects
MAX_FLIPS = 10000           # Cutoff to prevent infinite loops on hard instances
MAX_TRIES = 1               # Single restart sequence
NOISE_LEVELS = [0.0, 0.2, 0.4, 0.5, 0.55, 0.6, 0.8, 1.0] # Key points + sweet spot
VAR_COUNTS = [20, 40, 60, 80, 100]

# Hardness Parameters
RATIO_HARD = 4.26           # Phase transition (for Noise Experiment)
RATIO_EASY = 3.5            # Under-constrained (for Scalability Experiment)

def generate_random_3sat(n_vars, clause_ratio):
    """Generates a random 3-SAT instance."""
    n_clauses = int(n_vars * clause_ratio)
    clauses = []
    for _ in range(n_clauses):
        vars_in_clause = random.sample(range(1, n_vars + 1), 3)
        clause = [v if random.random() > 0.5 else -v for v in vars_in_clause]
        clauses.append(clause)
    return clauses

def run_trials(n_vars, p, ratio, num_trials):
    """Runs multiple trials on FRESH instances to get avg runtime."""
    success_times = []
    success_count = 0

    for i in range(num_trials):
        clauses = generate_random_3sat(n_vars, clause_ratio=ratio)
        solver = WalkSATSolver()
        solver.load_from_list(clauses, n_vars)
        
        start = time.time()
        result = solver.solve(max_flips=MAX_FLIPS, max_tries=MAX_TRIES, p=p)
        duration = time.time() - start
        
        if result:
            success_count += 1
            success_times.append(duration)
        
        # Simple progress indicator
        print(".", end="", flush=True)

    avg_time = np.mean(success_times) if success_times else 0
    return avg_time, success_count

def benchmark_noise_sensitivity():
    """
    Experiment 1: Noise Sensitivity
    Uses HARD instances (ratio 4.26) to prove noise is needed to escape local minima.
    """
    print(f"\n\n--- Exp 1: Noise Sensitivity (N=50, Ratio={RATIO_HARD}) ---")
    n_vars = 50
    avg_times = []
    
    for p in NOISE_LEVELS:
        print(f"\nTesting p={p}: ", end="")
        avg_t, successes = run_trials(n_vars, p, RATIO_HARD, TRIALS_PER_POINT)
        avg_times.append(avg_t)
        print(f" Time: {avg_t:.4f}s | Success: {successes}/{TRIALS_PER_POINT}")

    plt.figure(figsize=(10, 6))
    plt.plot(NOISE_LEVELS, avg_times, marker='o', color='b', label='Avg Runtime')
    plt.axvline(x=0.57, color='r', linestyle='--', label='Theoretical Optimum (~0.57)')
    plt.xlabel('Noise Probability (p)')
    plt.ylabel('Time to Solve (seconds)')
    plt.title(f'WalkSAT Performance vs. Noise (N={n_vars})')
    plt.legend()
    plt.grid(True)
    plt.savefig('walksat_noise.png')
    print("\nSaved 'walksat_noise.png'")

def benchmark_scalability():
    """
    Experiment 2: Scalability
    Uses EASIER instances (ratio 3.5) to isolate scaling behavior without timeouts.
    """
    print(f"\n\n--- Exp 2: Scalability (p=0.55, Ratio={RATIO_EASY}) ---")
    p_optimal = 0.55
    times = []
    
    for n in VAR_COUNTS:
        print(f"\nTesting N={n}: ", end="")
        avg_t, successes = run_trials(n, p_optimal, RATIO_EASY, TRIALS_PER_POINT)
        times.append(avg_t)
        print(f" Time: {avg_t:.4f}s | Success: {successes}/{TRIALS_PER_POINT}")

    plt.figure(figsize=(10, 6))
    plt.plot(VAR_COUNTS, times, marker='s', color='g', label='WalkSAT Scaling')
    plt.xlabel('Number of Variables (N)')
    plt.ylabel('Runtime (s)')
    plt.title('WalkSAT Scalability (Polynomial-like on Random SAT)')
    plt.grid(True)
    plt.savefig('walksat_scalability.png')
    print("\nSaved 'walksat_scalability.png'")

if __name__ == "__main__":
    benchmark_noise_sensitivity()
    benchmark_scalability()
    plt.show()