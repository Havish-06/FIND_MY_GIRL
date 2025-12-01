"""
Comprehensive Benchmarking Suite with Scalability Analysis
===========================================================
Tests all algorithms across multiple network sizes and generates performance plots.

Author: AAD Project Group
Date: December 2025
"""

import time
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Callable
import random

# Import our modules
from algorithms.graph import Graph
from algorithms.graph_generator import generate_social_network
from algorithms.traversal import (
    find_connected_components_bfs,
    find_connected_components_dfs,
    shortest_path_bfs
)
from algorithms.union_find import find_connected_components_union_find
from algorithms.centrality import (
    compute_degree_centrality,
    compute_betweenness_centrality,
    compute_closeness_centrality,
    compute_pagerank,
    compute_eigenvector_centrality
)
from algorithms.community_detection import (
    label_propagation,
    girvan_newman
)


class BenchmarkResult:
    """Store benchmark results for an algorithm."""
    
    def __init__(self, name: str):
        self.name = name
        self.sizes = []
        self.times = []
        self.memory = []
        self.complexity_class = None
    
    def add_result(self, size: int, time_sec: float, memory_mb: float):
        """Add a benchmark result."""
        self.sizes.append(size)
        self.times.append(time_sec)
        self.memory.append(memory_mb)
    
    def get_data(self):
        """Return benchmark data."""
        return self.sizes, self.times, self.memory


def benchmark_function(func: Callable, *args, **kwargs) -> Tuple[float, float, any]:
    """
    Benchmark a function with timing and memory profiling.
    
    Args:
        func: Function to benchmark
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        Tuple of (execution_time_seconds, peak_memory_mb, result)
    """
    # Start memory tracking
    tracemalloc.start()
    
    # Time the function
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    # Get peak memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    execution_time = end_time - start_time
    peak_memory_mb = peak / (1024 * 1024)  # Convert to MB
    
    return execution_time, peak_memory_mb, result


def generate_test_graphs(sizes: List[int]) -> Dict[int, Graph]:
    """
    Generate test graphs of different sizes.
    
    Args:
        sizes: List of network sizes to generate
    
    Returns:
        Dictionary mapping size to graph
    """
    print("Generating test graphs...")
    graphs = {}
    
    for size in sizes:
        print(f"  Generating {size}-node network...")
        avg_friends = min(10, size // 5)  # Scale average degree
        graph = generate_social_network(
            num_users=size,
            avg_friends=avg_friends,
            community_structure=True,
            num_communities=max(2, size // 50)
        )
        graphs[size] = graph
    
    print(f"Generated {len(graphs)} test graphs\n")
    return graphs


def benchmark_connected_components(graphs: Dict[int, Graph]) -> Dict[str, BenchmarkResult]:
    """Benchmark connected components algorithms."""
    print("=" * 70)
    print("BENCHMARKING: Connected Components Detection")
    print("=" * 70)
    
    results = {
        'BFS': BenchmarkResult('BFS'),
        'DFS': BenchmarkResult('DFS'),
        'Union-Find': BenchmarkResult('Union-Find')
    }
    
    for size, graph in sorted(graphs.items()):
        print(f"\nNetwork size: {size} nodes")
        
        # BFS
        exec_time, memory, _ = benchmark_function(find_connected_components_bfs, graph)
        results['BFS'].add_result(size, exec_time, memory)
        print(f"  BFS:        {exec_time:.6f}s, {memory:.2f}MB")
        
        # DFS
        exec_time, memory, _ = benchmark_function(find_connected_components_dfs, graph)
        results['DFS'].add_result(size, exec_time, memory)
        print(f"  DFS:        {exec_time:.6f}s, {memory:.2f}MB")
        
        # Union-Find
        exec_time, memory, _ = benchmark_function(find_connected_components_union_find, graph)
        results['Union-Find'].add_result(size, exec_time, memory)
        print(f"  Union-Find: {exec_time:.6f}s, {memory:.2f}MB")
    
    return results


def benchmark_centrality_measures(graphs: Dict[int, Graph]) -> Dict[str, BenchmarkResult]:
    """Benchmark centrality algorithms."""
    print("\n" + "=" * 70)
    print("BENCHMARKING: Centrality Measures")
    print("=" * 70)
    
    results = {
        'Degree': BenchmarkResult('Degree'),
        'Betweenness': BenchmarkResult('Betweenness'),
        'Closeness': BenchmarkResult('Closeness'),
        'PageRank': BenchmarkResult('PageRank'),
        'Eigenvector': BenchmarkResult('Eigenvector')
    }
    
    for size, graph in sorted(graphs.items()):
        print(f"\nNetwork size: {size} nodes")
        
        # Degree (very fast)
        exec_time, memory, _ = benchmark_function(compute_degree_centrality, graph)
        results['Degree'].add_result(size, exec_time, memory)
        print(f"  Degree:      {exec_time:.6f}s, {memory:.2f}MB")
        
        # Betweenness (slow for large graphs)
        if size <= 500:  # Skip for very large graphs
            exec_time, memory, _ = benchmark_function(compute_betweenness_centrality, graph)
            results['Betweenness'].add_result(size, exec_time, memory)
            print(f"  Betweenness: {exec_time:.6f}s, {memory:.2f}MB")
        
        # Closeness
        if size <= 500:
            exec_time, memory, _ = benchmark_function(compute_closeness_centrality, graph)
            results['Closeness'].add_result(size, exec_time, memory)
            print(f"  Closeness:   {exec_time:.6f}s, {memory:.2f}MB")
        
        # PageRank
        exec_time, memory, _ = benchmark_function(compute_pagerank, graph)
        results['PageRank'].add_result(size, exec_time, memory)
        print(f"  PageRank:    {exec_time:.6f}s, {memory:.2f}MB")
        
        # Eigenvector
        exec_time, memory, _ = benchmark_function(compute_eigenvector_centrality, graph)
        results['Eigenvector'].add_result(size, exec_time, memory)
        print(f"  Eigenvector: {exec_time:.6f}s, {memory:.2f}MB")
    
    return results


def benchmark_community_detection(graphs: Dict[int, Graph]) -> Dict[str, BenchmarkResult]:
    """Benchmark community detection algorithms."""
    print("\n" + "=" * 70)
    print("BENCHMARKING: Community Detection")
    print("=" * 70)
    
    results = {
        'Label Propagation': BenchmarkResult('Label Propagation'),
        'Girvan-Newman': BenchmarkResult('Girvan-Newman')
    }
    
    for size, graph in sorted(graphs.items()):
        print(f"\nNetwork size: {size} nodes")
        
        # Label Propagation (fast)
        exec_time, memory, _ = benchmark_function(label_propagation, graph)
        results['Label Propagation'].add_result(size, exec_time, memory)
        print(f"  Label Prop.: {exec_time:.6f}s, {memory:.2f}MB")
        
        # Girvan-Newman (very slow, skip large graphs)
        if size <= 100:  # Only test on very small graphs
            num_communities = max(2, size // 50)
            exec_time, memory, _ = benchmark_function(girvan_newman, graph, num_communities)
            results['Girvan-Newman'].add_result(size, exec_time, memory)
            print(f"  Girvan-Newman: {exec_time:.6f}s, {memory:.2f}MB")
    
    return results


def plot_scalability(results: Dict[str, BenchmarkResult], title: str, 
                     filename: str, log_scale: bool = False):
    """
    Create scalability plot for benchmark results.
    
    Args:
        results: Dictionary of algorithm names to BenchmarkResult objects
        title: Plot title
        filename: Output filename
        log_scale: Whether to use log scale for y-axis
    """
    plt.figure(figsize=(12, 6))
    
    # Plot 1: Execution Time
    plt.subplot(1, 2, 1)
    for name, result in results.items():
        sizes, times, _ = result.get_data()
        if times:  # Only plot if we have data
            plt.plot(sizes, times, marker='o', label=name, linewidth=2)
    
    plt.xlabel('Network Size (nodes)', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.title(f'{title}\nExecution Time vs Network Size', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    if log_scale:
        plt.yscale('log')
        plt.xscale('log')
    
    # Plot 2: Memory Usage
    plt.subplot(1, 2, 2)
    for name, result in results.items():
        sizes, _, memory = result.get_data()
        if memory:  # Only plot if we have data
            plt.plot(sizes, memory, marker='s', label=name, linewidth=2)
    
    plt.xlabel('Network Size (nodes)', fontsize=12)
    plt.ylabel('Peak Memory (MB)', fontsize=12)
    plt.title(f'{title}\nMemory Usage vs Network Size', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\nSaved plot: {filename}")
    plt.close()


def fit_complexity_curve(sizes: List[int], times: List[float]) -> Tuple[str, float]:
    """
    Fit execution time to theoretical complexity classes.
    
    Returns:
        Tuple of (complexity_class, r_squared)
    """
    if len(sizes) < 3:
        return "Insufficient data", 0.0
    
    sizes_arr = np.array(sizes)
    times_arr = np.array(times)
    
    # Try different complexity classes
    models = {
        'O(n)': sizes_arr,
        'O(n log n)': sizes_arr * np.log(sizes_arr),
        'O(n²)': sizes_arr ** 2,
        'O(n³)': sizes_arr ** 3
    }
    
    best_fit = None
    best_r2 = -np.inf
    
    for name, x in models.items():
        # Linear regression
        coeffs = np.polyfit(x, times_arr, 1)
        predicted = coeffs[0] * x + coeffs[1]
        
        # R-squared
        ss_res = np.sum((times_arr - predicted) ** 2)
        ss_tot = np.sum((times_arr - np.mean(times_arr)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        if r2 > best_r2:
            best_r2 = r2
            best_fit = name
    
    return best_fit, best_r2


def generate_complexity_report(all_results: Dict[str, Dict[str, BenchmarkResult]]):
    """Generate complexity analysis report."""
    print("\n" + "=" * 70)
    print("COMPLEXITY ANALYSIS REPORT")
    print("=" * 70)
    
    for category, results in all_results.items():
        print(f"\n{category}:")
        print("-" * 70)
        print(f"{'Algorithm':<25} {'Best Fit':<15} {'R² Score':<10} {'Avg Time':<15}")
        print("-" * 70)
        
        for name, result in results.items():
            sizes, times, _ = result.get_data()
            if times:
                complexity, r2 = fit_complexity_curve(sizes, times)
                avg_time = np.mean(times)
                print(f"{name:<25} {complexity:<15} {r2:>8.4f}   {avg_time:>10.6f}s")


def create_comparison_table(all_results: Dict[str, Dict[str, BenchmarkResult]]):
    """Create performance comparison table."""
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON TABLE")
    print("=" * 70)
    
    # Get common size for comparison
    comparison_size = 200
    
    print(f"\nPerformance at {comparison_size} nodes:")
    print("-" * 70)
    print(f"{'Category':<25} {'Algorithm':<20} {'Time (s)':<12} {'Memory (MB)':<12}")
    print("-" * 70)
    
    for category, results in all_results.items():
        first = True
        for name, result in results.items():
            sizes, times, memory = result.get_data()
            if comparison_size in sizes:
                idx = sizes.index(comparison_size)
                category_label = category if first else ""
                print(f"{category_label:<25} {name:<20} {times[idx]:>10.6f}  {memory[idx]:>10.2f}")
                first = False


def main():
    """Run comprehensive benchmark suite."""
    print("=" * 70)
    print("COMPREHENSIVE BENCHMARKING SUITE")
    print("Social Network Analysis - Scalability Testing")
    print("=" * 70)
    
    # Define network sizes to test
    # Smaller sizes for expensive algorithms
    sizes = [50, 100, 200, 500, 1000]
    
    print(f"\nTesting network sizes: {sizes}")
    print(f"This may take several minutes...\n")
    
    # Generate test graphs
    graphs = generate_test_graphs(sizes)
    
    # Run benchmarks
    all_results = {}
    
    # 1. Connected Components
    cc_results = benchmark_connected_components(graphs)
    all_results['Connected Components'] = cc_results
    plot_scalability(cc_results, 'Connected Components Detection', 
                    'outputs/benchmark_connected_components.png')
    
    # 2. Centrality Measures
    cent_results = benchmark_centrality_measures(graphs)
    all_results['Centrality Measures'] = cent_results
    plot_scalability(cent_results, 'Centrality Measures', 
                    'outputs/benchmark_centrality.png', log_scale=True)
    
    # 3. Community Detection
    comm_results = benchmark_community_detection(graphs)
    all_results['Community Detection'] = comm_results
    plot_scalability(comm_results, 'Community Detection', 
                    'outputs/benchmark_community_detection.png')
    
    # Generate reports
    generate_complexity_report(all_results)
    create_comparison_table(all_results)
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - benchmark_connected_components.png")
    print("  - benchmark_centrality.png")
    print("  - benchmark_community_detection.png")
    print("\nCheck the plots to see scalability analysis!")


if __name__ == "__main__":
    main()
