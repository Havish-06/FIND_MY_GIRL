"""
Community Detection Algorithms
================================
Implementation of community detection algorithms from scratch.
Includes Girvan-Newman and Label Propagation algorithms.

"""

from collections import defaultdict, Counter
import random
from typing import List, Set, Dict, Any, Tuple
from .graph import Graph
from .traversal import find_connected_components_bfs
from .centrality import compute_betweenness_centrality


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


def compute_modularity_gain(graph, node: Any, community: int, 
                            node_to_community: Dict[Any, int],
                            k_i: float, sigma_tot: float, m: float) -> float:
    """
    Compute the modularity gain from moving a node to a community.
    
    Args:
        graph: The graph
        node: Node to move
        community: Target community
        node_to_community: Current node-to-community mapping
        k_i: Degree of node
        sigma_tot: Sum of degrees in target community
        m: Total edge weight (2 * number of edges for unweighted)
    
    Returns:
        Modularity gain (delta Q)
    """
    # Calculate k_i_in: sum of weights of links from node to nodes in community
    k_i_in = 0.0
    for neighbor in graph.get_neighbors(node):
        if node_to_community[neighbor] == community:
            k_i_in += 1.0  # Edge weight = 1 for unweighted graphs
    
    # Modularity gain formula
    delta_q = (k_i_in / m) - (sigma_tot * k_i / (2 * m * m))
    
    return delta_q


def louvain_first_phase(graph, node_to_community: Dict[Any, int]) -> Tuple[bool, Dict[Any, int]]:
    """
    First phase of Louvain: optimize modularity by moving nodes between communities.
    
    Args:
        graph: The graph
        node_to_community: Initial community assignment
    
    Returns:
        (improved, new_node_to_community) - whether improvement was made
    """
    nodes = list(graph.get_nodes())
    m = float(graph.number_of_edges())
    
    if m == 0:
        return False, node_to_community
    
    # Calculate total degree for each community
    community_degree = defaultdict(float)
    for node in nodes:
        community_degree[node_to_community[node]] += graph.degree(node)
    
    improved = False
    
    # Iterate until no improvement
    while True:
        local_improved = False
        random.shuffle(nodes)  # Random order for better convergence
        
        for node in nodes:
            current_community = node_to_community[node]
            node_degree = float(graph.degree(node))
            
            # Remove node from current community temporarily
            community_degree[current_community] -= node_degree
            
            # Find neighboring communities
            neighbor_communities = set()
            for neighbor in graph.get_neighbors(node):
                neighbor_communities.add(node_to_community[neighbor])
            
            # Add current community to consider staying
            neighbor_communities.add(current_community)
            
            # Find best community (maximum modularity gain)
            best_community = current_community
            best_gain = 0.0
            
            for community in neighbor_communities:
                sigma_tot = community_degree[community]
                gain = compute_modularity_gain(
                    graph, node, community, node_to_community,
                    node_degree, sigma_tot, m
                )
                
                if gain > best_gain:
                    best_gain = gain
                    best_community = community
            
            # Move node to best community
            if best_community != current_community and best_gain > 1e-10:
                node_to_community[node] = best_community
                community_degree[best_community] += node_degree
                local_improved = True
                improved = True
            else:
                # Put node back in current community
                community_degree[current_community] += node_degree
        
        if not local_improved:
            break
    
    return improved, node_to_community


def build_community_graph(graph, node_to_community: Dict[Any, int]):
    """
    Second phase of Louvain: build a new graph where nodes are communities.
    
    Args:
        graph: Original graph
        node_to_community: Community assignment
    
    Returns:
        New graph where each node represents a community
    """
    community_graph = Graph()
    
    # Get unique communities
    communities = set(node_to_community.values())
    
    # Add community nodes
    for community in communities:
        community_graph.add_node(community)
    
    # Add edges between communities (with weights for multi-edges)
    edge_weights = defaultdict(float)
    
    for u, v in graph.get_edges():
        comm_u = node_to_community[u]
        comm_v = node_to_community[v]
        
        if comm_u != comm_v:
            # Edge between different communities
            edge = tuple(sorted([comm_u, comm_v]))
            edge_weights[edge] += 1.0
    
    # Add weighted edges to community graph
    for (comm_u, comm_v), weight in edge_weights.items():
        if not community_graph.has_edge(comm_u, comm_v):
            community_graph.add_edge(comm_u, comm_v)
    
    return community_graph


def louvain_method(graph, max_iterations: int = 100) -> List[List[Any]]:
    """
    Louvain method for community detection.
    
    Fast modularity optimization algorithm that iteratively:
    1. Optimizes modularity by moving nodes between communities (Phase 1)
    2. Builds a new graph where nodes are communities (Phase 2)
    3. Repeats until no improvement
    
    Args:
        graph: The graph to analyze
        max_iterations: Maximum number of iterations
    
    Returns:
        List of communities (each community is a list of nodes)
    
    Time Complexity: O(m log n) on average - very fast!
    Space Complexity: O(n + m)
    """
    nodes = list(graph.get_nodes())
    
    if len(nodes) == 0:
        return []
    
    # Initialize: each node in its own community
    node_to_community = {node: i for i, node in enumerate(nodes)}
    
    # Keep track of original nodes in each community
    community_nodes = {i: [node] for i, node in enumerate(nodes)}
    
    current_graph = graph
    
    for iteration in range(max_iterations):
        # Phase 1: Optimize communities
        improved, node_to_community = louvain_first_phase(current_graph, node_to_community)
        
        if not improved:
            break
        
        # Update community_nodes mapping
        new_communities = defaultdict(list)
        for node, comm in node_to_community.items():
            # Get original nodes
            if isinstance(node, int) and node < len(nodes):
                # This is an original node
                new_communities[comm].append(node)
            else:
                # This is a meta-community, expand it
                if node in community_nodes:
                    new_communities[comm].extend(community_nodes[node])
                else:
                    new_communities[comm].append(node)
        
        community_nodes = dict(new_communities)
        
        # Phase 2: Build community graph
        current_graph = build_community_graph(current_graph, node_to_community)
        
        # Re-initialize communities for next iteration
        community_list = list(community_nodes.keys())
        node_to_community = {comm: i for i, comm in enumerate(community_list)}
        
        # Update community_nodes with new indices
        new_community_nodes = {}
        for i, comm in enumerate(community_list):
            new_community_nodes[i] = community_nodes[comm]
        community_nodes = new_community_nodes
    
    # Convert to list of communities
    return list(community_nodes.values())


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


def detect_communities(graph: Graph, method: str = "label_propagation", 
                       num_communities: int = None) -> Dict[str, Any]:
    """
    Detect communities using the specified method.
    
    Args:
        graph (Graph): The graph to analyze
        method (str): Method to use ("label_propagation", "girvan_newman", or "louvain")
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
    elif method == "louvain":
        communities = louvain_method(graph)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'label_propagation', 'girvan_newman', or 'louvain'.")
    
    # Calculate modularity
    mod = modularity(graph, communities)
    
    return {
        "communities": communities,
        "modularity": mod,
        "num_communities": len(communities)
    }
