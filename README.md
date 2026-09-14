*This project has been created as part of the 42 curriculum by lmongili.*

## Description
Fly-in is an advanced drone routing simulation system designed to navigate a fleet of autonomous drones through a network of interconnected zones. The primary goal of the project is to route all drones from a central starting hub to a destination hub in the fewest possible simulation turns. The simulation enforces strict movement constraints, handling dynamic zone capacities (`max_drones`), connection limits (`max_link_capacity`), and specific zone behaviors like `restricted` (requiring 2 turns to cross) and `priority` (preferred routing). 

## Instructions
The project is written in Python and uses standard tools for dependency management and execution.

**Requirements:**
* Python 3.10 or later.

**Makefile Usage:**
A `Makefile` is provided at the root of the project to automate common tasks. Use the following commands:
* `make install`: Installs project dependencies (such as `pygame` and `pydantic`).
* `make run`: Executes the main script to launch the application.
* `make debug`: Runs the main script in debug mode using Python's built-in debugger (`pdb`).
* `make clean`: Cleans up temporary files and caches (e.g., `__pycache__`, `.mypy_cache`).
* `make lint`: Runs `flake8` and `mypy` with strict type-checking flags to ensure code quality.

## Resources
## Algorithm Choices and Implementation Strategy
To solve the complex routing problem without causing deadlocks or exceeding zone capacities, the project implements a **Space-Time A* (Cooperative A*)** algorithm. 

* **Time-Expanded Graph:** Instead of standard spatial pathfinding, the algorithm treats time (turns) as a third dimension. Drones can choose to `MOVE`, `TRANSIT` (for 2-turn restricted zones), or `WAIT` in their current position to let traffic clear.
* **Reservation Table:** Every `Zone` and `Connection` maintains a dictionary mapping a specific turn to the number of drones occupying it. When a path is found for a drone, it "reserves" its slots in the future, effectively reducing the available capacity for subsequent drones during those specific turns.
* **Priority Queue & Heuristics:** The algorithm uses Python's `heapq` to explore the most promising paths first. The sorting key (`f_cost`) combines the accumulated turns (`g_cost`) with the Manhattan distance to the destination (`h_cost`). 
* **Fractional Priority Cost:** To prioritize `priority` zones without breaking the integer-based turn system, moving to a priority zone internally costs `0.9999` mathematically to trick the priority queue, while the simulation still accurately advances by exactly 1 discrete turn.

### Visual Representation Features
The project features a full Graphical User Interface built with **Pygame** to enhance the user experience by providing clear, real-time visual feedback of the simulation.

* **Dynamic Menus:** Users can browse and select different map files dynamically through an interactive menu system.
* **Smooth Animation (LERP):** Instead of drones instantly teleporting between zones, the visualizer uses Linear Interpolation to animate drones smoothly gliding across connections over the duration of the simulation turns.
* **Custom Sprites & Spatial Clarity:** Standard colored circles are dynamically replaced with custom Pokéball sprites representing different zone types (e.g., normal, blocked, restricted). To prevent visual clutter when multiple drones travel the same path, an ID-based pixel offset is applied so the "swarm" remains visible without overlapping perfectly.

## Example Input and Expected Output

**Example Input Map (`easy_map.txt`):**
```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal

```

**Example Output Map (`easy_map.txt`):**
```text
DD0-waypoint1
DD0-waypoint2 DD1-waypoint1
DD0-goal DD1-waypoint2
DD1-goal

