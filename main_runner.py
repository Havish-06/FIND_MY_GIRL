from social_graph import *
import random

if __name__ == "__main__":
    # --- STAGE 1 & 2: GENERATION & ATTRIBUTE INJECTION ---
    generator = RealisticSocialGraph(n_users=150)
    G_original = generator.generate() 
    
    # --- STAGE 3: ANALYSIS ---
    G_LC = find_social_circles(G_original)       
    G_analyzed = calculate_centralities(G_LC)     
    G_final, n_comm = detect_and_store_communities(G_analyzed) 
    
    # Find a user to recommend for (e.g., User ID 50, with fallback)
    test_user_id = 50 
    if test_user_id not in G_final.nodes():
        test_user_id = random.choice(list(G_final.nodes()))
        
    # --- STAGE 4: FRIEND RECOMMENDER SYSTEM ---
    recommendation_results = recommend_friends(
        G_final, 
        user_id=test_user_id,
        w_structural=0.6,    
        w_attribute=0.4,     
        community_bonus=0.2,
        max_distance=4       
    )

    # --- 5. REPORTING (Recommendation Table) ---
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

    # --- 6. VISUALIZATION ---
    visualize_network_analysis(G_final, centrality_key='pagerank_c')