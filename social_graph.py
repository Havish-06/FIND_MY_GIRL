import networkx as nx
import random
import matplotlib.pyplot as plt

# ==============================================================================
# 1. GRAPH GENERATION CLASS
# ==============================================================================

class RealisticSocialGraph:
    """Creates a scale-free, high-clustering graph (Holme-Kim) and assigns attributes."""
    def __init__(self, n_users=150):
        self.n = n_users
        self.G = None
        self.affiliations = ["University A", "University B", "Tech Corp", "Startup Inc", "Freelance", "Retired"]
        self.interests = ["Tech", "Music", "Hiking", "Gaming", "Cooking", "Sci-Fi", "Politics"]

    def generate(self):
        print(f"1. Generating Holme-Kim Topology (n={self.n})...")
        # Holme-Kim model: scale-free (m=2) with high clustering (p=0.5)
        self.G = nx.powerlaw_cluster_graph(n=self.n, m=2, p=0.5, seed=42)
        
        print("2. Detecting Structural Communities to inject Homophily...")
        # Use initial structural communities to guide attribute assignment
        communities = list(nx.community.greedy_modularity_communities(self.G))
        print(f"   -> Found {len(communities)} structural communities.")

        for comm_idx, community in enumerate(communities):
            primary_affil = self.affiliations[comm_idx % len(self.affiliations)]
            primary_interest = self.interests[comm_idx % len(self.interests)]
            
            for node in community:
                # 80% chance of matching community theme (Homophily)
                if random.random() < 0.8:
                    assigned_affil = primary_affil
                    assigned_tags = [primary_interest] + random.sample(self.interests, k=random.randint(1, 2))
                # 20% chance of random attributes (Noise)
                else:
                    assigned_affil = random.choice(self.affiliations)
                    assigned_tags = random.sample(self.interests, k=random.randint(2, 3))
                
                assigned_tags = list(set(assigned_tags))
                
                # Store all attributes
                self.G.nodes[node]['id'] = node
                self.G.nodes[node]['name'] = f"User_{node}"
                self.G.nodes[node]['affiliation'] = assigned_affil
                self.G.nodes[node]['tags'] = assigned_tags
                self.G.nodes[node]['ground_truth_community'] = comm_idx

        print("3. Graph Populated with Logic-Driven Attributes.")
        return self.G

# ==============================================================================
# 2. ANALYSIS AND COMMUNITY FUNCTIONS
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
            
    return GLC

def calculate_centralities(GLC):
    """Calculates and stores Degree, Betweenness, and PageRank centralities."""
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
    return GLC

def detect_and_store_communities(G):
    """Detects final communities and stores them as 'community_id'."""
    print("\n--- COMMUNITY DETECTION (Greedy Modularity) ---")
    communities = nx.community.greedy_modularity_communities(G)
    
    # Store the result as a node attribute 'community_id'
    for i, community in enumerate(communities):
        for node in community:
            # We store the community_id on the *final* graph G
            G.nodes[node]['community_id'] = i
    
    print(f"Detected and stored {len(communities)} final communities.")
    return G, len(communities)

# ==============================================================================
# 3. RECOMMENDER FUNCTIONS
# ==============================================================================

def calculate_interest_similarity(G, u, v):
    """Calculates Jaccard Similarity between the tags of two users (Attribute Score)."""
    tags_u = set(G.nodes[u].get('tags', []))
    tags_v = set(G.nodes[v].get('tags', []))

    if not tags_u and not tags_v:
        return 0.0
    
    intersection = len(tags_u.intersection(tags_v))
    union = len(tags_u.union(tags_v))
    
    return intersection / union

def recommend_friends(G, user_id, w_structural=0.6, w_attribute=0.4, community_bonus=0.2, max_distance=4):
    """
    Generates friend recommendations using a composite scoring model with penalties.
    """
    if user_id not in G.nodes():
        return f"User ID {user_id} not found."

    print(f"\n--- FRIEND RECOMMENDATIONS FOR USER {user_id} ---")
    
    # 1. Identify Candidates
    candidates = set(G.nodes()) - set(G.neighbors(user_id)) - {user_id}
    if not candidates: return "No potential candidates found."

    recommendation_scores = {}
    
    # 2. Pre-calculate Structural Indices (Jaccard)
    jaccard_scores = {
        (u, v): score for u, v, score in nx.jaccard_coefficient(G, [(user_id, c) for c in candidates])
    }
    
    # 3. Iterate through candidates and calculate the composite score
    for candidate_id in candidates:
        final_score = 0
        
        # --- A. Shortest Path Penalty (Hard Filter) ---
        try:
            shortest_path_distance = nx.shortest_path_length(G, source=user_id, target=candidate_id)
        except nx.NetworkXNoPath:
            shortest_path_distance = float('inf') 

        # If too far apart, the score is 0 and we skip to the next candidate
        if shortest_path_distance > max_distance:
             recommendation_scores[candidate_id] = 0
             continue 

        # --- B. Structural Term ---
        structural_score = jaccard_scores.get((user_id, candidate_id), 0)
        
        # --- C. Attribute Term ---
        attribute_score = calculate_interest_similarity(G, user_id, candidate_id)
        
        # --- D. Community Bonus ---
        community_match = False
        user_comm = G.nodes[user_id].get('community_id') 
        candidate_comm = G.nodes[candidate_id].get('community_id')
        if user_comm is not None and user_comm == candidate_comm:
             community_match = True

        bonus = community_bonus if community_match else 0
        
        # --- E. Final Composite Score ---
        final_score = (w_structural * structural_score) + \
                      (w_attribute * attribute_score) + \
                      bonus

        recommendation_scores[candidate_id] = final_score

    # 4. Sort and return the top 5 recommendations
    top_recommendations = sorted(recommendation_scores.items(), key=lambda item: item[1], reverse=True)[:5]
    
    # 5. Prepare Detailed Results
    print(f"Weights: Structural ({w_structural}), Attribute ({w_attribute}), Community Bonus ({community_bonus}), Max Distance ({max_distance})")
    
    results = []
    for rank, (uid, score) in enumerate(top_recommendations, 1):
        # We check the stored score, which might be 0 due to the path penalty
        if score == 0: continue 

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
# 4. VISUALIZATION FUNCTION
# ==============================================================================

def visualize_network_analysis(G, centrality_key='pagerank_c'):
    """Creates a compelling visualization highlighting Community and Centrality."""
    print(f"\n--- VISUALIZING NETWORK (Color by Community, Size by {centrality_key.upper()}) ---")

    if not G.nodes():
        print("Graph is empty. Cannot visualize.")
        return

    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)
    
    # Node Colors: Use the detected 'community_id'
    color_map = [G.nodes[n].get('community_id', G.nodes[n].get('ground_truth_community', 0)) for n in G.nodes()]
    
    # Node Size: Use the specified centrality score
    sizes = [G.nodes[n].get(centrality_key, 0) * 8000 + 100 for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos,
        node_size=sizes,
        node_color=color_map,
        cmap=plt.cm.coolwarm, 
        alpha=0.8,
        linewidths=0.5,
        edgecolors='black'
    )
    nx.draw_networkx_edges(G, pos, alpha=0.3)

    plt.title(f"Social Network Analysis: Communities & Influence ({centrality_key.upper()})", fontsize=16)
    plt.axis('off')
    plt.show()

# ==============================================================================
# 5. MAIN EXECUTION BLOCK
# ==============================================================================

if __name__ == "__main__":
    # 1. GENERATION & ATTRIBUTE INJECTION
    generator = RealisticSocialGraph(n_users=150)
    G_original = generator.generate() 
    
    # 2. ANALYSIS
    G_LC = find_social_circles(G_original)       # Get Largest Component (GLC)
    G_analyzed = calculate_centralities(G_LC)     # Calculate centralities on GLC
    # G_final is the GLC, now with all centrality attributes
    G_final, n_comm = detect_and_store_communities(G_analyzed) # Detect and store 'community_id'
    
    # Find a user to recommend for (e.g., User ID 50)
    test_user_id = 50 
    if test_user_id not in G_final.nodes():
        # Fallback to a random user if the hardcoded ID is not in the Largest Component
        test_user_id = random.choice(list(G_final.nodes()))
        
    # 3. FRIEND RECOMMENDER SYSTEM
    recommendation_results = recommend_friends(
        G_final, 
        user_id=test_user_id,
        w_structural=0.6,    
        w_attribute=0.4,     
        community_bonus=0.2,
        max_distance=4       # Implement Shortest Path Penalty
    )

    # 4. REPORTING (Recommendation Table)
    print("\n--- FINAL RECOMMENDATION TABLE ---")
    if isinstance(recommendation_results, list) and recommendation_results:
        print(f"Recommendations for User {test_user_id} (Affiliation: {G_final.nodes[test_user_id]['affiliation']}, Tags: {G_final.nodes[test_user_id]['tags']})")
        
        print("-" * 100)
        header = f"{'Rank':<5}{'User ID':<10}{'Final Score':<15}{'Struct. Score':<15}{'Interest Score':<15}{'Shared Friends':<18}{'Shared Tags'}"
        print(header)
        print("-" * 100)
        
        for r in recommendation_results:
            print(
                f"{r['Rank']:<5}{r['User ID']:<10}{r['Final Score']:<15}{r['Structural Score']:<15}{r['Interest Score']:<15}{r['Shared Friends Count']:<18}{r['Shared Tags']}"
            )
        print("-" * 100)
    else:
        print(recommendation_results)

    # 5. VISUALIZATION
    # We visualize the Largest Connected Component
    visualize_network_analysis(G_final, centrality_key='pagerank_c')