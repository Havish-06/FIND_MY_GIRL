import networkx as nx
import random
import matplotlib.pyplot as plt

class RealisticSocialGraph:
    def __init__(self, n_users=200):
        self.n = n_users
        self.G = None
        # The "Universe" of possible data
        self.affiliations = ["University A", "University B", "Tech Corp", "Startup Inc", "Freelance", "Retired"]
        self.interests = ["Tech", "Music", "Hiking", "Gaming", "Cooking", "Sci-Fi", "Politics"]

    def generate(self):
        print(f"1. Generating Holme-Kim Topology (n={self.n})...")
        # Step A: Create the Structure (Edges)
        # m=2: Each new node attaches to 2 existing nodes
        # p=0.5: 50% chance of forming a triangle (High Clustering)
        self.G = nx.powerlaw_cluster_graph(n=self.n, m=2, p=0.5)
        
        # Step B: Detect Communities (To fake the Homophily)
        # We find the structural clusters first so we can give them meaning
        print("2. Detecting Structural Communities to inject Homophily...")
        # distinct communities identified by the algorithm
        communities = list(nx.community.greedy_modularity_communities(self.G))
        
        print(f"   -> Found {len(communities)} structural communities.")

        # Step C: Assign Attributes based on Community
        for comm_idx, community in enumerate(communities):
            # Pick a "Theme" for this community
            # e.g. This group is mostly "University A" people who like "Tech"
            primary_affil = self.affiliations[comm_idx % len(self.affiliations)]
            primary_interest = self.interests[comm_idx % len(self.interests)]
            
            for node in community:
                # --- THE "REALISM" LOGIC (The Affiliation Hack) ---
                # 80% chance to fit the community theme (Homophily)
                # 20% chance to be random (Noise/Reality)
                if random.random() < 0.8:
                    assigned_affil = primary_affil
                    # Make sure the primary interest is included
                    # We take the primary + 1 or 2 random extras
                    assigned_tags = [primary_interest] + random.sample(self.interests, k=random.randint(1, 2))
                else:
                    # Total random assignment for the "Outsiders"
                    assigned_affil = random.choice(self.affiliations)
                    assigned_tags = random.sample(self.interests, k=random.randint(2, 3))
                
                # Cleanup: Remove duplicates in tags (e.g. ['Tech', 'Tech'])
                assigned_tags = list(set(assigned_tags))
                
                # --- ASSIGN ALL ATTRIBUTES TO NODE ---
                self.G.nodes[node]['id'] = node
                self.G.nodes[node]['name'] = f"User_{node}"
                self.G.nodes[node]['age'] = random.randint(18, 65)
                self.G.nodes[node]['affiliation'] = assigned_affil
                self.G.nodes[node]['tags'] = assigned_tags
                self.G.nodes[node]['location'] = {
                    'x': round(random.uniform(0, 100), 2),
                    'y': round(random.uniform(0, 100), 2)
                }
                # Store the 'ground truth' community for verification/debugging
                self.G.nodes[node]['ground_truth_community'] = comm_idx

        print("3. Graph Populated with Logic-Driven Attributes.")
        return self.G

    def visualize_sample(self):
        """Simple visualization to check if it worked"""
        if not self.G:
            print("Graph not generated yet.")
            return

        # Draw the graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(self.G, seed=42)
        
        # Color by "Ground Truth" community to see the clusters
        colors = [self.G.nodes[n]['ground_truth_community'] for n in self.G.nodes()]
        
        nx.draw_networkx_nodes(self.G, pos, node_size=50, node_color=colors, cmap=plt.cm.tab20, alpha=0.8)
        nx.draw_networkx_edges(self.G, pos, alpha=0.3)
        plt.title(f"Holme-Kim Graph ({self.n} nodes) with Homophily Injection")
        plt.axis('off')
        plt.show()

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Initialize
    generator = RealisticSocialGraph(n_users=150)
    
    # 2. Run the Generation
    G = generator.generate()

    # 3. Verify the "Affiliation Hack"
    # Let's pick 3 random nodes from Community 0 and see if they share attributes
    print("\n--- VERIFYING HOMOPHILY IN COMMUNITY 0 ---")
    
    # Find nodes in community 0
    nodes_in_c0 = [n for n in G.nodes() if G.nodes[n]['ground_truth_community'] == 0]
    
    # Print the first 5
    for node in nodes_in_c0[:5]:
        print(f"User {node}: Works at '{G.nodes[node]['affiliation']}' | Likes {G.nodes[node]['tags']}")
    
    print("\n(Notice how most of them share the same workplace or interest tag?)")

    # 4. Visualize
    generator.visualize_sample()