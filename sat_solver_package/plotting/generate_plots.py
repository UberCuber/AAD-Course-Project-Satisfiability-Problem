#!/usr/bin/env python3
"""
Professional Plot Generation for SAT Solver Benchmarking
Generates 8 comprehensive plots for research paper quality analysis
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
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Color scheme for solvers
SOLVER_COLORS = {
    'basic_dpll': '#1f77b4',
    'unit_prop': '#ff7f0e',
    'vsids': '#2ca02c',
    'dlis': '#d62728',
    'mom': '#9467bd',
    'jw': '#8c564b',
    'dlcs': '#e377c2',
    'phase_saving': '#7f7f7f',
    'backjumping': '#bcbd22',
    'random': '#17becf',
    'cdcl_solver': '#ff1493'  # Hot pink for CDCL to stand out
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
    print(f"  UF20: {len(uf20)} results")
    print(f"  UF50: {len(uf50)} results")
    print(f"  UF100: {len(uf100)} results")
    
    return df

def plot1_time_per_heuristic(df):
    """Plot 1: Line graph for each heuristic across all datasets"""
    print("\nGenerating Plot 1: Time per heuristic across datasets...")
    
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    axes = axes.flatten()
    
    solvers = df['solver'].unique()
    
    for idx, solver in enumerate(sorted(solvers)):
        ax = axes[idx]
        solver_data = df[df['solver'] == solver].copy()
        
        for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
            dataset_data = solver_data[solver_data['dataset'] == dataset].sort_values('instance')
            
            if len(dataset_data) > 0:
                # Use instance index for x-axis
                x = range(len(dataset_data))
                y = dataset_data['time_seconds'].values
                
                ax.plot(x, y, label=dataset, alpha=0.7, linewidth=1)
        
        ax.set_title(solver_data['solver_name'].iloc[0], fontweight='bold')
        ax.set_xlabel('Instance Index')
        ax.set_ylabel('Time (seconds)')
        ax.set_yscale('log')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Hide extra subplots if any
    for idx in range(len(solvers), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle('Execution Time per Solver Across Problem Sizes', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('results/plots/01_time_per_heuristic.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/01_time_per_heuristic.png")

def plot2_memory_per_heuristic(df):
    """Plot 2: Memory usage per heuristic across all datasets"""
    print("\nGenerating Plot 2: Memory per heuristic across datasets...")
    
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    axes = axes.flatten()
    
    # Exclude CDCL from this plot because memory is not instrumented for the C++ binary
    solvers = [s for s in sorted(df['solver'].unique()) if s != 'cdcl_solver']
    
    for idx, solver in enumerate(solvers):
        ax = axes[idx]
        solver_data = df[df['solver'] == solver].copy()
        
        for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
            dataset_data = solver_data[solver_data['dataset'] == dataset].sort_values('instance')
            
            if len(dataset_data) > 0:
                x = range(len(dataset_data))
                y = dataset_data['memory_kb'].values
                
                ax.plot(x, y, label=dataset, alpha=0.7, linewidth=1)
        
        ax.set_title(solver_data['solver_name'].iloc[0], fontweight='bold')
        ax.set_xlabel('Instance Index')
        ax.set_ylabel('Memory (KB)')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Hide extra subplots
    for idx in range(len(solvers), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle('Memory Usage per Solver Across Problem Sizes', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('results/plots/02_memory_per_heuristic.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/02_memory_per_heuristic.png")

def plot3_time_comparison_per_dataset(df):
    """Plot 3: Time comparison for each dataset"""
    print("\nGenerating Plot 3: Time comparison per dataset...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Calculate median time per solver
        solver_stats = dataset_data.groupby('solver').agg({
            'time_seconds': ['median', 'mean', 'std'],
            'solver_name': 'first'
        }).reset_index()
        
        solver_stats.columns = ['solver', 'median_time', 'mean_time', 'std_time', 'solver_name']
        solver_stats = solver_stats.sort_values('median_time')
        
        # Create bar plot with error bars
        x = range(len(solver_stats))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in solver_stats['solver']]
        
        ax.bar(x, solver_stats['median_time'], yerr=solver_stats['std_time'], 
               capsize=3, alpha=0.8, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x)
        ax.set_xticklabels(solver_stats['solver'], rotation=45, ha='right')
        ax.set_ylabel('Median Time (seconds)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Solver Performance Comparison by Problem Size', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/03_time_comparison_per_dataset.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/03_time_comparison_per_dataset.png")

def plot4_memory_comparison_per_dataset(df):
    """Plot 4: Memory comparison for each dataset"""
    print("\nGenerating Plot 4: Memory comparison per dataset...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Calculate median memory per solver
        solver_stats = dataset_data.groupby('solver').agg({
            'memory_kb': ['median', 'mean', 'std'],
            'solver_name': 'first'
        }).reset_index()
        
        solver_stats.columns = ['solver', 'median_mem', 'mean_mem', 'std_mem', 'solver_name']
        solver_stats = solver_stats.sort_values('median_mem')
        
        x = range(len(solver_stats))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in solver_stats['solver']]
        
        ax.bar(x, solver_stats['median_mem'], yerr=solver_stats['std_mem'],
               capsize=3, alpha=0.8, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x)
        ax.set_xticklabels(solver_stats['solver'], rotation=45, ha='right')
        ax.set_ylabel('Median Memory (KB)')
        ax.set_title(dataset, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Memory Usage Comparison by Problem Size', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/04_memory_comparison_per_dataset.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/04_memory_comparison_per_dataset.png")

def plot5_decisions_scatter(df):
    """Plot 5: Decisions required scatter plot"""
    print("\nGenerating Plot 5: Decisions scatter plot...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Sample data if too large for scatter
        if len(dataset_data) > 1000:
            dataset_data = dataset_data.sample(n=1000, random_state=42)
        
        for solver in sorted(dataset_data['solver'].unique()):
            solver_data = dataset_data[dataset_data['solver'] == solver]
            
            ax.scatter(solver_data['num_decisions'], solver_data['time_seconds'],
                      label=solver, alpha=0.6, s=20, 
                      color=SOLVER_COLORS.get(solver, '#666666'))
        
        ax.set_xlabel('Number of Decisions')
        ax.set_ylabel('Time (seconds)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(loc='best', fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Decisions vs. Time Across Solvers', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/05_decisions_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/05_decisions_scatter.png")

def plot6_time_vs_decisions_correlation(df):
    """Plot 6: Time vs decisions correlation"""
    print("\nGenerating Plot 6: Time vs decisions correlation...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # Select key solvers to highlight
    key_solvers = ['basic_dpll', 'vsids', 'cdcl_solver', 'mom', 'backjumping', 'random']
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for row, solver in enumerate(['basic_dpll', 'cdcl_solver']):
        for col, dataset in enumerate(datasets):
            ax = axes[row, col]
            
            data = df[(df['solver'] == solver) & (df['dataset'] == dataset)]
            
            if len(data) > 0:
                # Scatter plot
                ax.scatter(data['num_decisions'], data['time_seconds'], 
                          alpha=0.5, s=15, color=SOLVER_COLORS.get(solver, '#666666'))
                
                # Add trend line
                if len(data) > 1:
                    z = np.polyfit(np.log10(data['num_decisions'] + 1), 
                                  np.log10(data['time_seconds'] + 1e-6), 1)
                    p = np.poly1d(z)
                    x_trend = np.logspace(np.log10(data['num_decisions'].min()),
                                         np.log10(data['num_decisions'].max()), 100)
                    y_trend = 10 ** p(np.log10(x_trend))
                    ax.plot(x_trend, y_trend, 'r--', linewidth=2, alpha=0.7, label='Trend')
                    
                    # Calculate correlation
                    corr = data['num_decisions'].corr(data['time_seconds'])
                    ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes,
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
                ax.set_xlabel('Number of Decisions')
                ax.set_ylabel('Time (seconds)')
                ax.set_title(f"{data['solver_name'].iloc[0]} - {dataset}", fontweight='bold')
                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=8)
    
    plt.suptitle('Time-Decisions Correlation Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/06_time_decisions_correlation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/06_time_decisions_correlation.png")

def plot7_speedup_relative_to_baseline(df):
    """Plot 7: Speedup relative to baseline (basic_dpll)"""
    print("\nGenerating Plot 7: Speedup relative to baseline...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Calculate median time per solver
        solver_times = dataset_data.groupby('solver')['time_seconds'].median()
        baseline_time = solver_times.get('basic_dpll', 1.0)
        
        # Calculate speedup
        speedups = (baseline_time / solver_times).sort_values(ascending=False)
        
        # Get solver names
        solver_names = df[df['solver'].isin(speedups.index)].groupby('solver')['solver_name'].first()
        
        x = range(len(speedups))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in speedups.index]
        
        bars = ax.bar(x, speedups.values, alpha=0.8, color=colors, 
                     edgecolor='black', linewidth=0.5)
        
        # Add horizontal line at y=1 (baseline)
        ax.axhline(y=1, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Baseline (Basic DPLL)')
        
        # Color bars differently if slower than baseline
        for i, (bar, val) in enumerate(zip(bars, speedups.values)):
            if val < 1:
                bar.set_color('lightcoral')
                bar.set_alpha(0.5)
        
        ax.set_xticks(x)
        ax.set_xticklabels(speedups.index, rotation=45, ha='right')
        ax.set_ylabel('Speedup (×)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(fontsize=8)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, speedups.values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}×', ha='center', va='bottom', fontsize=7)
    
    plt.suptitle('Speedup Relative to Basic DPLL (Higher is Better)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/07_speedup_relative_to_baseline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/07_speedup_relative_to_baseline.png")

def plot8_success_rate(df):
    """Plot 8: Success rate (non-timeout rate)"""
    print("\nGenerating Plot 8: Success rate...")
    
    # Reload data to include timeouts
    uf20_all = pd.read_csv('results/uf20_benchmark.csv')
    uf50_all = pd.read_csv('results/uf50_benchmark.csv')
    uf100_all = pd.read_csv('results/uf100_benchmark.csv')
    
    uf20_all['dataset'] = 'UF20 (20 vars)'
    uf50_all['dataset'] = 'UF50 (50 vars)'
    uf100_all['dataset'] = 'UF100 (100 vars)'
    
    df_all = pd.concat([uf20_all, uf50_all, uf100_all], ignore_index=True)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df_all[df_all['dataset'] == dataset]
        
        # Calculate success rate per solver
        success_rates = []
        solver_list = []
        
        for solver in sorted(dataset_data['solver'].unique()):
            solver_data = dataset_data[dataset_data['solver'] == solver]
            total = len(solver_data)
            successful = len(solver_data[solver_data['timeout'] == 0])
            success_rate = (successful / total) * 100 if total > 0 else 0
            
            success_rates.append(success_rate)
            solver_list.append(solver)
        
        # Sort by success rate
        sorted_indices = np.argsort(success_rates)[::-1]
        success_rates = [success_rates[i] for i in sorted_indices]
        solver_list = [solver_list[i] for i in sorted_indices]
        
        x = range(len(success_rates))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in solver_list]
        
        bars = ax.bar(x, success_rates, alpha=0.8, color=colors,
                     edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x)
        ax.set_xticklabels(solver_list, rotation=45, ha='right')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_ylim([0, 105])
        ax.axhline(y=100, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add percentage labels
        for i, (bar, val) in enumerate(zip(bars, success_rates)):
            ax.text(bar.get_x() + bar.get_width()/2., val + 1,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=7)
    
    plt.suptitle('Solver Success Rate (Non-Timeout)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/08_success_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: results/plots/08_success_rate.png")

def generate_summary_statistics(df):
    """Generate summary statistics table"""
    print("\nGenerating summary statistics...")
    
    summary_data = []
    
    for dataset in ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']:
        dataset_data = df[df['dataset'] == dataset]
        
        for solver in sorted(dataset_data['solver'].unique()):
            solver_data = dataset_data[dataset_data['solver'] == solver]
            
            summary_data.append({
                'Dataset': dataset,
                'Solver': solver_data['solver_name'].iloc[0],
                'Median Time (s)': f"{solver_data['time_seconds'].median():.6f}",
                'Mean Time (s)': f"{solver_data['time_seconds'].mean():.6f}",
                'Std Time (s)': f"{solver_data['time_seconds'].std():.6f}",
                'Median Decisions': f"{solver_data['num_decisions'].median():.0f}",
                'Median Memory (KB)': f"{solver_data['memory_kb'].median():.0f}",
                'Instances': len(solver_data)
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('results/plots/summary_statistics.csv', index=False)
    print("  ✓ Saved: results/plots/summary_statistics.csv")
    
    return summary_df

def main():
    """Main function to generate all plots"""
    print("=" * 80)
    print("SAT Solver Benchmark Visualization")
    print("=" * 80)
    
    # Create output directory
    Path('results/plots').mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data()
    
    # Generate all plots
    plot1_time_per_heuristic(df)
    plot2_memory_per_heuristic(df)
    plot3_time_comparison_per_dataset(df)
    plot4_memory_comparison_per_dataset(df)
    plot5_decisions_scatter(df)
    plot6_time_vs_decisions_correlation(df)
    plot7_speedup_relative_to_baseline(df)
    plot8_success_rate(df)
    
    # Generate summary statistics
    summary = generate_summary_statistics(df)
    
    print("\n" + "=" * 80)
    print("All plots generated successfully!")
    print("=" * 80)
    print("\nPlots saved in: results/plots/")
    print("\n1. 01_time_per_heuristic.png - Time trends for each solver")
    print("2. 02_memory_per_heuristic.png - Memory usage trends")
    print("3. 03_time_comparison_per_dataset.png - Performance comparison")
    print("4. 04_memory_comparison_per_dataset.png - Memory comparison")
    print("5. 05_decisions_scatter.png - Decisions vs time scatter")
    print("6. 06_time_decisions_correlation.png - Correlation analysis")
    print("7. 07_speedup_relative_to_baseline.png - Speedup metrics")
    print("8. 08_success_rate.png - Solver success rates")
    print("\nSummary: summary_statistics.csv")
    print("=" * 80)

if __name__ == '__main__':
    main()
