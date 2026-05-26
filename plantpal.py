from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import time

app = Flask(__name__)
CORS(app) 

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/plantpal.css')
def styles():
    return send_from_directory('.', 'plantpal.css')

# data structures

class MinHeap:
    def __init__(self):
        self.heap = []

    def _key(self, plant):
        return plant["days_until_care"]

    def _parent(self, i):
        return (i - 1) // 2

    def _left(self, i):
        return 2 * i + 1

    def _right(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _bubble_up(self, i):
        while i > 0:
            p = self._parent(i)
            if self._key(self.heap[p]) > self._key(self.heap[i]):
                self._swap(i, p)
                i = p
            else:
                break

    def _heapify_down(self, i):
        n = len(self.heap)
        while True:
            smallest = i
            l, r = self._left(i), self._right(i)
            if l < n and self._key(self.heap[l]) < self._key(self.heap[smallest]):
                smallest = l
            if r < n and self._key(self.heap[r]) < self._key(self.heap[smallest]):
                smallest = r
            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break

    def insert(self, plant):
        self.heap.append(plant)
        self._bubble_up(len(self.heap) - 1)

    def extract_min(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return min_val

    def peek(self):
        return self.heap[0] if self.heap else None

    def remove(self, plant_id):
        idx = next((i for i, p in enumerate(self.heap) if p["id"] == plant_id), -1)
        if idx == -1:
            return
        if idx == len(self.heap) - 1:
            self.heap.pop()
            return
        self.heap[idx] = self.heap.pop()
        self._bubble_up(idx)
        self._heapify_down(idx)

    def to_list(self):
        return list(self.heap)

    def size(self):
        return len(self.heap)


class Graph:
    def __init__(self):
        self.adj = {} 

    def add_node(self, node_id):
        if node_id not in self.adj:
            self.adj[node_id] = []

    def add_edge(self, a, b):
        self.add_node(a)
        self.add_node(b)
        if b not in self.adj[a]:
            self.adj[a].append(b)
        if a not in self.adj[b]:
            self.adj[b].append(a)

    def remove_node(self, node_id):
        self.adj.pop(node_id, None)
        for key in self.adj:
            self.adj[key] = [n for n in self.adj[key] if n != node_id]

    def bfs(self, start_id):
        if start_id not in self.adj:
            return []
        visited = {start_id}
        queue = [start_id]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self.adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def neighbors(self, node_id):
        return self.adj.get(node_id, [])

    def get_adj_list(self):
        return self.adj


heap = MinHeap()
graph = Graph()
plants = {}       
next_id = 1

COMPAT_RULES = [
    ("🌿", "🌴"), ("🌿", "🌸"), ("🌴", "🌾"), ("🌺", "🌸"),
    ("🌵", "🌾"), ("🍃", "🌿"), ("🌻", "🌺"), ("🌸", "🍃"),
    ("🌴", "🌺"), ("🌿", "🌻"), ("🌾", "🌸")
]

def compute_days(last_watered_ts, frequency):
    now = time.time()
    next_care = last_watered_ts + frequency * 86400
    return max(0, round((next_care - now) / 86400))

def build_plant(data, plant_id, last_watered=None):
    freq = data.get("frequency", 7)
    lw = last_watered or (time.time() - freq * 86400 * 0.5)
    return {
        "id": plant_id,
        "name": data["name"],
        "type": data.get("type", "Unknown species"),
        "location": data.get("location", "indoors"),
        "frequency": freq,
        "emoji": data.get("emoji", "🌿"),
        "last_watered": lw,
        "days_until_care": compute_days(lw, freq)
    }

def refresh_days(plant):
    """Recalculate days_until_care (called before any heap operation)"""
    plant["days_until_care"] = compute_days(plant["last_watered"], plant["frequency"])
    return plant

def add_companion_edges(plant):
    for a, b in COMPAT_RULES:
        if plant["emoji"] in (a, b):
            other_emoji = b if plant["emoji"] == a else a
            for p in plants.values():
                if p["id"] != plant["id"] and p["emoji"] == other_emoji:
                    graph.add_edge(plant["id"], p["id"])

# seed starter plants
def seed():
    global next_id
    starters = [
        {"name": "Monstera Mochi",  "type": "Monstera deliciosa",   "location": "living room", "frequency": 7,  "emoji": "🌿"},
        {"name": "Cactus Lil",      "type": "Cereus repandus",       "location": "windowsill",  "frequency": 14, "emoji": "🌵"},
        {"name": "Orchid Ophelia",  "type": "Phalaenopsis",           "location": "bedroom",     "frequency": 5,  "emoji": "🌸"},
        {"name": "Fern Fernanda",   "type": "Nephrolepis exaltata",  "location": "bathroom",    "frequency": 3,  "emoji": "🍃"},
        {"name": "Sunny",           "type": "Helianthus annuus",     "location": "balcony",     "frequency": 2,  "emoji": "🌻"},
    ]
    import random
    for s in starters:
        lw = time.time() - s["frequency"] * 86400 * (0.3 + random.random() * 0.9)
        plant = build_plant(s, next_id, last_watered=lw)
        plants[next_id] = plant
        heap.insert(plant)
        graph.add_node(next_id)
        add_companion_edges(plant)
        next_id += 1

seed()

# api routes

@app.route("/plants", methods=["GET"])
def get_plants():
    """Return all plants sorted by urgency (heap order)"""
    all_plants = []
    for p in plants.values():
        refresh_days(p)
        all_plants.append(p)
    all_plants.sort(key=lambda x: x["days_until_care"])
    return jsonify(all_plants)


@app.route("/plants", methods=["POST"])
def add_plant():
    """Add a new plant"""
    global next_id
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    plant = build_plant(data, next_id)
    plants[next_id] = plant
    heap.insert(plant)
    graph.add_node(next_id)
    add_companion_edges(plant)
    next_id += 1

    return jsonify(plant), 201


@app.route("/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    """Delete a plant"""
    if plant_id not in plants:
        return jsonify({"error": "plant not found"}), 404
    heap.remove(plant_id)
    graph.remove_node(plant_id)
    del plants[plant_id]
    return jsonify({"ok": True})


@app.route("/plants/<int:plant_id>/water", methods=["POST"])
def water_plant(plant_id):
    """Mark a plant as watered — removes from heap and re-inserts"""
    if plant_id not in plants:
        return jsonify({"error": "plant not found"}), 404
    plant = plants[plant_id]
    plant["last_watered"] = time.time()
    refresh_days(plant)
    heap.remove(plant_id)
    heap.insert(plant)
    return jsonify(plant)


@app.route("/heap", methods=["GET"])
def get_heap():
    """Return the raw heap array (for visualization)"""
    arr = []
    for p in heap.to_list():
        refresh_days(p)
        arr.append(p)
    return jsonify(arr)


@app.route("/graph", methods=["GET"])
def get_graph():
    """Return adjacency list"""
    return jsonify(graph.get_adj_list())


@app.route("/graph/bfs/<int:start_id>", methods=["GET"])
def bfs(start_id):
    """Run BFS from a given plant node"""
    if start_id not in plants:
        return jsonify({"error": "plant not found"}), 404
    order = graph.bfs(start_id)
    result = [plants[i] for i in order if i in plants]
    return jsonify({"order": order, "plants": result})


@app.route("/stats", methods=["GET"])
def get_stats():
    """Summary stats"""
    all_p = list(plants.values())
    for p in all_p:
        refresh_days(p)
    return jsonify({
        "total": len(all_p),
        "urgent": sum(1 for p in all_p if p["days_until_care"] == 0),
        "this_week": sum(1 for p in all_p if p["days_until_care"] <= 7),
        "healthy": sum(1 for p in all_p if p["days_until_care"] > 7),
    })


#  RUN

if __name__ == "__main__":
    print(" PlantPal backend running at http://localhost:5000")
    app.run(debug=True, port=5000)