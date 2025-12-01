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

# Configure matplotlib for high-quality output
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Computer Modern Roman']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

# Professional color scheme
ALGORITHM_COLORS = {
    'DPLL-SAT': '#ab1d39',           # Blue
    'MRV Backtracking': '#110975'    # Orange
}

class SudokuBenchmarkPlotter:
    """Generate comprehensive publication-quality benchmark plots."""
    
    def __init__(self, csv_file: str = 'sudoku_benchmark_hf_results.csv'):
        """Load and prepare benchmark data."""
        print("=" * 80)
        print("📊 SUDOKU SOLVER BENCHMARK - COMPREHENSIVE ANALYSIS")
        print("=" * 80)
        print(f"\n📂 Loading data from: {csv_file}")
        
        self.df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(self.df)} puzzle results")
        
        # Create output directory
        Path('results/plots').mkdir(parents=True, exist_ok=True)
        
        self.prepare_data()
        
    def prepare_data(self):
        """Prepare and clean data for analysis."""
        print("\n🔧 Preparing data...")
        
        # Convert to milliseconds
        self.df['dpll_time_ms'] = self.df['dpll_avg_time'] * 1000
        self.df['mrv_time_ms'] = self.df['mrv_avg_time'] * 1000
        
        # Create categorical ordering
        self.difficulty_order = ['Easy', 'Medium', 'Hard', 'Expert']
        self.df['difficulty_level'] = pd.Categorical(
            self.df['difficulty_level'],
            categories=self.difficulty_order,
            ordered=True
        )
        
        # Long format for seaborn
        self.df_time_long = pd.melt(
            self.df,
            id_vars=['puzzle_id', 'difficulty_level', 'empty_cells'],
            value_vars=['dpll_time_ms', 'mrv_time_ms'],
            var_name='Algorithm',
            value_name='Time (ms)'
        )
        self.df_time_long['Algorithm'] = self.df_time_long['Algorithm'].map({
            'dpll_time_ms': 'DPLL-SAT',
            'mrv_time_ms': 'MRV Backtracking'
        })
        
        self.df_memory_long = pd.melt(
            self.df,
            id_vars=['puzzle_id', 'difficulty_level', 'empty_cells'],
            value_vars=['dpll_avg_memory', 'mrv_avg_memory'],
            var_name='Algorithm',
            value_name='Memory (MB)'
        )
        self.df_memory_long['Algorithm'] = self.df_memory_long['Algorithm'].map({
            'dpll_avg_memory': 'DPLL-SAT',
            'mrv_avg_memory': 'MRV Backtracking'
        })
        
        print("✅ Data preparation complete")
        print(f"   • Total puzzles: {len(self.df)}")
        print(f"   • Difficulty distribution: {dict(self.df['difficulty_level'].value_counts())}")
        print(f"   • Empty cells range: {self.df['empty_cells'].min()}-{self.df['empty_cells'].max()}")
        
    def plot_05_scatter_time_complexity(self):
        """Plot 5: Scatter plot showing time vs complexity with regression."""
        print("\n[1/2] Generating: Time-complexity scatter plot...")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Scatter for both algorithms
        for algo, color in ALGORITHM_COLORS.items():
            subset = self.df_time_long[self.df_time_long['Algorithm'] == algo]
            
            ax.scatter(subset['empty_cells'], subset['Time (ms)'],
                      alpha=0.6, s=60, label=algo, color=color,
                      edgecolors='black', linewidths=0.5)
            
            # Add regression line
            if len(subset) > 1:
                z = np.polyfit(subset['empty_cells'], subset['Time (ms)'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(subset['empty_cells'].min(), 
                                    subset['empty_cells'].max(), 100)
                ax.plot(x_line, p(x_line), '--', color=color, 
                       linewidth=2.5, alpha=0.8, label=f'{algo} trend')
                
                # Calculate correlation
                corr = np.corrcoef(subset['empty_cells'], subset['Time (ms)'])[0, 1]
                ax.text(0.02, 0.98 if algo == 'DPLL-SAT' else 0.90,
                       f'{algo} r = {corr:.3f}',
                       transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor=color, alpha=0.3),
                       fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Number of Empty Cells', fontweight='bold', fontsize=12)
        ax.set_ylabel('Execution Time (ms)', fontweight='bold', fontsize=12)
        ax.set_title('Execution Time vs. Puzzle Complexity (with Trends)', 
                    fontweight='bold', fontsize=14)
        ax.legend(framealpha=0.9, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig('results/plots/05_scatter_time_complexity.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 05_scatter_time_complexity.png")
        
    def plot_06_scatter_memory_complexity(self):
        """Plot 6: Scatter plot showing memory vs complexity."""
        print("\n[2/2] Generating: Memory-complexity scatter plot...")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Scatter for both algorithms
        for algo, color in ALGORITHM_COLORS.items():
            subset = self.df_memory_long[self.df_memory_long['Algorithm'] == algo]
            
            ax.scatter(subset['empty_cells'], subset['Memory (MB)'],
                      alpha=0.6, s=60, label=algo, color=color,
                      edgecolors='black', linewidths=0.5)
            
            # Add regression line
            if len(subset) > 1:
                z = np.polyfit(subset['empty_cells'], subset['Memory (MB)'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(subset['empty_cells'].min(), 
                                    subset['empty_cells'].max(), 100)
                ax.plot(x_line, p(x_line), '--', color=color, 
                       linewidth=2.5, alpha=0.8, label=f'{algo} trend')
                
                # Calculate correlation
                corr = np.corrcoef(subset['empty_cells'], subset['Memory (MB)'])[0, 1]
                ax.text(0.02, 0.98 if algo == 'DPLL-SAT' else 0.90,
                       f'{algo} r = {corr:.3f}',
                       transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor=color, alpha=0.3),
                       fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Number of Empty Cells', fontweight='bold', fontsize=12)
        ax.set_ylabel('Memory Usage (MB)', fontweight='bold', fontsize=12)
        ax.set_title('Memory Usage vs. Puzzle Complexity (with Trends)', 
                    fontweight='bold', fontsize=14)
        ax.legend(framealpha=0.9, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results/plots/06_scatter_memory_complexity.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved: 06_scatter_memory_complexity.png")
        
    def generate_all_plots(self):
        """Generate selected benchmark plots."""
        print("\n" + "=" * 80)
        print("🎨 GENERATING BENCHMARK PLOTS")
        print("=" * 80)
        
        self.plot_05_scatter_time_complexity()
        self.plot_06_scatter_memory_complexity()
        
        print("\n" + "=" * 80)
        print("✅ ALL PLOTS GENERATED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📁 Output Location: results/plots/")
        print("\n📊 Generated Plots:")
        print("  1. 05_scatter_time_complexity.png - Time vs complexity with trends")
        print("  2. 06_scatter_memory_complexity.png - Memory vs complexity with trends")
        print("=" * 80)


def main():
    """Main function to generate all plots."""
    print("\n" + "=" * 80)
    print("📊 SUDOKU SOLVER BENCHMARK - PUBLICATION PLOTS")
    print("=" * 80)
    print("\n🔬 Research Focus:")
    print("   • Time vs Complexity Analysis")
    print("   • Memory vs Complexity Analysis")
    print("\n🆚 Algorithms:")
    print("   • DPLL-SAT: Davis-Putnam-Logemann-Loveland with SAT encoding")
    print("   • MRV Backtracking: Minimum Remaining Values heuristic")
    print("=" * 80)
    
    # Initialize plotter
    try:
        plotter = SudokuBenchmarkPlotter('sudoku_benchmark_hf_results.csv')
    except FileNotFoundError:
        print("\n❌ ERROR: CSV file not found!")
        print("   Expected file: sudoku_benchmark_hf_results.csv")
        print("   Please run compare.py first to generate benchmark data.")
        return
    except Exception as e:
        print(f"\n❌ ERROR loading data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate all plots
    plotter.generate_all_plots()
    
    print("\n💡 These plots are publication-ready for:")
    print("   • Research papers and journal submissions")
    print("   • Academic presentations and conferences")
    print("   • Technical reports and documentation")
    print("   • Thesis and dissertation chapters")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()