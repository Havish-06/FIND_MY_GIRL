"""
Union-Find (Disjoint Set Union) Data Structure
===============================================
Implementation of Union-Find with path compression and union by rank optimizations.
Used for efficient connected components detection and cycle detection.

Author: AAD Project Group
Date: December 2025
"""

from typing import Any, Dict, List, Set
from .graph import Graph


class UnionFind:
    """
    Union-Find (Disjoint Set Union) data structure.
    
    Supports two main operations:
    1. Find: Determine which set an element belongs to
    2. Union: Merge two sets together
    
    Optimizations:
    - Path Compression: Make tree flatter during find operations
    - Union by Rank: Attach smaller tree under root of larger tree
    
    These optimizations give nearly O(1) amortized time complexity.
    """
    
    def __init__(self):
        """
        Initialize an empty Union-Find structure.
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.parent = {}  # parent[x] = parent of x
        self.rank = {}    # rank[x] = approximate depth of tree rooted at x
        self.size = {}    # size[x] = number of elements in set rooted at x
    
    def make_set(self, x: Any) -> None:
        """
        Create a new set containing only element x.
        
        Args:
            x: Element to create a set for
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if x not in self.parent:
            self.parent[x] = x  # Initially, x is its own parent
            self.rank[x] = 0    # Initial rank is 0
            self.size[x] = 1    # Initial size is 1
    
    def find(self, x: Any) -> Any:
        """
        Find the representative (root) of the set containing x.
        Uses path compression to flatten the tree.
        
        Path Compression: Make every node on the path point directly to the root.
        This optimization ensures nearly O(1) amortized time.
        
        Args:
            x: Element to find the set representative for
        
        Returns:
            The representative of the set containing x
        
        Time Complexity: O(α(n)) amortized, where α is inverse Ackermann function
        Space Complexity: O(1)
        """
        if x not in self.parent:
            self.make_set(x)
        
        # If x is not the root, recursively find the root and compress the path
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        
        return self.parent[x]
    
    def union(self, x: Any, y: Any) -> bool:
        """
        Merge the sets containing x and y.
        Uses union by rank to keep trees balanced.
        
        Union by Rank: Attach the shorter tree under the root of the taller tree.
        This keeps the trees relatively flat.
        
        Args:
            x: Element from first set
            y: Element from second set
        
        Returns:
            True if union was performed (x and y were in different sets),
            False if they were already in the same set
        
        Time Complexity: O(α(n)) amortized, where α is inverse Ackermann function
        Space Complexity: O(1)
        """
        # Find representatives of both sets
        root_x = self.find(x)
        root_y = self.find(y)
        
        # If they're already in the same set, no union needed
        if root_x == root_y:
            return False
        
        # Union by rank: attach smaller tree under larger tree
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]
        else:
            # If ranks are equal, choose one as root and increment its rank
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
            self.size[root_x] += self.size[root_y]
        
        return True
    
    def connected(self, x: Any, y: Any) -> bool:
        """
        Check if x and y are in the same set (connected).
        
        Args:
            x: First element
            y: Second element
        
        Returns:
            True if x and y are in the same set, False otherwise
        
        Time Complexity: O(α(n)) amortized
        Space Complexity: O(1)
        """
        return self.find(x) == self.find(y)
    
    def get_set_size(self, x: Any) -> int:
        """
        Get the size of the set containing x.
        
        Args:
            x: Element to query
        
        Returns:
            Number of elements in the set containing x
        
        Time Complexity: O(α(n)) amortized
        Space Complexity: O(1)
        """
        root = self.find(x)
        return self.size[root]
    
    def get_all_sets(self) -> Dict[Any, Set[Any]]:
        """
        Get all disjoint sets as a dictionary.
        
        Returns:
            Dictionary mapping each root to its set of elements
        
        Time Complexity: O(n * α(n)) where n is the number of elements
        Space Complexity: O(n)
        """
        sets = {}
        for element in self.parent:
            root = self.find(element)
            if root not in sets:
                sets[root] = set()
            sets[root].add(element)
        return sets
    
    def number_of_sets(self) -> int:
        """
        Get the number of disjoint sets.
        
        Returns:
            Number of disjoint sets
        
        Time Complexity: O(n) where n is the number of elements
        Space Complexity: O(n)
        """
        roots = set()
        for element in self.parent:
            roots.add(self.find(element))
        return len(roots)


def find_connected_components_union_find(graph: Graph) -> List[List[Any]]:
    """
    Find all connected components using Union-Find algorithm.
    
    Algorithm:
    1. Initialize Union-Find with all nodes
    2. For each edge, union the two nodes
    3. Group nodes by their root representative
    
    Args:
        graph (Graph): The graph to analyze
    
    Returns:
        List of connected components, where each component is a list of nodes
    
    Time Complexity: O(E * α(V)) where E is edges, V is vertices, α is inverse Ackermann
    Space Complexity: O(V)

    use union-find to group nodes into connected components by processing all edges.
    """
    uf = UnionFind()
    
    # Initialize all nodes in Union-Find
    for node in graph.get_nodes():
        uf.make_set(node)
    
    # Union nodes connected by edges
    for u, v in graph.get_edges():
        uf.union(u, v)
    
    # Group nodes by their root representative
    components_dict = uf.get_all_sets()
    
    # Convert to list of lists
    components = [list(component) for component in components_dict.values()]
    
    return components


def detect_cycle_union_find(graph: Graph) -> bool:
    """
    Detect if the graph contains a cycle using Union-Find.
    
    Algorithm:
    1. For each edge (u, v):
    2. If u and v are already in the same set, a cycle exists
    3. Otherwise, union u and v
    
    Args:
        graph (Graph): The graph to check
    
    Returns:
        True if the graph contains a cycle, False otherwise
    
    Time Complexity: O(E * α(V)) where E is edges, V is vertices
    Space Complexity: O(V)

    iterate the edges of the graph and use union-find to detect cycles.
    if two nodes of an edge are already connected, a cycle is detected.
    """
    uf = UnionFind()
    
    # Initialize all nodes
    for node in graph.get_nodes():
        uf.make_set(node)
    
    # Check each edge
    visited_edges = set()
    
    for u, v in graph.get_edges():
        # Skip if we've already processed this edge (undirected graph)
        edge = tuple(sorted([u, v]))
        if edge in visited_edges:
            continue
        visited_edges.add(edge)
        
        # If u and v are already connected, adding this edge creates a cycle
        if uf.connected(u, v):
            return True
        
        # Union the two nodes
        uf.union(u, v)
    
    return False


def kruskal_mst(graph: Graph) -> List[tuple]:
    """
    Find Minimum Spanning Tree using Kruskal's algorithm with Union-Find.
    
    Algorithm:
    1. Sort all edges by weight
    2. For each edge in sorted order:
    3. If adding the edge doesn't create a cycle, add it to MST
    4. Use Union-Find to detect cycles
    
    Args:
        graph (Graph): The graph (must be connected)
    
    Returns:
        List of edges in the MST as tuples (u, v, weight)
    
    Time Complexity: O(E log E) for sorting edges
    Space Complexity: O(V + E)
    """
    uf = UnionFind()
    
    # Initialize all nodes
    for node in graph.get_nodes():
        uf.make_set(node)
    
    # Get all edges with weights and sort by weight
    edges = []
    visited_edges = set()
    
    for u, v in graph.get_edges():
        edge = tuple(sorted([u, v]))
        if edge not in visited_edges:
            weight = graph.get_edge_weight(u, v)
            edges.append((weight, u, v))
            visited_edges.add(edge)
    
    edges.sort()  # Sort by weight (first element of tuple)
    
    mst = []
    
    # Process edges in order of increasing weight
    for weight, u, v in edges:
        # If u and v are not connected, add this edge to MST
        if not uf.connected(u, v):
            uf.union(u, v)
            mst.append((u, v, weight))
            
            # MST is complete when we have V-1 edges
            if len(mst) == graph.number_of_nodes() - 1:
                break
    
    return mst
