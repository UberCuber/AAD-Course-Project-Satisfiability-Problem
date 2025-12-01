#!/usr/bin/env python3
"""
Advanced Analysis Plots for SAT Solver Benchmarking
Generates additional insightful visualizations beyond the basic 8 plots
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

# Configure matplotlib
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

# Color scheme
SOLVER_COLORS = {
    'basic_dpll': '#1f77b4', 'unit_prop': '#ff7f0e', 'vsids': '#2ca02c',
    'dlis': '#d62728', 'mom': '#9467bd', 'jw': '#8c564b',
    'dlcs': '#e377c2', 'phase_saving': '#7f7f7f', 'backjumping': '#bcbd22',
    'random': '#17becf', 'cdcl_solver': '#ff1493'
}

def load_data():
    """Load all benchmark data"""
    print("Loading benchmark data...")
    
    uf20 = pd.read_csv('results/uf20_benchmark.csv')
    uf50 = pd.read_csv('results/uf50_benchmark.csv')
    uf100 = pd.read_csv('results/uf100_benchmark.csv')
    
    uf20['dataset'] = 'UF20 (20 vars)'
    uf50['dataset'] = 'UF50 (50 vars)'
    uf100['dataset'] = 'UF100 (100 vars)'
    
    uf20['num_vars'] = 20
    uf50['num_vars'] = 50
    uf100['num_vars'] = 100
    
    df = pd.concat([uf20, uf50, uf100], ignore_index=True)
    df['time_seconds'] = pd.to_numeric(df['time_seconds'], errors='coerce')
    df = df[df['timeout'] == 0]
    df = df[df['result'].isin(['SAT', 'UNSAT'])]
    
    return df

def plot_a1_backtrack_efficiency(df):
    """Plot A1: Backtrack Efficiency - Time per Backtrack"""
    print("\nGenerating Advanced Plot A1: Backtrack Efficiency...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset].copy()
        
        # Calculate time per backtrack (excluding solvers with 0 backtracks)
        dataset_data = dataset_data[dataset_data['num_backtracks'] > 0]
        dataset_data['time_per_backtrack'] = dataset_data['time_seconds'] / dataset_data['num_backtracks']
        
        solver_stats = dataset_data.groupby('solver').agg({
            'time_per_backtrack': ['median', 'std'],
            'solver_name': 'first'
        }).reset_index()
        
        solver_stats.columns = ['solver', 'median_tpb', 'std_tpb', 'solver_name']
        solver_stats = solver_stats.sort_values('median_tpb')
        
        x = range(len(solver_stats))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in solver_stats['solver']]
        
        ax.bar(x, solver_stats['median_tpb'] * 1000, yerr=solver_stats['std_tpb'] * 1000,
               capsize=3, alpha=0.8, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xticks(x)
        ax.set_xticklabels(solver_stats['solver'], rotation=45, ha='right')
        ax.set_ylabel('Time per Backtrack (ms)')
        ax.set_title(dataset, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Backtracking Efficiency: Time Cost per Backtrack Operation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A01_backtrack_efficiency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A01_backtrack_efficiency.png")

def plot_a2_decision_quality(df):
    """Plot A2: Decision Quality - Backtracks per Decision"""
    print("\nGenerating Advanced Plot A2: Decision Quality...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset].copy()
        
        # Calculate backtracks per decision (decision quality metric)
        dataset_data = dataset_data[dataset_data['num_decisions'] > 0]
        dataset_data['backtracks_per_decision'] = dataset_data['num_backtracks'] / dataset_data['num_decisions']
        
        solver_stats = dataset_data.groupby('solver').agg({
            'backtracks_per_decision': ['median', 'mean'],
            'solver_name': 'first'
        }).reset_index()
        
        solver_stats.columns = ['solver', 'median_bpd', 'mean_bpd', 'solver_name']
        solver_stats = solver_stats.sort_values('median_bpd')
        
        x = range(len(solver_stats))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in solver_stats['solver']]
        
        # Create bar plot
        bars = ax.bar(x, solver_stats['median_bpd'], alpha=0.8, color=colors,
                     edgecolor='black', linewidth=0.5)
        
        # Highlight good performers (low backtracks per decision)
        for i, (bar, val) in enumerate(zip(bars, solver_stats['median_bpd'])):
            if val < 1.0:  # Good: fewer backtracks than decisions
                bar.set_edgecolor('green')
                bar.set_linewidth(2)
        
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='1:1 Ratio')
        
        ax.set_xticks(x)
        ax.set_xticklabels(solver_stats['solver'], rotation=45, ha='right')
        ax.set_ylabel('Backtracks per Decision')
        ax.set_title(dataset, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Decision Quality: Backtracks per Decision (Lower is Better)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A02_decision_quality.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A02_decision_quality.png")

def plot_a3_scalability_analysis(df):
    """Plot A3: Scalability - How solvers scale with problem size"""
    print("\nGenerating Advanced Plot A3: Scalability Analysis...")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Calculate median time for each solver-dataset combination
    scalability_data = df.groupby(['solver', 'num_vars']).agg({
        'time_seconds': 'median',
        'solver_name': 'first'
    }).reset_index()
    
    # Plot lines for each solver
    for solver in sorted(scalability_data['solver'].unique()):
        solver_data = scalability_data[scalability_data['solver'] == solver]
        
        ax.plot(solver_data['num_vars'], solver_data['time_seconds'],
               marker='o', markersize=8, linewidth=2.5, alpha=0.8,
               label=solver_data['solver_name'].iloc[0],
               color=SOLVER_COLORS.get(solver, '#666666'))
    
    ax.set_xlabel('Number of Variables', fontsize=12, fontweight='bold')
    ax.set_ylabel('Median Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Scalability Analysis: Performance Growth with Problem Size', fontsize=14, fontweight='bold')
    ax.set_xticks([20, 50, 100])
    ax.set_yscale('log')
    ax.legend(loc='best', ncol=2, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A03_scalability_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A03_scalability_analysis.png")

def plot_a4_performance_distribution(df):
    """Plot A4: Performance Distribution - Violin plots showing variance"""
    print("\nGenerating Advanced Plot A4: Performance Distribution...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Prepare data for violin plot
        solvers_ordered = dataset_data.groupby('solver')['time_seconds'].median().sort_values().index
        
        plot_data = []
        positions = []
        for i, solver in enumerate(solvers_ordered):
            solver_times = dataset_data[dataset_data['solver'] == solver]['time_seconds'].values
            plot_data.append(solver_times)
            positions.append(i)
        
        # Create violin plot
        parts = ax.violinplot(plot_data, positions=positions, widths=0.7, showmeans=True, showmedians=True)
        
        # Color the violins
        for i, pc in enumerate(parts['bodies']):
            solver = solvers_ordered[i]
            pc.set_facecolor(SOLVER_COLORS.get(solver, '#666666'))
            pc.set_alpha(0.7)
        
        ax.set_xticks(positions)
        ax.set_xticklabels(solvers_ordered, rotation=45, ha='right')
        ax.set_ylabel('Execution Time (seconds)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Performance Distribution: Time Variance Across Instances', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A04_performance_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A04_performance_distribution.png")

def plot_a5_heatmap_solver_comparison(df):
    """Plot A5: Heatmap - Pairwise solver comparison"""
    print("\nGenerating Advanced Plot A5: Solver Comparison Heatmap...")
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Create pivot table of median times
        solver_times = dataset_data.groupby('solver')['time_seconds'].median().sort_values()
        solvers = solver_times.index.tolist()
        
        # Calculate speedup matrix
        speedup_matrix = np.zeros((len(solvers), len(solvers)))
        for i, solver_i in enumerate(solvers):
            for j, solver_j in enumerate(solvers):
                time_i = solver_times[solver_i]
                time_j = solver_times[solver_j]
                speedup_matrix[i, j] = time_j / time_i  # How much faster is i compared to j
        
        # Create heatmap
        im = ax.imshow(speedup_matrix, cmap='RdYlGn', aspect='auto', vmin=0.5, vmax=2.0)
        
        ax.set_xticks(range(len(solvers)))
        ax.set_yticks(range(len(solvers)))
        ax.set_xticklabels(solvers, rotation=45, ha='right')
        ax.set_yticklabels(solvers)
        ax.set_title(dataset, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Speedup Factor', rotation=270, labelpad=20)
        
        # Add text annotations
        for i in range(len(solvers)):
            for j in range(len(solvers)):
                text = ax.text(j, i, f'{speedup_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=6)
    
    plt.suptitle('Pairwise Speedup Comparison (Row/Column Ratio)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A05_solver_comparison_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A05_solver_comparison_heatmap.png")

def plot_a6_efficiency_frontier(df):
    """Plot A6: Pareto Frontier - Time vs Decisions trade-off"""
    print("\nGenerating Advanced Plot A6: Efficiency Frontier...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Calculate median decisions and time per solver
        solver_stats = dataset_data.groupby('solver').agg({
            'num_decisions': 'median',
            'time_seconds': 'median',
            'solver_name': 'first'
        }).reset_index()
        
        # Scatter plot
        for _, row in solver_stats.iterrows():
            ax.scatter(row['num_decisions'], row['time_seconds'],
                      s=200, alpha=0.7, color=SOLVER_COLORS.get(row['solver'], '#666666'),
                      edgecolors='black', linewidth=1.5, zorder=3)
            
            # Add labels
            ax.annotate(row['solver'], 
                       xy=(row['num_decisions'], row['time_seconds']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=7, alpha=0.8)
        
        ax.set_xlabel('Median Decisions')
        ax.set_ylabel('Median Time (seconds)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add diagonal reference lines
        ax.plot([1, 10000], [1e-4, 100], 'k--', alpha=0.2, linewidth=1, label='Reference')
    
    plt.suptitle('Efficiency Frontier: Decision Count vs. Execution Time', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A06_efficiency_frontier.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A06_efficiency_frontier.png")

def plot_a7_variance_analysis(df):
    """Plot A7: Performance Variance - Coefficient of Variation"""
    print("\nGenerating Advanced Plot A7: Performance Variance...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Calculate coefficient of variation (CV = std/mean)
        solver_stats = dataset_data.groupby('solver').agg({
            'time_seconds': ['mean', 'std'],
            'solver_name': 'first'
        }).reset_index()
        
        solver_stats.columns = ['solver', 'mean_time', 'std_time', 'solver_name']
        solver_stats['cv'] = solver_stats['std_time'] / solver_stats['mean_time']
        solver_stats = solver_stats.sort_values('cv')
        
        x = range(len(solver_stats))
        colors = [SOLVER_COLORS.get(s, '#666666') for s in solver_stats['solver']]
        
        bars = ax.bar(x, solver_stats['cv'] * 100, alpha=0.8, color=colors,
                     edgecolor='black', linewidth=0.5)
        
        # Highlight consistent performers (low CV)
        for i, (bar, val) in enumerate(zip(bars, solver_stats['cv'])):
            if val < 0.5:  # Less than 50% variance
                bar.set_edgecolor('green')
                bar.set_linewidth(2)
        
        ax.set_xticks(x)
        ax.set_xticklabels(solver_stats['solver'], rotation=45, ha='right')
        ax.set_ylabel('Coefficient of Variation (%)')
        ax.set_title(dataset, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add reference line at 50%
        ax.axhline(y=50, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='50% threshold')
        ax.legend(fontsize=8)
    
    plt.suptitle('Performance Consistency: Coefficient of Variation (Lower = More Consistent)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A07_variance_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A07_variance_analysis.png")

def plot_a8_correlation_matrix(df):
    """Plot A8: Correlation Matrix - Between performance metrics"""
    print("\nGenerating Advanced Plot A8: Metric Correlation Matrix...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Select metrics for correlation
        metrics = dataset_data[['time_seconds', 'num_decisions', 'num_backtracks', 'memory_kb']]
        
        # Calculate correlation matrix
        corr_matrix = metrics.corr()
        
        # Create heatmap
        im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        labels = ['Time', 'Decisions', 'Backtracks', 'Memory']
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)
        ax.set_title(dataset, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation', rotation=270, labelpad=20)
        
        # Add correlation values
        for i in range(len(labels)):
            for j in range(len(labels)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", 
                             color="white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black",
                             fontsize=10, fontweight='bold')
    
    plt.suptitle('Performance Metrics Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A08_correlation_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A08_correlation_matrix.png")

def plot_a9_winner_analysis(df):
    """Plot A9: Instance-wise Winner Analysis"""
    print("\nGenerating Advanced Plot A9: Winner Analysis...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Find winner (fastest) for each instance
        winners = dataset_data.loc[dataset_data.groupby('instance')['time_seconds'].idxmin()]
        winner_counts = winners['solver'].value_counts()
        
        # Create pie chart
        colors = [SOLVER_COLORS.get(s, '#666666') for s in winner_counts.index]
        
        wedges, texts, autotexts = ax.pie(winner_counts.values, 
                                           labels=winner_counts.index,
                                           autopct='%1.1f%%',
                                           colors=colors,
                                           startangle=90,
                                           textprops={'fontsize': 9})
        
        # Make percentage text bold and white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
        
        ax.set_title(f'{dataset}\nWinner Distribution', fontweight='bold')
    
    plt.suptitle('Instance-wise Winner Analysis: Which Solver is Fastest Most Often?', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A09_winner_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A09_winner_analysis.png")

def plot_a10_performance_percentiles(df):
    """Plot A10: Performance Percentiles - Box plots"""
    print("\nGenerating Advanced Plot A10: Performance Percentiles...")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    datasets = ['UF20 (20 vars)', 'UF50 (50 vars)', 'UF100 (100 vars)']
    
    for idx, dataset in enumerate(datasets):
        ax = axes[idx]
        dataset_data = df[df['dataset'] == dataset]
        
        # Prepare data for box plot
        solvers_ordered = dataset_data.groupby('solver')['time_seconds'].median().sort_values().index
        
        plot_data = []
        positions = []
        for i, solver in enumerate(solvers_ordered):
            solver_times = dataset_data[dataset_data['solver'] == solver]['time_seconds'].values
            plot_data.append(solver_times)
            positions.append(i)
        
        # Create box plot
        bp = ax.boxplot(plot_data, positions=positions, widths=0.6, patch_artist=True,
                       showfliers=True, notch=True)
        
        # Color boxes
        for i, (box, solver) in enumerate(zip(bp['boxes'], solvers_ordered)):
            box.set_facecolor(SOLVER_COLORS.get(solver, '#666666'))
            box.set_alpha(0.7)
        
        ax.set_xticks(positions)
        ax.set_xticklabels(solvers_ordered, rotation=45, ha='right')
        ax.set_ylabel('Execution Time (seconds)')
        ax.set_title(dataset, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Performance Percentiles: Distribution with Outliers', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/advanced/A10_performance_percentiles.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: A10_performance_percentiles.png")

def main():
    """Main function to generate advanced analysis plots"""
    print("=" * 80)
    print("Advanced SAT Solver Analysis - Additional Insights")
    print("=" * 80)
    
    # Create output directory
    Path('results/plots/advanced').mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data()
    
    # Generate advanced plots
    plot_a1_backtrack_efficiency(df)
    plot_a2_decision_quality(df)
    plot_a3_scalability_analysis(df)
    plot_a4_performance_distribution(df)
    plot_a5_heatmap_solver_comparison(df)
    plot_a6_efficiency_frontier(df)
    plot_a7_variance_analysis(df)
    plot_a8_correlation_matrix(df)
    plot_a9_winner_analysis(df)
    plot_a10_performance_percentiles(df)
    
    print("\n" + "=" * 80)
    print("Advanced Analysis Complete!")
    print("=" * 80)
    print("\nGenerated 10 additional plots revealing:")
    print("  • Backtracking efficiency metrics")
    print("  • Decision quality analysis")
    print("  • Scalability patterns")
    print("  • Performance distributions and variance")
    print("  • Pairwise solver comparisons")
    print("  • Efficiency frontiers")
    print("  • Performance consistency")
    print("  • Metric correlations")
    print("  • Instance-wise winner statistics")
    print("  • Percentile distributions")
    print("\nAll plots saved in: results/plots/advanced/")
    print("=" * 80)

if __name__ == '__main__':
    main()
