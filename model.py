from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agent import FanAgent, WallAgent

class StadiumModel(Model):
    def __init__(self, width, height, num_fans):
        super().__init__()
        self.num_fans = num_fans
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.gate_pos = (0, 0) 

        self._build_walls()

        for _ in range(self.num_fans):
            # Upewniamy się, że krzesełka są po prawej stronie boiska (za bramkami)
            seat_x = self.random.randrange(width // 2 + 1, width)
            seat_y = self.random.randrange(1, height)
            
            agent = FanAgent(self.next_id(), self, (seat_x, seat_y))
            self.schedule.add(agent)
            
            # Wszyscy zaczynają w punkcie (0,0) - symulacja gęstego tłumu przed wejściem
            self.grid.place_agent(agent, self.gate_pos)

    def _build_walls(self):
        # Tworzymy ścianę w połowie szerokości boiska z małą przerwą (wąskie gardło)
        wall_x = self.grid.width // 2
        gate_y = self.grid.height // 2 

        for y in range(self.grid.height):
            if y != gate_y: 
                wall = WallAgent(self.next_id(), self)
                self.grid.place_agent(wall, (wall_x, y))

    def step(self):
        self.schedule.step()