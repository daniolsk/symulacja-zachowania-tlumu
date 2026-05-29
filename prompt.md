Project Summary: Stadium Entry Logistics Simulation

Project Goal:  
 An agent-based microscopic crowd simulation developed to analyze stadium entry dynamics, bottleneck management, and
pathfinding. Unlike standard evacuation models, this focuses on the inflow process, simulating ticket scanning delays and
seating logistics.

Technical Stack:

- Language: Python 3.x
- Framework: Mesa 2.1.4 (pinned for ModularVisualization compatibility).

---

Current Architecture & Features

1. Core Modules

- run.py: Entry point for launching the Tornado-based visualization server.
- server.py: Handles visualization logic (CanvasGrid, ChartModule, TextElement) and interactive parameter sliders.
- model.py: Defines StadiumModel. Manages the 30x30 MultiGrid, agent spawning, wall construction, and data collection.
- agent.py:
  - WallAgent: Static barrier representing stadium infrastructure.
  - FanAgent: Moving entities using BFS pathfinding to reach assigned seats while avoiding walls and other moving agents.

2. Implemented Mechanics

- Dynamic Bottleneck: The number of gates (1–5) and their width (1–5 cells) can be adjusted via sliders.
- Ticket Scanning: Agents reaching a gate enter a "scanning" state for a configurable number of steps, during which they turn
  yellow.
- Advanced Pathfinding: BFS with Moore neighborhood (diagonal movement) and randomized neighbor selection to prevent
  deterministic "L-shape" patterns.
- Seating Logistics: Agents are assigned target seats. They can "squeeze" through already seated agents (green circles) but
  are blocked by agents currently in the queue (red circles).
- Localized Spawn: Fans spawn randomly along the left edge ($x=0$) to simulate arrival from the concourse.

3. Metrics & Data Collection (DataCollector)

- Przepustowość (Throughput): Real-time count of fans passing gates per step.
- Średni czas wejścia (Mean Entry Time): Average steps taken for fans to reach their seats.
- Długość kolejki (Queue Length): Count of agents in the "pressure zone" immediately before the gates.

---

Recent Modifications

- Grid Scaling: Expanded from 20x20 to 30x30.
- Interactive Parameters: Added sliders for fan count, gate count, gate width, and service time.
- Localization: Translated all UI labels and metrics to Polish.
- UI/UX: Added vertical padding (Spacer class) to the visualization.
- Bug Fixes: Resolved ImportError for Slider and TextElement by mapping them to the specific mesa_viz_tornado implementation.

Note for Next Agent:  
 The environment is sensitive to Mesa versioning. Ensure all imports for visualization modules are checked against
mesa_viz_tornado if mesa.visualization fails. Pathfinding is currently calculated every step; optimization (path caching) is a
recommended next step for larger fan counts.
