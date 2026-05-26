# 📦 FastBox Delivery System Simulator

A Python-based logistics simulator for a fictional delivery company **FastBox**. This program simulates one day of delivery operations — assigning packages to the nearest agents, calculating travel distances, and generating a detailed performance report.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **JSON Parsing** | Reads warehouse, agent, and package data from JSON files (supports multiple formats) |
| **Nearest Agent Assignment** | Assigns each package to the closest delivery agent using Euclidean distance |
| **Delivery Simulation** | Simulates agent travel: current position → warehouse → destination |
| **Report Generation** | Outputs `report.json` with per-agent stats and best performer |
| **Random Delivery Delays** | *(Bonus)* Simulates realistic random delays for each delivery |
| **ASCII Route Map** | *(Bonus)* Visualizes warehouse, agent, and destination positions on an ASCII grid |
| **Mid-Day Agent Join** | *(Bonus)* A new agent dynamically joins the fleet halfway through the day |
| **CSV Export** | *(Bonus)* Exports the top-performing agent's stats to `top_performer.csv` |

---

## 📁 Project Structure

```
Python Assignment -2026/
├── delivery_system.py                          # Main Python script
├── base_case.json                              # Sample input data
├── report.json                                 # Generated output report
├── top_performer.csv                           # Bonus: best agent CSV export
├── README.md                                   # This file
├── Python Assignment(Delivery System).pdf      # Assignment instructions
└── Python Assignment(Delivery System Test Cases)/
    ├── test_case_1.json
    ├── test_case_2.json
    ├── ...
    └── test_case_10.json
```

---

## ⚙️ How to Run

### Prerequisites
- Python 3.6 or higher

### Run with default input (base_case.json):
```bash
python delivery_system.py
```

### Run with a specific test case:
```bash
python delivery_system.py base_case.json
python delivery_system.py "Python Assignment(Delivery System Test Cases)/test_case_1.json"
python delivery_system.py "Python Assignment(Delivery System Test Cases)/test_case_5.json"
```

---

## 📊 Sample Output

### Report (report.json):
```json
{
  "A1": {"packages_delivered": 2, "total_distance": 121.21, "efficiency": 60.6},
  "A2": {"packages_delivered": 2, "total_distance": 79.21, "efficiency": 39.6},
  "A3": {"packages_delivered": 1, "total_distance": 14.14, "efficiency": 14.14},
  "best_agent": "A3"
}
```

### Terminal Output:
```
╔══════════════════════════════════════════════════════════╗
║         📦 FastBox Delivery System Simulator 📦         ║
╚══════════════════════════════════════════════════════════╝

📦 P1 → Agent A1: [5, 5] → W1[0, 0] → Dest[30, 40]  |  Distance: 57.07
📦 P2 → Agent A2: [60, 60] → W2[50, 75] → Dest[70, 90]  |  Distance: 43.03
...
🏆 BEST AGENT: A3 (Efficiency: 14.14 units/package)
```

---

## 🧮 Algorithm

1. **Parse** the JSON input file
2. **For each package** (in order):
   - Find the package's warehouse location
   - Calculate Euclidean distance from every agent to that warehouse
   - Assign the package to the **nearest agent**
   - Agent travels: `current_position → warehouse → destination`
   - Update the agent's position to the destination
3. **Calculate efficiency** = `total_distance / packages_delivered` for each agent
4. **Best agent** = the one with the **lowest efficiency** (least distance per package)
5. **Save** the report to `report.json`

### Euclidean Distance Formula:
```
distance = √((x₂ - x₁)² + (y₂ - y₁)²)
```

---

## 📋 Input JSON Format

The program supports two input formats:

### Format A (base_case.json):
```json
{
  "warehouses": [{"id": "W1", "location": [0, 0]}],
  "agents": [{"id": "A1", "location": [5, 5]}],
  "packages": [{"id": "P1", "warehouse_id": "W1", "destination": [30, 40]}]
}
```

### Format B (test cases):
```json
{
  "warehouses": {"W1": [0, 0]},
  "agents": {"A1": [5, 5]},
  "packages": [{"id": "P1", "warehouse": "W1", "destination": [30, 40]}]
}
```

---

## 👤 Author

**Mayuri Lokhande**

---
