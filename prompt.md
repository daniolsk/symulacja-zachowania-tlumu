Project Summary: Stadium Entry Logistics Simulation

Project Goal:
An agent-based microscopic crowd simulation developed to analyze stadium entry dynamics, bottleneck management, and pathfinding. Unlike standard evacuation models, this focuses on the inflow process, simulating ticket scanning delays and seating logistics.

Technical Stack:

- Language: Python 3.x
- Framework: Mesa 2.1.4 (pinned for ModularVisualization compatibility)
- Visualization: mesa_viz_tornado (Slider import workaround for Mesa 2.x)
- Entry point: `python run.py` → Tornado server at http://127.0.0.1:8521

---

Current Architecture

1. Core Modules

- `run.py`: Launches the Tornado-based visualization server.
- `server.py`: CanvasGrid (50×50), three ChartModules, Spacer padding, and interactive parameter sliders (Polish labels).
- `model.py`: Defines `StadiumModel`. Manages the 50×50 MultiGrid, stadium construction, fan spawning, simulation step, and DataCollector metrics.
- `agent.py`:
  - `WallAgent`: Static barrier (pitch boundary and outer perimeter).
  - `SeatAgent`: Fixed seat with row/seat numbering; tracks `is_occupied`.
  - `FanAgent`: Moving entity with cost-based pathfinding, gate queuing, and deadlock handling.

2. Stadium Layout (`StadiumModel._build_stadium`)

The stadium is a square ring centered on the grid midpoint `(cx, cy) = (width//2, height//2)`:

- `d_pitch = 8`: Inner pitch area — fully walled off.
- `d_outer = 18`: Outer perimeter wall; gates are openings cut into this ring.
- Between pitch and outer wall: alternating **seat rows** (`r % 2 == 0`) and **aisle rows** (`r % 2 == 1`), where `r = d - d_pitch`.
- Seat placement skips diagonal corner passages (3 cells wide) and mid-side passages (2 cells wide).
- Gates are evenly distributed along the outer perimeter; `gate_width` controls how many perimeter cells each gate spans.
- `num_gates` can range from 1 to 12 (slider in `server.py`).

3. Fan Lifecycle (`FanAgent.step`)

Each fan is assigned a random `SeatAgent` at spawn and follows this sequence:

1. **Spawn** — random position on the full grid border (top, bottom, left, right edges).
2. **Gate selection** (once) — controlled by `smart_entry`:
   - `1` (smart): gate closest to assigned seat (Manhattan distance).
   - `0` (dumb): gate closest to spawn position.
3. **Approach gate** — pathfind to `target_gate` while `has_scanned == False`.
4. **Scan** — at assigned gate, enter `is_scanning` state for `gate_service_time` steps (rendered yellow); cannot move during scan.
5. **Walk to seat** — pathfind to `seat_pos` after scanning.
6. **Sit** — mark `is_seated`, set `seat_agent.is_occupied`, record `entry_time` (rendered green).

Visualization colors: red = moving, yellow = scanning, green = seated.

4. Pathfinding (`FanAgent.find_path`)

Cost-based search (Dijkstra / A*-style) using `heapq`, Moore neighborhood (8 directions), randomized neighbor order to avoid deterministic paths.

**Hard blocks:**
- Wall cells.
- Before scan: cells inside the stadium bowl (`d_next < 18`) — cannot cut across the pitch without a ticket.
- Before scan: foreign gate cells — must use assigned gate only.
- After scan: cells outside the bowl (`d_next > 18`) — no re-exiting once inside.

**Soft costs:**
- Normal cell: base cost 1.
- Another fan's seat cell: base cost 15 (avoid but usable in congestion).
- Moving fans on cell: +5 per fan (crowd avoidance).

Path is recalculated when the target changes (`gate` → `seat`) or when movement is blocked (see queuing below). It is **not** recomputed every step.

5. Queuing & Deadlock Handling

- **Default rule:** one moving fan per cell — creates natural single-file queues.
- **Blocked 3 steps:** recalculate path (try alternate route around obstruction).
- **Blocked 6+ steps:** allow "squeeze" onto occupied cell if fewer than 4 moving fans present; otherwise recalculate path and reset counter to 3.

Seated fans (green) do not block movement — only moving fans count as obstacles.

6. Interactive Parameters (sliders in `server.py`)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `num_fans` | 100 | 10–336 | Total fans (max = available seats) |
| `num_gates` | 4 | 1–12 | Evenly spaced gates on outer perimeter |
| `gate_width` | 2 | 1–5 | Width of each gate in cells |
| `gate_service_time` | 5 | 1–20 | Steps to scan a ticket at gate |
| `smart_entry` | 1 | 0–1 | 1 = gate nearest seat; 0 = gate nearest spawn |

Grid dimensions (`width`, `height`) are fixed at 50 in `server.py` model_params.

7. Metrics & Data Collection (DataCollector)

- **Przepustowość (Throughput):** Count of fans who *finished scanning* during the current step (set difference of `has_scanned` before/after `schedule.step()`).
- **Średni czas wejścia (Mean Entry Time):** Average `entry_time` (simulation step when seated) across all seated fans.
- **Długość kolejki (Queue Length):** Count of fans who have not yet scanned and are not currently scanning (`not has_scanned and not is_scanning`).

---

Simulation Step Flow

```
StadiumModel.step()
  ├─ reset fans_entered_this_step
  ├─ snapshot fans with has_scanned
  ├─ schedule.step()  →  each FanAgent.step()
  ├─ count newly scanned fans (throughput)
  └─ datacollector.collect()
```

Agent activation order is randomized each step via `RandomActivation`.

---

Notes for Next Agent

- **Mesa versioning:** The environment is sensitive to Mesa version. If `mesa.visualization` imports fail, check `mesa_viz_tornado` (currently used for `Slider`; `CanvasGrid`, `ChartModule`, `TextElement`, and `ModularServer` import from `mesa.visualization`).
- **Pathfinding performance:** Path is cached in `self.path` and only recomputed on target change or blocking. For very large fan counts, further optimization (e.g. incremental replanning) may still help.
- **Seat capacity:** Max fans is capped by the number of `SeatAgent` instances created during `_build_stadium` (slider max is 336).
- **Comments in code:** Polish inline comments in `agent.py` document non-obvious pathfinding and queuing rules.
