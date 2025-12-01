# Social Network Analysis Project

A comprehensive implementation of graph algorithms for social network analysis, all built from scratch without NetworkX.

## 📁 Project Structure

```
FIND_MY_GIRL/
├── algorithms/          # Core algorithm implementations
│   ├── graph.py                    # Graph data structure
│   ├── traversal.py                # BFS, DFS, connected components
│   ├── union_find.py               # Union-Find data structure
│   ├── centrality.py               # Centrality measures
│   ├── community_detection.py      # Community detection algorithms
│   ├── graph_generator.py          # Holme-Kim network generator
│   ├── recommender.py              # Friend recommendation system
│   └── visualization.py            # Graph visualization utilities
│
├── scripts/            # Main execution scripts
│   ├── main.py                     # Main analysis pipeline
│   ├── benchmark.py                # Performance benchmarking
│   ├── analysis.py                 # Additional analysis tools
│   └── main_runner.py              # Alternative runner
│
├── tests/              # Test suites
│   ├── test_suite.py               # Comprehensive test suite
│   └── test_recommender.py         # Recommendation system tests
│
├── data/               # Generated data files
│   └── generated_graph.pkl         # Saved network graphs
│
├── outputs/            # Visualization outputs
│   ├── social_network.png
│   ├── communities.png
│   ├── pagerank.png
│   ├── degree_distribution.png
│   └── benchmark_*.png
│
├── run_analysis.py     # Quick run: main analysis
├── run_benchmark.py    # Quick run: benchmarks
├── run_tests.py        # Quick run: test suite
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### Run Main Analysis
```bash
python run_analysis.py
# Or: python scripts/main.py
```

### Run Benchmarks
```bash
python run_benchmark.py
# Or: python scripts/benchmark.py
```

### Run Tests
```bash
python run_tests.py
# Or: python tests/test_suite.py
```

### Test Recommendations
```bash
python tests/test_recommender.py
```

## 📊 Features

- **Graph Algorithms**: BFS, DFS, shortest paths, connected components
- **Centrality Measures**: Degree, betweenness, closeness, PageRank, eigenvector
- **Community Detection**: Label propagation, Girvan-Newman
- **Network Generation**: Holme-Kim model with realistic community structure
- **Friend Recommendations**: Multi-factor recommendation system
- **Visualization**: High-quality, zoomable network visualizations
- **Benchmarking**: Comprehensive performance analysis

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🎯 Algorithms Implemented

All algorithms are implemented **from scratch** without using NetworkX:

1. **Traversal**: BFS, DFS
2. **Connected Components**: BFS, DFS, Union-Find
3. **Centrality**: Degree, Betweenness, Closeness, PageRank, Eigenvector
4. **Community Detection**: Label Propagation, Girvan-Newman
5. **Network Generation**: Holme-Kim preferential attachment + clustering
6. **Recommendation**: Common friends, personality/interest matching, PageRank

## 📈 Usage Examples

### Generate and Analyze Network
```python
from algorithms.graph_generator import generate_social_network
from algorithms.centrality import compute_all_centralities

# Generate realistic network
graph = generate_social_network(num_users=200, avg_friends=8)

# Compute centralities
centralities = compute_all_centralities(graph)
```

### Visualize Communities
```python
from algorithms.community_detection import detect_communities
from algorithms.visualization import visualize_communities

# Detect communities
result = detect_communities(graph, method="label_propagation")

# Visualize
visualize_communities(graph, result["communities"], 
                     filename="outputs/my_communities.png")
```

## 👥 Authors

AAD Project Group - December 2025

## 📄 License

Educational project for graph theory and algorithm analysis.
