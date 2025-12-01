"""
Graph Data Structure Implementation
===================================
A from-scratch implementation of an undirected graph using adjacency list representation.
No external graph libraries (like NetworkX) are used.

Author: AAD Project Group
Date: December 2025
"""

from collections import defaultdict, deque
from typing import List, Set, Dict, Tuple, Any


class Graph:
    """
    Undirected Graph implementation using adjacency list.
    
    Attributes:
        adj_list (dict): Adjacency list representation {node: set of neighbors}
        node_attributes (dict): Dictionary storing attributes for each node
        edge_weights (dict): Dictionary storing edge weights {(u,v): weight}
    """
    
    def __init__(self):
        """
        Initialize an empty graph.
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.adj_list = defaultdict(set)  # {node: {neighbor1, neighbor2, ...}}
        self.node_attributes = {}  # {node: {attribute_name: value}}
        self.edge_weights = {}  # {(u, v): weight}
    
    def add_node(self, node: Any, **attributes) -> None:
        """
        Add a node to the graph with optional attributes.
        
        Args:
            node: The node identifier (can be int, str, or any hashable type)
            **attributes: Optional key-value pairs for node attributes
        
        Time Complexity: O(1)
        Space Complexity: O(k) where k is the number of attributes
        
        Example:
            >>> g = Graph()
            >>> g.add_node(1, name="Alice", age=25)
        """
        if node not in self.adj_list:
            self.adj_list[node] = set()
        
        if attributes:
            if node not in self.node_attributes:
                self.node_attributes[node] = {}
            self.node_attributes[node].update(attributes)
    
    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        """
        Add an undirected edge between nodes u and v.
        
        Args:
            u: First node
            v: Second node
            weight: Edge weight (default: 1.0)
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        
        Example:
            >>> g = Graph()
            >>> g.add_edge(1, 2)
            >>> g.add_edge(1, 3, weight=2.5)
        """
        # Ensure both nodes exist
        self.add_node(u)
        self.add_node(v)
        
        # Add edge (undirected, so add both directions)
        self.adj_list[u].add(v)
        self.adj_list[v].add(u)
        
        # Store edge weight (normalize edge direction for undirected graph)
        edge = tuple(sorted([u, v]))
        self.edge_weights[edge] = weight
    
    def remove_edge(self, u: Any, v: Any) -> None:
        """
        Remove an edge between nodes u and v.
        
        Args:
            u: First node
            v: Second node
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if u in self.adj_list and v in self.adj_list[u]:
            self.adj_list[u].discard(v)
            self.adj_list[v].discard(u)
            
            edge = tuple(sorted([u, v]))
            if edge in self.edge_weights:
                del self.edge_weights[edge]
    
    def get_neighbors(self, node: Any) -> Set[Any]:
        """
        Get all neighbors of a node.
        
        Args:
            node: The node to query
        
        Returns:
            Set of neighboring nodes
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return self.adj_list.get(node, set())
    
    def get_nodes(self) -> List[Any]:
        """
        Get all nodes in the graph.
        
        Returns:
            List of all nodes
        
        Time Complexity: O(n) where n is the number of nodes
        Space Complexity: O(n)
        """
        return list(self.adj_list.keys())
    
    def get_edges(self) -> List[Tuple[Any, Any]]:
        """
        Get all edges in the graph.
        
        Returns:
            List of tuples representing edges
        
        Time Complexity: O(n + m) where n is nodes and m is edges
        Space Complexity: O(m)
        """
        edges = []
        visited = set()
        
        for u in self.adj_list:
            for v in self.adj_list[u]:
                edge = tuple(sorted([u, v]))
                if edge not in visited:
                    edges.append((u, v))
                    visited.add(edge)
        
        return edges
    
    def degree(self, node: Any) -> int:
        """
        Get the degree (number of neighbors) of a node.
        
        Args:
            node: The node to query
        
        Returns:
            Degree of the node
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return len(self.adj_list.get(node, set()))
    
    def get_edge_weight(self, u: Any, v: Any) -> float:
        """
        Get the weight of an edge.
        
        Args:
            u: First node
            v: Second node
        
        Returns:
            Edge weight, or 0 if edge doesn't exist
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        edge = tuple(sorted([u, v]))
        return self.edge_weights.get(edge, 0.0)
    
    def number_of_nodes(self) -> int:
        """
        Get the total number of nodes in the graph.
        
        Returns:
            Number of nodes
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return len(self.adj_list)
    
    def number_of_edges(self) -> int:
        """
        Get the total number of edges in the graph.
        
        Returns:
            Number of edges
        
        Time Complexity: O(n) where n is the number of nodes
        Space Complexity: O(1)
        """
        total = sum(len(neighbors) for neighbors in self.adj_list.values())
        return total // 2  # Divide by 2 because each edge is counted twice
    
    def has_edge(self, u: Any, v: Any) -> bool:
        """
        Check if an edge exists between two nodes.
        
        Args:
            u: First node
            v: Second node
        
        Returns:
            True if edge exists, False otherwise
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return v in self.adj_list.get(u, set())
    
    def get_node_attribute(self, node: Any, attribute: str, default=None) -> Any:
        """
        Get a specific attribute of a node.
        
        Args:
            node: The node to query
            attribute: The attribute name
            default: Default value if attribute doesn't exist
        
        Returns:
            The attribute value or default
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if node in self.node_attributes:
            return self.node_attributes[node].get(attribute, default)
        return default
    
    def __str__(self) -> str:
        """
        String representation of the graph.
        
        Returns:
            String showing nodes and edges
        """
        return f"Graph with {self.number_of_nodes()} nodes and {self.number_of_edges()} edges"
    
    def __repr__(self) -> str:
        """
        Detailed representation of the graph.
        
        Returns:
            String with adjacency list
        """
        return f"Graph({dict(self.adj_list)})"
