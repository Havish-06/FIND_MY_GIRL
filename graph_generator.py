"""
Synthetic Social Network Generator
===================================
Generate Facebook-like friendship graphs with personality tags.
All generation is done from scratch without external graph libraries.

Author: AAD Project Group
Date: December 2025
"""

import random
from typing import List, Dict, Any, Tuple
from graph import Graph


# Personality trait options
PERSONALITY_TRAITS = [
    "Outgoing", "Introverted", "Creative", "Analytical", "Adventurous",
    "Cautious", "Optimistic", "Realistic", "Organized", "Spontaneous",
    "Competitive", "Cooperative", "Ambitious", "Relaxed", "Perfectionist"
]

INTERESTS = [
    "Sports", "Music", "Art", "Technology", "Gaming", "Reading",
    "Cooking", "Travel", "Photography", "Fitness", "Movies", "Fashion",
    "Science", "Politics", "Nature", "Writing", "Dancing", "Volunteering"
]

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
    "Ivy", "Jack", "Kate", "Leo", "Mia", "Noah", "Olivia", "Paul",
    "Quinn", "Ruby", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xander",
    "Yara", "Zack", "Aria", "Ben", "Chloe", "David", "Emma", "Felix",
    "Gina", "Hugo", "Iris", "Jake", "Lena", "Max", "Nina", "Oscar"
]


def generate_random_name() -> str:
    """
    Generate a random person name.
    
    Returns:
        A random name from the FIRST_NAMES list
    
    Time Complexity: O(1)
    """
    return random.choice(FIRST_NAMES)


def generate_personality_tags(num_traits: int = 3) -> List[str]:
    """
    Generate random personality traits for a person.
    
    Args:
        num_traits (int): Number of traits to assign (default: 3)
    
    Returns:
        List of personality traits
    
    Time Complexity: O(k) where k is num_traits
    """
    return random.sample(PERSONALITY_TRAITS, min(num_traits, len(PERSONALITY_TRAITS)))


def generate_interests(num_interests: int = 3) -> List[str]:
    """
    Generate random interests for a person.
    
    Args:
        num_interests (int): Number of interests to assign (default: 3)
    
    Returns:
        List of interests
    
    Time Complexity: O(k) where k is num_interests
    """
    return random.sample(INTERESTS, min(num_interests, len(INTERESTS)))


def generate_social_network(num_users: int, 
                           avg_friends: int = 10,
                           community_structure: bool = True,
                           num_communities: int = 3) -> Graph:
    """
    Generate a synthetic Facebook-like social network.
    
    Algorithm:
    1. Create users with random personality tags and interests
    2. If community_structure is True, divide users into communities
    3. Generate friendships based on:
       - Higher probability within same community
       - Shared interests increase friendship probability
       - Similar personality traits increase friendship probability
    
    Args:
        num_users (int): Number of users in the network
        avg_friends (int): Average number of friends per user
        community_structure (bool): Whether to create community structure
        num_communities (int): Number of communities (if community_structure=True)
    
    Returns:
        Graph: The generated social network with node attributes
    
    Time Complexity: O(n^2) where n is num_users (checking all pairs)
    Space Complexity: O(n + m) where m is number of edges
    """
    G = Graph()
    
    # Assign users to communities
    if community_structure:
        community_assignment = {}
        users_per_community = num_users // num_communities
        
        for i in range(num_users):
            community_id = min(i // users_per_community, num_communities - 1)
            community_assignment[i] = community_id
    
    # Create users with attributes
    for user_id in range(num_users):
        name = generate_random_name()
        personality = generate_personality_tags(num_traits=3)
        interests = generate_interests(num_interests=random.randint(2, 5))
        age = random.randint(18, 65)
        
        attributes = {
            "name": name,
            "personality": personality,
            "interests": interests,
            "age": age,
            "user_id": user_id
        }
        
        if community_structure:
            attributes["community"] = community_assignment[user_id]
        
        G.add_node(user_id, **attributes)
    
    # Generate friendships
    target_edges = (num_users * avg_friends) // 2  # Each edge connects two people
    edges_created = 0
    
    # Calculate friendship probabilities for all pairs
    friendship_pairs = []
    
    for i in range(num_users):
        for j in range(i + 1, num_users):
            # Calculate friendship probability
            prob = calculate_friendship_probability(
                G, i, j, community_structure, community_assignment if community_structure else None
            )
            
            friendship_pairs.append((i, j, prob))
    
    # Sort by probability (higher first)
    friendship_pairs.sort(key=lambda x: x[2], reverse=True)
    
    # Create friendships based on probabilities
    for i, j, prob in friendship_pairs:
        if edges_created >= target_edges:
            break
        
        # Random chance based on probability
        if random.random() < prob:
            G.add_edge(i, j)
            edges_created += 1
    
    # Ensure each user has at least one friend (if possible)
    for user_id in range(num_users):
        if G.degree(user_id) == 0 and num_users > 1:
            # Find a user to befriend
            potential_friends = [u for u in range(num_users) if u != user_id]
            if potential_friends:
                friend = random.choice(potential_friends)
                G.add_edge(user_id, friend)
    
    return G


def calculate_friendship_probability(graph: Graph, user1: int, user2: int,
                                    community_structure: bool,
                                    community_assignment: Dict[int, int] = None) -> float:
    """
    Calculate the probability of friendship between two users.
    
    Based on:
    - Community membership (same community = higher probability)
    - Shared interests
    - Similar personality traits
    - Age similarity
    
    Args:
        graph (Graph): The graph
        user1 (int): First user ID
        user2 (int): Second user ID
        community_structure (bool): Whether communities are used
        community_assignment (Dict): Community assignments
    
    Returns:
        Probability of friendship (0.0 to 1.0)
    
    Time Complexity: O(k) where k is number of attributes
    """
    base_prob = 0.05  # Base probability for any two users
    prob = base_prob
    
    # Community bonus
    if community_structure and community_assignment:
        if community_assignment[user1] == community_assignment[user2]:
            prob += 0.3  # Much higher probability within same community
        else:
            prob += 0.05  # Small probability across communities
    
    # Shared interests
    interests1 = set(graph.get_node_attribute(user1, "interests", []))
    interests2 = set(graph.get_node_attribute(user2, "interests", []))
    shared_interests = len(interests1 & interests2)
    
    if shared_interests > 0:
        prob += 0.1 * shared_interests  # Each shared interest adds 10%
    
    # Similar personality
    personality1 = set(graph.get_node_attribute(user1, "personality", []))
    personality2 = set(graph.get_node_attribute(user2, "personality", []))
    shared_traits = len(personality1 & personality2)
    
    if shared_traits > 0:
        prob += 0.05 * shared_traits  # Each shared trait adds 5%
    
    # Age similarity (closer ages = higher probability)
    age1 = graph.get_node_attribute(user1, "age", 30)
    age2 = graph.get_node_attribute(user2, "age", 30)
    age_diff = abs(age1 - age2)
    
    if age_diff < 5:
        prob += 0.1
    elif age_diff < 10:
        prob += 0.05
    
    # Cap probability at 1.0
    return min(prob, 1.0)


def generate_small_world_network(num_users: int, k: int = 6, p: float = 0.1) -> Graph:
    """
    Generate a small-world network using Watts-Strogatz model.
    
    Algorithm:
    1. Create a ring lattice: each node connected to k nearest neighbors
    2. Rewire each edge with probability p to a random node
    
    This creates a network with high clustering and short path lengths,
    similar to real social networks.
    
    Args:
        num_users (int): Number of nodes
        k (int): Each node connected to k nearest neighbors (must be even)
        p (float): Rewiring probability
    
    Returns:
        Graph: Small-world network
    
    Time Complexity: O(n * k)
    Space Complexity: O(n + n*k)
    """
    G = Graph()
    
    # Add nodes with attributes
    for i in range(num_users):
        G.add_node(i,
                  name=generate_random_name(),
                  personality=generate_personality_tags(),
                  interests=generate_interests(),
                  age=random.randint(18, 65))
    
    # Create ring lattice
    for i in range(num_users):
        for j in range(1, k // 2 + 1):
            neighbor = (i + j) % num_users
            if not G.has_edge(i, neighbor):
                G.add_edge(i, neighbor)
    
    # Rewire edges
    edges = list(G.get_edges())
    for u, v in edges:
        if random.random() < p:
            # Remove old edge
            G.remove_edge(u, v)
            
            # Add new edge to random node
            possible_targets = [n for n in range(num_users) 
                              if n != u and not G.has_edge(u, n)]
            
            if possible_targets:
                new_target = random.choice(possible_targets)
                G.add_edge(u, new_target)
    
    return G


def generate_scale_free_network(num_users: int, m: int = 3) -> Graph:
    """
    Generate a scale-free network using Barabási-Albert preferential attachment model.
    
    Algorithm:
    1. Start with m nodes fully connected
    2. Add nodes one by one
    3. Each new node connects to m existing nodes
    4. Probability of connecting to a node is proportional to its degree (preferential attachment)
    
    This creates a network with power-law degree distribution,
    where a few nodes have very high degree (hubs).
    
    Args:
        num_users (int): Total number of nodes
        m (int): Number of edges for each new node
    
    Returns:
        Graph: Scale-free network
    
    Time Complexity: O(n * m)
    Space Complexity: O(n + n*m)
    """
    G = Graph()
    
    # Start with m fully connected nodes
    for i in range(m):
        G.add_node(i,
                  name=generate_random_name(),
                  personality=generate_personality_tags(),
                  interests=generate_interests(),
                  age=random.randint(18, 65))
    
    for i in range(m):
        for j in range(i + 1, m):
            G.add_edge(i, j)
    
    # Add remaining nodes with preferential attachment
    for new_node in range(m, num_users):
        # Add new node
        G.add_node(new_node,
                  name=generate_random_name(),
                  personality=generate_personality_tags(),
                  interests=generate_interests(),
                  age=random.randint(18, 65))
        
        # Get current nodes and their degrees
        existing_nodes = list(range(new_node))
        degrees = [G.degree(node) for node in existing_nodes]
        total_degree = sum(degrees)
        
        if total_degree == 0:
            # If all degrees are 0, use uniform probability
            probabilities = [1.0 / len(existing_nodes)] * len(existing_nodes)
        else:
            # Preferential attachment: probability proportional to degree
            probabilities = [d / total_degree for d in degrees]
        
        # Select m nodes to connect to (without replacement)
        targets = []
        for _ in range(min(m, len(existing_nodes))):
            # Choose based on probabilities
            chosen = random.choices(existing_nodes, weights=probabilities, k=1)[0]
            
            if chosen not in targets:
                targets.append(chosen)
                # Remove chosen from options
                idx = existing_nodes.index(chosen)
                existing_nodes.pop(idx)
                probabilities.pop(idx)
                
                # Renormalize probabilities
                total_prob = sum(probabilities)
                if total_prob > 0:
                    probabilities = [p / total_prob for p in probabilities]
        
        # Add edges
        for target in targets:
            G.add_edge(new_node, target)
    
    return G
