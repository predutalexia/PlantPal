# PlantPal - Plant Care Tracker

PlantPal is a web application that helps you manage your plant collection by tracking watering schedules and visualizing plant compatibility. It was built as a final project for Advanced Data Structures, demonstrating real-world usage of a **min-heap** and a **graph with BFS traversal**.

---

## Project Structure

```
final project/
  index.html       — frontend (UI + data structures in JavaScript)
  plantpal.css     — all styles
  plantpal.py      — Python/Flask backend (serves the app)
  README.md        — this file
```

---

## How to Run

### Requirements
- Python 3.x
- Flask and flask-cors

### Install dependencies
```bash
pip install flask flask-cors
```

### Start the server
```bash
python plantpal.py
```

### Open the app
Go to **http://localhost:5000** in your browser.

> No other installation needed. The frontend is pure HTML/CSS/JS with no external frameworks.

---

## What the App Does

- **Add plants** with a name, species, location, watering frequency and emoji
- **Care queue** — shows which plant needs watering most urgently, always sorted by days remaining
- **Water a plant** — marks it as watered and reschedules it in the queue
- **Heap visualizer** — shows the internal min-heap tree structure and array representation in real time
- **Companion graph** — shows which plants are compatible with each other, with BFS traversal
- **localStorage** — your plants are saved in the browser and persist across page refreshes

---

## Data Structure 1 — Min-Heap

### What it is
A **min-heap** is a complete binary tree where every node's value is smaller than or equal to its children. The smallest element is always at the root, making it instantly accessible in O(1).

### How PlantPal uses it
Each plant is a node in the heap. Its **key** is `daysUntilCare` — the number of days until it needs to be watered. The plant with the fewest days is always at the root of the heap, which means PlantPal always knows the most urgent plant instantly.

When you water a plant:
1. The plant is **removed** from the heap
2. Its `lastWatered` date is updated to today
3. It is **re-inserted** with the new next care date
4. The heap reorganizes itself automatically

### Operations and complexity

| Operation | Complexity | Description |
|---|---|---|
| insert | O(log n) | add a plant, bubble up to correct position |
| extract-min | O(log n) | remove most urgent plant, heapify down |
| peek | O(1) | see most urgent plant without removing |
| remove | O(log n) | remove a specific plant by id |
| build heap | O(n) | build from existing array of plants |

### Implementation
The heap is implemented from scratch in JavaScript as a `MinHeap` class with:
- `insert(plant)` — appends and calls `_bubbleUp()`
- `extractMin()` — swaps root with last element, pops, calls `_heapifyDown()`
- `remove(id)` — finds by id, replaces with last element, bubbles up or down
- `toArray()` — returns a copy of the internal array for visualization

---

## Data Structure 2 — Graph with BFS

### What it is
An **undirected graph** stored as an **adjacency list**. Each plant is a node. An edge between two plants means they are compatible companions — they grow well together.

### How PlantPal uses it
When you add a plant, edges are automatically added based on two rules:
1. **Emoji compatibility** — predefined pairs of plant types that are botanically compatible
2. **Watering frequency** — plants with similar watering schedules (within 3 days) are auto-connected, since they likely share similar soil and light conditions

**BFS (Breadth-First Search)** is used to traverse the graph from any starting plant. It visits all direct companions first (level 1), then companions of companions (level 2), and so on — revealing the full network in order of closeness.

This is more useful than DFS for companion planting because you want to know your closest companions first, not the deepest chain.

### Operations and complexity

| Operation | Complexity | Description |
|---|---|---|
| addNode | O(1) | add a plant to the graph |
| addEdge | O(1) | add compatibility link between two plants |
| BFS traversal | O(V + E) | visit all reachable companions |
| neighbors lookup | O(degree) | find all companions of a plant |

### Implementation
The graph is implemented from scratch in JavaScript as a `Graph` class with:
- `addNode(id)` — adds a key to the adjacency Map
- `addEdge(a, b)` — adds b to a's list and a to b's list (undirected)
- `removeNode(id)` — deletes the node and cleans up all references
- `bfs(startId)` — standard BFS using a queue and visited set, returns ordered array of ids

---

## Data Persistence

Plants are saved to **localStorage** in the browser. Every time you add, water, or delete a plant, the full plant list is serialized to JSON and stored. On page load, saved plants are restored automatically. If no saved data exists, a set of preset plants is loaded as a starting point.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (no frameworks) |
| Backend | Python, Flask, flask-cors |
| Storage | localStorage (browser) |
| Visualization | HTML Canvas (graph), DOM (heap tree) |
