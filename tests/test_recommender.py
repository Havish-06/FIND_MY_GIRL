"""
Friend Recommendation System
Implement a friend recommendation system for social networks from scratch.
Uses multiple strategies: common friends, personality similarity, and interest matching.
Leverages existing implementations from centrality.py, community_detection.py, and traversal.py.
"""

from typing import List, Dict, Tuple, Any, Set
from algorithms.graph import Graph
from collections import Counter, deque
import math

# Import existing implementations
from algorithms.centrality import compute_pagerank
from algorithms.community_detection import detect_communities
from algorithms.traversal import find_connected_components_bfs


# ==============================================================================
# 1. BFS FOR SHORTEST PATH (LIGHTWEIGHT VERSION - ONLY USED IF NEEDED)
# ==============================================================================

# Note: We don't need a separate shortest path function anymore because
# bfs_find_candidates_within_distance already computes distances during BFS!


# ==============================================================================
# 2. BFS TO FIND ALL CANDIDATES WITHIN MAX DISTANCE
# ==============================================================================

def bfs_find_candidates_within_distance(graph: Graph, user: Any, max_distance: int = 4) -> Dict[Any, int]:
    """
    Use BFS to find all nodes within max_distance hops from user.
    Returns only candidates (excludes user and direct friends).
    
    This is much more efficient than checking all nodes in the graph!
    
    Args:
        graph (Graph): The social network graph
        user: User ID
        max_distance (int): Maximum distance to search
    
    Returns:
        Dictionary mapping candidate_id -> distance
    
    Time Complexity: O(V + E) in worst case, but typically much faster
    Space Complexity: O(V)
    """
    if user not in graph.get_nodes():
        return {}
    
    queue = deque([(user, 0)])
    distances = {user: 0}
    direct_friends = graph.get_neighbors(user)
    
    while queue:
        current, dist = queue.popleft()
        
        # Don't explore beyond max_distance
        if dist >= max_distance:
            continue
            
        for neighbor in graph.get_neighbors(current):
            if neighbor not in distances:
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))
    
    # Return only candidates: exclude user and direct friends (distance > 1)
    candidates = {node: dist for node, dist in distances.items() 
                  if dist > 1 and node not in direct_friends and node != user}
    
    return candidates


# ==============================================================================
# 3. JACCARD COEFFICIENT FOR STRUCTURAL SIMILARITY (COMMON NEIGHBORS)
# ==============================================================================

def calculate_jaccard_structural(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate Jaccard coefficient based on common neighbors (structural score).
    Retrieves direct neighbors from adjacency list (O(1) lookup).
    
    Jaccard = |intersection| / |union|
    
    Args:
        graph (Graph): The social network graph
        user1: First user ID
        user2: Second user ID
    
    Returns:
        Jaccard coefficient (0.0 to 1.0)
    
    Time Complexity: O(d) where d is average degree
    Space Complexity: O(d)
    """
    # Get direct neighbors from adjacency list (simple dictionary lookup)
    neighbors1 = graph.get_neighbors(user1)
    neighbors2 = graph.get_neighbors(user2)
    
    # Calculate intersection and union
    intersection = neighbors1 & neighbors2
    union = neighbors1 | neighbors2
    
    if len(union) == 0:
        return 0.0
    
    return len(intersection) / len(union)


# ==============================================================================
# 4. JACCARD COEFFICIENT FOR INTEREST SIMILARITY (PERSONALITY TAGS)
# ==============================================================================

def calculate_jaccard_interests(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate Jaccard similarity based on shared interests/personality tags.
    
    Jaccard = |shared_interests| / |total_unique_interests|
    
    Args:
        graph (Graph): The social network graph
        user1: First user ID
        user2: Second user ID
    
    Returns:
        Jaccard coefficient for interests (0.0 to 1.0)
    
    Time Complexity: O(k) where k is number of interests
    Space Complexity: O(k)
    """
    # Get interests for both users
    interests1 = set(graph.get_node_attribute(user1, 'interests', []))
    interests2 = set(graph.get_node_attribute(user2, 'interests', []))
    
    # Also consider personality traits
    personality1 = set(graph.get_node_attribute(user1, 'personality', []))
    personality2 = set(graph.get_node_attribute(user2, 'personality', []))
    
    # Combine interests and personality
    tags1 = interests1 | personality1
    tags2 = interests2 | personality2
    
    # Calculate Jaccard
    intersection = tags1 & tags2
    union = tags1 | tags2
    
    if len(union) == 0:
        return 0.0
    
    return len(intersection) / len(union)


# ==============================================================================
# 5. COMMUNITY DETECTION (USE EXISTING IMPLEMENTATION)
# ==============================================================================

# Note: We use find_connected_components_bfs from traversal.py instead of reimplementing
# This function is already imported at the top of the file


# ==============================================================================
# 6. CHECK IF TWO USERS BELONG TO SAME COMMUNITY
# ==============================================================================

def check_community_match(graph: Graph, user1: Any, user2: Any, 
                         components: List[List[Any]]) -> Tuple[bool, int]:
    """
    Check if two users belong to the same connected component (community).
    
    Args:
        graph (Graph): The social network graph
        user1: First user ID
        user2: Second user ID
        components: List of connected components
    
    Returns:
        Tuple of (same_community: bool, community_size: int)
    
    Time Complexity: O(C) where C is number of components
    Space Complexity: O(1)
    """
    for component in components:
        if user1 in component and user2 in component:
            return True, len(component)
    
    return False, 0


# ==============================================================================
# 7. DYNAMIC COMMUNITY BONUS CALCULATION
# ==============================================================================

def calculate_dynamic_community_bonus(community_size: int) -> float:
    """
    Calculate a dynamic bonus inversely proportional to community size.
    Smaller communities get higher bonuses (more exclusive).
    
    Args:
        community_size (int): Size of the community
    
    Returns:
        Bonus score (0.0 to 0.4)
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    MIN_SIZE_THRESHOLD = 5
    MAX_BONUS = 0.4
    SCALING_FACTOR = 10
    
    effective_size = max(community_size, MIN_SIZE_THRESHOLD)
    bonus = MAX_BONUS * (SCALING_FACTOR / (effective_size + SCALING_FACTOR))
    
    return min(bonus, MAX_BONUS)


# ==============================================================================
# 8. PAGERANK-BASED POPULARITY PENALTY
# ==============================================================================

def calculate_pagerank_penalty(graph: Graph, user: Any, 
                              pagerank_data: Dict[Any, float],
                              threshold_percentile: float = 95.0) -> float:
    """
    Calculate penalty for highly popular users (based on PageRank).
    Users with PageRank above the threshold get penalized.
    
    Args:
        graph (Graph): The social network graph
        user: User ID to check
        pagerank_data: Dictionary of {user_id: pagerank_score}
        threshold_percentile: Percentile threshold for "famous" users
    
    Returns:
        Penalty value (0.0 if not famous, otherwise a positive penalty)
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if not pagerank_data:
        return 0.0
    
    user_pagerank = pagerank_data.get(user, 0.0)
    
    # Calculate threshold
    pageranks = sorted(pagerank_data.values())
    threshold_index = int(len(pageranks) * threshold_percentile / 100.0)
    threshold = pageranks[min(threshold_index, len(pageranks) - 1)]
    
    # Apply penalty if above threshold
    if user_pagerank > threshold:
        return 0.3  # Fixed penalty for famous users
    
    return 0.0


# ==============================================================================
# 9. LEGACY FUNCTION (KEPT FOR BACKWARDS COMPATIBILITY)
# ==============================================================================

def calculate_comprehensive_score(graph: Graph, 
                                 user: Any, 
                                 candidate: Any,
                                 components: List[List[Any]],
                                 pagerank_data: Dict[Any, float],
                                 w_structural: float = 0.6,
                                 w_attribute: float = 0.4,
                                 max_distance: int = 4,
                                 popularity_penalty_weight: float = 0.3) -> Dict[str, Any]:
    """
    
    **NOTE**: This function is kept for backwards compatibility but is NOT used
    in the optimized recommend_friends function. The optimized version uses BFS
    to find candidates within max_distance and then scores them directly.
    
    Algorithm:    Calculate comprehensive recommendation score from scratch.

    1. Calculate shortest path distance (reject if > max_distance)
    2. Calculate structural score (Jaccard on common neighbors)
    3. Calculate attribute score (Jaccard on interests/personality)
    4. Add community bonus if same community
    5. Apply popularity penalty based on PageRank
    
    Args:
        graph (Graph): The social network graph
        user: Source user ID
        candidate: Candidate user ID to evaluate
        components: List of connected components
        pagerank_data: Dictionary of PageRank scores
        w_structural: Weight for structural score
        w_attribute: Weight for attribute score
        max_distance: Maximum path distance allowed
        popularity_penalty_weight: Weight for popularity penalty
    
    Returns:
        Dictionary with scores and metadata
    
    Time Complexity: O(V + E) for shortest path, O(d) for Jaccard
    Space Complexity: O(V)
    """
    # Simple BFS for distance (lightweight check)
    queue = deque([(user, 0)])
    visited = {user}
    distance = float('inf')
    
    while queue:
        current, dist = queue.popleft()
        
        if current == candidate:
            distance = dist
            break
        
        if dist >= max_distance:
            continue
        
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    
    if distance > max_distance or distance == float('inf'):
        return {
            'final_score': 0.0,
            'distance': distance,
            'rejected': True
        }
    
    # Step 2: Calculate structural score (common neighbors)
    structural_score = calculate_jaccard_structural(graph, user, candidate)
    
    # Step 3: Calculate attribute score (interests/personality)
    attribute_score = calculate_jaccard_interests(graph, user, candidate)
    
    # Step 4: Calculate community bonus
    same_community, community_size = check_community_match(graph, user, candidate, components)
    community_bonus = 0.0
    
    if same_community:
        community_bonus = calculate_dynamic_community_bonus(community_size)
    
    # Step 5: Calculate initial composite score
    initial_score = (w_structural * structural_score) + \
                   (w_attribute * attribute_score) + \
                   community_bonus
    
    # Step 6: Apply popularity penalty
    penalty = calculate_pagerank_penalty(graph, candidate, pagerank_data)
    final_score = initial_score - penalty
    
    # Ensure non-negative score
    final_score = max(0.0, final_score)
    
    # Get common friends count
    common_friends = graph.get_neighbors(user) & graph.get_neighbors(candidate)
    
    # Get shared interests and personality
    interests1 = set(graph.get_node_attribute(user, 'interests', []))
    interests2 = set(graph.get_node_attribute(candidate, 'interests', []))
    personality1 = set(graph.get_node_attribute(user, 'personality', []))
    personality2 = set(graph.get_node_attribute(candidate, 'personality', []))
    
    shared_tags = (interests1 & interests2) | (personality1 & personality2)
    
    return {
        'final_score': final_score,
        'distance': distance,
        'structural_score': structural_score,
        'attribute_score': attribute_score,
        'community_bonus': community_bonus,
        'popularity_penalty': penalty,
        'common_friends_count': len(common_friends),
        'shared_tags': list(shared_tags),
        'rejected': False
    }


# ==============================================================================
# 10. MAIN RECOMMENDATION FUNCTION
# ==============================================================================

def recommend_friends(graph: Graph, 
                     user: Any, 
                     pagerank_data: Dict[Any, float] = None,
                     k: int = 5,
                     w_structural: float = 0.6,
                     w_attribute: float = 0.4,
                     max_distance: int = 4,
                     popularity_penalty: float = 0.3) -> List[Dict[str, Any]]:
    """
    Recommend friends for a user using comprehensive scoring from scratch.
    
    **OPTIMIZED VERSION**: Only evaluates candidates within max_distance hops!
    
    Algorithm:
    1. Use BFS to find all candidates within max_distance (much faster than checking all nodes!)
    2. Find connected components (communities) using existing traversal.py implementation
    3. For each candidate within distance:
       a. Calculate structural score (Jaccard on neighbors)
       b. Calculate attribute score (Jaccard on interests)
       c. Add community bonus if same component
       d. Apply popularity penalty based on PageRank
    4. Sort by final score and return top k
    
    Args:
        graph (Graph): The social network graph
        user: User ID to generate recommendations for
        pagerank_data: Dictionary of {user_id: pagerank_score} (from centrality.py)
        k (int): Number of recommendations to return
        w_structural: Weight for structural similarity
        w_attribute: Weight for attribute similarity
        max_distance: Maximum path distance (only candidates within this distance are considered)
        popularity_penalty: Penalty for popular users
    
    Returns:
        List of recommendation dictionaries sorted by score
    
    Time Complexity: O(V + E) for BFS + O(k * d) for scoring k candidates
    Space Complexity: O(V)
    
    **Performance Improvement**: Instead of evaluating ALL nodes (O(V^2)), we only evaluate
    nodes within max_distance hops, which is typically much smaller!
    """
    if user not in graph.get_nodes():
        print(f"Error: User ID {user} not found in graph.")
        return []
    
    # Initialize PageRank data if not provided
    if pagerank_data is None:
        pagerank_data = {}
    
    # Step 1: Find all candidates within max_distance using BFS (OPTIMIZED!)
    print(f"\n[1] Finding candidates within distance {max_distance} using BFS...")
    candidates_with_distances = bfs_find_candidates_within_distance(graph, user, max_distance)
    
    if not candidates_with_distances:
        print("    No candidates found within the specified distance.")
        return []
    
    print(f"    Found {len(candidates_with_distances)} candidates within distance {max_distance}")
    print(f"    (This is much faster than evaluating all {graph.number_of_nodes()} nodes!)")
    
    # Step 2: Detect communities using proper community detection algorithm
    print("\n[2] Detecting communities using Label Propagation...")
    try:
        from community_detection import detect_communities
        community_result = detect_communities(graph, method="label_propagation")
        components = community_result["communities"]
        print(f"    Found {len(components)} communities (Modularity: {community_result['modularity']:.3f})")
    except Exception as e:
        # Fallback to connected components if community detection fails
        print(f"    Community detection failed ({e}), using connected components...")
        components = find_connected_components_bfs(graph)
        print(f"    Found {len(components)} connected components")
    
    # Step 3: Evaluate only the candidates found by BFS
    print(f"\n[3] Evaluating {len(candidates_with_distances)} candidates...")
    recommendations = []
    
    for candidate, distance in candidates_with_distances.items():
        # Calculate structural score (Jaccard on neighbors)
        structural_score = calculate_jaccard_structural(graph, user, candidate)
        
        # Calculate attribute score (Jaccard on interests)
        attribute_score = calculate_jaccard_interests(graph, user, candidate)
        
        # Calculate community bonus
        same_community, community_size = check_community_match(graph, user, candidate, components)
        community_bonus = 0.0
        
        if same_community:
            community_bonus = calculate_dynamic_community_bonus(community_size)
        
        # Calculate initial composite score
        initial_score = (w_structural * structural_score) + \
                       (w_attribute * attribute_score) + \
                       community_bonus
        
        # Apply popularity penalty (using PageRank from centrality.py)
        penalty = calculate_pagerank_penalty(graph, candidate, pagerank_data)
        final_score = initial_score - penalty
        
        # Ensure non-negative score
        final_score = max(0.0, final_score)
        
        if final_score > 0:
            # Get common friends count
            common_friends = graph.get_neighbors(user) & graph.get_neighbors(candidate)
            
            # Get shared interests and personality
            interests1 = set(graph.get_node_attribute(user, 'interests', []))
            interests2 = set(graph.get_node_attribute(candidate, 'interests', []))
            personality1 = set(graph.get_node_attribute(user, 'personality', []))
            personality2 = set(graph.get_node_attribute(candidate, 'personality', []))
            
            shared_tags = (interests1 & interests2) | (personality1 & personality2)
            
            recommendations.append({
                'user_id': candidate,
                'final_score': final_score,
                'distance': distance,
                'structural_score': structural_score,
                'attribute_score': attribute_score,
                'community_bonus': community_bonus,
                'popularity_penalty': penalty,
                'common_friends_count': len(common_friends),
                'shared_tags': list(shared_tags),
                'rejected': False
            })
    
    # Step 4: Sort by final score
    recommendations.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Step 5: Return top k
    print(f"    Generated {len(recommendations)} valid recommendations")
    return recommendations[:k]


# ==============================================================================
# 11. USER PROFILE DISPLAY
# ==============================================================================

def display_user_profile(graph: Graph, user: Any, 
                        pagerank_data: Dict[Any, float] = None,
                        components: List[List[Any]] = None):
    """
    Display detailed profile of a user for debugging.
    
    Args:
        graph (Graph): The social network graph
        user: User ID to display
        pagerank_data: Dictionary of PageRank scores
        components: List of connected components
    """
    if user not in graph.get_nodes():
        print(f"User ID {user} not found in graph.")
        return
    
    print("\n" + "=" * 60)
    print(f"USER PROFILE: {user}")
    print("=" * 60)
    
    # Basic info
    name = graph.get_node_attribute(user, 'name', 'N/A')
    age = graph.get_node_attribute(user, 'age', 'N/A')
    print(f"Name: {name}")
    print(f"Age: {age}")
    
    # Interests and personality
    interests = graph.get_node_attribute(user, 'interests', [])
    personality = graph.get_node_attribute(user, 'personality', [])
    print(f"Interests: {', '.join(interests) if interests else 'None'}")
    print(f"Personality: {', '.join(personality) if personality else 'None'}")
    
    # Direct connections
    friends = graph.get_neighbors(user)
    print(f"\nDirect Friends: {len(friends)}")
    print(f"Friend IDs: {sorted(list(friends))[:10]}{'...' if len(friends) > 10 else ''}")
    
    # Community info
    if components:
        for idx, component in enumerate(components):
            if user in component:
                print(f"\nCommunity ID: {idx}")
                print(f"Community Size: {len(component)}")
                break
    
    # PageRank (fame index)
    if pagerank_data and user in pagerank_data:
        pr_score = pagerank_data[user]
        pageranks = sorted(pagerank_data.values(), reverse=True)
        rank = pageranks.index(pr_score) + 1
        print(f"\nPageRank Score: {pr_score:.6f}")
        print(f"Fame Rank: {rank} out of {len(pageranks)}")
    
    print("=" * 60)


# ==============================================================================
# 12. INTERACTIVE RECOMMENDATION SYSTEM
# ==============================================================================

def interactive_recommend_friends(graph: Graph, 
                                 pagerank_data: Dict[Any, float] = None):
    """
    Interactive friend recommendation system.
    Allows user to select a node and get recommendations.
    
    Args:
        graph (Graph): The social network graph
        pagerank_data: Dictionary of PageRank scores
    """
    nodes = graph.get_nodes()
    
    if not nodes:
        print("Error: Graph has no nodes.")
        return
    
    print("\n" + "=" * 70)
    print("FRIEND RECOMMENDATION SYSTEM")
    print("=" * 70)
    print(f"\nNetwork has {len(nodes)} users")
    print(f"User IDs range from {min(nodes)} to {max(nodes)}")
    
    # Precompute communities using proper community detection
    try:
        from community_detection import detect_communities
        community_result = detect_communities(graph, method="label_propagation")
        components = community_result["communities"]
        print(f"\n[Detected {len(components)} communities with modularity {community_result['modularity']:.3f}]")
    except Exception as e:
        print(f"\n[Community detection unavailable, using connected components]")
        components = find_connected_components_bfs(graph)
    
    while True:
        print("\n" + "-" * 70)
        user_input = input("Enter a User ID (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Exiting recommendation system.")
            break
        
        try:
            user_id = int(user_input)
            
            if user_id not in nodes:
                print(f"Error: User ID {user_id} not found. Try another ID.")
                continue
            
            # Display user profile
            display_user_profile(graph, user_id, pagerank_data, components)
            
            # Generate recommendations
            print("\n[3] Generating recommendations...")
            recommendations = recommend_friends(
                graph, user_id, pagerank_data,
                k=5,
                w_structural=0.6,
                w_attribute=0.4,
                max_distance=4,
                popularity_penalty=0.3
            )
            
            # Display recommendations
            print("\n" + "=" * 70)
            print("TOP 5 FRIEND RECOMMENDATIONS")
            print("=" * 70)
            
            if not recommendations:
                print("No recommendations found.")
            else:
                for rank, rec in enumerate(recommendations, 1):
                    print(f"\nRank {rank}: User {rec['user_id']}")
                    print(f"  Final Score: {rec['final_score']:.4f}")
                    print(f"  Structural Score: {rec['structural_score']:.3f}")
                    print(f"  Attribute Score: {rec['attribute_score']:.3f}")
                    print(f"  Community Bonus: {rec['community_bonus']:.3f}")
                    print(f"  Popularity Penalty: {rec['popularity_penalty']:.3f}")
                    print(f"  Distance: {rec['distance']}")
                    print(f"  Common Friends: {rec['common_friends_count']}")
                    print(f"  Shared Tags: {', '.join(rec['shared_tags']) if rec['shared_tags'] else 'None'}")
            
            print("=" * 70)
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"Error: {e}")


# ==============================================================================
# 13. TEST MAIN
# ==============================================================================

if __name__ == "__main__":
    import random
    import pickle
    import os
    from algorithms.graph_generator import generate_social_network
    
    print("\n" + "=" * 70)
    print("TESTING FRIEND RECOMMENDATION SYSTEM")
    print("=" * 70)
    
    # Try to load previously generated graph from main.py
    if os.path.exists('data/generated_graph.pkl'):
        print("\n[1] Loading graph from 'data/generated_graph.pkl'...")
        try:
            with open('data/generated_graph.pkl', 'rb') as f:
                test_graph = pickle.load(f)
            print(f"    Loaded network with {test_graph.number_of_nodes()} nodes")
            print(f"    and {test_graph.number_of_edges()} edges")
            print("    (This is the graph generated by main.py)")
        except Exception as e:
            print(f"    Failed to load graph: {e}")
            print("    Generating new graph instead...")
            test_graph = None
    else:
        print("\n[1] No saved graph found (run main.py first to generate one)")
        print("    Generating new test graph...")
        test_graph = None
    
    # Generate new graph if loading failed
    if test_graph is None:
        random.seed(42)
        test_graph = generate_social_network(
            num_users=50,
            avg_friends=6,
            community_structure=True,
            num_communities=None  # Auto-calculate
        )
        print(f"    Generated network with {test_graph.number_of_nodes()} nodes")
        print(f"    and {test_graph.number_of_edges()} edges")
    
    # Compute PageRank for the network
    print("\n[2] Computing PageRank scores...")
    pagerank_scores = compute_pagerank(test_graph)
    print(f"    PageRank computed for {len(pagerank_scores)} users")
    
    # Run interactive recommendation system
    print("\n[3] Starting interactive recommendation system...")
    interactive_recommend_friends(test_graph, pagerank_scores)