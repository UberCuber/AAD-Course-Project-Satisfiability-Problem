import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_sat_unsat_comparison_plot(sat_csv_path, unsat_csv_path):
    """
    Creates a comparison plot of SAT vs UNSAT solver performance metrics
    """
    # Read the CSV files
    sat_df = pd.read_csv(sat_csv_path)
    unsat_df = pd.read_csv(unsat_csv_path)
    
    # Calculate aggregate statistics for each dataset
    sat_stats = {
        'avg_time': sat_df['avg_time_sec'].mean(),
        'median_time': sat_df['median_time_sec'].mean(),
        'stdev_time': sat_df['stdev_time_sec'].mean()
    }
    
    unsat_stats = {
        'avg_time': unsat_df['avg_time_sec'].mean(),
        'median_time': unsat_df['median_time_sec'].mean(), 
        'stdev_time': unsat_df['stdev_time_sec'].mean()
    }
    
    # Prepare data for plotting
    metrics = ['avg_time_sec', 'median_time_sec', 'stdev_time_sec']
    sat_values = [sat_stats['avg_time'], sat_stats['median_time'], sat_stats['stdev_time']]
    unsat_values = [unsat_stats['avg_time'], unsat_stats['median_time'], unsat_stats['stdev_time']]
    
    # Set up the plot
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bars
    sat_bars = ax.bar(x - width/2, sat_values, width, label='SAT', color='#4285F4', alpha=0.8)
    unsat_bars = ax.bar(x + width/2, unsat_values, width, label='UNSAT', color='#EA4335', alpha=0.8)
    
    # Customize the plot
    ax.set_xlabel('Time Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('SAT vs UNSAT Solver Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.4f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=9)
    
    add_value_labels(sat_bars)
    add_value_labels(unsat_bars)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print("\n===== Performance Summary =====")
    print(f"SAT Instances ({len(sat_df)} files):")
    print(f"  Average Time: {sat_stats['avg_time']:.6f}s")
    print(f"  Median Time:  {sat_stats['median_time']:.6f}s") 
    print(f"  Std Dev Time: {sat_stats['stdev_time']:.6f}s")
    
    print(f"\nUNSAT Instances ({len(unsat_df)} files):")  
    print(f"  Average Time: {unsat_stats['avg_time']:.6f}s")
    print(f"  Median Time:  {unsat_stats['median_time']:.6f}s")
    print(f"  Std Dev Time: {unsat_stats['stdev_time']:.6f}s")
    print("===============================")

# Alternative version with sum totals instead of averages
def create_sat_unsat_total_comparison_plot(sat_csv_path, unsat_csv_path):
    """
    Creates a comparison plot showing total time across all instances
    """
    # Read the CSV files
    sat_df = pd.read_csv(sat_csv_path)
    unsat_df = pd.read_csv(unsat_csv_path)
    
    # Calculate total statistics
    sat_totals = {
        'avg_time': sat_df['avg_time_sec'].sum(),
        'median_time': sat_df['median_time_sec'].sum(),
        'stdev_time': sat_df['stdev_time_sec'].sum()
    }
    
    unsat_totals = {
        'avg_time': unsat_df['avg_time_sec'].sum(),
        'median_time': unsat_df['median_time_sec'].sum(),
        'stdev_time': unsat_df['stdev_time_sec'].sum()
    }
    
    # Prepare data for plotting
    metrics = ['Total Avg Time', 'Total Median Time', 'Total Std Dev']
    sat_values = [sat_totals['avg_time'], sat_totals['median_time'], sat_totals['stdev_time']]
    unsat_values = [unsat_totals['avg_time'], unsat_totals['median_time'], unsat_totals['stdev_time']]
    
    # Set up the plot
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create bars
    sat_bars = ax.bar(x - width/2, sat_values, width, label='SAT', color='#4285F4', alpha=0.8)
    unsat_bars = ax.bar(x + width/2, unsat_values, width, label='UNSAT', color='#EA4335', alpha=0.8)
    
    # Customize the plot
    ax.set_xlabel('Time Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('SAT vs UNSAT Test Suite Execution Durations (s)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=10, fontweight='bold')
    
    add_value_labels(sat_bars)
    add_value_labels(unsat_bars)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Usage example - replace with your actual file paths
    sat_csv = "dpll_results_sat.csv"  # Your SAT results file
    unsat_csv = "dpll_results_unsat.csv"  # Your UNSAT results file
    
    # Create average comparison plot
    print("Creating average-based comparison plot...")
    create_sat_unsat_comparison_plot(sat_csv, unsat_csv)
    
    # Create total comparison plot (like in your reference image)
    print("Creating total-based comparison plot...")
    create_sat_unsat_total_comparison_plot(sat_csv, unsat_csv)