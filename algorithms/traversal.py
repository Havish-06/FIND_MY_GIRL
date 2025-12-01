"""
Graph Traversal Algorithms
===========================
Implementation of BFS and DFS for graph traversal and connected components analysis.
All algorithms are implemented from scratch without using external graph libraries.
"""

from collections import deque
from typing import List, Set, Dict, Any
from .graph import Graph


def bfs(graph: Graph, start_node: Any) -> List[Any]:
    """
    Breadth-First Search (BFS) traversal starting from a given node.
    
    Algorithm:
    1. Start from the source node and mark it as visited
    2. Use a queue to explore neighbors level by level
    3. For each node, visit all its unvisited neighbors before moving deeper
    
    Args:
        graph (Graph): The graph to traverse
        start_node: The starting node for BFS
    
    Returns:
        List of nodes in BFS order
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for visited set and queue
    """
    if start_node not in graph.get_nodes():
        return []
    
    visited = set()  # Keep track of visited nodes
    queue = deque([start_node])  # Queue for BFS
    bfs_order = []  # Store the order of traversal
    
    visited.add(start_node)
    
    while queue:
        # Dequeue a node from the front
        current = queue.popleft()
        bfs_order.append(current)
        
        # Explore all neighbors of the current node
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return bfs_order


def dfs(graph: Graph, start_node: Any) -> List[Any]:
    """
    Depth-First Search (DFS) traversal starting from a given node (iterative).
    
    Algorithm:
    1. Start from the source node and mark it as visited
    2. Use a stack to explore neighbors depth-first
    3. For each node, explore as deep as possible before backtracking
    
    Args:
        graph (Graph): The graph to traverse
        start_node: The starting node for DFS
    
    Returns:
        List of nodes in DFS order
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for visited set and stack
    """
    if start_node not in graph.get_nodes():
        return []
    
    visited = set()  # Keep track of visited nodes
    stack = [start_node]  # Stack for DFS
    dfs_order = []  # Store the order of traversal
    
    while stack:
        # Pop a node from the top of the stack
        current = stack.pop()
        
        if current not in visited:
            visited.add(current)
            dfs_order.append(current)
            
            # Push all unvisited neighbors to the stack
            for neighbor in graph.get_neighbors(current):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return dfs_order


def dfs_recursive(graph: Graph, start_node: Any, visited: Set[Any] = None) -> List[Any]:
    """
    Depth-First Search (DFS) traversal using recursion.
    
    Algorithm:
    1. Mark current node as visited
    2. Recursively visit all unvisited neighbors
    3. Return when all reachable nodes are visited
    
    Args:
        graph (Graph): The graph to traverse
        start_node: The starting node for DFS
        visited (Set): Set of already visited nodes (used in recursion)
    
    Returns:
        List of nodes in DFS order
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for visited set and recursion stack
    """
    if visited is None:
        visited = set()
    
    if start_node not in graph.get_nodes():
        return []
    
    dfs_order = []
    
    if start_node not in visited:
        visited.add(start_node)
        dfs_order.append(start_node)
        
        # Recursively visit all unvisited neighbors
        for neighbor in graph.get_neighbors(start_node):
            if neighbor not in visited:
                dfs_order.extend(dfs_recursive(graph, neighbor, visited))
    
    return dfs_order


def find_connected_components_bfs(graph: Graph) -> List[List[Any]]:
    """
    Find all connected components in the graph using BFS.
    
    Algorithm:
    1. Iterate through all nodes in the graph
    2. For each unvisited node, perform BFS to find its component
    3. All nodes reached in one BFS belong to the same component
    
    Args:
        graph (Graph): The graph to analyze
    
    Returns:
        List of connected components, where each component is a list of nodes
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for visited set and components storage
    """
    visited = set()
    components = []
    
    # Iterate through all nodes
    for node in graph.get_nodes():
        if node not in visited:
            # Find all nodes in this component using BFS
            component = []
            queue = deque([node])
            visited.add(node)
            
            while queue:
                current = queue.popleft()
                component.append(current)
                
                # Explore neighbors
                for neighbor in graph.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            components.append(component)
    
    return components


def find_connected_components_dfs(graph: Graph) -> List[List[Any]]:
    """
    Find all connected components in the graph using DFS.
    
    Algorithm:
    1. Iterate through all nodes in the graph
    2. For each unvisited node, perform DFS to find its component
    3. All nodes reached in one DFS belong to the same component
    
    Args:
        graph (Graph): The graph to analyze
    
    Returns:
        List of connected components, where each component is a list of nodes
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for visited set and components storage
    """
    visited = set()
    components = []
    
    # Iterate through all nodes
    for node in graph.get_nodes():
        if node not in visited:
            # Find all nodes in this component using DFS
            component = []
            stack = [node]
            
            while stack:
                current = stack.pop()
                
                if current not in visited:
                    visited.add(current)
                    component.append(current)
                    
                    # Explore neighbors
                    for neighbor in graph.get_neighbors(current):
                        if neighbor not in visited:
                            stack.append(neighbor)
            
            components.append(component)
    
    return components


def shortest_path_bfs(graph: Graph, start: Any, end: Any) -> List[Any]:
    """
    Find the shortest path between two nodes using BFS.
    
    In an unweighted graph, BFS guarantees the shortest path.
    
    Algorithm:
    1. Use BFS to explore nodes level by level
    2. Keep track of parent nodes to reconstruct the path
    3. Backtrack from end to start using parent pointers
    
    Args:
        graph (Graph): The graph to search
        start: Starting node
        end: Destination node
    
    Returns:
        List of nodes representing the shortest path, or empty list if no path exists
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for visited set, queue, and parent tracking
    """
    if start not in graph.get_nodes() or end not in graph.get_nodes():
        return []
    
    if start == end:
        return [start]
    
    visited = set([start])
    queue = deque([start])
    parent = {start: None}  # Track parent nodes for path reconstruction
    
    # BFS to find the shortest path
    while queue:
        current = queue.popleft()
        
        # If we reached the destination, reconstruct the path
        if current == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1]  # Reverse to get path from start to end
        
        # Explore neighbors
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
    
    # No path found
    return []


def is_connected(graph: Graph) -> bool:
    """
    Check if the graph is connected (all nodes are in one component).
    
    Args:
        graph (Graph): The graph to check
    
    Returns:
        True if graph is connected, False otherwise
    
    Time Complexity: O(V + E) where V is vertices and E is edges
    Space Complexity: O(V) for BFS visited set
    """
    nodes = graph.get_nodes()
    if not nodes:
        return True
    
    # Perform BFS from the first node
    visited = bfs(graph, nodes[0])
    
    # If BFS visits all nodes, the graph is connected
    return len(visited) == len(nodes)
