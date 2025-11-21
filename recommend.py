import networkx as nx
import random
import math
from collections import deque, Counter
# from generate import RealisticSocialGraph  # Import moved to __main__

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
    
    # --- MODULAR FEATURE EXTRACTION (HOLME.PY STYLE) ---
    def jaccard_coefficient(self, user1, user2):
        """Calculate Jaccard coefficient between two users"""
        return list(nx.jaccard_coefficient(self.G, [(user1, user2)]))[0][2]
    
    def adamic_adar_score(self, user1, user2):
        """Calculate Adamic-Adar score using NetworkX"""
        return list(nx.adamic_adar_index(self.G, [(user1, user2)]))[0][2]
    
    def attribute_similarity(self, user1, user2):
        """Calculate attribute-based similarity (age, location, tags, affiliation)"""
        u1 = self.G.nodes[user1]
        u2 = self.G.nodes[user2]
        score = 0
        
        # Age similarity
        age_diff = abs(u1['age'] - u2['age'])
        score += max(0, 20 - age_diff) / 20
        
        # Affiliation match
        if u1.get('affiliation') == u2.get('affiliation'):
            score += 1
        
        # Tags overlap
        overlap = len(set(u1['tags']) & set(u2['tags']))
        score += overlap * 0.6
        
        # Location proximity
        dist = math.sqrt((u1['location']['x'] - u2['location']['x'])**2 + 
                        (u1['location']['y'] - u2['location']['y'])**2)
        score += max(0, (100 - dist) / 100)
        
        return score
    
    def score_candidate(self, user_id, candidate_id):
        """Calculate total score and feature breakdown for a candidate"""
        features = {}
        
        # Structural features
        features['mutual_friends'] = 2.5 * self.mutual_friends(user_id, candidate_id)
        features['jaccard'] = 1.0 * self.jaccard_coefficient(user_id, candidate_id)
        features['adamic_adar'] = 1.2 * self.adamic_adar_score(user_id, candidate_id)
        
        # Community feature
        same_comm = 1 if self.node_communities.get(user_id) == self.node_communities.get(candidate_id) else 0
        features['same_community'] = 1.5 * same_comm
        
        # Attribute similarity
        features['attribute_similarity'] = 1.5 * self.attribute_similarity(user_id, candidate_id)
        
        # PageRank boost
        features['pagerank_boost'] = 1.0 * (self.pagerank_scores.get(candidate_id, 0) * 10)
        
        total_score = sum(features.values())
        return total_score, features

    # --- 4. FULL FEATURE RECOMMENDER (OPTIMIZED & MODULAR) ---
    def recommend_friends_advanced(self, user_id, top_k=3, explain=False):
        print(f"\n--- 4. ADVANCED LINK PREDICTION FOR {self.G.nodes[user_id]['name']} ---")
        
        # Ensure prerequisites
        if not self.node_communities: self.detect_communities_label_prop()
        if not self.pagerank_scores: self.calculate_pagerank()
        
        target = self.G.nodes[user_id]
        
        # --- CANDIDATE GENERATION ---
        candidates_pool = self.get_candidates(user_id)
        
        print(f"-> Narrowed down from {len(self.G.nodes())} total users to {len(candidates_pool)} candidates (Friends-of-Friends with ≥1 mutual friend).")

        # --- SCORE ALL CANDIDATES ---
        scored_candidates = []
        
        for candidate_id in candidates_pool:
            total_score, features = self.score_candidate(user_id, candidate_id)
            
            scored_candidates.append({
                'id': candidate_id,
                'name': self.G.nodes[candidate_id]['name'],
                'score': total_score,
                'features': features,
                'profile': self.G.nodes[candidate_id]
            })

        # Sort by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # --- DISPLAY RESULTS ---
        print(f"\nUser Profile: {target['name']}, Age {target['age']}, {target.get('affiliation', 'N/A')}")
        print(f"Location: ({target['location']['x']}, {target['location']['y']}), Interests: {target['tags']}")
        print(f"\nTop {top_k} Recommendations:")
        
        if not scored_candidates:
            print("  No recommendations found (User has no friends-of-friends).")
        else:
            for i, rec in enumerate(scored_candidates[:top_k], 1):
                print(f"\n  #{i}: {rec['name']} (Total Score: {rec['score']:.2f})")
                
                if explain:
                    print(f"      Profile: Age {rec['profile']['age']}, {rec['profile'].get('affiliation', 'N/A')}")
                    print(f"      Tags: {rec['profile']['tags']}")
                    print(f"      Feature Breakdown:")
                    for feature, value in rec['features'].items():
                        print(f"        - {feature:25s}: {value:.3f}")
        
        return scored_candidates[:top_k]

if __name__ == "__main__":
    # Import here to avoid circular dependency
    import sys
    sys.path.append('..')
    from generate import RealisticSocialGraph
    
    gen = RealisticSocialGraph(n_users=100)
    G = gen.generate()
    
    analyzer = ManualSocialAnalyzer(G)
    
    # Test with explanation enabled
    print("\n" + "="*70)
    print("TESTING WITH DETAILED EXPLANATIONS")
    print("="*70)
    analyzer.recommend_friends_advanced(user_id=0, top_k=5, explain=True)