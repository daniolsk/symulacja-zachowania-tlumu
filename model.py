from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import FanAgent, WallAgent, SeatAgent

def get_throughput(model):
    return model.fans_entered_this_step

def get_mean_entry_time(model):
    seated_fans = [a for a in model.schedule.agents if isinstance(a, FanAgent) and a.is_seated]
    if not seated_fans:
        return 0
    return sum(a.entry_time for a in seated_fans) / len(seated_fans)

def get_queue_length(model):
    count = sum(1 for a in model.schedule.agents if isinstance(a, FanAgent) and not a.has_scanned and not a.is_scanning)
    return count

class StadiumModel(Model):
    def __init__(self, width, height, num_fans, gate_service_time=5, gate_width=1, num_gates=4, smart_entry=1):
        super().__init__()
        self.num_fans = num_fans
        self.gate_service_time = gate_service_time
        self.gate_width = gate_width
        self.num_gates = num_gates
        self.smart_entry = smart_entry
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.fans_entered_this_step = 0

        self.datacollector = DataCollector(
            model_reporters={
                "Przepustowość": get_throughput,
                "Średni czas wejścia": get_mean_entry_time,
                "Długość kolejki": get_queue_length
            }
        )
        
        self.gate_positions = set()
        self.gate_centers = []
        self.available_seats = []
        
        self._build_stadium()

        spawn_points = []
        for x in range(self.grid.width):
            spawn_points.append((x, 0))
            spawn_points.append((x, self.grid.height - 1))
        for y in range(1, self.grid.height - 1):
            spawn_points.append((0, y))
            spawn_points.append((self.grid.width - 1, y))

        for _ in range(self.num_fans):
            if not self.available_seats:
                break
            
            seat_agent = self.random.choice(self.available_seats)
            self.available_seats.remove(seat_agent)
            
            agent = FanAgent(self.next_id(), self, seat_agent, self.smart_entry)
            self.schedule.add(agent)
            
            spawn_x, spawn_y = self.random.choice(spawn_points)
            self.grid.place_agent(agent, (spawn_x, spawn_y))

    def _place_wall(self, x, y):
        wall = WallAgent(self.next_id(), self)
        self.grid.place_agent(wall, (x, y))

    def _build_stadium(self):
        cx, cy = self.grid.width // 2, self.grid.height // 2
        d_outer = 18
        d_pitch = 8
        
        perimeter = []
        for x in range(cx - d_outer, cx + d_outer + 1): perimeter.append((x, cy + d_outer))
        for y in range(cy + d_outer - 1, cy - d_outer, -1): perimeter.append((cx + d_outer, y))
        for x in range(cx + d_outer, cx - d_outer - 1, -1): perimeter.append((x, cy - d_outer))
        for y in range(cy - d_outer + 1, cy + d_outer): perimeter.append((cx - d_outer, y))
        
        if self.num_gates > 0:
            step = len(perimeter) / self.num_gates
            for i in range(self.num_gates):
                idx = int(i * step)
                center_x, center_y = perimeter[idx]
                self.gate_centers.append((center_x, center_y))
                for dw in range(-(self.gate_width // 2), (self.gate_width - 1) // 2 + 1):
                    idx_w = (idx + dw) % len(perimeter)
                    self.gate_positions.add(perimeter[idx_w])
        
        seat_num_counter = 1
        for d in range(d_pitch + 1, d_outer):
            r = d - d_pitch
            # r % 2 == 1 -> rząd ścieżek
            # r % 2 == 0 -> rząd krzesełek
            if r % 2 == 0:
                row_number = r // 2
                
                # Zbieranie koordynatów pierścienia d w odpowiedniej kolejności dla ładnej numeracji
                seats_in_ring = []
                for x in range(cx - d, cx + d + 1): seats_in_ring.append((x, cy + d))
                for y in range(cy + d - 1, cy - d, -1): seats_in_ring.append((cx + d, y))
                for x in range(cx + d, cx - d - 1, -1): seats_in_ring.append((x, cy - d))
                for y in range(cy - d + 1, cy + d): seats_in_ring.append((cx - d, y))
                
                for (x, y) in seats_in_ring:
                    if abs(x - cx) == abs(y - cy) or abs(abs(x - cx) - abs(y - cy)) == 1:
                        # Zostawiamy szersze puste przekątne przejścia (po 3 kratki w rogu)
                        continue
                        
                    if x == cx or y == cy or x == cx - 1 or y == cy - 1:
                        # Dodatkowe 2-kratkowe przejścia na środku każdego boku
                        continue
                    
                    seat_agent = SeatAgent(self.next_id(), self, row_number, seat_num_counter)
                    self.grid.place_agent(seat_agent, (x, y))
                    self.schedule.add(seat_agent)
                    self.available_seats.append(seat_agent)
                    seat_num_counter += 1
            
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                d = max(abs(x - cx), abs(y - cy))
                
                if d > d_outer:
                    continue
                
                if d == d_outer:
                    if (x, y) not in self.gate_positions:
                        self._place_wall(x, y)
                    continue
                
                if d <= d_pitch:
                    self._place_wall(x, y)
                    continue

    def step(self):
        self.fans_entered_this_step = 0
        pre_step_scanned = {a.unique_id for a in self.schedule.agents if isinstance(a, FanAgent) and a.has_scanned}
        
        self.schedule.step()
        
        post_step_scanned = {a.unique_id for a in self.schedule.agents if isinstance(a, FanAgent) and a.has_scanned}
        self.fans_entered_this_step = len(post_step_scanned - pre_step_scanned)
        
        self.datacollector.collect(self)
