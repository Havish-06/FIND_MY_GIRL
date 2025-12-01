<<<<<<< HEAD
import networkx as nx
import random
import matplotlib.pyplot as plt

# ==============================================================================
# 1. GRAPH GENERATION (Your Original Code)
# ==============================================================================

class RealisticSocialGraph:
    def __init__(self, n_users=150): # Set to 150 for faster execution
        self.n = n_users
        self.G = None
        self.affiliations = ["University A", "University B", "Tech Corp", "Startup Inc", "Freelance", "Retired"]
        self.interests = ["Tech", "Music", "Hiking", "Gaming", "Cooking", "Sci-Fi", "Politics"]

    def generate(self):
        print(f"1. Generating Holme-Kim Topology (n={self.n})...")
        # Creates a scale-free graph with high clustering (p=0.5)
        self.G = nx.powerlaw_cluster_graph(n=self.n, m=2, p=0.5, seed=42)
        
        print("2. Detecting Structural Communities to inject Homophily...")
        # Note: Using the community structure found here to assign attributes
        communities = list(nx.community.greedy_modularity_communities(self.G))
        print(f"   -> Found {len(communities)} structural communities.")

        for comm_idx, community in enumerate(communities):
            primary_affil = self.affiliations[comm_idx % len(self.affiliations)]
            primary_interest = self.interests[comm_idx % len(self.interests)]
            
            for node in community:
                if random.random() < 0.8:
                    assigned_affil = primary_affil
                    assigned_tags = [primary_interest] + random.sample(self.interests, k=random.randint(1, 2))
                else:
                    assigned_affil = random.choice(self.affiliations)
                    assigned_tags = random.sample(self.interests, k=random.randint(2, 3))
                
                assigned_tags = list(set(assigned_tags))
                
                self.G.nodes[node]['id'] = node
                self.G.nodes[node]['name'] = f"User_{node}"
                self.G.nodes[node]['age'] = random.randint(18, 65)
                self.G.nodes[node]['affiliation'] = assigned_affil
                self.G.nodes[node]['tags'] = assigned_tags
                self.G.nodes[node]['ground_truth_community'] = comm_idx

        print("3. Graph Populated with Logic-Driven Attributes.")
        return self.G

# ==============================================================================
# 2. ANALYSIS FUNCTIONS
# ==============================================================================

def find_social_circles(G):
    """Finds all connected components and returns the Largest Connected Component (GLC)."""
    print("\n--- CONNECTED COMPONENTS ANALYSIS ---")
    
    components = list(nx.connected_components(G))
    n_circles = len(components)
    print(f"Total Isolated Social Circles Found: {n_circles}")
    
    if not G.nodes():
        return nx.Graph()
        
    largest_component_nodes = max(components, key=len)
    GLC = G.subgraph(largest_component_nodes).copy()
    
    print(f"Largest Circle Size: {len(GLC.nodes())} nodes ({len(GLC.nodes())/len(G.nodes()):.2%} of total)")
    
    # Store component ID for all nodes
    for i, component in enumerate(components):
        for node in component:
            G.nodes[node]['component_id'] = i
            
    return GLC

def calculate_centralities(GLC):
    """Calculates Degree, Betweenness, and PageRank centralities."""
    print("\n--- CENTRALITY ANALYSIS ---")
    if not GLC.nodes(): return GLC

    degree_c = nx.degree_centrality(GLC)
    betweenness_c = nx.betweenness_centrality(GLC)
    pagerank_c = nx.pagerank(GLC)
    
    for node in GLC.nodes():
        GLC.nodes[node]['degree_c'] = degree_c.get(node, 0)
        GLC.nodes[node]['betweenness_c'] = betweenness_c.get(node, 0)
        GLC.nodes[node]['pagerank_c'] = pagerank_c.get(node, 0)
        
    print("Centrality scores calculated and stored.")

    top_degree = sorted(degree_c.items(), key=lambda item: item[1], reverse=True)[:3]
    top_betweenness = sorted(betweenness_c.items(), key=lambda item: item[1], reverse=True)[:3]
    top_pagerank = sorted(pagerank_c.items(), key=lambda item: item[1], reverse=True)[:3]
    
    print(f"  * **Highest Degree (Popularity):** {[f'User {u} ({c:.3f})' for u, c in top_degree]}")
    print(f"  * **Highest Betweenness (Brokerage):** {[f'User {u} ({c:.3f})' for u, c in top_betweenness]}")
    print(f"  * **Highest PageRank (Prestige):** {[f'User {u} ({c:.3f})' for u, c in top_pagerank]}")
    
    return GLC

def detect_and_store_communities(G):
    """Detects final communities using Greedy Modularity and stores them as 'community_id'."""
    print("\n--- COMMUNITY DETECTION (Greedy Modularity) ---")
    
    communities = nx.community.greedy_modularity_communities(G)
    
    # Store the result as a node attribute 'community_id'
    for i, community in enumerate(communities):
        for node in community:
            G.nodes[node]['community_id'] = i
    
    print(f"Detected and stored {len(communities)} final communities.")
    return G, len(communities)

# ==============================================================================
# 3. RECOMMENDER FUNCTIONS
# ==============================================================================

def calculate_interest_similarity(G, u, v):
    """Calculates Jaccard Similarity between the tags of two users."""
    tags_u = set(G.nodes[u].get('tags', []))
    tags_v = set(G.nodes[v].get('tags', []))

    if not tags_u and not tags_v:
        return 0.0
    
    intersection = len(tags_u.intersection(tags_v))
    union = len(tags_u.union(tags_v))
    
    return intersection / union

def recommend_friends(G, user_id, w_structural=0.6, w_attribute=0.4, community_bonus=0.2):
    """Generates friend recommendations using a composite scoring model."""
    if user_id not in G.nodes():
        return f"User ID {user_id} not found."

    print(f"\n--- FRIEND RECOMMENDATIONS FOR USER {user_id} ---")
    
    candidates = set(G.nodes()) - set(G.neighbors(user_id)) - {user_id}
    if not candidates: return "No potential candidates found."

    recommendation_scores = {}
    
    # Pre-calculate Structural Indices (Jaccard)
    jaccard_scores = {
        (u, v): score for u, v, score in nx.jaccard_coefficient(G, [(user_id, c) for c in candidates])
    }
    
    for candidate_id in candidates:
        structural_score = jaccard_scores.get((user_id, candidate_id), 0)
        attribute_score = calculate_interest_similarity(G, user_id, candidate_id)
        
        community_match = False
        user_comm = G.nodes[user_id].get('community_id') 
        candidate_comm = G.nodes[candidate_id].get('community_id')
        if user_comm is not None and user_comm == candidate_comm:
             community_match = True

        bonus = community_bonus if community_match else 0
        
        final_score = (w_structural * structural_score) + \
                      (w_attribute * attribute_score) + \
                      bonus

        recommendation_scores[candidate_id] = final_score

    top_recommendations = sorted(recommendation_scores.items(), key=lambda item: item[1], reverse=True)[:5]
    
    # Print Detailed Results
    print(f"Weights: Structural ({w_structural}), Attribute ({w_attribute}), Community Bonus ({community_bonus})")
    
    results = []
    for rank, (uid, score) in enumerate(top_recommendations, 1):
        struct_score = jaccard_scores.get((user_id, uid), 0)
        attr_score = calculate_interest_similarity(G, user_id, uid)
        
        results.append({
            'Rank': rank,
            'User ID': uid,
            'Final Score': f"{score:.4f}",
            'Structural Score': f"{struct_score:.3f}",
            'Interest Score': f"{attr_score:.3f}",
            'Shared Tags': list(set(G.nodes[user_id].get('tags', [])).intersection(set(G.nodes[uid].get('tags', [])))),
            'Shared Friends Count': len(list(nx.common_neighbors(G, user_id, uid)))
        })
        
    return results

# ==============================================================================
# 4. VISUALIZATION FUNCTION (The Project's Final Deliverable)
# ==============================================================================

def visualize_network_analysis(G, centrality_key='pagerank_c'):
    """
    Creates a compelling visualization highlighting Community and Centrality.
    """
    print(f"\n--- VISUALIZING NETWORK (Color by Community, Size by {centrality_key.upper()}) ---")

    if not G.nodes():
        print("Graph is empty. Cannot visualize.")
        return

    # Use spring layout for a naturally clustered look
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)
    
    # 1. Node Colors: Use the detected 'community_id'
    try:
        color_map = [G.nodes[n].get('community_id', 0) for n in G.nodes()]
    except:
        # Fallback if 'community_id' wasn't successfully stored
        color_map = 'blue'

    # 2. Node Size: Use the specified centrality score
    try:
        # Scale the centrality score (e.g., PageRank) for visual effect
        sizes = [G.nodes[n].get(centrality_key, 0) * 8000 + 100 for n in G.nodes()]
    except:
        sizes = 100

    # Draw Nodes and Edges
    nx.draw_networkx_nodes(
        G, pos,
        node_size=sizes,
        node_color=color_map,
        cmap=plt.cm.coolwarm, # Use a colorful colormap
        alpha=0.8,
        linewidths=0.5,
        edgecolors='black'
    )
    nx.draw_networkx_edges(G, pos, alpha=0.3)

    plt.title(f"Social Network Analysis: Communities & Influence ({centrality_key.upper()})", fontsize=16)
    plt.axis('off')
    plt.show()
    

# ==============================================================================
# 5. MAIN EXECUTION BLOCK (Putting it all together)
# ==============================================================================

if __name__ == "__main__":
    # --- STAGE 1 & 2: GENERATION & ATTRIBUTE INJECTION ---
    generator = RealisticSocialGraph(n_users=150)
    G_original = generator.generate() 
    
    # --- STAGE 3: ANALYSIS ---
    G_LC = find_social_circles(G_original) # Get Largest Component
    G_analyzed = calculate_centralities(G_LC) # Calculate and store centralities
    G_final, n_comm = detect_and_store_communities(G_analyzed) # Detect and store 'community_id'

    # --- STAGE 4: FRIEND RECOMMENDER SYSTEM ---
    
    # Pick a random user from the largest component for demonstration
    test_user = random.choice(list(G_final.nodes()))
    
    recommendation_results = recommend_friends(
        G_final, 
        user_id=test_user,
        w_structural=0.6,    # Prioritize shared friends
        w_attribute=0.4,     # Secondary focus on shared interests
        community_bonus=0.2  # Bonus for being in the same cluster
    )

    print("\n--- FINAL RECOMMENDATION TABLE ---")
    if isinstance(recommendation_results, list):
        # Format and print the results clearly
        print(f"Recommendations for User {test_user} (Affiliation: {G_final.nodes[test_user]['affiliation']}, Tags: {G_final.nodes[test_user]['tags']})")
        
        # Simple table output
        print("-" * 100)
        print(f"{'Rank':<5}{'User ID':<10}{'Final Score':<15}{'Struct. Score':<15}{'Interest Score':<15}{'Shared Friends':<18}{'Shared Tags'}")
        print("-" * 100)
        
        for r in recommendation_results:
            print(
                f"{r['Rank']:<5}{r['User ID']:<10}{r['Final Score']:<15}{r['Structural Score']:<15}{r['Interest Score']:<15}{r['Shared Friends Count']:<18}{r['Shared Tags']}"
            )
        print("-" * 100)
    else:
        print(recommendation_results)

    # --- STAGE 5: VISUALIZATION ---
    visualize_network_analysis(G_final, centrality_key='pagerank_c')
=======
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
)
from traversal import (
    bfs, dfs,
    find_connected_components_bfs,
    find_connected_components_dfs,
    shortest_path_bfs,
    is_connected
)
from union_find import (
    find_connected_components_union_find,
    detect_cycle_union_find
)
from centrality import (
    compute_all_centralities,
    get_top_k_central_nodes
)
from community_detection import (
    detect_communities,
    modularity
)
from recommender import (
    recommend_friends,
    friends_of_friends,
    evaluate_recommendations
)
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
>>>>>>> temp-fix-branch
