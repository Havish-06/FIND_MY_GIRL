"""
Realistic Social Network Generator with Holme-Kim Model
========================================================
Generate Facebook-like friendship graphs with:
- Holme-Kim algorithm (preferential attachment + triangle formation)
- Multiple disjoint communities (like separate cities)
- Isolated island nodes (minimal connections)
- Homophily-based personality tags and interests

All generation is done from scratch without external graph libraries.

Author: AAD Project Group
Date: December 2025
"""

import random
from typing import List, Dict, Any, Set, Tuple
from .graph import Graph


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


class RealisticSocialGraph:
    """
    Generate realistic social networks with Holme-Kim model.
    
    Key Features:
    - Holme-Kim algorithm: combines preferential attachment (rich get richer)
      with triangle formation (friends of friends become friends)
    - Multiple disjoint communities (separate "cities")
    - Island nodes with minimal connections
    - Homophily: similar users more likely to connect
    """
    
    def __init__(self, n_users: int = 5, m: int = 2, p: float = 0.5,
                 num_communities: int = 3, island_ratio: float = 0.1):
        """
        Initialize realistic social graph generator.
        
        Args:
            n_users: Total number of users
            m: Number of edges for each new node (Holme-Kim parameter)
            p: Probability of triangle formation (0.0-1.0)
            num_communities: Number of disjoint communities (cities)
            island_ratio: Fraction of users as isolated islands
        """
        self.n_users = n_users
        self.m = m
        self.p = p
        self.num_communities = num_communities
        self.island_ratio = island_ratio
        self.graph = None
        
    def _generate_holme_kim_scratch(self, start_node: int, num_nodes: int,
                                   community_id: int, 
                                   community_interests: List[str],
                                   community_personality: List[str]) -> None:
        """
        Generate a Holme-Kim subgraph from scratch (no NetworkX).
        
        Holme-Kim Algorithm:
        1. Start with m+1 fully connected nodes
        2. For each new node:
           a. Connect to m existing nodes via preferential attachment
           b. For each connection, with probability p, also connect to
              a random neighbor of the target (forms triangles)
        
        Args:
            start_node: Starting node ID for this community
            num_nodes: Number of nodes in this community
            community_id: Community identifier
            community_interests: Dominant interests for this community
            community_personality: Dominant personality traits
        
        Time Complexity: O(n * m) where n = num_nodes
        """
        if num_nodes < self.m + 1:
            # For very small communities, just fully connect them
            for i in range(start_node, start_node + num_nodes):
                # Add node with attributes
                self._add_user_node(i, community_id, community_interests, 
                                  community_personality)
                
                # Connect to all previous nodes in this community
                for j in range(start_node, i):
                    self.graph.add_edge(i, j)
            return
        
        # Step 1: Create initial m+1 fully connected nodes
        initial_nodes = self.m + 1
        for i in range(start_node, start_node + initial_nodes):
            self._add_user_node(i, community_id, community_interests,
                              community_personality)
            
            # Connect to all previous nodes
            for j in range(start_node, i):
                self.graph.add_edge(i, j)
        
        # Step 2: Add remaining nodes with Holme-Kim attachment
        for new_node_idx in range(start_node + initial_nodes, start_node + num_nodes):
            # Add new node
            self._add_user_node(new_node_idx, community_id, community_interests,
                              community_personality)
            
            # Get list of existing nodes in this community
            existing_nodes = list(range(start_node, new_node_idx))
            
            # Calculate degrees for preferential attachment
            degrees = [self.graph.degree(node) for node in existing_nodes]
            total_degree = sum(degrees)
            
            if total_degree == 0:
                probabilities = [1.0 / len(existing_nodes)] * len(existing_nodes)
            else:
                probabilities = [d / total_degree for d in degrees]
            
            # Preferential attachment: select m target nodes
            targets = []
            for _ in range(min(self.m, len(existing_nodes))):
                # Weighted random choice
                chosen = random.choices(existing_nodes, weights=probabilities, k=1)[0]
                
                if chosen not in targets:
                    targets.append(chosen)
                    # Remove chosen from pool
                    idx = existing_nodes.index(chosen)
                    existing_nodes.pop(idx)
                    probabilities.pop(idx)
                    
                    # Renormalize
                    total = sum(probabilities)
                    if total > 0:
                        probabilities = [p / total for p in probabilities]
            
            # Add edges to selected targets
            for target in targets:
                self.graph.add_edge(new_node_idx, target)
                
                # Triangle formation: with probability p, connect to a random
                # neighbor of target (creating a triangle)
                if random.random() < self.p:
                    # Get neighbors of target (excluding new_node itself)
                    target_neighbors = [n for n in self.graph.get_neighbors(target)
                                      if n != new_node_idx 
                                      and not self.graph.has_edge(new_node_idx, n)]
                    
                    if target_neighbors:
                        # Pick random neighbor to form triangle
                        triangle_node = random.choice(target_neighbors)
                        self.graph.add_edge(new_node_idx, triangle_node)
    
    def _add_user_node(self, user_id: int, community_id: int,
                      community_interests: List[str],
                      community_personality: List[str]) -> None:
        """
        Add a user node with attributes based on community homophily.
        
        Args:
            user_id: User node ID
            community_id: Community this user belongs to
            community_interests: Dominant interests for this community
            community_personality: Dominant personality traits
        """
        # Homophily: 70% chance to adopt community interests/personality
        interests = []
        for interest in community_interests:
            if random.random() < 0.7:
                interests.append(interest)
        
        # Add random interests
        remaining = [i for i in INTERESTS if i not in interests]
        num_extra = random.randint(0, 2)
        if remaining:
            interests.extend(random.sample(remaining, min(num_extra, len(remaining))))
        
        # Similar for personality
        personality = []
        for trait in community_personality:
            if random.random() < 0.7:
                personality.append(trait)
        
        remaining_traits = [t for t in PERSONALITY_TRAITS if t not in personality]
        num_extra_traits = random.randint(0, 1)
        if remaining_traits:
            personality.extend(random.sample(remaining_traits, 
                                           min(num_extra_traits, len(remaining_traits))))
        
        # Add node
        self.graph.add_node(user_id,
                           name=random.choice(FIRST_NAMES),
                           personality=personality,
                           interests=interests,
                           age=random.randint(18, 65),
                           community=community_id,
                           user_id=user_id)
    
    def generate(self) -> Graph:
        """
        Generate the complete realistic social network.
        
        Structure:
        1. Divide users into communities and islands
        2. Each community is a separate Holme-Kim graph (disjoint component)
        3. Islands are isolated nodes with few connections
        4. Add weak ties between communities (rare cross-community edges)
        
        Returns:
            Graph: The generated social network
        
        Time Complexity: O(n * m) where n = n_users
        Space Complexity: O(n + edges)
        """
        self.graph = Graph()
        
        # Calculate sizes
        num_islands = int(self.n_users * self.island_ratio)
        num_community_users = self.n_users - num_islands
        users_per_community = num_community_users // self.num_communities
        
        # Generate community-specific interests and personality
        community_traits = []
        for i in range(self.num_communities):
            comm_interests = random.sample(INTERESTS, 3)
            comm_personality = random.sample(PERSONALITY_TRAITS, 2)
            community_traits.append((comm_interests, comm_personality))
        
        # Generate disjoint communities using Holme-Kim
        # Use varied community sizes for realism (Zipf distribution approximation)
        community_sizes = []
        remaining_users = num_community_users
        
        for i in range(self.num_communities - 1):
            # Larger communities first, smaller ones later (realistic distribution)
            size = int(remaining_users / (self.num_communities - i) * random.uniform(0.8, 1.3))
            size = max(self.m + 2, min(size, remaining_users - (self.num_communities - i - 1) * (self.m + 2)))
            community_sizes.append(size)
            remaining_users -= size
        
        # Last community gets remaining users
        community_sizes.append(max(self.m + 2, remaining_users))
        
        current_node = 0
        for comm_id in range(self.num_communities):
            comm_size = community_sizes[comm_id]
            
            comm_interests, comm_personality = community_traits[comm_id]
            
            # Generate Holme-Kim subgraph for this community
            self._generate_holme_kim_scratch(current_node, comm_size, comm_id,
                                           comm_interests, comm_personality)
            
            current_node += comm_size
        
        # Add island nodes (small isolated groups)
        island_start = current_node
        remaining_islands = num_islands
        current_island_node = island_start
        
        while remaining_islands > 0:
            # Create small island groups of 2-5 people
            island_group_size = min(random.randint(2, 5), remaining_islands)
            
            # Create the island group
            for i in range(island_group_size):
                user_id = current_island_node + i
                
                # Random interests and personality (not community-based)
                interests = random.sample(INTERESTS, random.randint(1, 4))
                personality = random.sample(PERSONALITY_TRAITS, random.randint(1, 3))
                
                self.graph.add_node(user_id,
                                   name=random.choice(FIRST_NAMES),
                                   personality=personality,
                                   interests=interests,
                                   age=random.randint(18, 65),
                                   community=-1,  # Special marker for islands
                                   user_id=user_id)
                
                # Connect within island group (fully connected small group)
                for j in range(current_island_node, user_id):
                    if self.graph.get_node_attribute(j, "community") == -1:  # Only connect to other island nodes in this group
                        self.graph.add_edge(user_id, j)
                
                # Each island member has 0-1 connections to main communities
                if random.random() < 0.5 and current_node > 0:  # 50% chance of external connection
                    target = random.randint(0, current_node - 1)
                    self.graph.add_edge(user_id, target)
            
            current_island_node += island_group_size
            remaining_islands -= island_group_size
        
        # Add weak ties between communities (cross-community edges)
        # Real social networks have 5-10% cross-community connections
        num_weak_ties = int(num_community_users * 0.08)  # 8% cross-community ties for realism
        
        for _ in range(num_weak_ties):
            # Pick two different communities
            comm1, comm2 = random.sample(range(self.num_communities), 2)
            
            # Find nodes in each community
            nodes_comm1 = [n for n in range(self.n_users - num_islands)
                          if self.graph.get_node_attribute(n, "community") == comm1]
            nodes_comm2 = [n for n in range(self.n_users - num_islands)
                          if self.graph.get_node_attribute(n, "community") == comm2]
            
            if nodes_comm1 and nodes_comm2:
                node1 = random.choice(nodes_comm1)
                node2 = random.choice(nodes_comm2)
                
                if not self.graph.has_edge(node1, node2):
                    self.graph.add_edge(node1, node2)
        
        return self.graph


def generate_social_network(num_users: int, 
                           avg_friends: int = 10,
                           community_structure: bool = True,
                           num_communities: int = 3) -> Graph:
    """
    Generate a realistic social network using Holme-Kim model.
    
    This is the main entry point that maintains backward compatibility
    with the original interface while using the new Holme-Kim generation.
    
    Algorithm:
    1. Use Holme-Kim model for preferential attachment + triangle formation
    2. Create multiple disjoint communities (separate graph components)
    3. Add isolated "island" nodes with minimal connections
    4. Add weak cross-community ties for realism
    
    Args:
        num_users (int): Number of users in the network
        avg_friends (int): Average number of friends per user (used to tune m parameter)
        community_structure (bool): Whether to create community structure
        num_communities (int): Number of communities (if community_structure=True)
    
    Returns:
        Graph: The generated social network with node attributes
    
    Time Complexity: O(n * m) where n is num_users, m is edges per node
    Space Complexity: O(n + edges)
    """
    if not community_structure:
        # Single community case
        num_communities = 1
    elif num_communities is None:
        # Auto-calculate communities based on network size
        # Rule: roughly sqrt(n)/2 communities for balanced distribution
        import math
        num_communities = max(2, int(math.sqrt(num_users) / 2))
    
    # Calculate m parameter from avg_friends
    # Holme-Kim creates roughly m edges per node, plus triangle edges
    # Triangle formation adds ~p*m extra edges per node
    # So: avg_friends ≈ m * (1 + p)
    p = 0.5  # Triangle formation probability
    m = max(1, int(avg_friends / (1 + p)))
    
    # Generate using realistic model
    generator = RealisticSocialGraph(
        n_users=num_users,
        m=m,
        p=p,
        num_communities=num_communities,
        island_ratio=0.15  # 15% island nodes - more realistic for social networks
    )
    
    return generator.generate()


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
                  name=random.choice(FIRST_NAMES),
                  personality=random.sample(PERSONALITY_TRAITS, 3),
                  interests=random.sample(INTERESTS, random.randint(2, 5)),
                  age=random.randint(18, 65),
                  community=0)
    
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
                  name=random.choice(FIRST_NAMES),
                  personality=random.sample(PERSONALITY_TRAITS, 3),
                  interests=random.sample(INTERESTS, random.randint(2, 5)),
                  age=random.randint(18, 65),
                  community=0)
    
    for i in range(m):
        for j in range(i + 1, m):
            G.add_edge(i, j)
    
    # Add remaining nodes with preferential attachment
    for new_node in range(m, num_users):
        # Add new node
        G.add_node(new_node,
                  name=random.choice(FIRST_NAMES),
                  personality=random.sample(PERSONALITY_TRAITS, 3),
                  interests=random.sample(INTERESTS, random.randint(2, 5)),
                  age=random.randint(18, 65),
                  community=0)
        
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
