# Quick Reference Guide

## Running the Project

### 1. Complete Analysis Pipeline
```bash
python main.py
```
Generates a 100-node network and performs full analysis with visualizations.

### 2. Test Suite
```bash
python test_suite.py
```
Runs all unit tests to verify algorithms work correctly.

### 3. Simple Demo
```bash
python analysis.py
```
Runs analysis on Zachary's Karate Club graph.

---

## Common Code Snippets

### Create a Custom Graph
```python
from graph import Graph

G = Graph()
G.add_node(1, name="Alice", age=25)
G.add_node(2, name="Bob", age=30)
G.add_edge(1, 2)
```

### Find Connected Components
```python
from traversal import find_connected_components_bfs

components = find_connected_components_bfs(G)
print(f"Number of components: {len(components)}")
```

### Compute PageRank
```python
from centrality import compute_pagerank

pagerank = compute_pagerank(G, alpha=0.85)
top_node = max(pagerank, key=pagerank.get)
print(f"Most influential: {top_node}")
```

### Detect Communities
```python
from community_detection import detect_communities

result = detect_communities(G, method="label_propagation")
print(f"Communities: {len(result['communities'])}")
print(f"Modularity: {result['modularity']:.4f}")
```

### Get Friend Recommendations
```python
from recommender import recommend_friends

recs = recommend_friends(G, user_id=0, k=10)
for user, score in recs[:5]:
    print(f"Recommend User {user}: {score:.3f}")
```

### Visualize Network
```python
from visualization import visualize_graph

visualize_graph(G, title="My Network", 
               filename="network.png", show=True)
```

---

## Algorithm Complexity Quick Reference

| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| BFS | O(V+E) | O(V) | Shortest paths, connectivity |
| DFS | O(V+E) | O(V) | Component finding, cycle detection |
| Union-Find | O(α(V)) | O(V) | Fast component queries |
| Degree Centrality | O(V) | O(V) | Quick importance measure |
| Betweenness | O(V×E) | O(V+E) | Bridge nodes, bottlenecks |
| PageRank | O(k(V+E)) | O(V) | Influence ranking |
| Label Propagation | O(kE) | O(V) | Fast community detection |

---

## Project Structure at a Glance

```
Core Algorithms:
  graph.py              → Graph data structure
  traversal.py          → BFS, DFS
  union_find.py         → Union-Find with optimizations
  centrality.py         → All centrality measures
  community_detection.py → Community algorithms

Applications:
  graph_generator.py    → Synthetic network creation
  recommender.py        → Friend recommendation
  visualization.py      → Network plotting

Executables:
  main.py              → Full analysis pipeline
  analysis.py          → Simple demo
  test_suite.py        → Unit tests
```

---

## Configuration Parameters

### Network Generation
```python
generate_social_network(
    num_users=100,        # Number of nodes
    avg_friends=15,       # Average degree
    community_structure=True,  # Create communities
    num_communities=4     # Number of communities
)
```

### PageRank
```python
compute_pagerank(
    G,
    alpha=0.85,          # Damping factor (0-1)
    max_iter=100,        # Max iterations
    tol=1e-6            # Convergence threshold
)
```

### Community Detection
```python
detect_communities(
    G,
    method="label_propagation",  # or "girvan_newman", "greedy_modularity"
    num_communities=None         # Target number (optional)
)
```

---

## Troubleshooting

**Problem**: ImportError: No module named 'matplotlib'
**Solution**: `pip install matplotlib`

**Problem**: Graph appears empty
**Solution**: Check that edges are added after nodes

**Problem**: Slow performance on large graphs
**Solution**: Use faster algorithms (BFS over Betweenness) or reduce network size

**Problem**: Communities not detected
**Solution**: Try different methods; some work better on different graph structures

---

## File Size Guide

| File | Lines | Purpose |
|------|-------|---------|
| graph.py | ~240 | Core data structure |
| traversal.py | ~280 | BFS, DFS algorithms |
| union_find.py | ~320 | Disjoint set operations |
| centrality.py | ~400 | All centrality measures |
| community_detection.py | ~380 | Community algorithms |
| graph_generator.py | ~400 | Network generation |
| recommender.py | ~450 | Recommendation system |
| visualization.py | ~450 | Plotting functions |
| main.py | ~350 | Analysis pipeline |

**Total**: ~3,300 lines of well-commented code

---

## Key Features Checklist

- [x] Graph implemented from scratch (no NetworkX for core operations)
- [x] BFS, DFS, Union-Find for components
- [x] Degree, Betweenness, Closeness, PageRank, Eigenvector centrality
- [x] Label Propagation, Girvan-Newman, Greedy Modularity communities
- [x] Friend recommender with multiple strategies
- [x] Personality tags and interests on nodes
- [x] Force-directed layout visualization
- [x] Comprehensive docstrings with complexity analysis
- [x] Modular, well-organized code
- [x] Full test suite
- [x] Detailed README

---

## Performance Tips

1. **For large graphs (>1000 nodes)**:
   - Use Union-Find for components (fastest)
   - Skip Betweenness centrality (O(V×E))
   - Use Label Propagation for communities (fastest)

2. **For visualization**:
   - Reduce iterations in force-directed layout
   - Use circular layout for speed
   - Save to file instead of showing (faster)

3. **For testing**:
   - Start with small graphs (10-50 nodes)
   - Gradually increase size
   - Profile slow sections with `time.time()`

---

**Questions?** Check README.md for full documentation.
