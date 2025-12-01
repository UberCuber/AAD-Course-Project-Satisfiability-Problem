#!/usr/bin/env python3
"""
Generate Individual Plots for Each Solver
Creates separate high-quality plots for time and memory per solver
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

# Configure matplotlib for high-quality output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.markersize'] = 4
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Color scheme for datasets
DATASET_COLORS = {
    'UF20 (20 vars)': '#2E86AB',    # Blue
    'UF50 (50 vars)': '#A23B72',    # Purple
    'UF100 (100 vars)': '#F18F01'   # Orange
}

# Marker styles for datasets
DATASET_MARKERS = {
    'UF20 (20 vars)': 'o',
    'UF50 (50 vars)': 's',
    'UF100 (100 vars)': '^'
}

def load_data():
    """Load all benchmark data"""
    print("Loading benchmark data...")
    
    uf20 = pd.read_csv('results/uf20_benchmark.csv')
    uf50 = pd.read_csv('results/uf50_benchmark.csv')
    uf100 = pd.read_csv('results/uf100_benchmark.csv')
    
    # Add dataset identifier
    uf20['dataset'] = 'UF20 (20 vars)'
    uf50['dataset'] = 'UF50 (50 vars)'
    uf100['dataset'] = 'UF100 (100 vars)'
    
    # Add variable count for sorting
    uf20['num_vars'] = 20
    uf50['num_vars'] = 50
    uf100['num_vars'] = 100
    
    # Combine all data
    df = pd.concat([uf20, uf50, uf100], ignore_index=True)
    
    # Convert time to float and filter out timeouts/errors
    df['time_seconds'] = pd.to_numeric(df['time_seconds'], errors='coerce')
    df = df[df['timeout'] == 0]
    df = df[df['result'].isin(['SAT', 'UNSAT'])]
    
    print(f"Loaded {len(df)} results")
    
    return df

def plot_individual_time(df, solver, solver_name, output_dir):
    """Create individual time plot for a solver"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    solver_data = df[df['solver'] == solver].copy()
    
    for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
        dataset_data = solver_data[solver_data['dataset'] == dataset].sort_values('instance')
        
        if len(dataset_data) > 0:
            # Use instance index for x-axis
            x = range(len(dataset_data))
            y = dataset_data['time_seconds'].values
            
            # Plot with markers
            ax.plot(x, y, 
                   label=dataset, 
                   alpha=0.8, 
                   linewidth=2,
                   marker=DATASET_MARKERS[dataset],
                   markersize=3,
                   markevery=max(1, len(x) // 30),  # Show ~30 markers
                   color=DATASET_COLORS[dataset])
    
    ax.set_title(f'{solver_name}', fontweight='bold', fontsize=14)
    ax.set_xlabel('Instance Index', fontsize=12)
    ax.set_ylabel('Execution Time (seconds)', fontsize=12)
    ax.set_yscale('log')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics box
    stats_text = []
    for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
        dataset_data = solver_data[solver_data['dataset'] == dataset]
        if len(dataset_data) > 0:
            median_time = dataset_data['time_seconds'].median()
            stats_text.append(f"{dataset.split()[0]}: {median_time:.4f}s")
    
    if stats_text:
        textstr = 'Median Times:\n' + '\n'.join(stats_text)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/time_{solver}.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_individual_memory(df, solver, solver_name, output_dir):
    """Create individual memory plot for a solver"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    solver_data = df[df['solver'] == solver].copy()
    
    for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
        dataset_data = solver_data[solver_data['dataset'] == dataset].sort_values('instance')
        
        if len(dataset_data) > 0:
            x = range(len(dataset_data))
            y = dataset_data['memory_kb'].values
            
            # Plot with markers
            ax.plot(x, y, 
                   label=dataset, 
                   alpha=0.8, 
                   linewidth=2,
                   marker=DATASET_MARKERS[dataset],
                   markersize=3,
                   markevery=max(1, len(x) // 30),  # Show ~30 markers
                   color=DATASET_COLORS[dataset])
    
    ax.set_title(f'{solver_name}', fontweight='bold', fontsize=14)
    ax.set_xlabel('Instance Index', fontsize=12)
    ax.set_ylabel('Memory Usage (KB)', fontsize=12)
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics box
    stats_text = []
    for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
        dataset_data = solver_data[solver_data['dataset'] == dataset]
        if len(dataset_data) > 0:
            median_mem = dataset_data['memory_kb'].median()
            stats_text.append(f"{dataset.split()[0]}: {median_mem:.0f} KB")
    
    if stats_text:
        textstr = 'Median Memory:\n' + '\n'.join(stats_text)
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/memory_{solver}.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main function to generate individual plots"""
    print("=" * 80)
    print("Individual Solver Plot Generation")
    print("=" * 80)
    
    # Create output directories
    time_dir = Path('results/plots/individual_time')
    memory_dir = Path('results/plots/individual_memory')
    time_dir.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data()
    
    # Get unique solvers
    solvers = sorted(df['solver'].unique())
    solver_names = df.groupby('solver')['solver_name'].first()
    
    print(f"\nGenerating individual plots for {len(solvers)} solvers...")
    print("-" * 80)
    
    # Generate plots for each solver
    for idx, solver in enumerate(solvers, 1):
        solver_name = solver_names[solver]
        
        print(f"[{idx}/{len(solvers)}] {solver_name}")
        
        # Time plot
        plot_individual_time(df, solver, solver_name, time_dir)
        print(f"  ✓ Time plot: individual_time/time_{solver}.png")
        
        # Memory plot
        plot_individual_memory(df, solver, solver_name, memory_dir)
        print(f"  ✓ Memory plot: individual_memory/memory_{solver}.png")
    
    print("\n" + "=" * 80)
    print("All individual plots generated successfully!")
    print("=" * 80)
    print(f"\nTime plots saved in: {time_dir}/")
    print(f"Memory plots saved in: {memory_dir}/")
    print(f"\nTotal: {len(solvers)} time plots + {len(solvers)} memory plots = {len(solvers)*2} plots")
    print("=" * 80)

if __name__ == '__main__':
    main()
