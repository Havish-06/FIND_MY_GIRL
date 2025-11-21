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