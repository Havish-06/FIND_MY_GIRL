"""
Graph Visualization Module
===========================
Visualize social networks, communities, and analysis results.
"""

import math
import random
from typing import List, Dict, Any, Tuple
from .graph import Graph


def force_directed_layout(graph: Graph, iterations: int = 50, 
                         k: float = None, seed: int = None) -> Dict[Any, Tuple[float, float]]:
    """
    Compute force-directed layout for graph visualization using Fruchterman-Reingold algorithm.
    
    Algorithm:
    1. Initialize node positions randomly
    2. Calculate repulsive forces between all node pairs
    3. Calculate attractive forces for connected nodes
    4. Update positions based on forces
    5. Repeat with cooling
    
    Args:
        graph (Graph): The graph to layout
        iterations (int): Number of iterations
        k (float): Optimal distance between nodes
        seed (int): Random seed for reproducible layouts
    
    Returns:
        Dictionary mapping nodes to (x, y) positions
    
    Time Complexity: O(iterations * n^2) where n is nodes
    Space Complexity: O(n)
    """
    nodes = graph.get_nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    # Set random seed for reproducible layouts
    if seed is not None:
        random.seed(seed)
    
    # Set optimal distance - ULTRA MAXIMIZED for extreme node separation
    if k is None:
        k = math.sqrt(50.0 / n)  # Increased to 50.0 for ultra clarity
    
    # Initialize positions randomly - ULTRA LARGE AREA
    positions = {}
    for node in nodes:
        positions[node] = (random.uniform(0, 20), random.uniform(0, 20))  # Increased to (0,20) for ultra separation
    
    # Initial temperature - ULTRA MAXIMIZED
    temperature = 5.0  # Increased to 5.0 for ultra maximum spreading force
    
    for iteration in range(iterations):
        # Calculate forces
        forces = {node: [0.0, 0.0] for node in nodes}
        
        # Repulsive forces between all pairs
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i + 1:]:
                x1, y1 = positions[node1]
                x2, y2 = positions[node2]
                
                dx = x1 - x2
                dy = y1 - y2
                
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < 0.01:  # Avoid division by zero
                    distance = 0.01
                    dx = random.uniform(-0.01, 0.01)
                    dy = random.uniform(-0.01, 0.01)
                
                # Repulsive force: f_r = k^2 / d
                repulsion = k * k / distance
                
                fx = (dx / distance) * repulsion
                fy = (dy / distance) * repulsion
                
                forces[node1][0] += fx
                forces[node1][1] += fy
                forces[node2][0] -= fx
                forces[node2][1] -= fy
        
        # Attractive forces for edges
        for u, v in graph.get_edges():
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            
            dx = x1 - x2
            dy = y1 - y2
            
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 0.01:
                distance = 0.01
            
            # Attractive force: f_a = d^2 / k
            attraction = distance * distance / k
            
            fx = (dx / distance) * attraction
            fy = (dy / distance) * attraction
            
            forces[u][0] -= fx
            forces[u][1] -= fy
            forces[v][0] += fx
            forces[v][1] += fy
        
        # Update positions with temperature cooling
        for node in nodes:
            fx, fy = forces[node]
            
            force_magnitude = math.sqrt(fx * fx + fy * fy)
            
            if force_magnitude > 0.01:
                # Limit displacement by temperature
                displacement = min(force_magnitude, temperature)
                
                dx = (fx / force_magnitude) * displacement
                dy = (fy / force_magnitude) * displacement
                
                x, y = positions[node]
                positions[node] = (x + dx, y + dy)
        
        # Cool down
        temperature *= 0.95
    
    return positions


def circular_layout(graph: Graph) -> Dict[Any, Tuple[float, float]]:
    """
    Arrange nodes in a circle.
    
    Args:
        graph (Graph): The graph to layout
    
    Returns:
        Dictionary mapping nodes to (x, y) positions
    
    Time Complexity: O(n) where n is nodes
    Space Complexity: O(n)
    """
    nodes = graph.get_nodes()
    n = len(nodes)
    
    if n == 0:
        return {}
    
    positions = {}
    
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = math.cos(angle)
        y = math.sin(angle)
        positions[node] = (x, y)
    
    return positions


def spring_layout(graph: Graph, iterations: int = 50) -> Dict[Any, Tuple[float, float]]:
    """
    Spring layout (alias for force-directed layout).
    
    Args:
        graph (Graph): The graph to layout
        iterations (int): Number of iterations
    
    Returns:
        Dictionary mapping nodes to (x, y) positions
    
    Time Complexity: O(iterations * n^2)
    Space Complexity: O(n)
    """
    return force_directed_layout(graph, iterations)


def visualize_graph(graph: Graph, 
                   positions: Dict[Any, Tuple[float, float]] = None,
                   node_colors: List[str] = None,
                   node_labels: Dict[Any, str] = None,
                   title: str = "Social Network Graph",
                   filename: str = None,
                   show: bool = True,
                   figsize: Tuple[int, int] = (40, 40)):
    """
    Visualize a graph using matplotlib.
    
    Args:
        graph (Graph): The graph to visualize
        positions (Dict): Node positions (if None, uses force-directed layout)
        node_colors (List): List of colors for nodes
        node_labels (Dict): Custom labels for nodes
        title (str): Plot title
        filename (str): If provided, save to this file
        show (bool): Whether to display the plot
        figsize (Tuple): Figure size
    
    Time Complexity: O(n + m) where n is nodes and m is edges
    Space Complexity: O(n)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Error: matplotlib is required for visualization")
        print("Install it with: pip install matplotlib")
        return
    
    nodes = graph.get_nodes()
    
    if not nodes:
        print("Graph is empty, nothing to visualize")
        return
    
    # Compute layout if not provided
    if positions is None:
        positions = force_directed_layout(graph, seed=42)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw edges - thinner for large graphs
    for u, v in graph.get_edges():
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        ax.plot([x1, x2], [y1, y2], 'gray', linewidth=0.2, alpha=0.3, zorder=1)
    
    # Draw nodes - scale size based on number of nodes
    x_coords = [positions[node][0] for node in nodes]
    y_coords = [positions[node][1] for node in nodes]
    
    if node_colors is None:
        node_colors = ['skyblue'] * len(nodes)
    
    # Dynamic node size: smaller for larger graphs
    node_size = max(50, min(300, 10000 / len(nodes)))
    
    ax.scatter(x_coords, y_coords, c=node_colors, s=node_size, alpha=0.8, 
              edgecolors='black', linewidths=0.5, zorder=2)
    
    # Draw labels - smaller font for large graphs
    if node_labels is None:
        node_labels = {node: str(node) for node in nodes}
    
    # Dynamic font size
    font_size = max(4, min(8, 100 / math.sqrt(len(nodes))))
    
    for node in nodes:
        x, y = positions[node]
        label = node_labels.get(node, str(node))
        ax.text(x, y, label, fontsize=font_size, ha='center', va='center', zorder=3)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if filename:
        # Save at ultra-high DPI for zooming capability
        plt.savefig(filename, dpi=600, bbox_inches='tight')
        print(f"Graph saved to {filename} (high-res, zoomable)")
    
    if show:
        plt.show()
    else:
        plt.close()


def visualize_communities(graph: Graph, communities: List[List[Any]],
                         title: str = "Community Detection",
                         filename: str = None,
                         show: bool = True,
                         figsize: Tuple[int, int] = (40, 40)):
    """
    Visualize graph with communities highlighted in different colors.
    
    Args:
        graph (Graph): The graph to visualize
        communities (List): List of communities
        title (str): Plot title
        filename (str): If provided, save to this file
        show (bool): Whether to display the plot
        figsize (Tuple): Figure size
    
    Time Complexity: O(n + m)
    Space Complexity: O(n)
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
    except ImportError:
        print("Error: matplotlib is required for visualization")
        return
    
    # Assign colors to communities
    num_communities = len(communities)
    colors = cm.rainbow([i / num_communities for i in range(num_communities)])
    
    node_to_community = {}
    for comm_id, community in enumerate(communities):
        for node in community:
            node_to_community[node] = comm_id
    
    # Create color list for nodes
    node_colors = []
    for node in graph.get_nodes():
        comm_id = node_to_community.get(node, 0)
        color = colors[comm_id % num_communities]
        node_colors.append(color)
    
    # Compute layout
    positions = force_directed_layout(graph, seed=42)
    
    # Visualize
    visualize_graph(graph, positions, node_colors=node_colors, 
                   title=f"{title} ({num_communities} communities)",
                   filename=filename, show=show, figsize=figsize)


def visualize_centrality(graph: Graph, centrality: Dict[Any, float],
                        centrality_name: str = "Centrality",
                        filename: str = None,
                        show: bool = True,
                        figsize: Tuple[int, int] = (40, 40)):
    """
    Visualize graph with node sizes based on centrality scores.
    
    Args:
        graph (Graph): The graph to visualize
        centrality (Dict): Centrality scores for nodes
        centrality_name (str): Name of centrality measure
        filename (str): If provided, save to this file
        show (bool): Whether to display the plot
        figsize (Tuple): Figure size
    
    Time Complexity: O(n + m)
    Space Complexity: O(n)
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
    except ImportError:
        print("Error: matplotlib is required for visualization")
        return
    
    nodes = graph.get_nodes()
    
    if not nodes:
        return
    
    # Compute layout
    positions = force_directed_layout(graph, seed=42)
    
    # Normalize centrality for visualization
    max_centrality = max(centrality.values()) if centrality.values() else 1
    min_centrality = min(centrality.values()) if centrality.values() else 0
    
    if max_centrality == min_centrality:
        normalized = {node: 0.5 for node in nodes}
    else:
        normalized = {node: (centrality.get(node, 0) - min_centrality) / 
                     (max_centrality - min_centrality) for node in nodes}
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw edges - thinner for large graphs
    for u, v in graph.get_edges():
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        ax.plot([x1, x2], [y1, y2], 'gray', linewidth=0.2, alpha=0.2, zorder=1)
    
    # Dynamic sizing
    node_size_base = max(50, min(300, 10000 / len(nodes)))
    font_size = max(4, min(8, 100 / math.sqrt(len(nodes))))
    
    # Draw nodes with sizes based on centrality
    for node in nodes:
        x, y = positions[node]
        size = node_size_base + normalized[node] * node_size_base * 3  # 1x to 4x size range
        color_value = normalized[node]
        color = cm.Reds(0.3 + color_value * 0.7)  # Color from light to dark red
        
        ax.scatter([x], [y], s=size, c=[color], alpha=0.8,
                  edgecolors='black', linewidths=0.5, zorder=2)
        
        # Label
        ax.text(x, y, str(node), fontsize=font_size, ha='center', va='center', zorder=3)
    
    ax.set_title(f"{centrality_name} Visualization", fontsize=16, fontweight='bold')
    ax.axis('off')
    ax.set_aspect('equal')
    
    # Add colorbar
    sm = cm.ScalarMappable(cmap=cm.Reds, 
                          norm=plt.Normalize(vmin=min_centrality, vmax=max_centrality))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(centrality_name, rotation=270, labelpad=20)
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=600, bbox_inches='tight')
        print(f"Visualization saved to {filename} (high-res, zoomable)")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_degree_distribution(graph: Graph, filename: str = None, 
                            show: bool = True):
    """
    Plot the degree distribution of the graph.
    
    Args:
        graph (Graph): The graph to analyze
        filename (str): If provided, save to this file
        show (bool): Whether to display the plot
    
    Time Complexity: O(n) where n is nodes
    Space Complexity: O(n)
    """
    try:
        import matplotlib.pyplot as plt
        from collections import Counter
    except ImportError:
        print("Error: matplotlib is required for visualization")
        return
    
    # Calculate degrees
    degrees = [graph.degree(node) for node in graph.get_nodes()]
    
    if not degrees:
        print("Graph is empty")
        return
    
    # Count degree frequencies
    degree_counts = Counter(degrees)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    degrees_sorted = sorted(degree_counts.keys())
    counts = [degree_counts[d] for d in degrees_sorted]
    
    ax.bar(degrees_sorted, counts, color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Degree', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Degree Distribution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {filename}")
    
    if show:
        plt.show()
    else:
        plt.close()
