"""
Test Script for Friend Recommendation System
=============================================
Tests the refactored recommender system with all algorithms from scratch.

Author: AAD Project Group
Date: December 2025
"""

from graph import Graph
from graph_generator import generate_social_network
from recommender import interactive_recommend_friends
from centrality import compute_all_centralities


def main():
    """Main test function."""
    print("\n" + "=" * 70)
    print("FRIEND RECOMMENDATION SYSTEM - TEST")
    print("=" * 70)
    
    # Step 1: Generate a social network
    print("\n[Step 1] Generating social network...")
    print("Creating network with 50 users, average 8 friends per user...")
    
    graph = generate_social_network(
        num_users=50,
        avg_friends=8,
        community_structure=True,
        num_communities=3
    )
    
    print(f"✓ Generated graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    
    # Step 2: Calculate PageRank (simulating analysis team output)
    print("\n[Step 2] Computing PageRank scores (simulating analysis data)...")
    
    try:
        # Try to use centrality computation
        centralities = compute_all_centralities(graph)
        pagerank_data = centralities.get('pagerank', {})
        print(f"✓ Computed PageRank for {len(pagerank_data)} nodes")
    except Exception as e:
        print(f"⚠ Could not compute PageRank: {e}")
        print("  Using empty PageRank data...")
        pagerank_data = {}
    
    # Step 3: Run interactive recommendation system
    print("\n[Step 3] Starting interactive recommendation system...")
    print("\n" + "=" * 70)
    
    interactive_recommend_friends(graph, pagerank_data)
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
