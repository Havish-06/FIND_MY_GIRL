"""
Social Network Analysis - Main Script
======================================
Comprehensive analysis of Facebook-like social networks with:
- Connected components analysis
- Centrality measures
- Community detection
- Friend recommendations
- Visualization

All algorithms implemented from scratch without NetworkX.

Author: AAD Project Group
Date: December 2025
"""

import random
import time
from typing import Dict, List, Any

# Import our custom modules
from graph import Graph
from graph_generator import (
    generate_social_network, 
    generate_small_world_network,
    generate_scale_free_network
)#havish


from traversal import (
    bfs, dfs,
    find_connected_components_bfs,
    find_connected_components_dfs,
    shortest_path_bfs,
    is_connected
)#sashank


from union_find import (
    find_connected_components_union_find,
    detect_cycle_union_find
)#anish


from centrality import (
    compute_all_centralities,
    get_top_k_central_nodes
)#havish

from community_detection import (
    detect_communities,
    modularity
)#anish


from recommender import (
    recommend_friends,
    friends_of_friends,
    evaluate_recommendations
)#abhinav 



from visualization import (
    visualize_graph,
    visualize_communities,
    visualize_centrality,
    plot_degree_distribution
)


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def analyze_connectivity(graph: Graph):
    """
    Analyze graph connectivity using multiple methods.
    
    Args:
        graph (Graph): The graph to analyze
    """
    print_section_header("CONNECTIVITY ANALYSIS")
    
    # Check if graph is connected
    connected = is_connected(graph)
    print(f"\n[1] Graph Connectivity")
    print(f"    Is the graph connected? {connected}")
    
    # Find connected components using different algorithms
    print(f"\n[2] Connected Components Detection")
    
    # BFS method
    start_time = time.time()
    components_bfs = find_connected_components_bfs(graph)
    bfs_time = time.time() - start_time
    print(f"    BFS Method: {len(components_bfs)} components (Time: {bfs_time:.6f}s)")
    
    # DFS method
    start_time = time.time()
    components_dfs = find_connected_components_dfs(graph)
    dfs_time = time.time() - start_time
    print(f"    DFS Method: {len(components_dfs)} components (Time: {dfs_time:.6f}s)")
    
    # Union-Find method
    start_time = time.time()
    components_uf = find_connected_components_union_find(graph)
    uf_time = time.time() - start_time
    print(f"    Union-Find: {len(components_uf)} components (Time: {uf_time:.6f}s)")
    
    # Show component sizes
    if len(components_bfs) > 1:
        print(f"\n[3] Component Sizes:")
        for i, component in enumerate(components_bfs, 1):
            print(f"    Component {i}: {len(component)} nodes")
    
    # Cycle detection
    has_cycle = detect_cycle_union_find(graph)
    print(f"\n[4] Cycle Detection")
    print(f"    Does the graph contain cycles? {has_cycle}")


def analyze_centrality(graph: Graph):
    """
    Compute and analyze various centrality measures.
    
    Args:
        graph (Graph): The graph to analyze
    """
    print_section_header("CENTRALITY ANALYSIS")
    
    print("\n[1] Computing Centrality Measures...")
    
    # Compute all centralities
    start_time = time.time()
    centralities = compute_all_centralities(graph)
    total_time = time.time() - start_time
    
    print(f"    Computation completed in {total_time:.2f} seconds")
    
    # Display top nodes for each measure
    measures = ["degree", "betweenness", "closeness", "pagerank", "eigenvector"]
    
    for measure in measures:
        print(f"\n[2] Top 10 Nodes by {measure.capitalize()} Centrality:")
        top_nodes = get_top_k_central_nodes(centralities[measure], k=10)
        
        for rank, (node, score) in enumerate(top_nodes, 1):
            # Get node attributes
            name = graph.get_node_attribute(node, "name", f"User{node}")
            personality = graph.get_node_attribute(node, "personality", [])
            
            print(f"    {rank:2d}. Node {node:3d} ({name:10s}) - "
                  f"Score: {score:.4f} - Traits: {', '.join(personality[:2])}")
    
    return centralities


def analyze_communities(graph: Graph):
    """
    Detect and analyze communities in the graph.
    
    Args:
        graph (Graph): The graph to analyze
    """
    print_section_header("COMMUNITY DETECTION")
    
    methods = [
        ("label_propagation", "Label Propagation"),
        ("girvan_newman", "Girvan-Newman"),
        ("greedy_modularity", "Greedy Modularity")
    ]
    
    results = {}
    
    for method, method_name in methods:
        print(f"\n[{methods.index((method, method_name)) + 1}] {method_name} Algorithm")
        
        try:
            start_time = time.time()
            
            if method == "girvan_newman":
                result = detect_communities(graph, method=method, num_communities=3)
            else:
                result = detect_communities(graph, method=method)
            
            elapsed_time = time.time() - start_time
            
            communities = result["communities"]
            mod = result["modularity"]
            
            print(f"    Number of communities: {len(communities)}")
            print(f"    Modularity: {mod:.4f}")
            print(f"    Computation time: {elapsed_time:.4f}s")
            
            # Show community sizes
            print(f"    Community sizes: {[len(c) for c in communities]}")
            
            results[method] = result
            
        except Exception as e:
            print(f"    Error: {e}")
    
    # Return the best result (highest modularity)
    if results:
        best_method = max(results.keys(), key=lambda k: results[k]["modularity"])
        print(f"\n[4] Best Method: {best_method} "
              f"(Modularity: {results[best_method]['modularity']:.4f})")
        return results[best_method]
    
    return None


def analyze_recommendations(graph: Graph, sample_users: int = 5):
    """
    Generate and analyze friend recommendations.
    
    Args:
        graph (Graph): The graph to analyze
        sample_users (int): Number of users to generate recommendations for
    """
    print_section_header("FRIEND RECOMMENDATION SYSTEM")
    
    nodes = graph.get_nodes()
    
    if len(nodes) == 0:
        print("    No users in the graph")
        return
    
    # Select random users for demonstration
    sample_size = min(sample_users, len(nodes))
    sample_nodes = random.sample(nodes, sample_size)
    
    print(f"\n[1] Generating Recommendations for {sample_size} Random Users\n")
    
    for i, user in enumerate(sample_nodes, 1):
        # Get user info
        name = graph.get_node_attribute(user, "name", f"User{user}")
        personality = graph.get_node_attribute(user, "personality", [])
        interests = graph.get_node_attribute(user, "interests", [])
        num_friends = graph.degree(user)
        
        print(f"    User {i}: {name} (ID: {user})")
        print(f"    Current friends: {num_friends}")
        print(f"    Personality: {', '.join(personality)}")
        print(f"    Interests: {', '.join(interests[:3])}")
        
        # Generate recommendations
        recommendations = recommend_friends(graph, user, k=5)
        
        if recommendations:
            print(f"    Top 5 Friend Recommendations:")
            for rank, (rec_user, score) in enumerate(recommendations, 1):
                rec_name = graph.get_node_attribute(rec_user, "name", f"User{rec_user}")
                rec_interests = graph.get_node_attribute(rec_user, "interests", [])
                
                # Calculate common friends
                from recommender import get_common_friends
                common = get_common_friends(graph, user, rec_user)
                
                print(f"      {rank}. {rec_name} (ID: {rec_user}) - "
                      f"Score: {score:.3f} - Common friends: {len(common)}")
        else:
            print(f"    No recommendations available")
        
        print()


def generate_network_statistics(graph: Graph):
    """
    Generate comprehensive network statistics.
    
    Args:
        graph (Graph): The graph to analyze
    """
    print_section_header("NETWORK STATISTICS")
    
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    
    # Basic statistics
    print(f"\n[1] Basic Statistics")
    print(f"    Number of nodes: {len(nodes)}")
    print(f"    Number of edges: {len(edges)}")
    
    # Degree statistics
    degrees = [graph.degree(node) for node in nodes]
    
    if degrees:
        avg_degree = sum(degrees) / len(degrees)
        max_degree = max(degrees)
        min_degree = min(degrees)
        
        print(f"\n[2] Degree Statistics")
        print(f"    Average degree: {avg_degree:.2f}")
        print(f"    Maximum degree: {max_degree}")
        print(f"    Minimum degree: {min_degree}")
        print(f"    Density: {(2 * len(edges)) / (len(nodes) * (len(nodes) - 1)):.4f}")
    
    # Personality distribution
    print(f"\n[3] Personality Trait Distribution")
    trait_counts = {}
    
    for node in nodes:
        traits = graph.get_node_attribute(node, "personality", [])
        for trait in traits:
            trait_counts[trait] = trait_counts.get(trait, 0) + 1
    
    # Show top 5 traits
    top_traits = sorted(trait_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for trait, count in top_traits:
        print(f"    {trait}: {count} users")
    
    # Interest distribution
    print(f"\n[4] Interest Distribution")
    interest_counts = {}
    
    for node in nodes:
        interests = graph.get_node_attribute(node, "interests", [])
        for interest in interests:
            interest_counts[interest] = interest_counts.get(interest, 0) + 1
    
    # Show top 5 interests
    top_interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for interest, count in top_interests:
        print(f"    {interest}: {count} users")


def main():
    """
    Main analysis pipeline.
    """
    print("\n" + "=" * 70)
    print("  SOCIAL NETWORK ANALYSIS - COMPREHENSIVE PROJECT")
    print("  Graph Theory Algorithms - Implemented from Scratch")
    print("=" * 70)
    
    # Configuration
    NUM_USERS = 100
    AVG_FRIENDS = 15
    NUM_COMMUNITIES = 4
    
    print(f"\n[Configuration]")
    print(f"  Network size: {NUM_USERS} users")
    print(f"  Average friends: {AVG_FRIENDS}")
    print(f"  Communities: {NUM_COMMUNITIES}")
    
    # Generate social network
    print_section_header("NETWORK GENERATION")
    print(f"\n[1] Generating Social Network...")
    
    start_time = time.time()
    graph = generate_social_network(
        num_users=NUM_USERS,
        avg_friends=AVG_FRIENDS,
        community_structure=True,
        num_communities=NUM_COMMUNITIES
    )
    gen_time = time.time() - start_time
    
    print(f"    Network generated in {gen_time:.2f} seconds")
    print(f"    Nodes: {graph.number_of_nodes()}")
    print(f"    Edges: {graph.number_of_edges()}")
    
    # Run all analyses
    generate_network_statistics(graph)
    analyze_connectivity(graph)
    centralities = analyze_centrality(graph)
    community_result = analyze_communities(graph)
    analyze_recommendations(graph, sample_users=3)
    
    # Visualization
    print_section_header("VISUALIZATION")
    print("\n[1] Generating Visualizations...")
    
    try:
        # Visualize the graph
        print("    - Creating network visualization...")
        visualize_graph(graph, title="Social Network", 
                       filename="social_network.png", show=False)
        
        # Visualize communities
        if community_result:
            print("    - Creating community visualization...")
            visualize_communities(graph, community_result["communities"],
                                title="Community Structure",
                                filename="communities.png", show=False)
        
        # Visualize PageRank
        if centralities:
            print("    - Creating PageRank visualization...")
            visualize_centrality(graph, centralities["pagerank"],
                               centrality_name="PageRank",
                               filename="pagerank.png", show=False)
        
        # Plot degree distribution
        print("    - Creating degree distribution plot...")
        plot_degree_distribution(graph, filename="degree_distribution.png", show=False)
        
        print("\n    All visualizations saved successfully!")
        
    except Exception as e:
        print(f"\n    Visualization skipped (install matplotlib): {e}")
    
    # Final summary
    print_section_header("ANALYSIS COMPLETE")
    print("\n  ✓ Network generated and analyzed successfully")
    print("  ✓ All algorithms implemented from scratch (no NetworkX)")
    print("  ✓ Results saved to files")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run main analysis
    main()
