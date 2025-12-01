import sys
import os
import time
import statistics
import csv
import requests
import json
from typing import List, Dict, Any
import tracemalloc
import psutil

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'DPLL-SAT-solver'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Sudoku-solver'))

from sudoku_encoder import SudokuToCNF
from dpll_basic import dpll, stats as dpll_stats
from sudoku_solver_mrv import solve_sudoku, initialize_domains

class SudokuBenchmarkComparison:
    """Benchmark comparing DPLL-SAT vs MRV Backtracking using Hugging Face API."""
    
    def __init__(self):
        self.dpll_solver = SudokuToCNF()
        self.results = []
        self.api_base_url = "https://datasets-server.huggingface.co/rows"
    
    def load_huggingface_dataset_api(self, num_samples: int = 50) -> List[str]:
        """Load Sudoku dataset from Hugging Face using REST API."""
        print("📥 Loading Sudoku dataset from Hugging Face API...")
        print("   Repository: Ritvik19/Sudoku-Dataset")
        print("   Using: Datasets Server REST API")
        
        puzzles = []
        offset = 0
        batch_size = 100
        
        try:
            while len(puzzles) < num_samples:
                # Construct API request
                params = {
                    'dataset': 'Ritvik19/Sudoku-Dataset',
                    'config': 'default',
                    'split': 'train',
                    'offset': offset,
                    'length': min(batch_size, num_samples - len(puzzles))
                }
                
                print(f"   📡 Fetching batch: offset={offset}, length={params['length']}...")
                
                # Make API request
                response = requests.get(self.api_base_url, params=params, timeout=30)
                
                if response.status_code != 200:
                    print(f"❌ API request failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                
                data = response.json()
                
                # Check if we have rows
                if 'rows' not in data or not data['rows']:
                    print(f"⚠️  No more data available at offset {offset}")
                    break
                
                # Extract puzzles from this batch
                batch_puzzles = []
                for row_data in data['rows']:
                    row = row_data.get('row', {})
                    
                    # Extract puzzle string - try different field names
                    puzzle_string = None
                    
                    # Common field names to check
                    possible_fields = ['puzzle', 'input', 'question', 'problem', 'sudoku', 'grid']
                    
                    for field in possible_fields:
                        if field in row and isinstance(row[field], str):
                            if len(row[field]) == 81 and row[field].isdigit():
                                puzzle_string = row[field]
                                break
                    
                    # If no obvious field found, check all string fields
                    if not puzzle_string:
                        for key, value in row.items():
                            if isinstance(value, str) and len(value) == 81 and value.isdigit():
                                puzzle_string = value
                                print(f"   🔍 Found puzzle in field '{key}'")
                                break
                    
                    if puzzle_string:
                        batch_puzzles.append(puzzle_string)
                        if len(puzzles) < 3:  # Show first few for verification
                            print(f"   Sample {len(puzzles)+1}: {puzzle_string[:20]}...{puzzle_string[-10:]}")
                
                puzzles.extend(batch_puzzles)
                print(f"   ✅ Loaded {len(batch_puzzles)} puzzles from this batch (Total: {len(puzzles)})")
                
                # If we got fewer than requested, we've reached the end
                if len(data['rows']) < params['length']:
                    print(f"   📊 Reached end of dataset")
                    break
                
                offset += batch_size
                
                # Don't overload the API
                time.sleep(0.5)
            
            if puzzles:
                print(f"✅ Successfully loaded {len(puzzles)} valid puzzles from API")
                
                # Show field structure from first row for debugging
                if 'rows' in data and data['rows']:
                    sample_row = data['rows'][0]['row']
                    print(f"   📋 Available fields: {list(sample_row.keys())}")
                    
            return puzzles[:num_samples]  # Ensure we don't exceed requested number
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error loading from API: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
        except Exception as e:
            print(f"❌ Error loading Hugging Face dataset via API: {e}")
        
        # Fallback to sample puzzles if API fails
        print("📝 Using fallback sample puzzles...")
        return [
            "467100805912835607085647192296351470708920351531408926073064510624519783159783064",
            "006513000001904036302060010063000000480070390009030065000007050000640000657001920", 
            "200080300060070084030500209000105408000000000402706000301007040720040060004010003",
            "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
            "800000000003600000070090200050007000000045700000100030001000068008500010090000400",
            "020000000000006300074080000000003002080040070600500000000090620005200080000000090",
            "300200000000107000706030500070009080900020004010800050009040301000702000000008006",
            "040000050001943600009000300580000009000580000900000012008000200006312700020000090"
        ]
    
    def string_to_grid(self, puzzle_string: str) -> List[List[int]]:
        """Convert 81-character string to 9x9 grid."""
        if len(puzzle_string) != 81:
            raise ValueError(f"Puzzle string must be 81 characters, got {len(puzzle_string)}")
        
        grid = []
        for i in range(9):
            row = []
            for j in range(9):
                index = i * 9 + j
                digit = int(puzzle_string[index])
                row.append(digit)
            grid.append(row)
        
        return grid
    
    def count_empty_cells(self, puzzle_string: str) -> int:
        """Count number of empty cells (0s) in puzzle."""
        return puzzle_string.count('0')
    
    def categorize_difficulty(self, empty_cells: int) -> str:
        """Categorize puzzle difficulty based on empty cells."""
        if empty_cells < 45:
            return "Easy"
        elif empty_cells < 55:
            return "Medium"
        elif empty_cells < 65:
            return "Hard"
        else:
            return "Expert"
    
    def solve_with_dpll_sat(self, puzzle_grid: List[List[int]], runs: int = 3) -> Dict[str, Any]:
        """Solve using DPLL-SAT approach with memory tracking."""
        times = []
        calls_list = []
        backtracks_list = []
        memory_usage_list = []
        solved = False
        
        for run in range(runs):
            # Reset stats
            for key in dpll_stats:
                dpll_stats[key] = 0
            
            # Start memory tracking
            tracemalloc.start()
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            start = time.perf_counter()
            try:
                clauses, num_vars = self.dpll_solver.encode_sudoku(puzzle_grid)
                assignment = dpll(clauses, {})
                end = time.perf_counter()
                
                # Get peak memory usage
                current, peak = tracemalloc.get_traced_memory()
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_used = max(peak / 1024 / 1024, memory_after - memory_before)  # MB
                
                times.append(end - start)
                calls_list.append(dpll_stats['calls'])
                backtracks_list.append(dpll_stats['backtracks'])
                memory_usage_list.append(memory_used)
                solved = (assignment is not None)
                
            except Exception as e:
                print(f"   ❌ DPLL-SAT error: {e}")
                times.append(float('inf'))
                calls_list.append(0)
                backtracks_list.append(0)
                memory_usage_list.append(0)
                solved = False
            finally:
                tracemalloc.stop()
        
        return {
            'avg_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
            'min_time': min(times),
            'max_time': max(times),
            'avg_calls': statistics.mean(calls_list),
            'avg_backtracks': statistics.mean(backtracks_list),
            'avg_memory': statistics.mean(memory_usage_list),
            'std_memory': statistics.stdev(memory_usage_list) if len(memory_usage_list) > 1 else 0,
            'peak_memory': max(memory_usage_list),
            'solved': solved,
            'success_rate': sum(1 for t in times if t != float('inf')) / len(times)
        }
    
    def solve_with_mrv_backtracking(self, puzzle_grid: List[List[int]], runs: int = 3) -> Dict[str, Any]:
        """Solve using MRV backtracking approach with memory tracking."""
        times = []
        memory_usage_list = []
        solved_count = 0
        
        for run in range(runs):
            # Create a copy for each run
            board_copy = [row[:] for row in puzzle_grid]
            
            # Start memory tracking
            tracemalloc.start()
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            start = time.perf_counter()
            try:
                domains = initialize_domains(board_copy)
                solved = solve_sudoku(board_copy, domains)
                end = time.perf_counter()
                
                # Get peak memory usage
                current, peak = tracemalloc.get_traced_memory()
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_used = max(peak / 1024 / 1024, memory_after - memory_before)  # MB
                
                times.append(end - start)
                memory_usage_list.append(memory_used)
                if solved:
                    solved_count += 1
                    
            except Exception as e:
                print(f"   ❌ MRV Backtracking error: {e}")
                times.append(float('inf'))
                memory_usage_list.append(0)
            finally:
                tracemalloc.stop()
        
        return {
            'avg_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
            'min_time': min(times),
            'max_time': max(times),
            'avg_calls': 0,  # MRV solver doesn't track calls in our version
            'avg_backtracks': 0,  # MRV solver doesn't track backtracks in our version
            'avg_memory': statistics.mean(memory_usage_list),
            'std_memory': statistics.stdev(memory_usage_list) if len(memory_usage_list) > 1 else 0,
            'peak_memory': max(memory_usage_list),
            'solved': solved_count > 0,
            'success_rate': solved_count / len(times)
        }
    
    def benchmark_dataset(self, puzzle_strings: List[str], runs: int = 3) -> List[Dict[str, Any]]:
        """Benchmark both algorithms on the loaded dataset."""
        results = []
        
        print("=" * 80)
        print("SUDOKU SOLVER BENCHMARK - HUGGING FACE API DATASET")
        print("Repository: Ritvik19/Sudoku-Dataset")
        print("DPLL-SAT vs MRV Backtracking")
        print("=" * 80)
        print(f"📊 Dataset size: {len(puzzle_strings)} puzzles")
        print(f"🔄 Runs per puzzle: {runs}")
        print("=" * 80)
        
        for idx, puzzle_string in enumerate(puzzle_strings):
            try:
                puzzle_grid = self.string_to_grid(puzzle_string)
                empty_cells = self.count_empty_cells(puzzle_string)
                difficulty = self.categorize_difficulty(empty_cells)
                
                print(f"\n🧩 PUZZLE {idx + 1}/{len(puzzle_strings)}: {difficulty} ({empty_cells} empty)")
                print(f"   String: {puzzle_string[:30]}...{puzzle_string[-15:]}")
                
                # Test DPLL-SAT
                print("   🔷 Running DPLL-SAT...", end=" ", flush=True)
                dpll_results = self.solve_with_dpll_sat(puzzle_grid, runs)
                print(f"✓ {dpll_results['avg_time']:.5f}s")
                
                # Test MRV Backtracking
                print("   🔸 Running MRV Backtracking...", end=" ", flush=True)
                mrv_results = self.solve_with_mrv_backtracking(puzzle_grid, runs)
                print(f"✓ {mrv_results['avg_time']:.5f}s")
                
                # Compile results
                result = {
                    'puzzle_id': idx + 1,
                    'puzzle_string': puzzle_string,
                    'difficulty_level': difficulty,
                    'empty_cells': empty_cells,
                    
                    # DPLL-SAT Results
                    'dpll_avg_time': dpll_results['avg_time'],
                    'dpll_median_time': dpll_results['median_time'],
                    'dpll_std_time': dpll_results['std_time'],
                    'dpll_min_time': dpll_results['min_time'],
                    'dpll_max_time': dpll_results['max_time'],
                    'dpll_avg_memory': dpll_results['avg_memory'],
                    'dpll_std_memory': dpll_results['std_memory'],
                    'dpll_peak_memory': dpll_results['peak_memory'],
                    'dpll_avg_calls': dpll_results['avg_calls'],
                    'dpll_avg_backtracks': dpll_results['avg_backtracks'],
                    'dpll_solved': dpll_results['solved'],
                    'dpll_success_rate': dpll_results['success_rate'],
                    
                    # MRV Backtracking Results
                    'mrv_avg_time': mrv_results['avg_time'],
                    'mrv_median_time': mrv_results['median_time'],
                    'mrv_std_time': mrv_results['std_time'],
                    'mrv_min_time': mrv_results['min_time'],
                    'mrv_max_time': mrv_results['max_time'],
                    'mrv_avg_memory': mrv_results['avg_memory'],
                    'mrv_std_memory': mrv_results['std_memory'],
                    'mrv_peak_memory': mrv_results['peak_memory'],
                    'mrv_solved': mrv_results['solved'],
                    'mrv_success_rate': mrv_results['success_rate'],
                }
                
                results.append(result)
                
                # Quick comparison
                if (result['mrv_avg_time'] > 0 and result['dpll_avg_time'] > 0 and 
                    result['mrv_avg_time'] != float('inf') and result['dpll_avg_time'] != float('inf')):
                    
                    speedup_ratio = result['mrv_avg_time'] / result['dpll_avg_time']
                    winner = "DPLL-SAT" if speedup_ratio > 1 else "MRV"
                    ratio = speedup_ratio if speedup_ratio > 1 else 1/speedup_ratio
                    print(f"   🏆 {winner} wins by {ratio:.2f}× | Memory: DPLL={result['dpll_avg_memory']:.1f}MB, MRV={result['mrv_avg_memory']:.1f}MB")
                
            except Exception as e:
                print(f"   ❌ Error processing puzzle {idx + 1}: {e}")
                continue
        
        return results
    
    def save_results_to_csv(self, results: List[Dict[str, Any]], filename: str = 'sudoku_benchmark_results.csv'):
        """Save results to CSV for analysis."""
        if not results:
            print("❌ No results to save")
            return
        
        print(f"\n💾 Saving results to '{filename}'...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✅ Results saved successfully!")
        print(f"📊 Total puzzles benchmarked: {len(results)}")
        
        # Show CSV column info
        print(f"\n📋 CSV Structure:")
        print("   📄 File: sudoku_benchmark_results.csv")
        print(f"   🗂️  Columns: {len(fieldnames)} total")
        print("   📊 Data includes:")
        print("      • Puzzle info: ID, string, difficulty, empty cells")
        print("      • DPLL-SAT metrics: time, memory, calls, backtracks, success rate")
        print("      • MRV Backtracking metrics: time, memory, success rate")
        print("      • Statistical measures: mean, median, std dev, min, max")
        
    def print_summary_analysis(self, results: List[Dict[str, Any]]):
        """Print comprehensive summary analysis of benchmark results."""
        if not results:
            print("❌ No results to analyze")
            return
            
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE BENCHMARK ANALYSIS")
        print("=" * 80)
        
        # Filter valid results
        valid_results = [r for r in results 
                        if r['dpll_avg_time'] != float('inf') and r['mrv_avg_time'] != float('inf')]
        
        if not valid_results:
            print("❌ No valid results for comparison")
            return
        
        print(f"📈 DATASET OVERVIEW:")
        print(f"   Total puzzles processed: {len(results)}")
        print(f"   Successfully solved by both: {len(valid_results)}")
        print(f"   Success rate: {len(valid_results)/len(results)*100:.1f}%")
        
        # Time analysis
        dpll_times = [r['dpll_avg_time'] for r in valid_results]
        mrv_times = [r['mrv_avg_time'] for r in valid_results]
        
        # Memory analysis  
        dpll_memory = [r['dpll_avg_memory'] for r in valid_results]
        mrv_memory = [r['mrv_avg_memory'] for r in valid_results]
        
        # Win counts
        dpll_time_wins = sum(1 for r in valid_results if r['dpll_avg_time'] < r['mrv_avg_time'])
        mrv_time_wins = len(valid_results) - dpll_time_wins
        
        dpll_memory_wins = sum(1 for r in valid_results if r['dpll_avg_memory'] < r['mrv_avg_memory'])
        mrv_memory_wins = len(valid_results) - dpll_memory_wins
        
        print(f"\n⏱️  TIME PERFORMANCE ANALYSIS:")
        print(f"   🥇 DPLL-SAT wins: {dpll_time_wins}/{len(valid_results)} puzzles ({dpll_time_wins/len(valid_results)*100:.1f}%)")
        print(f"   🥈 MRV Backtracking wins: {mrv_time_wins}/{len(valid_results)} puzzles ({mrv_time_wins/len(valid_results)*100:.1f}%)")
        print(f"   📊 DPLL-SAT Stats:")
        print(f"      • Average: {sum(dpll_times)/len(dpll_times):.5f}s")
        print(f"      • Median:  {statistics.median(dpll_times):.5f}s")
        print(f"      • Std Dev: {statistics.stdev(dpll_times):.5f}s")
        print(f"      • Range:   {min(dpll_times):.5f}s - {max(dpll_times):.5f}s")
        print(f"   📊 MRV Backtracking Stats:")
        print(f"      • Average: {sum(mrv_times)/len(mrv_times):.5f}s")
        print(f"      • Median:  {statistics.median(mrv_times):.5f}s")
        print(f"      • Std Dev: {statistics.stdev(mrv_times):.5f}s")
        print(f"      • Range:   {min(mrv_times):.5f}s - {max(mrv_times):.5f}s")
        
        overall_speedup = sum(mrv_times) / sum(dpll_times)
        if overall_speedup > 1:
            print(f"   🏆 OVERALL WINNER: DPLL-SAT ({overall_speedup:.2f}× faster)")
        else:
            print(f"   🏆 OVERALL WINNER: MRV Backtracking ({1/overall_speedup:.2f}× faster)")
        
        print(f"\n💾 MEMORY USAGE ANALYSIS:")
        print(f"   🥇 DPLL-SAT wins: {dpll_memory_wins}/{len(valid_results)} puzzles ({dpll_memory_wins/len(valid_results)*100:.1f}%)")
        print(f"   🥈 MRV Backtracking wins: {mrv_memory_wins}/{len(valid_results)} puzzles ({mrv_memory_wins/len(valid_results)*100:.1f}%)")
        print(f"   📊 DPLL-SAT Memory:")
        print(f"      • Average: {sum(dpll_memory)/len(dpll_memory):.2f}MB")
        print(f"      • Peak:    {max(dpll_memory):.2f}MB")
        print(f"      • Range:   {min(dpll_memory):.2f}MB - {max(dpll_memory):.2f}MB")
        print(f"   📊 MRV Backtracking Memory:")
        print(f"      • Average: {sum(mrv_memory)/len(mrv_memory):.2f}MB")
        print(f"      • Peak:    {max(mrv_memory):.2f}MB")
        print(f"      • Range:   {min(mrv_memory):.2f}MB - {max(mrv_memory):.2f}MB")
        
        memory_efficiency = sum(dpll_memory) / sum(mrv_memory)
        if memory_efficiency > 1:
            print(f"   💾 MEMORY WINNER: MRV Backtracking ({memory_efficiency:.2f}× less memory)")
        else:
            print(f"   💾 MEMORY WINNER: DPLL-SAT ({1/memory_efficiency:.2f}× less memory)")
        
        # Algorithm-specific metrics
        print(f"\n🔧 ALGORITHM-SPECIFIC METRICS:")
        avg_calls = sum(r['dpll_avg_calls'] for r in valid_results) / len(valid_results)
        avg_backtracks = sum(r['dpll_avg_backtracks'] for r in valid_results) / len(valid_results)
        print(f"   📞 DPLL Average Calls: {avg_calls:.0f}")
        print(f"   ↩️  DPLL Average Backtracks: {avg_backtracks:.0f}")
        print(f"   📊 Backtrack Ratio: {avg_backtracks/avg_calls*100:.1f}%")
        
        # Difficulty breakdown
        print(f"\n📊 PERFORMANCE BY DIFFICULTY LEVEL:")
        difficulties = {}
        for result in valid_results:
            diff = result['difficulty_level']
            if diff not in difficulties:
                difficulties[diff] = {
                    'dpll_wins': 0, 'mrv_wins': 0, 'total': 0,
                    'dpll_times': [], 'mrv_times': []
                }
            difficulties[diff]['total'] += 1
            difficulties[diff]['dpll_times'].append(result['dpll_avg_time'])
            difficulties[diff]['mrv_times'].append(result['mrv_avg_time'])
            
            if result['dpll_avg_time'] < result['mrv_avg_time']:
                difficulties[diff]['dpll_wins'] += 1
            else:
                difficulties[diff]['mrv_wins'] += 1
        
        for diff, stats in sorted(difficulties.items()):
            dpll_pct = (stats['dpll_wins'] / stats['total']) * 100
            mrv_pct = (stats['mrv_wins'] / stats['total']) * 100
            dpll_avg = sum(stats['dpll_times']) / len(stats['dpll_times'])
            mrv_avg = sum(stats['mrv_times']) / len(stats['mrv_times'])
            
            print(f"   🎯 {diff} ({stats['total']} puzzles):")
            print(f"      DPLL-SAT: {stats['dpll_wins']} wins ({dpll_pct:.1f}%) | Avg: {dpll_avg:.5f}s")
            print(f"      MRV B.T.: {stats['mrv_wins']} wins ({mrv_pct:.1f}%) | Avg: {mrv_avg:.5f}s")


def main():
    """Main benchmark execution with Hugging Face API."""
    
    print("🚀 Sudoku Solver Benchmark - Hugging Face API")
    print("=" * 60)
    print("📋 Source: Ritvik19/Sudoku-Dataset (via REST API)")
    print("🆚 Algorithms: DPLL-SAT vs MRV Backtracking")
    print("📡 API: https://datasets-server.huggingface.co/rows")
    print("=" * 60)
    
    # Initialize benchmark
    benchmark = SudokuBenchmarkComparison()
    
    # Load dataset from Hugging Face API
    puzzles = benchmark.load_huggingface_dataset_api(num_samples=30)  # Adjust sample size as needed
    
    if not puzzles:
        print("❌ No puzzles loaded. Exiting...")
        return
    
    # Run benchmark (3 runs per puzzle for statistical significance)
    results = benchmark.benchmark_dataset(puzzles, runs=3)
    
    # Save results to CSV
    benchmark.save_results_to_csv(results, 'sudoku_benchmark_hf_results.csv')
    
    # Print comprehensive analysis
    benchmark.print_summary_analysis(results)
    
    print("\n" + "=" * 80)
    print("🎯 BENCHMARK COMPLETE!")
    print("📁 Results saved to: sudoku_benchmark_hf_results.csv")
    print("💡 Analysis Tools:")
    print("   • Import CSV into Excel for charts and pivot tables")
    print("   • Use Python pandas for advanced statistical analysis")
    print("   • Load in R for publication-quality visualizations")
    print("=" * 80)


if __name__ == "__main__":
    main()