*This project has been created as part of the 42 curriculum by aredouan.*

# Fly In

## Description
Fly In is a Python project that simulates drone traffic on a map made of zones and connections.
The goal is to compute valid routes for multiple drones while respecting zone occupancy limits,
connection capacity, restricted zones, and priority zones.

The program parses a text-based map description, plans routes for every drone, prints the turn-by-turn movements, and optionally displays the result in a pygame window.

## Instructions

### Requirements
- Python 3.14+
- `pygame-ce`

### Installation
If you want to use the provided virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Execution
Run the simulator with a map file:

```bash
python main.py 03_priority_puzzle.txt
```

The program will:
1. Parse the map file.
2. Compute drone routes.
3. Print the drone movements turn by turn.
4. Open the visualizer window.

### Input format overview
The map file supports declarations such as:
- `nb_drones: <number>`
- `start_hub: <name> <x> <y> [options]`
- `hub: <name> <x> <y> [options]`
- `end_hub: <name> <x> <y> [options]`
- `connection: <zone1>-<zone2> [max_link_capacity=<n>]`

## Algorithm and Implementation Strategy
The project uses an A*-style pathfinding approach.

### Pathfinding
- Each search state stores the current zone, the current turn, the accumulated path, and a heuristic score.
- The heuristic is based on Euclidean distance between the current zone and the destination.
- The open set is handled with a priority queue so the most promising route is explored first.

### Constraints handling
- A `ReservationTable` keeps track of zone occupancy and connection usage by turn.
- Drones can wait in place when needed.
- Restricted zones require extra time to cross.
- Priority zones are handled with favorable movement cost so they can be preferred when useful.
- Connection capacity and swap conflicts are checked before adding a move to the search frontier.

### Simulation strategy
- The simulation plans one path per drone.
- After a path is found, every zone and connection on that route is reserved in the table.
- This prevents later drones from reusing the same limited resources in the same turn.

## Visual Representation
The pygame visualizer makes the simulation easier to understand by showing the map and the drones in motion.

### Features
- Zones are displayed as colored circles.
- Connections are drawn as lines with thickness reflecting link capacity.
- Drone positions are interpolated between turns for smooth animation.
- Zone names and drone identifiers are rendered on screen.
- The map is automatically scaled and centered to fit the window.

### User experience benefits
The visual layer helps confirm that the planned routes are valid and readable.
It also makes it easier to spot congestion, detours, and the effect of priority or restricted zones.

## Example
### Input
The repository includes [03_priority_puzzle.txt](03_priority_puzzle.txt) as a ready-to-run example.

### Expected output
When running the sample map, the program prints movement updates similar to:

```text
D0-fast_junction D2-start-slow_path1
D0-fast_path D1-fast_junction D2-slow_path1 D4-start-slow_path1
D0-merge_point D1-fast_path D2-slow_path2 D3-fast_junction D4-start-slow_path1
D0-goal D1-merge_point D2-merge_point D3-fast_path D4-slow_path2
D1-goal D2-goal D3-merge_point D4-merge_point
D3-goal D4-goal
```

The visualizer then opens and animates the drones across the map.

## Resources
- Python documentation: https://docs.python.org/3/
- `heapq` documentation: https://docs.python.org/3/library/heapq.html
- `dataclasses` documentation: https://docs.python.org/3/library/dataclasses.html
- `enum` documentation: https://docs.python.org/3/library/enum.html
- `pygame-ce` documentation: https://pyga.me/docs/
- A* search overview: https://en.wikipedia.org/wiki/A*_search_algorithm

## AI Usage
AI was used to help draft and organize this README, based on the existing source code and sample map files.
It was also used to summarize the algorithm, the visualization features, and the expected runtime behavior.
The implementation itself remains in the project source code.
