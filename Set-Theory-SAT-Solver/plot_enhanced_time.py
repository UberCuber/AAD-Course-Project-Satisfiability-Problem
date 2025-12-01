#!/usr/bin/env python3
"""
Enhanced Solving Time Visualization - Focused on Clean, Appealing Comparison
Prioritizes time comparison with optimized bar chart visibility for both solvers
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style and colors
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("notebook", font_scale=1.1)
SET_COLOR = '#FF6B6B'  # Coral red for Set-Based
CDCL_COLOR = '#4ECDC4'  # Turquoise for CDCL

def load_data(csv_path):
    """Load benchmark results from CSV"""
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df)} instances")
    return df

def plot_enhanced_time_comparison(df, output_dir):
    """Create enhanced time comparison with separate scales for bar visibility"""
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)
    
    # ============= MAIN PLOT: Dual Y-Axis Line Plot =============
    ax_main = fig.add_subplot(gs[0, :])
    x = np.arange(len(df))
    
    # Primary y-axis for Set-Based
    ax_main.plot(x, df['set_time'], label='Set-Based Solver', color=SET_COLOR, 
                 linewidth=2.5, alpha=0.85, marker='o', markersize=4, markevery=5)
    ax_main.set_xlabel('Instance Index', fontsize=14, fontweight='bold')
    ax_main.set_ylabel('Set-Based Time (seconds)', fontsize=14, fontweight='bold', color=SET_COLOR)
    ax_main.tick_params(axis='y', labelcolor=SET_COLOR, labelsize=12)
    ax_main.tick_params(axis='x', labelsize=12)
    ax_main.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
    ax_main.spines['left'].set_color(SET_COLOR)
    ax_main.spines['left'].set_linewidth(2)
    
    # Secondary y-axis for CDCL
    ax_main_twin = ax_main.twinx()
    ax_main_twin.plot(x, df['cdcl_time'], label='CDCL Solver', color=CDCL_COLOR, 
                      linewidth=2.5, alpha=0.85, marker='s', markersize=4, markevery=5)
    ax_main_twin.set_ylabel('CDCL Time (seconds)', fontsize=14, fontweight='bold', color=CDCL_COLOR)
    ax_main_twin.tick_params(axis='y', labelcolor=CDCL_COLOR, labelsize=12)
    ax_main_twin.spines['right'].set_color(CDCL_COLOR)
    ax_main_twin.spines['right'].set_linewidth(2)
    
    ax_main.set_title('Solving Time Comparison - All 100 Instances', 
                     fontsize=16, fontweight='bold', pad=15)
    
    # Combined legend
    lines1, labels1 = ax_main.get_legend_handles_labels()
    lines2, labels2 = ax_main_twin.get_legend_handles_labels()
    ax_main.legend(lines1 + lines2, labels1 + labels2, fontsize=13, 
                  loc='upper left', framealpha=0.95, edgecolor='black')
    
    # ============= BAR CHART 1: Set-Based (First 30) =============
    ax1 = fig.add_subplot(gs[1, 0])
    n = 30
    x_bar = np.arange(n)
    colors_gradient = plt.cm.Reds(np.linspace(0.5, 0.9, n))
    
    bars1 = ax1.bar(x_bar, df['set_time'][:n], color=colors_gradient, 
                    edgecolor='black', linewidth=0.8, alpha=0.85)
    ax1.set_xlabel('Instance Index', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Set-Based Solver - First 30 Instances', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax1.set_xticks(x_bar[::5])
    ax1.set_xticklabels(x_bar[::5])
    
    # ============= BAR CHART 2: CDCL (First 30) - OPTIMIZED SCALE =============
    ax2 = fig.add_subplot(gs[1, 1])
    colors_gradient2 = plt.cm.GnBu(np.linspace(0.5, 0.9, n))
    
    bars2 = ax2.bar(x_bar, df['cdcl_time'][:n], color=colors_gradient2, 
                    edgecolor='black', linewidth=0.8, alpha=0.85)
    ax2.set_xlabel('Instance Index', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('CDCL Solver - First 30 Instances', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.set_xticks(x_bar[::5])
    ax2.set_xticklabels(x_bar[::5])
    
    # OPTIMIZE Y-AXIS for CDCL visibility
    cdcl_max = df['cdcl_time'][:n].max()
    cdcl_min = df['cdcl_time'][:n].min()
    y_margin = (cdcl_max - cdcl_min) * 0.15
    ax2.set_ylim(max(0, cdcl_min - y_margin), cdcl_max + y_margin)
    
    # ============= SIDE-BY-SIDE BAR COMPARISON (First 20) =============
    ax3 = fig.add_subplot(gs[1, 2])
    n2 = 20
    x_comp = np.arange(n2)
    width = 0.38
    
    bars_set = ax3.bar(x_comp - width/2, df['set_time'][:n2], width, 
                       label='Set-Based', color=SET_COLOR, alpha=0.8, 
                       edgecolor='black', linewidth=0.8)
    bars_cdcl = ax3.bar(x_comp + width/2, df['cdcl_time'][:n2], width, 
                        label='CDCL', color=CDCL_COLOR, alpha=0.8, 
                        edgecolor='black', linewidth=0.8)
    
    ax3.set_xlabel('Instance Index', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax3.set_title(f'Direct Comparison - First {n2} Instances', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=11, framealpha=0.95, edgecolor='black')
    ax3.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax3.set_xticks(x_comp[::4])
    ax3.set_xticklabels(x_comp[::4])
    
    # ============= LOG-SCALE SCATTER PLOT =============
    ax4 = fig.add_subplot(gs[2, 0])
    scatter = ax4.scatter(df['set_time'], df['cdcl_time'], alpha=0.7, s=80, 
                         c=df['speedup_ratio'], cmap='viridis', 
                         edgecolors='black', linewidth=0.8)
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.set_xlabel('Set-Based Time (log scale)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('CDCL Time (log scale)', fontsize=12, fontweight='bold')
    ax4.set_title('Time Correlation (Log-Log Scale)', fontsize=13, fontweight='bold')
    
    # Diagonal line
    min_t = min(df['set_time'].min(), df['cdcl_time'].min())
    max_t = max(df['set_time'].max(), df['cdcl_time'].max())
    ax4.plot([min_t, max_t], [min_t, max_t], 'r--', alpha=0.6, linewidth=2, 
             label='Equal Time Line')
    
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Speedup Ratio', fontsize=11, fontweight='bold')
    ax4.legend(fontsize=10, loc='upper left', framealpha=0.95)
    ax4.grid(True, alpha=0.3, linestyle='--')
    
    # ============= VIOLIN PLOT =============
    ax5 = fig.add_subplot(gs[2, 1])
    
    # Create violin plots
    parts = ax5.violinplot([df['set_time'], df['cdcl_time']], 
                           positions=[1, 2], widths=0.6,
                           showmeans=True, showmedians=True)
    
    # Color the violins
    colors_violin = [SET_COLOR, CDCL_COLOR]
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors_violin[i])
        pc.set_alpha(0.7)
        pc.set_edgecolor('black')
        pc.set_linewidth(1.5)
    
    # Style the other elements
    for partname in ['cmeans', 'cmedians', 'cbars', 'cmaxes', 'cmins']:
        if partname in parts:
            parts[partname].set_edgecolor('black')
            parts[partname].set_linewidth(1.5)
    
    ax5.set_xticks([1, 2])
    ax5.set_xticklabels(['Set-Based', 'CDCL'], fontsize=11, fontweight='bold')
    ax5.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax5.set_title('Time Distribution (Violin Plot)', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # ============= STATISTICS PANEL =============
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    stats_text = f"""╔══════════════════════════════════════╗
║      PERFORMANCE STATISTICS          ║
╚══════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SET-BASED SOLVER
  Mean Time:     {df['set_time'].mean():>8.4f} s
  Median Time:   {df['set_time'].median():>8.4f} s
  Min Time:      {df['set_time'].min():>8.4f} s
  Max Time:      {df['set_time'].max():>8.4f} s
  Std Dev:       {df['set_time'].std():>8.4f} s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CDCL SOLVER
  Mean Time:     {df['cdcl_time'].mean():>8.6f} s
  Median Time:   {df['cdcl_time'].median():>8.6f} s
  Min Time:      {df['cdcl_time'].min():>8.6f} s
  Max Time:      {df['cdcl_time'].max():>8.6f} s
  Std Dev:       {df['cdcl_time'].std():>8.6f} s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SPEEDUP METRICS
  Average:       {df['speedup_ratio'].mean():>8.2f}x
  Median:        {df['speedup_ratio'].median():>8.2f}x
  Maximum:       {df['speedup_ratio'].max():>8.2f}x
  Minimum:       {df['speedup_ratio'].min():>8.2f}x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTANCES ANALYZED: {len(df)}
    """
    
    ax6.text(0.1, 0.5, stats_text, fontsize=10, ha='left', va='center',
            family='monospace', 
            bbox=dict(boxstyle='round', facecolor='#F5F5DC', alpha=0.9, 
                     edgecolor='black', linewidth=2))
    
    # Overall title
    fig.suptitle('🎯 Comprehensive Solving Time Analysis: Set-Based vs CDCL 🎯', 
                fontsize=18, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    output_path = output_dir / 'enhanced_solving_time_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_path.name}")
    plt.close()

def plot_focused_bar_charts(df, output_dir):
    """Create focused bar charts with optimized scales"""
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.patch.set_facecolor('white')
    
    # ============= SET-BASED: First 40 instances =============
    ax1 = axes[0, 0]
    n = 40
    x = np.arange(n)
    colors1 = plt.cm.Reds(np.linspace(0.4, 0.95, n))
    
    bars1 = ax1.bar(x, df['set_time'][:n], color=colors1, 
                    edgecolor='black', linewidth=0.7, alpha=0.85)
    ax1.set_xlabel('Instance Index', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Time (seconds)', fontsize=13, fontweight='bold')
    ax1.set_title('Set-Based Solver - First 40 Instances', fontsize=14, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.35, axis='y', linestyle='--', linewidth=0.8)
    ax1.set_xticks(x[::5])
    
    # Add mean line
    mean_set = df['set_time'][:n].mean()
    ax1.axhline(mean_set, color='darkred', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_set:.3f}s', alpha=0.7)
    ax1.legend(fontsize=11)
    
    # ============= CDCL: First 40 instances - OPTIMIZED Y-AXIS =============
    ax2 = axes[0, 1]
    colors2 = plt.cm.GnBu(np.linspace(0.4, 0.95, n))
    
    bars2 = ax2.bar(x, df['cdcl_time'][:n], color=colors2, 
                    edgecolor='black', linewidth=0.7, alpha=0.85)
    ax2.set_xlabel('Instance Index', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Time (seconds)', fontsize=13, fontweight='bold')
    ax2.set_title('CDCL Solver - First 40 Instances (Optimized Scale)', 
                 fontsize=14, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.35, axis='y', linestyle='--', linewidth=0.8)
    ax2.set_xticks(x[::5])
    
    # OPTIMIZE Y-AXIS for better visibility
    cdcl_max = df['cdcl_time'][:n].max()
    cdcl_min = df['cdcl_time'][:n].min()
    y_range = cdcl_max - cdcl_min
    ax2.set_ylim(max(0, cdcl_min - y_range*0.1), cdcl_max + y_range*0.1)
    
    # Add mean line
    mean_cdcl = df['cdcl_time'][:n].mean()
    ax2.axhline(mean_cdcl, color='darkblue', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_cdcl:.4f}s', alpha=0.7)
    ax2.legend(fontsize=11)
    
    # ============= SET-BASED: Last 40 instances =============
    ax3 = axes[1, 0]
    x2 = np.arange(n)
    start_idx = len(df) - n
    colors3 = plt.cm.Oranges(np.linspace(0.4, 0.95, n))
    
    bars3 = ax3.bar(x2, df['set_time'][start_idx:].values, color=colors3, 
                    edgecolor='black', linewidth=0.7, alpha=0.85)
    ax3.set_xlabel('Instance Index', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Time (seconds)', fontsize=13, fontweight='bold')
    ax3.set_title(f'Set-Based Solver - Last 40 Instances ({start_idx}-{len(df)-1})', 
                 fontsize=14, fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.35, axis='y', linestyle='--', linewidth=0.8)
    ax3.set_xticks(x2[::5])
    ax3.set_xticklabels([start_idx + i for i in x2[::5]])
    
    mean_set2 = df['set_time'][start_idx:].mean()
    ax3.axhline(mean_set2, color='darkorange', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_set2:.3f}s', alpha=0.7)
    ax3.legend(fontsize=11)
    
    # ============= CDCL: Last 40 instances - OPTIMIZED Y-AXIS =============
    ax4 = axes[1, 1]
    colors4 = plt.cm.Purples(np.linspace(0.4, 0.95, n))
    
    bars4 = ax4.bar(x2, df['cdcl_time'][start_idx:].values, color=colors4, 
                    edgecolor='black', linewidth=0.7, alpha=0.85)
    ax4.set_xlabel('Instance Index', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Time (seconds)', fontsize=13, fontweight='bold')
    ax4.set_title(f'CDCL Solver - Last 40 Instances (Optimized Scale)', 
                 fontsize=14, fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.35, axis='y', linestyle='--', linewidth=0.8)
    ax4.set_xticks(x2[::5])
    ax4.set_xticklabels([start_idx + i for i in x2[::5]])
    
    # OPTIMIZE Y-AXIS
    cdcl_max2 = df['cdcl_time'][start_idx:].max()
    cdcl_min2 = df['cdcl_time'][start_idx:].min()
    y_range2 = cdcl_max2 - cdcl_min2
    ax4.set_ylim(max(0, cdcl_min2 - y_range2*0.1), cdcl_max2 + y_range2*0.1)
    
    mean_cdcl2 = df['cdcl_time'][start_idx:].mean()
    ax4.axhline(mean_cdcl2, color='purple', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_cdcl2:.4f}s', alpha=0.7)
    ax4.legend(fontsize=11)
    
    plt.suptitle('Detailed Bar Chart Analysis - Optimized for Visibility', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = output_dir / 'focused_bar_charts.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_path.name}")
    plt.close()

def main():
    """Main execution"""
    csv_path = Path('benchmark_results/benchmark_results.csv')
    output_dir = Path('benchmark_results/plots')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("🎨 ENHANCED SOLVING TIME VISUALIZATION")
    print("="*70)
    print()
    
    df = load_data(csv_path)
    
    print("\n[1/2] Generating comprehensive time comparison...")
    plot_enhanced_time_comparison(df, output_dir)
    
    print("[2/2] Generating focused bar charts with optimized scales...")
    plot_focused_bar_charts(df, output_dir)
    
    print("\n" + "="*70)
    print("✅ ALL ENHANCED PLOTS GENERATED")
    print(f"📂 Output: {output_dir.absolute()}")
    print("="*70)
    
    print("\n📊 Quick Stats:")
    print(f"  Set-Based: {df['set_time'].mean():.4f}s avg, {df['set_time'].max():.4f}s max")
    print(f"  CDCL:      {df['cdcl_time'].mean():.6f}s avg, {df['cdcl_time'].max():.6f}s max")
    print(f"  Speedup:   {df['speedup_ratio'].mean():.2f}x average")

if __name__ == '__main__':
    main()
