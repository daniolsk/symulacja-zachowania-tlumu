from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import FanAgent, WallAgent

def get_throughput(model):
    return model.fans_entered_this_step

def get_mean_entry_time(model):
    seated_fans = [a for a in model.schedule.agents if isinstance(a, FanAgent) and a.is_seated]
    if not seated_fans:
        return 0
    return sum(a.entry_time for a in seated_fans) / len(seated_fans)

def get_queue_length(model):
    # Liczymy fanów w obszarze przed bramkami (np. 3 kolumny przed ścianą)
    wall_x = model.grid.width // 2
    count = 0
    for agent in model.schedule.agents:
        if isinstance(agent, FanAgent) and not agent.has_scanned:
            x, y = agent.pos
            if wall_x - 3 <= x < wall_x:
                count += 1
    return count

class StadiumModel(Model):
    def __init__(self, width, height, num_fans, gate_service_time=5, gate_width=1, num_gates=2):
        super().__init__()
        self.num_fans = num_fans
        self.gate_service_time = gate_service_time
        self.gate_width = gate_width
        self.num_gates = num_gates
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
        
        # Rozmieszczamy bramki równomiernie wzdłuż ściany
        wall_x = self.grid.width // 2
        self.gate_positions = []
        
        if self.num_gates > 0:
            # Dzielimy wysokość na num_gates + 1 części, aby umieścić bramki w punktach podziału
            # Przykład: 1 bramka -> środek (height/2)
            # 2 bramki -> 1/3 i 2/3
            for i in range(1, self.num_gates + 1):
                center_y = (height * i) // (self.num_gates + 1)
                
                # Obliczamy pola dla danej bramki na podstawie gate_width
                start_y = center_y - (self.gate_width // 2)
                for j in range(self.gate_width):
                    y_pos = start_y + j
                    if 0 <= y_pos < height:
                        self.gate_positions.append((wall_x, y_pos))

        self._build_walls()

        for _ in range(self.num_fans):
            # Krzesełka co najmniej 2 pola na prawo od bramki (wall_x + 3)
            seat_x = self.random.randrange(wall_x + 3, width)
            seat_y = self.random.randrange(1, height)
            
            agent = FanAgent(self.next_id(), self, (seat_x, seat_y))
            self.schedule.add(agent)
            
            # Start w losowym miejscu po lewej stronie (x=0)
            spawn_x = 0
            spawn_y = self.random.randrange(0, height)
            self.grid.place_agent(agent, (spawn_x, spawn_y))

    def _build_walls(self):
        wall_x = self.grid.width // 2
        for y in range(self.grid.height):
            if (wall_x, y) not in self.gate_positions: 
                wall = WallAgent(self.next_id(), self)
                self.grid.place_agent(wall, (wall_x, y))

    def step(self):
        self.fans_entered_this_step = 0
        # Śledzimy ilu fanów przeszło przez bramkę w tym kroku
        pre_step_scanned = {a.unique_id for a in self.schedule.agents if isinstance(a, FanAgent) and a.has_scanned}
        
        self.schedule.step()
        
        post_step_scanned = {a.unique_id for a in self.schedule.agents if isinstance(a, FanAgent) and a.has_scanned}
        self.fans_entered_this_step = len(post_step_scanned - pre_step_scanned)
        
        self.datacollector.collect(self)
