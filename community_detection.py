"""
Community Detection Algorithms
================================
Implementation of community detection algorithms from scratch.
Includes Girvan-Newman and Label Propagation algorithms.

Author: AAD Project Group
Date: December 2025
"""

from collections import defaultdict, Counter
import random
from typing import List, Set, Dict, Any, Tuple
from graph import Graph
from traversal import find_connected_components_bfs
from centrality import compute_betweenness_centrality


def girvan_newman(graph: Graph, num_communities: int = 2) -> List[List[Any]]:
    """
    Girvan-Newman algorithm for community detection.
    
    Algorithm:
    1. Calculate betweenness centrality for all edges
    2. Remove edge with highest betweenness
    3. Recalculate betweenness
    4. Repeat until desired number of communities is reached
    
    Interpretation:
    - Edges with high betweenness connect different communities
    - Removing them gradually separates the graph into communities
    
    Args:
        graph (Graph): The graph to analyze
        num_communities (int): Desired number of communities
    
    Returns:
        List of communities, where each community is a list of nodes
    
    Time Complexity: O(m^2 * n) where m is edges, n is vertices
    Space Complexity: O(n + m)
    """
    # Create a copy of the graph to work with
    working_graph = Graph()
    
    # Copy all nodes
    for node in graph.get_nodes():
        working_graph.add_node(node)
    
    # Copy all edges
    for u, v in graph.get_edges():
        working_graph.add_edge(u, v)
    
    # Keep removing edges until we have the desired number of components
    while True:
        # Check current number of components
        components = find_connected_components_bfs(working_graph)
        
        if len(components) >= num_communities:
            return components
        
        # Calculate edge betweenness
        edge_betweenness = compute_edge_betweenness(working_graph)
        
        if not edge_betweenness:
            # No more edges to remove
            break
        
        # Find edge with maximum betweenness
        max_edge = max(edge_betweenness, key=edge_betweenness.get)
        
        # Remove the edge
        working_graph.remove_edge(max_edge[0], max_edge[1])
    
    return find_connected_components_bfs(working_graph)


def compute_edge_betweenness(graph: Graph) -> Dict[Tuple[Any, Any], float]:
    """
    Compute betweenness centrality for all edges.
    
    Edge betweenness: number of shortest paths that pass through an edge.
    
    Args:
        graph (Graph): The graph to analyze
    
    Returns:
        Dictionary mapping edges to their betweenness scores
    
    Time Complexity: O(n * m) where n is vertices and m is edges
    Space Complexity: O(n + m)
    """
    edge_betweenness = defaultdict(float)
    nodes = graph.get_nodes()
    
    # For each node as source
    for source in nodes:
        # Stack for backtracking
        stack = []
        
        # Predecessors on shortest paths
        predecessors = {node: [] for node in nodes}
        
        # Number of shortest paths
        num_paths = {node: 0 for node in nodes}
        num_paths[source] = 1
        
        # Distance from source
        distance = {node: -1 for node in nodes}
        distance[source] = 0
        
        # BFS
        from collections import deque
        queue = deque([source])
        
        while queue:
            current = queue.popleft()
            stack.append(current)
            
            for neighbor in graph.get_neighbors(current):
                # First time visiting neighbor
                if distance[neighbor] < 0:
                    queue.append(neighbor)
                    distance[neighbor] = distance[current] + 1
                
                # Shortest path to neighbor via current
                if distance[neighbor] == distance[current] + 1:
                    num_paths[neighbor] += num_paths[current]
                    predecessors[neighbor].append(current)
        
        # Backtracking to accumulate edge betweenness
        edge_flow = defaultdict(float)
        node_flow = {node: 0.0 for node in nodes}
        
        while stack:
            w = stack.pop()
            
            for v in predecessors[w]:
                # Flow through edge (v, w)
                flow = (num_paths[v] / num_paths[w]) * (1.0 + node_flow[w])
                edge = tuple(sorted([v, w]))
                edge_flow[edge] += flow
                node_flow[v] += flow
        
        # Add to total edge betweenness
        for edge, flow in edge_flow.items():
            edge_betweenness[edge] += flow
    
    return edge_betweenness


def label_propagation(graph: Graph, max_iter: int = 100) -> List[List[Any]]:
    """
    Label Propagation algorithm for community detection.
    
    Algorithm:
    1. Initialize each node with a unique label
    2. Iteratively update each node's label to the most common label among its neighbors
    3. Repeat until convergence or max iterations
    
    Interpretation:
    - Nodes in the same community will converge to the same label
    - Fast and simple algorithm for large graphs
    
    Args:
        graph (Graph): The graph to analyze
        max_iter (int): Maximum number of iterations
    
    Returns:
        List of communities, where each community is a list of nodes
    
    Time Complexity: O(k * m) where k is iterations and m is edges
    Space Complexity: O(n) where n is vertices
    """
    nodes = graph.get_nodes()
    
    # Initialize: each node gets its own unique label
    labels = {node: i for i, node in enumerate(nodes)}
    
    # Iterate until convergence
    for iteration in range(max_iter):
        # Randomize node order to break ties randomly
        shuffled_nodes = nodes.copy()
        random.shuffle(shuffled_nodes)
        
        changed = False
        
        for node in shuffled_nodes:
            # Get labels of neighbors
            neighbor_labels = [labels[neighbor] for neighbor in graph.get_neighbors(node)]
            
            if not neighbor_labels:
                continue
            
            # Find most common label among neighbors
            label_counts = Counter(neighbor_labels)
            most_common_label = label_counts.most_common(1)[0][0]
            
            # Update label if it changed
            if labels[node] != most_common_label:
                labels[node] = most_common_label
                changed = True
        
        # If no labels changed, we've converged
        if not changed:
            break
    
    # Group nodes by their final labels
    communities = defaultdict(list)
    for node, label in labels.items():
        communities[label].append(node)
    
    return list(communities.values())


def modularity(graph: Graph, communities: List[List[Any]]) -> float:
    """
    Calculate modularity of a community partition.
    
    Modularity measures the quality of a division of a network into communities.
    Higher modularity indicates stronger community structure.
    
    Formula: Q = 1/(2m) * Σ[A_ij - (k_i * k_j)/(2m)] * δ(c_i, c_j)
    where:
    - m is the number of edges
    - A_ij is 1 if there's an edge between i and j, 0 otherwise
    - k_i is the degree of node i
    - δ(c_i, c_j) is 1 if i and j are in the same community, 0 otherwise
    
    Args:
        graph (Graph): The graph
        communities (List[List[Any]]): List of communities
    
    Returns:
        Modularity score (typically between -0.5 and 1.0)
    
    Time Complexity: O(m + n) where m is edges and n is vertices
    Space Complexity: O(n)
    """
    # Create a mapping from node to community
    node_to_community = {}
    for comm_id, community in enumerate(communities):
        for node in community:
            node_to_community[node] = comm_id
    
    m = graph.number_of_edges()
    
    if m == 0:
        return 0.0
    
    Q = 0.0
    
    # Calculate modularity
    for node_i in graph.get_nodes():
        for node_j in graph.get_nodes():
            # Check if nodes are in the same community
            if node_to_community[node_i] != node_to_community[node_j]:
                continue
            
            # A_ij: 1 if edge exists, 0 otherwise
            A_ij = 1.0 if graph.has_edge(node_i, node_j) else 0.0
            
            # Degrees
            k_i = graph.degree(node_i)
            k_j = graph.degree(node_j)
            
            # Add to modularity
            Q += A_ij - (k_i * k_j) / (2.0 * m)
    
    # Normalize by 2m
    Q /= (2.0 * m)
    
    return Q


def greedy_modularity_communities(graph: Graph, max_communities: int = None) -> List[List[Any]]:
    """
    Greedy modularity maximization for community detection.
    
    Algorithm (Clauset-Newman-Moore):
    1. Start with each node in its own community
    2. Repeatedly merge communities that increase modularity the most
    3. Stop when modularity stops increasing or max_communities is reached
    
    Args:
        graph (Graph): The graph to analyze
        max_communities (int): Maximum number of communities (None for auto)
    
    Returns:
        List of communities
    
    Time Complexity: O(n^2 * log n) where n is vertices
    Space Complexity: O(n^2)
    """
    nodes = graph.get_nodes()
    
    # Start with each node in its own community
    communities = [[node] for node in nodes]
    
    # Create node to community mapping
    node_to_comm = {node: i for i, node in enumerate(nodes)}
    
    best_modularity = modularity(graph, communities)
    
    while len(communities) > 1:
        if max_communities and len(communities) <= max_communities:
            break
        
        best_merge = None
        best_delta_q = -float('inf')
        
        # Try all pairs of communities
        for i in range(len(communities)):
            for j in range(i + 1, len(communities)):
                # Merge communities i and j
                merged = communities[:i] + communities[i+1:j] + communities[j+1:]
                merged.append(communities[i] + communities[j])
                
                # Calculate modularity change
                new_q = modularity(graph, merged)
                delta_q = new_q - best_modularity
                
                if delta_q > best_delta_q:
                    best_delta_q = delta_q
                    best_merge = (i, j)
        
        # If no improvement, stop
        if best_delta_q <= 0:
            break
        
        # Perform best merge
        i, j = best_merge
        merged_community = communities[i] + communities[j]
        
        # Remove old communities and add merged one
        communities = [communities[k] for k in range(len(communities)) if k not in [i, j]]
        communities.append(merged_community)
        
        best_modularity += best_delta_q
    
    return communities


def detect_communities(graph: Graph, method: str = "label_propagation", 
                       num_communities: int = None) -> Dict[str, Any]:
    """
    Detect communities using the specified method.
    
    Args:
        graph (Graph): The graph to analyze
        method (str): Method to use ("label_propagation", "girvan_newman", "greedy_modularity")
        num_communities (int): Desired number of communities (for some methods)
    
    Returns:
        Dictionary with "communities" and "modularity" keys
    
    Time Complexity: Depends on method chosen
    Space Complexity: O(n)
    """
    if method == "label_propagation":
        communities = label_propagation(graph)
    elif method == "girvan_newman":
        if num_communities is None:
            num_communities = 2
        communities = girvan_newman(graph, num_communities)
    elif method == "greedy_modularity":
        communities = greedy_modularity_communities(graph, num_communities)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Calculate modularity
    mod = modularity(graph, communities)
    
    return {
        "communities": communities,
        "modularity": mod,
        "num_communities": len(communities)
    }
