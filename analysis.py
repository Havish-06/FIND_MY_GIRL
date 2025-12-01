import networkx as nx

# ===========================================================
# 1. DEGREE CENTRALITY
# ===========================================================
def compute_degree_centrality(G):
    """
    Degree Centrality:
    Measures how many direct connections a node has.
    Normalized by (N - 1).
    """
    centrality = {}
    N = len(G.nodes())
    for node in G.nodes():
        centrality[node] = G.degree[node] / (N - 1)
    return centrality


# ===========================================================
# 2. BETWEENNESS CENTRALITY
# ===========================================================
def compute_betweenness_centrality(G):
    """
    Betweenness Centrality:
    Measures how often a node lies on the shortest paths between other nodes.
    Uses Brandes' algorithm internally.
    """
    return nx.betweenness_centrality(G, normalized=True)


# ===========================================================
# 3. PAGE RANK
# ===========================================================
def compute_pagerank(G, damping=0.85):
    """
    PageRank:
    Measures influence of a node based on the influence of its neighbors.
    """
    return nx.pagerank(G, alpha=damping)


# ===========================================================
# 4. WRAPPER FUNCTION (OPTIONAL)
# ===========================================================
def compute_all_centralities(G):
    """
    Computes all three centrality measures and returns them
    in a single dictionary.
    """
    degree = compute_degree_centrality(G)
    between = compute_betweenness_centrality(G)
    pagerank = compute_pagerank(G)

    return {
        "degree": degree,
        "betweenness": between,
        "pagerank": pagerank
    }


# ===========================================================
# 5. DEMO CODE (REMOVE IF USING AS LIBRARY)
# ===========================================================
if __name__ == "__main__":
    # Example: small graph
    G = nx.karate_club_graph()

    centralities = compute_all_centralities(G)

    print("\n=== DEGREE CENTRALITY ===")
    print(centralities["degree"])

    print("\n=== BETWEENNESS CENTRALITY ===")
    print(centralities["betweenness"])

    print("\n=== PAGE RANK ===")
    print(centralities["pagerank"])
