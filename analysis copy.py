
"""
Graph Analysis Module - From Scratch Implementation
====================================================
This module serves as the main entry point for graph analysis operations.
All algorithms are implemented from scratch without NetworkX.

Author: AAD Project Group
Date: December 2025
"""

from graph import Graph
from centrality import (
    compute_degree_centrality,
    compute_betweenness_centrality,
    compute_pagerank,
    compute_closeness_centrality,
    compute_eigenvector_centrality,
    compute_all_centralities,
    get_top_k_central_nodes
)
from traversal import (
    bfs, dfs, dfs_recursive,
    find_connected_components_bfs,
    find_connected_components_dfs,
    shortest_path_bfs,
    is_connected
)
from union_find import (
    UnionFind,
    find_connected_components_union_find,
    detect_cycle_union_find,
    kruskal_mst
)


def create_karate_club_graph() -> Graph:
    """
    Create Zachary's Karate Club graph for testing.
    
    This is a famous social network of friendships between 34 members of a 
    karate club at a US university in the 1970s.
    
    Returns:
        Graph: The karate club social network
    
    Time Complexity: O(V + E)
    Space Complexity: O(V + E)
    """
    G = Graph()
    
    # Add all 34 members
    for i in range(34):
        G.add_node(i)
    
    # Add friendships (edges) - Zachary's Karate Club network
    edges = [
        (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
        (0, 10), (0, 11), (0, 12), (0, 13), (0, 17), (0, 19), (0, 21), (0, 31),
        (1, 2), (1, 3), (1, 7), (1, 13), (1, 17), (1, 19), (1, 21), (1, 30),
        (2, 3), (2, 7), (2, 8), (2, 9), (2, 13), (2, 27), (2, 28), (2, 32),
        (3, 7), (3, 12), (3, 13),
        (4, 6), (4, 10),
        (5, 6), (5, 10), (5, 16),
        (6, 16),
        (8, 30), (8, 32), (8, 33),
        (9, 33),
        (13, 33),
        (14, 32), (14, 33), 
        (15, 32), (15, 33),
        (18, 32), (18, 33),
        (19, 33),
        (20, 32), (20, 33),
        (22, 32), (22, 33),
        (23, 25), (23, 27), (23, 29), (23, 32), (23, 33),
        (24, 25), (24, 27), (24, 31),
        (25, 31),
        (26, 29), (26, 33),
        (27, 33),
        (28, 31), (28, 33),
        (29, 32), (29, 33),
        (30, 32), (30, 33),
        (31, 32), (31, 33),
        (32, 33)
    ]
    
    for u, v in edges:
        G.add_edge(u, v)
    
    return G


# ===========================================================
# DEMO CODE
# ===========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("GRAPH ANALYSIS - FROM SCRATCH IMPLEMENTATION")
    print("=" * 60)
    
    # Create test graph (Zachary's Karate Club)
    print("\n[1] Creating Zachary's Karate Club Graph...")
    G = create_karate_club_graph()
    print(f"    Nodes: {G.number_of_nodes()}")
    print(f"    Edges: {G.number_of_edges()}")
    
    # Test connectivity
    print("\n[2] Testing Graph Connectivity...")
    connected = is_connected(G)
    print(f"    Is graph connected? {connected}")
    
    # Find connected components
    print("\n[3] Finding Connected Components...")
    components_bfs = find_connected_components_bfs(G)
    components_dfs = find_connected_components_dfs(G)
    components_uf = find_connected_components_union_find(G)
    
    print(f"    Number of components (BFS): {len(components_bfs)}")
    print(f"    Number of components (DFS): {len(components_dfs)}")
    print(f"    Number of components (Union-Find): {len(components_uf)}")
    
    # Compute all centrality measures
    print("\n[4] Computing Centrality Measures...")
    centralities = compute_all_centralities(G)
    
    print("\n    === TOP 5 NODES BY DEGREE CENTRALITY ===")
    top_degree = get_top_k_central_nodes(centralities["degree"], k=5)
    for node, score in top_degree:
        print(f"    Node {node}: {score:.4f}")
    
    print("\n    === TOP 5 NODES BY BETWEENNESS CENTRALITY ===")
    top_betweenness = get_top_k_central_nodes(centralities["betweenness"], k=5)
    for node, score in top_betweenness:
        print(f"    Node {node}: {score:.4f}")
    
    print("\n    === TOP 5 NODES BY PAGERANK ===")
    top_pagerank = get_top_k_central_nodes(centralities["pagerank"], k=5)
    for node, score in top_pagerank:
        print(f"    Node {node}: {score:.4f}")
    
    print("\n    === TOP 5 NODES BY CLOSENESS CENTRALITY ===")
    top_closeness = get_top_k_central_nodes(centralities["closeness"], k=5)
    for node, score in top_closeness:
        print(f"    Node {node}: {score:.4f}")
    
    print("\n    === TOP 5 NODES BY EIGENVECTOR CENTRALITY ===")
    top_eigenvector = get_top_k_central_nodes(centralities["eigenvector"], k=5)
    for node, score in top_eigenvector:
        print(f"    Node {node}: {score:.4f}")
    
    # Test shortest path
    print("\n[5] Finding Shortest Path (Node 0 to Node 33)...")
    path = shortest_path_bfs(G, 0, 33)
    print(f"    Path: {' -> '.join(map(str, path))}")
    print(f"    Path length: {len(path) - 1} edges")
    
    # Test cycle detection
    print("\n[6] Testing Cycle Detection...")
    has_cycle = detect_cycle_union_find(G)
    print(f"    Graph has cycle? {has_cycle}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
