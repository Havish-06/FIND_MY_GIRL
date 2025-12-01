"""
Friend Recommendation System
=============================
Implement a friend recommendation system for social networks.
Uses multiple strategies: common friends, personality similarity, and interest matching.

Author: AAD Project Group
Date: December 2025
"""

from typing import List, Dict, Tuple, Any
from graph import Graph
from collections import Counter


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Calculate Jaccard similarity between two sets.
    
    Jaccard similarity = |A ∩ B| / |A ∪ B|
    
    Args:
        set1 (set): First set
        set2 (set): Second set
    
    Returns:
        Similarity score between 0 and 1
    
    Time Complexity: O(|set1| + |set2|)
    Space Complexity: O(|set1| + |set2|)
    """
    if not set1 and not set2:
        return 0.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Cosine similarity = (A · B) / (||A|| * ||B||)
    
    Args:
        vec1 (List[float]): First vector
        vec2 (List[float]): Second vector
    
    Returns:
        Similarity score between -1 and 1
    
    Time Complexity: O(n) where n is vector length
    Space Complexity: O(1)
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def get_common_friends(graph: Graph, user1: Any, user2: Any) -> set:
    """
    Get the set of common friends between two users.
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
    
    Returns:
        Set of common friends
    
    Time Complexity: O(min(deg(u1), deg(u2)))
    Space Complexity: O(min(deg(u1), deg(u2)))
    """
    friends1 = graph.get_neighbors(user1)
    friends2 = graph.get_neighbors(user2)
    
    return friends1 & friends2


def common_friends_score(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate friend recommendation score based on common friends.
    
    Higher score = more common friends.
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
    
    Returns:
        Number of common friends
    
    Time Complexity: O(min(deg(u1), deg(u2)))
    Space Complexity: O(min(deg(u1), deg(u2)))
    """
    common = get_common_friends(graph, user1, user2)
    return len(common)


def adamic_adar_score(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate Adamic-Adar score for friend recommendation.
    
    Adamic-Adar gives more weight to common friends with fewer connections
    (less "popular" common friends are more significant).
    
    Formula: Σ 1/log(|N(z)|) for all common neighbors z
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
    
    Returns:
        Adamic-Adar score
    
    Time Complexity: O(min(deg(u1), deg(u2)))
    Space Complexity: O(min(deg(u1), deg(u2)))
    """
    import math
    
    common = get_common_friends(graph, user1, user2)
    
    if not common:
        return 0.0
    
    score = 0.0
    for friend in common:
        friend_degree = graph.degree(friend)
        if friend_degree > 1:  # Avoid log(1) = 0
            score += 1.0 / math.log(friend_degree)
    
    return score


def personality_similarity_score(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate similarity based on personality traits.
    
    Uses Jaccard similarity on personality trait sets.
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
    
    Returns:
        Personality similarity score (0 to 1)
    
    Time Complexity: O(k) where k is number of traits
    Space Complexity: O(k)
    """
    personality1 = set(graph.get_node_attribute(user1, "personality", []))
    personality2 = set(graph.get_node_attribute(user2, "personality", []))
    
    return jaccard_similarity(personality1, personality2)


def interest_similarity_score(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate similarity based on shared interests.
    
    Uses Jaccard similarity on interest sets.
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
    
    Returns:
        Interest similarity score (0 to 1)
    
    Time Complexity: O(k) where k is number of interests
    Space Complexity: O(k)
    """
    interests1 = set(graph.get_node_attribute(user1, "interests", []))
    interests2 = set(graph.get_node_attribute(user2, "interests", []))
    
    return jaccard_similarity(interests1, interests2)


def age_similarity_score(graph: Graph, user1: Any, user2: Any) -> float:
    """
    Calculate similarity based on age.
    
    Returns a score that decreases with age difference.
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
    
    Returns:
        Age similarity score (0 to 1)
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    age1 = graph.get_node_attribute(user1, "age", 30)
    age2 = graph.get_node_attribute(user2, "age", 30)
    
    age_diff = abs(age1 - age2)
    
    # Exponential decay: closer ages = higher score
    # e^(-0.05 * age_diff) gives smooth decay
    import math
    return math.exp(-0.05 * age_diff)


def calculate_recommendation_score(graph: Graph, user1: Any, user2: Any,
                                   weights: Dict[str, float] = None) -> float:
    """
    Calculate comprehensive friend recommendation score.
    
    Combines multiple factors:
    - Common friends (Adamic-Adar)
    - Personality similarity
    - Interest similarity
    - Age similarity
    
    Args:
        graph (Graph): The social network
        user1: First user
        user2: Second user
        weights (Dict): Weights for each factor
    
    Returns:
        Overall recommendation score
    
    Time Complexity: O(min(deg(u1), deg(u2)))
    Space Complexity: O(min(deg(u1), deg(u2)))
    """
    if weights is None:
        # Default weights
        weights = {
            "common_friends": 0.4,
            "personality": 0.2,
            "interests": 0.3,
            "age": 0.1
        }
    
    # Calculate individual scores
    common_score = adamic_adar_score(graph, user1, user2)
    personality_score = personality_similarity_score(graph, user1, user2)
    interest_score = interest_similarity_score(graph, user1, user2)
    age_score = age_similarity_score(graph, user1, user2)
    
    # Normalize common friends score (Adamic-Adar can be unbounded)
    # Use tanh to map to [0, 1]
    import math
    common_score_normalized = math.tanh(common_score / 5.0)
    
    # Weighted combination
    total_score = (
        weights["common_friends"] * common_score_normalized +
        weights["personality"] * personality_score +
        weights["interests"] * interest_score +
        weights["age"] * age_score
    )
    
    return total_score


def recommend_friends(graph: Graph, user: Any, k: int = 10,
                     exclude_existing: bool = True) -> List[Tuple[Any, float]]:
    """
    Recommend k friends for a given user.
    
    Algorithm:
    1. For each non-friend user, calculate recommendation score
    2. Sort by score (descending)
    3. Return top k recommendations
    
    Args:
        graph (Graph): The social network
        user: User to recommend friends for
        k (int): Number of recommendations
        exclude_existing (bool): Whether to exclude existing friends
    
    Returns:
        List of tuples (recommended_user, score) sorted by score
    
    Time Complexity: O(n * d) where n is users and d is avg degree
    Space Complexity: O(n)
    """
    if user not in graph.get_nodes():
        return []
    
    # Get existing friends
    existing_friends = graph.get_neighbors(user)
    
    recommendations = []
    
    # Evaluate all potential friends
    for candidate in graph.get_nodes():
        # Skip self
        if candidate == user:
            continue
        
        # Skip existing friends if requested
        if exclude_existing and candidate in existing_friends:
            continue
        
        # Calculate recommendation score
        score = calculate_recommendation_score(graph, user, candidate)
        recommendations.append((candidate, score))
    
    # Sort by score (descending)
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k
    return recommendations[:k]


def friends_of_friends(graph: Graph, user: Any, k: int = 10) -> List[Tuple[Any, int]]:
    """
    Recommend friends of friends (FoF) for a user.
    
    This is a simpler, faster algorithm that only considers
    friends of existing friends.
    
    Args:
        graph (Graph): The social network
        user: User to recommend friends for
        k (int): Number of recommendations
    
    Returns:
        List of tuples (recommended_user, num_common_friends)
    
    Time Complexity: O(d^2) where d is average degree
    Space Complexity: O(d^2)
    """
    if user not in graph.get_nodes():
        return []
    
    # Get existing friends
    friends = graph.get_neighbors(user)
    
    # Count friends of friends
    fof_counts = Counter()
    
    for friend in friends:
        # Get friends of this friend
        friends_of_friend = graph.get_neighbors(friend)
        
        for fof in friends_of_friend:
            # Don't recommend self or existing friends
            if fof != user and fof not in friends:
                fof_counts[fof] += 1
    
    # Sort by count (descending)
    recommendations = fof_counts.most_common(k)
    
    return recommendations


def evaluate_recommendations(graph: Graph, recommendations: List[Tuple[Any, float]],
                            user: Any) -> Dict[str, float]:
    """
    Evaluate the quality of friend recommendations.
    
    Metrics:
    - Average common friends with recommended users
    - Average personality similarity
    - Average interest similarity
    
    Args:
        graph (Graph): The social network
        recommendations (List): List of (user, score) tuples
        user: The user recommendations are for
    
    Returns:
        Dictionary of evaluation metrics
    
    Time Complexity: O(k * d) where k is recommendations and d is avg degree
    Space Complexity: O(1)
    """
    if not recommendations:
        return {
            "avg_common_friends": 0.0,
            "avg_personality_similarity": 0.0,
            "avg_interest_similarity": 0.0
        }
    
    total_common = 0
    total_personality = 0.0
    total_interests = 0.0
    
    for recommended_user, _ in recommendations:
        total_common += common_friends_score(graph, user, recommended_user)
        total_personality += personality_similarity_score(graph, user, recommended_user)
        total_interests += interest_similarity_score(graph, user, recommended_user)
    
    k = len(recommendations)
    
    return {
        "avg_common_friends": total_common / k,
        "avg_personality_similarity": total_personality / k,
        "avg_interest_similarity": total_interests / k
    }


def batch_recommend_friends(graph: Graph, users: List[Any] = None,
                            k: int = 5) -> Dict[Any, List[Tuple[Any, float]]]:
    """
    Generate friend recommendations for multiple users.
    
    Args:
        graph (Graph): The social network
        users (List): Users to generate recommendations for (None = all users)
        k (int): Number of recommendations per user
    
    Returns:
        Dictionary mapping each user to their recommendations
    
    Time Complexity: O(n^2 * d) where n is users and d is avg degree
    Space Complexity: O(n * k)
    """
    if users is None:
        users = graph.get_nodes()
    
    all_recommendations = {}
    
    for user in users:
        recommendations = recommend_friends(graph, user, k=k)
        all_recommendations[user] = recommendations
    
    return all_recommendations
