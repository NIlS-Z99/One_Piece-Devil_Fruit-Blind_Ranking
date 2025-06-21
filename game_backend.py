
import json
import random
import numpy as np

DEVIL_FRUITS_FILE = 'devil_fruits.json'
PLAYER_SCORES_FILE = 'player_scores.json'

def load_json(filename, default):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

class GameBackend:
    def __init__(self):
        self.fruits = load_json(DEVIL_FRUITS_FILE, [])
        self.scores = load_json(PLAYER_SCORES_FILE, {})
        self.current_fruits = []
        self.last_score = 0
        self.player_name = ""

    def start_new_round(self, player_name):
        self.player_name = player_name
        probs = [1/(fruit["times_picked"]+1) for fruit in self.fruits]
        probs = [prob/sum(probs) for prob in probs] 
        self.current_fruits = np.random.choice(self.fruits, 10, replace=False, p=probs)

    def get_random_fruit(self):
        pool = [f for f in self.current_fruits if not f.get("used")]
        if not pool: return None
        fruit = random.choice(pool)
        fruit["used"] = True
        return fruit

    def finish_round(self, player_ranking):
        # Calculate average ranking for each fruit used in this round
        ranked_fruits_with_avg = []
        for fruit in player_ranking:
            avg = fruit["sum_ranks"] / max(fruit["times_picked"], 1)
            ranked_fruits_with_avg.append((fruit, avg))

        # Update stats for each fruit
        for i, fruit in enumerate(player_ranking):
            fruit["sum_ranks"] += i + 1
            fruit["times_picked"] += 1
            fruit.pop("used")

        save_json(DEVIL_FRUITS_FILE, self.fruits)

        # Sort by average rank to get actual best ranking
        sorted_by_avg = sorted(ranked_fruits_with_avg, key=lambda x: x[1])
        avg_ranking = [fruit for fruit, _ in sorted_by_avg]

        # Compute error (difference between player rank and avg rank)
        score = 0
        for i, fruit in enumerate(player_ranking):
            actual_rank = avg_ranking.index(fruit)
            score += abs(actual_rank - i)

        self.last_score = score

        # Save player score
        best = self.scores.get(self.player_name, float("inf"))
        if score < best:
            self.scores[self.player_name] = score
        save_json(PLAYER_SCORES_FILE, self.scores)

        return ranked_fruits_with_avg
    
    def get_top_scores(self, top_n=10):
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1])
        return sorted_scores[:top_n]