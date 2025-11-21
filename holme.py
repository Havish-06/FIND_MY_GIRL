import networkx as nx
import random
import matplotlib.pyplot as plt
from networkx.algorithms import community

# =====================================================================
# 1. YOUR GRAPH GENERATOR (UNTOUCHED)
# =====================================================================

class RealisticSocialGraph:
    def __init__(self, n_users=200):
        self.n = n_users
        self.G = None
        self.affiliations = ["University A", "University B", "Tech Corp", "Startup Inc", "Freelance", "Retired"]
        self.interests = ["Tech", "Music", "Hiking", "Gaming", "Cooking", "Sci-Fi", "Politics"]

    def generate(self):
        print(f"1. Generating Holme-Kim Topology (n={self.n})...")
        self.G = nx.powerlaw_cluster_graph(n=self.n, m=2, p=0.5)
        
        print("2. Detecting Structural Communities...")
        communities = list(community.greedy_modularity_communities(self.G))
        print(f"   -> Found {len(communities)} structural communities.")

        for comm_idx, community_nodes in enumerate(communities):
            primary_affil = self.affiliations[comm_idx % len(self.affiliations)]
            primary_interest = self.interests[comm_idx % len(self.interests)]

            target_age = random.choice([20, 30, 45, 60])
            center_x = random.uniform(10, 90)
            center_y = random.uniform(10, 90)

            for node in community_nodes:
                if random.random() < 0.8:
                    assigned_affil = primary_affil
                    assigned_tags = [primary_interest] + random.sample(self.interests, k=random.randint(1, 2))
                    assigned_age = int(random.gauss(target_age, 5))
                    assigned_age = max(18, min(65, assigned_age))
                    loc_x = random.gauss(center_x, 10)
                    loc_y = random.gauss(center_y, 10)
                else:
                    assigned_affil = random.choice(self.affiliations)
                    assigned_tags = random.sample(self.interests, k=random.randint(2, 3))
                    assigned_age = random.randint(18, 65)
                    loc_x = random.uniform(0, 100)
                    loc_y = random.uniform(0, 100)

                loc_x = max(0, min(100, loc_x))
                loc_y = max(0, min(100, loc_y))
                assigned_tags = list(set(assigned_tags))

                self.G.nodes[node]["affiliation"] = assigned_affil
                self.G.nodes[node]["tags"] = assigned_tags
                self.G.nodes[node]["age"] = assigned_age
                self.G.nodes[node]["location"] = {"x": round(loc_x, 2), "y": round(loc_y, 2)}
                self.G.nodes[node]["community"] = comm_idx

        print("3. Graph generated with realistic homophily.")
        return self.G




# =====================================================================
# 2. FRIEND RECOMMENDATION ENGINE
# =====================================================================

# ------------------------------
# Structural Features
# ------------------------------
def mutual_friends(G, u, v):
    return len(set(G.neighbors(u)) & set(G.neighbors(v)))

def jaccard(G, u, v):
    return list(nx.jaccard_coefficient(G, [(u, v)]))[0][2]

def adamic_adar(G, u, v):
    return list(nx.adamic_adar_index(G, [(u, v)]))[0][2]

def same_community(G, u, v):
    return 1 if G.nodes[u]["community"] == G.nodes[v]["community"] else 0


# ------------------------------
# Attribute Similarity
# ------------------------------
def attribute_similarity(G, u, v):
    score = 0
    
    # Age similarity
    age_diff = abs(G.nodes[u]["age"] - G.nodes[v]["age"])
    score += max(0, 20 - age_diff) / 20
    
    # Affiliation match
    score += 1 if G.nodes[u]["affiliation"] == G.nodes[v]["affiliation"] else 0
    
    # Tags overlap
    overlap = len(set(G.nodes[u]["tags"]) & set(G.nodes[v]["tags"]))
    score += overlap * 0.6

    # Location proximity
    ux, uy = G.nodes[u]["location"]["x"], G.nodes[u]["location"]["y"]
    vx, vy = G.nodes[v]["location"]["x"], G.nodes[v]["location"]["y"]
    dist = ((ux - vx)**2 + (uy - vy)**2)**0.5
    score += max(0, (100 - dist) / 100)

    return score



# ------------------------------
# Candidate Filtering
# ------------------------------
def get_candidates(G, user):
    neighbors = set(G.neighbors(user))

    # Friends-of-friends
    fof = set()
    for f in neighbors:
        fof.update(G.neighbors(f))

    # Remove direct friends + self
    fof -= neighbors
    fof.discard(user)

    # Require at least 1 mutual friend
    final = [x for x in fof if mutual_friends(G, user, x) >= 1]
    return final



# ------------------------------
# Scoring Function
# ------------------------------
def score_user(G, u, v):
    features = {}

    features["mutual_friends"] = 2.5 * mutual_friends(G, u, v)
    features["jaccard"] = 1.0 * jaccard(G, u, v)
    features["adamic_adar"] = 1.2 * adamic_adar(G, u, v)
    features["same_community"] = 1.5 * same_community(G, u, v)
    features["attribute_similarity"] = 1.5 * attribute_similarity(G, u, v)

    total = sum(features.values())
    return total, features



# ------------------------------
# Main Recommendation Function
# ------------------------------
def recommend(G, user, top_k=5):
    candidates = get_candidates(G, user)

    scored = []
    for cand in candidates:
        total, feat = score_user(G, user, cand)
        scored.append((cand, total, feat))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]



# =====================================================================
# 3. EXPLANATION + VISUALIZATION
# =====================================================================
def explain_recommendations(G, user, recs):
    print("\n====== USER PROFILE ======")
    print(f"User {user}")
    print(G.nodes[user])

    print("\n====== RECOMMENDATIONS ======")
    for cand, total, feats in recs:
        print(f"\n-> Recommend {cand} (Score: {total:.3f})")
        print(f"Attributes: {G.nodes[cand]}")
        for k, v in feats.items():
            print(f"   {k:20s}: {v:.3f}")
    print()


def visualize(G, user, recs):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 10))

    colors = [G.nodes[n]["community"] for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=40, node_color=colors, cmap=plt.cm.tab20, alpha=0.7)
    nx.draw_networkx_edges(G, pos, alpha=0.2)

    rec_nodes = [r[0] for r in recs]

    nx.draw_networkx_nodes(G, pos, nodelist=[user], node_color="red", node_size=300)
    nx.draw_networkx_nodes(G, pos, nodelist=rec_nodes, node_color="green", node_size=200)

    plt.title(f"User {user} (red) with Recommendations (green)")
    plt.axis("off")
    plt.show()



# =====================================================================
# 4. RUN EVERYTHING
# =====================================================================

if __name__ == "__main__":
    generator = RealisticSocialGraph(n_users=150)
    G = generator.generate()

    user = 0
    recs = recommend(G, user, top_k=6)

    explain_recommendations(G, user, recs)
    visualize(G, user, recs)
