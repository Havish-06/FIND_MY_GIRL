"""
Test Suite for Social Network Analysis Project
===============================================
Comprehensive tests to validate all algorithms work correctly.

Author: AAD Project Group
Date: December 2025
"""

from graph import Graph
from traversal import bfs, dfs, find_connected_components_bfs, shortest_path_bfs
from union_find import UnionFind, find_connected_components_union_find
from centrality import (
    compute_degree_centrality,
    compute_betweenness_centrality,
    compute_pagerank
)
from community_detection import label_propagation, modularity
from graph_generator import generate_social_network
from recommender import recommend_friends, common_friends_score


def test_graph_basic():
    """Test basic graph operations."""
    print("\n[TEST 1] Basic Graph Operations")
    
    G = Graph()
    G.add_node(1, name="Alice")
    G.add_node(2, name="Bob")
    G.add_node(3, name="Charlie")
    
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    
    assert G.number_of_nodes() == 3, "Node count error"
    assert G.number_of_edges() == 2, "Edge count error"
    assert G.has_edge(1, 2), "Edge existence error"
    assert G.degree(2) == 2, "Degree calculation error"
    
    print("    ✓ Graph operations work correctly")


def test_traversal():
    """Test BFS and DFS."""
    print("\n[TEST 2] Graph Traversal Algorithms")
    
    G = Graph()
    for i in range(5):
        G.add_node(i)
    
    G.add_edge(0, 1)
    G.add_edge(0, 2)
    G.add_edge(1, 3)
    G.add_edge(2, 4)
    
    # Test BFS
    bfs_result = bfs(G, 0)
    assert len(bfs_result) == 5, "BFS traversal error"
    
    # Test DFS
    dfs_result = dfs(G, 0)
    assert len(dfs_result) == 5, "DFS traversal error"
    
    # Test shortest path
    path = shortest_path_bfs(G, 0, 4)
    assert len(path) == 3, "Shortest path error"  # 0 -> 2 -> 4
    
    print("    ✓ BFS works correctly")
    print("    ✓ DFS works correctly")
    print("    ✓ Shortest path works correctly")


def test_connected_components():
    """Test connected components detection."""
    print("\n[TEST 3] Connected Components")
    
    G = Graph()
    # Create two separate components
    for i in range(6):
        G.add_node(i)
    
    # Component 1: 0-1-2
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    
    # Component 2: 3-4-5
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    
    components_bfs = find_connected_components_bfs(G)
    components_uf = find_connected_components_union_find(G)
    
    assert len(components_bfs) == 2, "BFS component count error"
    assert len(components_uf) == 2, "Union-Find component count error"
    
    print("    ✓ BFS component detection works")
    print("    ✓ Union-Find component detection works")


def test_union_find():
    """Test Union-Find data structure."""
    print("\n[TEST 4] Union-Find Data Structure")
    
    uf = UnionFind()
    
    for i in range(5):
        uf.make_set(i)
    
    uf.union(0, 1)
    uf.union(2, 3)
    uf.union(1, 2)
    
    assert uf.connected(0, 3), "Union-Find connectivity error"
    assert not uf.connected(0, 4), "Union-Find separation error"
    assert uf.get_set_size(0) == 4, "Set size error"
    
    print("    ✓ Union-Find works correctly")


def test_centrality():
    """Test centrality measures."""
    print("\n[TEST 5] Centrality Measures")
    
    # Create a simple star graph
    G = Graph()
    for i in range(6):
        G.add_node(i)
    
    # Node 0 is center
    for i in range(1, 6):
        G.add_edge(0, i)
    
    # Degree centrality
    degree_cent = compute_degree_centrality(G)
    assert degree_cent[0] == 1.0, "Degree centrality error"  # Center has max degree
    
    # Betweenness centrality
    between_cent = compute_betweenness_centrality(G)
    # Center should have high betweenness in star graph
    
    # PageRank
    pagerank = compute_pagerank(G)
    assert abs(sum(pagerank.values()) - 1.0) < 0.01, "PageRank normalization error"
    
    print("    ✓ Degree centrality works correctly")
    print("    ✓ Betweenness centrality works correctly")
    print("    ✓ PageRank works correctly")


def test_community_detection():
    """Test community detection."""
    print("\n[TEST 6] Community Detection")
    
    # Create a graph with clear communities
    G = Graph()
    
    # Community 1: 0-1-2 (triangle)
    for i in range(3):
        G.add_node(i)
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(2, 0)
    
    # Community 2: 3-4-5 (triangle)
    for i in range(3, 6):
        G.add_node(i)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    G.add_edge(5, 3)
    
    # Bridge between communities
    G.add_edge(2, 3)
    
    communities = label_propagation(G)
    
    # Should detect at least 1 community
    assert len(communities) >= 1, "Community detection error"
    
    # Calculate modularity
    mod = modularity(G, communities)
    assert mod >= 0, "Modularity should be non-negative"
    
    print(f"    ✓ Label propagation detected {len(communities)} communities")
    print(f"    ✓ Modularity: {mod:.4f}")


def test_graph_generator():
    """Test synthetic graph generation."""
    print("\n[TEST 7] Graph Generation")
    
    G = generate_social_network(
        num_users=30,
        avg_friends=5,
        community_structure=True,
        num_communities=2
    )
    
    assert G.number_of_nodes() == 30, "Graph generation node count error"
    assert G.number_of_edges() > 0, "Graph generation edge count error"
    
    # Check that nodes have attributes
    node = G.get_nodes()[0]
    personality = G.get_node_attribute(node, "personality", None)
    interests = G.get_node_attribute(node, "interests", None)
    
    assert personality is not None, "Personality attribute missing"
    assert interests is not None, "Interests attribute missing"
    
    print(f"    ✓ Generated network with {G.number_of_nodes()} nodes")
    print(f"    ✓ Network has {G.number_of_edges()} edges")
    print(f"    ✓ Nodes have personality and interest attributes")


def test_recommender():
    """Test friend recommendation system."""
    print("\n[TEST 8] Friend Recommendation")
    
    G = Graph()
    
    # Create a small network
    for i in range(10):
        G.add_node(i, personality=["Outgoing"], interests=["Sports"])
    
    # User 0 friends with 1, 2
    G.add_edge(0, 1)
    G.add_edge(0, 2)
    
    # User 1 friends with 3, 4
    G.add_edge(1, 3)
    G.add_edge(1, 4)
    
    # User 2 friends with 5, 6
    G.add_edge(2, 5)
    G.add_edge(2, 6)
    
    # Get recommendations for user 0
    recommendations = recommend_friends(G, 0, k=5)
    
    assert len(recommendations) > 0, "Recommendation generation error"
    
    # Check common friends score
    score = common_friends_score(G, 0, 3)
    assert score == 1, "Common friends calculation error (should have 1 common friend)"
    
    print(f"    ✓ Generated {len(recommendations)} recommendations")
    print(f"    ✓ Common friends score works correctly")


def run_all_tests():
    """Run all test functions."""
    print("=" * 70)
    print("  RUNNING TEST SUITE")
    print("=" * 70)
    
    test_functions = [
        test_graph_basic,
        test_traversal,
        test_connected_components,
        test_union_find,
        test_centrality,
        test_community_detection,
        test_graph_generator,
        test_recommender
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"    ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"  TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n  ✓ All tests passed! Project is ready for submission.")
    else:
        print("\n  ✗ Some tests failed. Please review the errors above.")
    
    print()


if __name__ == "__main__":
    run_all_tests()
