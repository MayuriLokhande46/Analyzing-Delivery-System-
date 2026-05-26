"""
=============================================================================
 FastBox Delivery System Simulator
 Python Assignment - 2026
=============================================================================
 Description:
   Simulates one day of delivery operations for FastBox company.
   - Reads warehouse, agent, and package data from a JSON file.
   - Assigns each package to the nearest delivery agent.
   - Simulates the delivery process and tracks distances.
   - Generates a detailed performance report (report.json).

 Usage:
   python delivery_system.py                    → Uses base_case.json
   python delivery_system.py test_case_1.json   → Uses specified file

 Bonus Features Included:
   ✓ Random delivery delays
   ✓ ASCII route visualization
   ✓ New agent joining mid-day
   ✓ Top performer CSV export
=============================================================================
"""

import json
import sys
import math
import random
import csv
import os

# ─────────────────────────────────────────────
# Seed random for reproducible delay simulation
# ─────────────────────────────────────────────
random.seed(42)


# =============================================================================
# SECTION 1: UTILITY FUNCTIONS
# =============================================================================

def euclidean_distance(point1, point2):
    """
    Calculate the Euclidean (straight-line) distance between two 2D points.

    Formula: √((x2 - x1)² + (y2 - y1)²)

    Args:
        point1: [x, y] coordinates of first point
        point2: [x, y] coordinates of second point

    Returns:
        float: The Euclidean distance between the two points
    """
    dx = point2[0] - point1[0]  # Difference in x-coordinates
    dy = point2[1] - point1[1]  # Difference in y-coordinates
    return math.sqrt(dx * dx + dy * dy)


# =============================================================================
# SECTION 2: JSON PARSING (Handles BOTH input formats)
# =============================================================================

def load_data(filepath):
    """
    Load and parse the JSON input file.

    Handles two formats:
      Format A (base_case.json): arrays of objects with 'id' and 'location'
      Format B (test cases):     dictionaries mapping id → [x, y]

    Args:
        filepath: Path to the JSON input file

    Returns:
        tuple: (warehouses_dict, agents_dict, packages_list)
    """
    # Step 1: Open and read the JSON file
    with open(filepath, 'r') as file:
        data = json.load(file)

    # Step 2: Parse warehouses — handle both formats
    warehouses = {}
    if isinstance(data["warehouses"], list):
        # Format A: [{"id": "W1", "location": [0, 0]}, ...]
        for warehouse in data["warehouses"]:
            warehouses[warehouse["id"]] = warehouse["location"]
    elif isinstance(data["warehouses"], dict):
        # Format B: {"W1": [0, 0], "W2": [50, 75], ...}
        warehouses = dict(data["warehouses"])  # Make a copy

    # Step 3: Parse agents — handle both formats
    agents = {}
    if isinstance(data["agents"], list):
        # Format A: [{"id": "A1", "location": [5, 5]}, ...]
        for agent in data["agents"]:
            agents[agent["id"]] = agent["location"]
    elif isinstance(data["agents"], dict):
        # Format B: {"A1": [5, 5], "A2": [60, 60], ...}
        agents = dict(data["agents"])  # Make a copy

    # Step 4: Parse packages — handle 'warehouse' vs 'warehouse_id' key
    packages = []
    for pkg in data["packages"]:
        package = {
            "id": pkg["id"],
            # Try 'warehouse' first, then fallback to 'warehouse_id'
            "warehouse": pkg.get("warehouse", pkg.get("warehouse_id")),
            "destination": pkg["destination"]
        }
        packages.append(package)

    print(f"✅ Data loaded successfully from: {filepath}")
    print(f"   📦 Warehouses: {len(warehouses)} | 🚴 Agents: {len(agents)} | 📬 Packages: {len(packages)}")
    print()

    return warehouses, agents, packages


# =============================================================================
# SECTION 3: NEAREST AGENT ASSIGNMENT
# =============================================================================

def find_nearest_agent(warehouse_location, agent_positions):
    """
    Find the agent closest to a given warehouse using Euclidean distance.

    Args:
        warehouse_location: [x, y] of the warehouse
        agent_positions:    dict of {agent_id: [x, y]} current positions

    Returns:
        str: ID of the nearest agent
    """
    nearest_agent = None
    min_distance = float('inf')  # Start with infinity

    for agent_id, agent_pos in agent_positions.items():
        # Calculate distance from this agent to the warehouse
        distance = euclidean_distance(agent_pos, warehouse_location)

        # Update if this agent is closer
        if distance < min_distance:
            min_distance = distance
            nearest_agent = agent_id

    return nearest_agent


# =============================================================================
# SECTION 4: DELIVERY SIMULATION
# =============================================================================

def simulate_deliveries(warehouses, agents, packages):
    """
    Simulate the full day of deliveries.

    For each package (in order):
      1. Find the nearest agent to the package's warehouse
      2. Agent travels: current_position → warehouse (pickup)
      3. Agent travels: warehouse → destination (delivery)
      4. Update agent's position to the destination
      5. Track total distance and delivery count

    Args:
        warehouses: dict {warehouse_id: [x, y]}
        agents:     dict {agent_id: [x, y]}
        packages:   list of package dicts

    Returns:
        tuple: (agent_stats, delivery_log, delays)
    """
    # ── Initialize agent positions (copy so we don't modify original) ──
    agent_positions = {}
    for agent_id, pos in agents.items():
        agent_positions[agent_id] = list(pos)  # Copy the position

    # ── Initialize stats for each agent ──
    agent_stats = {}
    for agent_id in agents:
        agent_stats[agent_id] = {
            "packages_delivered": 0,
            "total_distance": 0.0,
            "packages_list": []  # Track which packages each agent delivered
        }

    # ── Delivery log for visualization ──
    delivery_log = []  # Stores each delivery step for ASCII viz
    delays = []        # Stores random delay info (bonus)

    # ── BONUS: New agent joining mid-day ──
    # A new agent "A_NEW" joins after half the packages are processed
    midpoint = len(packages) // 2
    new_agent_added = False

    print("=" * 60)
    print("🚚 DELIVERY SIMULATION STARTED")
    print("=" * 60)

    # ── Process each package one by one ──
    for index, package in enumerate(packages):
        pkg_id = package["id"]
        warehouse_id = package["warehouse"]
        destination = package["destination"]

        # Get warehouse location
        warehouse_location = warehouses[warehouse_id]

        # ── BONUS: Add new agent mid-day ──
        if index == midpoint and not new_agent_added:
            # New agent joins at the center of the grid
            all_x = [pos[0] for pos in agent_positions.values()]
            all_y = [pos[1] for pos in agent_positions.values()]
            center_x = sum(all_x) // len(all_x)
            center_y = sum(all_y) // len(all_y)
            new_agent_id = "A_NEW"
            agent_positions[new_agent_id] = [center_x, center_y]
            agent_stats[new_agent_id] = {
                "packages_delivered": 0,
                "total_distance": 0.0,
                "packages_list": []
            }
            new_agent_added = True
            print(f"\n🆕 NEW AGENT '{new_agent_id}' joined mid-day at position [{center_x}, {center_y}]!\n")

        # ── Step 1: Find nearest agent to the warehouse ──
        nearest_agent = find_nearest_agent(warehouse_location, agent_positions)

        # ── Step 2: Calculate distance — Agent → Warehouse (pickup) ──
        dist_to_warehouse = euclidean_distance(
            agent_positions[nearest_agent], warehouse_location
        )

        # ── Step 3: Calculate distance — Warehouse → Destination (delivery) ──
        dist_to_destination = euclidean_distance(
            warehouse_location, destination
        )

        # ── Step 4: Total distance for this delivery ──
        total_trip_distance = dist_to_warehouse + dist_to_destination

        # ── BONUS: Random delivery delay ──
        delay_minutes = random.randint(0, 30)  # 0 to 30 minute random delay
        delays.append({
            "package": pkg_id,
            "agent": nearest_agent,
            "delay_minutes": delay_minutes
        })

        # ── Step 5: Log the delivery details ──
        delivery_log.append({
            "package": pkg_id,
            "agent": nearest_agent,
            "agent_start": list(agent_positions[nearest_agent]),
            "warehouse": warehouse_id,
            "warehouse_pos": list(warehouse_location),
            "destination": list(destination),
            "dist_to_warehouse": round(dist_to_warehouse, 2),
            "dist_to_destination": round(dist_to_destination, 2),
            "total_distance": round(total_trip_distance, 2),
            "delay_minutes": delay_minutes
        })

        # ── Step 6: Update agent stats ──
        agent_stats[nearest_agent]["packages_delivered"] += 1
        agent_stats[nearest_agent]["total_distance"] += total_trip_distance
        agent_stats[nearest_agent]["packages_list"].append(pkg_id)

        # ── Step 7: Update agent's current position to the destination ──
        agent_positions[nearest_agent] = list(destination)

        # ── Print delivery info ──
        delay_str = f" (⏱️  +{delay_minutes}min delay)" if delay_minutes > 0 else ""
        print(f"  📦 {pkg_id} → Agent {nearest_agent}: "
              f"[{delivery_log[-1]['agent_start']}] → "
              f"{warehouse_id}{warehouse_location} → "
              f"Dest{destination}  |  "
              f"Distance: {total_trip_distance:.2f}{delay_str}")

    print()
    print("=" * 60)
    print("✅ ALL DELIVERIES COMPLETED!")
    print("=" * 60)
    print()

    return agent_stats, delivery_log, delays


# =============================================================================
# SECTION 5: REPORT GENERATION
# =============================================================================

def generate_report(agent_stats):
    """
    Generate the final delivery report.

    Calculates efficiency (distance per package) for each agent.
    Identifies the best agent (lowest efficiency = most efficient).

    Args:
        agent_stats: dict of agent performance data

    Returns:
        dict: The complete report ready to be saved as JSON
    """
    report = {}

    # ── Calculate efficiency for each agent ──
    best_agent = None
    best_efficiency = float('inf')

    for agent_id, stats in agent_stats.items():
        delivered = stats["packages_delivered"]
        distance = round(stats["total_distance"], 2)

        if delivered > 0:
            # Efficiency = total distance / packages delivered
            # Lower is better (less distance per package)
            efficiency = round(distance / delivered, 2)
        else:
            # Agent delivered nothing — no efficiency to calculate
            efficiency = 0.0

        report[agent_id] = {
            "packages_delivered": delivered,
            "total_distance": distance,
            "efficiency": efficiency
        }

        # Track best agent (lowest efficiency, must have delivered at least 1)
        if delivered > 0 and efficiency < best_efficiency:
            best_efficiency = efficiency
            best_agent = agent_id

    # ── Add best agent to report ──
    report["best_agent"] = best_agent

    return report


def save_report(report, filepath="report.json"):
    """
    Save the report dictionary to a JSON file.

    Args:
        report:   The report dictionary
        filepath: Output file path (default: report.json)
    """
    with open(filepath, 'w') as file:
        json.dump(report, file, indent=2)

    print(f"📄 Report saved to: {filepath}")


# =============================================================================
# SECTION 6: BONUS — ASCII ROUTE VISUALIZATION
# =============================================================================

def visualize_routes_ascii(warehouses, agents, delivery_log):
    """
    BONUS: Display an ASCII grid showing warehouses, agents, and delivery routes.

    Legend:
      W = Warehouse    A = Agent (starting)
      * = Destination   . = Route path

    Args:
        warehouses:    dict of warehouse locations
        agents:        dict of agent starting locations
        delivery_log:  list of delivery events
    """
    print("\n" + "=" * 60)
    print("🗺️  ASCII ROUTE MAP")
    print("=" * 60)

    # ── Determine grid size from all coordinates ──
    all_x = []
    all_y = []
    for pos in warehouses.values():
        all_x.append(pos[0])
        all_y.append(pos[1])
    for pos in agents.values():
        all_x.append(pos[0])
        all_y.append(pos[1])
    for entry in delivery_log:
        all_x.append(entry["destination"][0])
        all_y.append(entry["destination"][1])

    # Scale down to fit in terminal (max 50x25 grid)
    max_x = max(all_x) + 1
    max_y = max(all_y) + 1
    scale_x = max(1, max_x // 50)
    scale_y = max(1, max_y // 25)

    grid_w = min(max_x // scale_x + 2, 52)
    grid_h = min(max_y // scale_y + 2, 27)

    # ── Create empty grid ──
    grid = [['·' for _ in range(grid_w)] for _ in range(grid_h)]

    # ── Plot delivery destinations ──
    for entry in delivery_log:
        dx = min(entry["destination"][0] // scale_x, grid_w - 1)
        dy = min(entry["destination"][1] // scale_y, grid_h - 1)
        grid[dy][dx] = '✦'

    # ── Plot warehouses ──
    for wid, pos in warehouses.items():
        wx = min(pos[0] // scale_x, grid_w - 1)
        wy = min(pos[1] // scale_y, grid_h - 1)
        grid[wy][wx] = 'W'

    # ── Plot agent starting positions ──
    for aid, pos in agents.items():
        ax = min(pos[0] // scale_x, grid_w - 1)
        ay = min(pos[1] // scale_y, grid_h - 1)
        grid[ay][ax] = 'A'

    # ── Print the grid (flip Y so 0 is at bottom) ──
    print(f"\n  Scale: 1 cell = {scale_x}x{scale_y} units")
    print(f"  W = Warehouse | A = Agent Start | ✦ = Delivery Destination\n")

    # Top border
    print("  ┌" + "─" * grid_w + "┐")
    for row in reversed(grid):
        print("  │" + "".join(row) + "│")
    # Bottom border
    print("  └" + "─" * grid_w + "┘")
    print()


# =============================================================================
# SECTION 7: BONUS — RANDOM DELAY REPORT
# =============================================================================

def print_delay_report(delays):
    """
    BONUS: Print a summary of random delivery delays.

    Args:
        delays: List of delay records from simulation
    """
    print("=" * 60)
    print("⏱️  DELIVERY DELAY REPORT (Random Delays)")
    print("=" * 60)

    total_delay = 0
    delayed_count = 0

    for d in delays:
        if d["delay_minutes"] > 0:
            delayed_count += 1
            total_delay += d["delay_minutes"]
            print(f"  📦 {d['package']} (Agent {d['agent']}): "
                  f"+{d['delay_minutes']} min delay")

    if delayed_count == 0:
        print("  ✅ No delays today!")
    else:
        avg_delay = total_delay / delayed_count
        print(f"\n  📊 Summary: {delayed_count}/{len(delays)} deliveries delayed")
        print(f"  📊 Total delay: {total_delay} min | Average: {avg_delay:.1f} min")
    print()


# =============================================================================
# SECTION 8: BONUS — CSV EXPORT OF TOP PERFORMER
# =============================================================================

def export_top_performer_csv(report, filepath="top_performer.csv"):
    """
    BONUS: Export the top performing agent's stats to a CSV file.

    Args:
        report:   The generated report dictionary
        filepath: Output CSV file path
    """
    best_agent_id = report["best_agent"]

    if best_agent_id is None:
        print("⚠️  No top performer to export.")
        return

    best_stats = report[best_agent_id]

    # Write CSV file with headers and one data row
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Agent ID", "Packages Delivered",
                         "Total Distance", "Efficiency"])
        writer.writerow([
            best_agent_id,
            best_stats["packages_delivered"],
            best_stats["total_distance"],
            best_stats["efficiency"]
        ])

    print(f"📊 Top performer exported to: {filepath}")


# =============================================================================
# SECTION 9: DETAILED RESULTS DISPLAY
# =============================================================================

def print_detailed_results(report, delivery_log):
    """
    Print a nicely formatted summary of all results.

    Args:
        report:       The generated report dictionary
        delivery_log: List of delivery events
    """
    print("=" * 60)
    print("📊 FINAL DELIVERY REPORT")
    print("=" * 60)

    for key, value in report.items():
        if key == "best_agent":
            continue  # Print this separately at the end

        agent_id = key
        stats = value
        delivered = stats["packages_delivered"]
        distance = stats["total_distance"]
        efficiency = stats["efficiency"]

        # Find which packages this agent delivered
        pkg_list = [d["package"] for d in delivery_log if d["agent"] == agent_id]

        print(f"\n  🚴 Agent {agent_id}:")
        print(f"     Packages Delivered : {delivered}")
        print(f"     Packages           : {', '.join(pkg_list) if pkg_list else 'None'}")
        print(f"     Total Distance     : {distance:.2f} units")
        print(f"     Efficiency         : {efficiency:.2f} units/package")

    # ── Best Agent ──
    print(f"\n  {'─' * 40}")
    print(f"  🏆 BEST AGENT: {report['best_agent']} "
          f"(Efficiency: {report[report['best_agent']]['efficiency']:.2f} units/package)")
    print(f"  {'─' * 40}")
    print()


# =============================================================================
# SECTION 10: MAIN PROGRAM
# =============================================================================

def main():
    """
    Main function — entry point of the program.

    1. Determines which JSON file to use (command line arg or default)
    2. Loads and parses the data
    3. Runs the delivery simulation
    4. Generates and saves the report
    5. Displays results and bonus features
    """
    # ── Determine input file ──
    if len(sys.argv) > 1:
        # User specified a file as command line argument
        input_file = sys.argv[1]
    else:
        # Default to base_case.json
        input_file = "base_case.json"

    # ── Check if the file exists ──
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found!")
        print(f"   Usage: python delivery_system.py <input_file.json>")
        sys.exit(1)

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         📦 FastBox Delivery System Simulator 📦         ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print(f"║  Input File: {input_file:<43} ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # ── STEP 1: Load and parse the JSON data ──
    warehouses, agents, packages = load_data(input_file)

    # ── STEP 2 & 3: Simulate deliveries (includes assignment + distance calc) ──
    agent_stats, delivery_log, delays = simulate_deliveries(
        warehouses, agents, packages
    )

    # ── STEP 4: Generate the report ──
    report = generate_report(agent_stats)

    # ── STEP 5: Save report to report.json ──
    # Save in the same directory as the input file
    output_dir = os.path.dirname(os.path.abspath(input_file))
    report_path = os.path.join(output_dir, "report.json")
    save_report(report, report_path)

    # ── Display detailed results ──
    print_detailed_results(report, delivery_log)

    # ── BONUS: ASCII Route Visualization ──
    visualize_routes_ascii(warehouses, agents, delivery_log)

    # ── BONUS: Random Delay Report ──
    print_delay_report(delays)

    # ── BONUS: Export Top Performer to CSV ──
    csv_path = os.path.join(output_dir, "top_performer.csv")
    export_top_performer_csv(report, csv_path)

    print()
    print("✅ All tasks completed successfully!")
    print()


# ── Run the program ──
if __name__ == "__main__":
    main()
