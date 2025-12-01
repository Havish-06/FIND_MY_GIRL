"""
Centrality Measures - From Scratch Implementation
==================================================
Implementation of degree, betweenness, and PageRank centrality measures
without using NetworkX or any external graph libraries.
"""

from collections import defaultdict, deque
from typing import Dict, Any, List
from .graph import Graph


def compute_degree_centrality(graph: Graph) -> Dict[Any, float]:
    """
    Degree Centrality measures the fraction of nodes a node is connected to.
    
    Formula: C_D(v) = deg(v) / (n - 1)
    where deg(v) is the degree of node v and n is the total number of nodes.
    
    Interpretation:
    - High degree centrality = node has many direct connections
    - In social networks: popular individuals with many friends
    
    Args:
        graph (Graph): The graph to analyze
    
    Returns:
        Dictionary mapping each node to its degree centrality (0 to 1)
    
    Time Complexity: O(V) where V is the number of vertices
    Space Complexity: O(V)
    """
    centrality = {}
    n = graph.number_of_nodes()
    
    # Handle edge case of single node
    if n <= 1:
        return {node: 0.0 for node in graph.get_nodes()}
    
    # Calculate degree centrality for each node
    for node in graph.get_nodes():
        degree = graph.degree(node)
        # Normalize by dividing by maximum possible degree (n - 1)
        centrality[node] = degree / (n - 1)
    
    return centrality


def compute_betweenness_centrality(graph: Graph, normalized: bool = True) -> Dict[Any, float]:
    """
    Betweenness Centrality measures how often a node appears on shortest paths.
    
    Formula: C_B(v) = Σ(σ_st(v) / σ_st)
    where σ_st is the number of shortest paths from s to t,
    and σ_st(v) is the number of those paths passing through v.
    
    Uses Brandes' algorithm for efficient computation.
    
    Interpretation:
    - High betweenness = node is a bridge between communities
    - In social networks: people who connect different groups
    
    Args:
        graph (Graph): The graph to analyze
        normalized (bool): Whether to normalize the values (default: True)
    
    Returns:
        Dictionary mapping each node to its betweenness centrality
    
    Time Complexity: O(V * E) where V is vertices and E is edges
    Space Complexity: O(V + E)
    """
    betweenness = {node: 0.0 for node in graph.get_nodes()}
    nodes = graph.get_nodes()
    
    # Brandes' algorithm
    for source in nodes:
        # Stack to store nodes in order of non-increasing distance from source
        stack = []
        
        # Predecessors of each node on shortest paths from source
        predecessors = {node: [] for node in nodes}
        
        # Number of shortest paths from source to each node
        num_paths = {node: 0 for node in nodes}
        num_paths[source] = 1
        
        # Distance from source to each node
        distance = {node: -1 for node in nodes}
        distance[source] = 0
        
        # BFS to find shortest paths
        queue = deque([source])
        
        while queue:
            current = queue.popleft()
            stack.append(current)
            
            for neighbor in graph.get_neighbors(current):
                # First time we see this neighbor?
                if distance[neighbor] < 0:
                    queue.append(neighbor)
                    distance[neighbor] = distance[current] + 1
                
                # Is this a shortest path to neighbor?
                if distance[neighbor] == distance[current] + 1:
                    num_paths[neighbor] += num_paths[current]
                    predecessors[neighbor].append(current)
        
        # Accumulation phase: backtrack through the DAG
        dependency = {node: 0.0 for node in nodes}
        
        while stack:
            w = stack.pop()
            for v in predecessors[w]:
                # Distribute dependency
                dependency[v] += (num_paths[v] / num_paths[w]) * (1 + dependency[w])
            
            if w != source:
                betweenness[w] += dependency[w]
    
    # Normalization for undirected graphs
    if normalized:
        n = len(nodes)
        if n > 2:
            # For undirected graphs, divide by 2 (each path counted twice)
            # and normalize by (n-1)(n-2)/2
            scale = 1.0 / ((n - 1) * (n - 2))
            for node in betweenness:
                betweenness[node] *= scale
    
    return betweenness


def compute_closeness_centrality(graph: Graph, normalized: bool = True) -> Dict[Any, float]:
    """
    Closeness Centrality measures the average distance from a node to all other nodes.
    
    Formula: C_C(v) = (n - 1) / Σ(d(v, u))
    where d(v, u) is the shortest path distance from v to u.
    
    Interpretation:
    - High closeness = node can quickly reach all other nodes
    - In social networks: people who can spread information efficiently
    
    Args:
        graph (Graph): The graph to analyze
        normalized (bool): Whether to normalize by (n-1) (default: True)
    
    Returns:
        Dictionary mapping each node to its closeness centrality
    
    Time Complexity: O(V * (V + E)) where V is vertices and E is edges
    Space Complexity: O(V)
    """
    closeness = {}
    nodes = graph.get_nodes()
    n = len(nodes)
    
    for node in nodes:
        # BFS to find shortest paths from this node to all others
        distances = {n: float('inf') for n in nodes}
        distances[node] = 0
        
        queue = deque([node])
        
        while queue:
            current = queue.popleft()
            
            for neighbor in graph.get_neighbors(current):
                if distances[neighbor] == float('inf'):
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        
        # Sum of distances to all reachable nodes
        total_distance = sum(d for d in distances.values() if d != float('inf'))
        
        # Count reachable nodes (excluding the node itself)
        reachable = sum(1 for d in distances.values() if d != float('inf') and d > 0)
        
        if total_distance > 0:
            closeness[node] = reachable / total_distance
            
            # Normalize by the fraction of reachable nodes
            if normalized and n > 1:
                closeness[node] *= reachable / (n - 1)
        else:
            closeness[node] = 0.0
    
    return closeness


def compute_pagerank(graph: Graph, alpha: float = 0.85, max_iter: int = 100, 
                     tol: float = 1e-6) -> Dict[Any, float]:
    """
    PageRank measures the importance of nodes based on the link structure.
    
    Algorithm:
    1. Initialize all nodes with equal PageRank (1/n)
    2. Iteratively update PageRank based on incoming links
    3. PR(v) = (1-α)/n + α * Σ(PR(u)/deg(u)) for all u linking to v
    
    Interpretation:
    - High PageRank = node is linked to by important nodes
    - Originally used by Google to rank web pages
    - In social networks: influential individuals
    
    Args:
        graph (Graph): The graph to analyze
        alpha (float): Damping factor (probability of following a link), default 0.85
        max_iter (int): Maximum number of iterations, default 100
        tol (float): Convergence tolerance, default 1e-6
    
    Returns:
        Dictionary mapping each node to its PageRank score
    
    Time Complexity: O(k * (V + E)) where k is number of iterations
    Space Complexity: O(V)
    """
    nodes = graph.get_nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    # Initialize PageRank: all nodes start with equal probability
    pagerank = {node: 1.0 / n for node in nodes}
    
    # Teleportation probability (random jump to any node)
    teleport = (1.0 - alpha) / n
    
    for iteration in range(max_iter):
        new_pagerank = {}
        
        for node in nodes:
            # Start with teleportation probability
            rank = teleport
            
            # Add contributions from incoming links
            for neighbor in graph.get_neighbors(node):
                neighbor_degree = graph.degree(neighbor)
                
                if neighbor_degree > 0:
                    # Each neighbor contributes its PageRank divided by its degree
                    rank += alpha * pagerank[neighbor] / neighbor_degree
            
            new_pagerank[node] = rank
        
        # Check for convergence
        # Calculate the maximum change in PageRank values
        diff = max(abs(new_pagerank[node] - pagerank[node]) for node in nodes)
        
        pagerank = new_pagerank
        
        # If change is below tolerance, we've converged
        if diff < tol:
            break
    
    return pagerank


def compute_eigenvector_centrality(graph: Graph, max_iter: int = 100, 
                                   tol: float = 1e-6) -> Dict[Any, float]:
    """
    Eigenvector Centrality measures influence based on connections to influential nodes.
    
    Algorithm (Power Iteration):
    1. Initialize all nodes with equal centrality
    2. Iteratively update: centrality(v) = Σ centrality(u) for neighbors u
    3. Normalize to prevent values from exploding
    
    Interpretation:
    - Similar to PageRank but simpler (no damping factor)
    - High eigenvector centrality = connected to other high-centrality nodes
    
    Args:
        graph (Graph): The graph to analyze
        max_iter (int): Maximum number of iterations, default 100
        tol (float): Convergence tolerance, default 1e-6
    
    Returns:
        Dictionary mapping each node to its eigenvector centrality
    
    Time Complexity: O(k * (V + E)) where k is number of iterations
    Space Complexity: O(V)
    """
    nodes = graph.get_nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    # Initialize: all nodes start with equal centrality
    centrality = {node: 1.0 / n for node in nodes}
    
    for iteration in range(max_iter):
        new_centrality = {node: 0.0 for node in nodes}
        
        # Update centrality based on neighbors
        for node in nodes:
            for neighbor in graph.get_neighbors(node):
                new_centrality[node] += centrality[neighbor]
        
        # Normalize to prevent overflow
        norm = sum(new_centrality.values())
        
        if norm == 0:
            # If all values are 0, reset to uniform distribution
            new_centrality = {node: 1.0 / n for node in nodes}
        else:
            new_centrality = {node: val / norm for node, val in new_centrality.items()}
        
        # Check for convergence
        diff = max(abs(new_centrality[node] - centrality[node]) for node in nodes)
        
        centrality = new_centrality
        
        if diff < tol:
            break
    
    return centrality


def compute_all_centralities(graph: Graph) -> Dict[str, Dict[Any, float]]:
    """
    Compute all centrality measures and return them in a single dictionary.
    
    Args:
        graph (Graph): The graph to analyze
    
    Returns:
        Dictionary with keys: "degree", "betweenness", "closeness", "pagerank", "eigenvector"
        Each value is a dictionary mapping nodes to their centrality scores
    
    Time Complexity: O(V * E) dominated by betweenness centrality
    Space Complexity: O(V)
    """
    return {
        "degree": compute_degree_centrality(graph),
        "betweenness": compute_betweenness_centrality(graph),
        "closeness": compute_closeness_centrality(graph),
        "pagerank": compute_pagerank(graph),
        "eigenvector": compute_eigenvector_centrality(graph)
    }


def get_top_k_central_nodes(centrality: Dict[Any, float], k: int = 10) -> List[tuple]:
    """
    Get the top k nodes with highest centrality scores.
    
    Args:
        centrality (Dict): Dictionary mapping nodes to centrality scores
        k (int): Number of top nodes to return
    
    Returns:
        List of tuples (node, score) sorted by score in descending order
    
    Time Complexity: O(n log n) for sorting
    Space Complexity: O(n)
    """
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    return sorted_nodes[:k]
