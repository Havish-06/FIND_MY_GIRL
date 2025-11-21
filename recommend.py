import networkx as nx
import random
import math
from collections import deque, Counter
from generate import RealisticSocialGraph

class ManualSocialAnalyzer:
    def __init__(self, graph):
        self.G = graph
        self.node_communities = {} 
        self.pagerank_scores = {}

    # --- 1. CONNECTIVITY ---
    def get_connected_components(self):
        print("\n--- 1. MANUAL CONNECTIVITY ---")
        visited = set()
        components = []
        for node in self.G.nodes():
            if node not in visited:
                current_component = set()
                queue = deque([node])
                visited.add(node)
                current_component.add(node)
                while queue:
                    curr = queue.popleft()
                    for neighbor in self.G.neighbors(curr):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            current_component.add(neighbor)
                            queue.append(neighbor)
                components.append(current_component)
        print(f"Found {len(components)} connected components.")
        return components

    # --- 2. PAGERANK ---
    def calculate_pagerank(self, iterations=20, damping=0.85):
        print("\n--- 2. MANUAL PAGERANK ---")
        nodes = list(self.G.nodes())
        N = len(nodes)
        scores = {node: 1.0 / N for node in nodes}
        
        for i in range(iterations):
            new_scores = {}
            for node in nodes:
                incoming_score = 0
                for neighbor in self.G.neighbors(node):
                    neighbor_degree = len(list(self.G.neighbors(neighbor)))
                    if neighbor_degree > 0:
                        incoming_score += scores[neighbor] / neighbor_degree
                new_scores[node] = ((1 - damping) / N) + (damping * incoming_score)
            scores = new_scores

        self.pagerank_scores = scores
        top_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        print("Top 3 Influencers:")
        for rank, (node, score) in enumerate(top_nodes, 1):
            print(f"  #{rank}: {self.G.nodes[node]['name']} (Score: {score:.5f})")
        return scores

    # --- 3. COMMUNITY DETECTION ---
    def detect_communities_label_prop(self, max_iter=15):
        print("\n--- 3. MANUAL COMMUNITY DETECTION ---")
        nodes = list(self.G.nodes())
        labels = {node: node for node in nodes}
        
        for i in range(max_iter):
            changes = 0
            random.shuffle(nodes)
            for node in nodes:
                neighbors = list(self.G.neighbors(node))
                if not neighbors: continue
                neighbor_labels = [labels[n] for n in neighbors]
                most_common = Counter(neighbor_labels).most_common(1)[0][0]
                if labels[node] != most_common:
                    labels[node] = most_common
                    changes += 1
            if changes == 0: break
        
        self.node_communities = labels
        print("Community detection converged.")
        return labels

    # --- HELPER FUNCTIONS FOR CANDIDATE FILTERING ---
    def mutual_friends(self, user1, user2):
        """Count mutual friends between two users"""
        friends1 = set(self.G.neighbors(user1))
        friends2 = set(self.G.neighbors(user2))
        return len(friends1.intersection(friends2))
    
    def get_candidates(self, user):
        """Get candidate recommendations using friends-of-friends approach"""
        neighbors = set(self.G.neighbors(user))

        # Friends-of-friends
        fof = set()
        for f in neighbors:
            fof.update(self.G.neighbors(f))

        # Remove direct friends + self
        fof -= neighbors
        fof.discard(user)

        # Require at least 1 mutual friend
        final = [x for x in fof if self.mutual_friends(user, x) >= 1]
        return final

    # --- 4. FULL FEATURE RECOMMENDER (OPTIMIZED) ---
    def recommend_friends_advanced(self, user_id):
        print(f"\n--- 4. ADVANCED LINK PREDICTION FOR {self.G.nodes[user_id]['name']} ---")
        
        # Ensure prerequisites
        if not self.node_communities: self.detect_communities_label_prop()
        if not self.pagerank_scores: self.calculate_pagerank()
        
        target = self.G.nodes[user_id]
        target_friends = set(self.G.neighbors(user_id))
        
        # --- OPTIMIZATION: CANDIDATE GENERATION (Friends-of-Friends) ---
        # Use the cleaner get_candidates function
        candidates_pool = self.get_candidates(user_id)
        
        print(f"-> Narrowed down from {len(self.G.nodes())} total users to {len(candidates_pool)} candidates (Friends-of-Friends with ≥1 mutual friend).")

        candidates = []
        
        for candidate_id in candidates_pool:
            cand = self.G.nodes[candidate_id]
            candidate_friends = set(self.G.neighbors(candidate_id))
            
            # 1. Structural (Adamic-Adar)
            common_neighbors = target_friends.intersection(candidate_friends)
            adamic = 0
            for common in common_neighbors:
                deg = len(list(self.G.neighbors(common)))
                if deg > 1: adamic += 1 / math.log(deg)

            # 2. Community
            same_comm = 1 if self.node_communities.get(user_id) == self.node_communities.get(candidate_id) else 0

            # 3. Content (Tags)
            t_tags = set(target['tags'])
            c_tags = set(cand['tags'])
            tag_match = len(t_tags.intersection(c_tags))

            # 4. Preferential Attachment
            pref_attach = len(target_friends) * len(candidate_friends)

            # 5. PageRank Boost
            pr_boost = self.pagerank_scores.get(candidate_id, 0) * 10

            # 6. Age Similarity
            age_diff = abs(target['age'] - cand['age'])
            age_score = 1.0 / (1.0 + age_diff)

            # 7. Geographic Proximity
            dist = math.sqrt((target['location']['x'] - cand['location']['x'])**2 + 
                             (target['location']['y'] - cand['location']['y'])**2)
            geo_score = 1.0 / (1.0 + (dist * 0.1))

            # --- WEIGHTED FORMULA ---
            total_score = (
                (adamic * 1.5) +        # Structural
                (same_comm * 2.0) +     # Community
                (tag_match * 1.0) +     # Interests
                (age_score * 0.8) +     # Demographics
                (geo_score * 0.8) +     # Location
                (pr_boost * 1.0) +      # Status
                (pref_attach * 0.001)   # Degree
            )

            candidates.append({
                'name': cand['name'],
                'score': total_score,
                'reasons': {
                    'Comm': bool(same_comm),
                    'Tags': tag_match,
                    'AgeDiff': age_diff,
                    'Dist': round(dist, 1)
                }
            })

        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"User Profile: Age {target['age']}, Loc ({target['location']['x']}, {target['location']['y']})")
        print("Top 3 Recommendations:")
        if not candidates:
            print("  No recommendations found (User has no friends-of-friends).")
        for i, res in enumerate(candidates[:3], 1):
            print(f"  #{i}: {res['name']} (Score: {res['score']:.2f})")
            print(f"      Stats: {res['reasons']}")

if __name__ == "__main__":
    gen = RealisticSocialGraph(n_users=100)
    G = gen.generate()
    
    analyzer = ManualSocialAnalyzer(G)
    analyzer.recommend_friends_advanced(user_id=0)