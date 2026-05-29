from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agent import FanAgent, WallAgent

class StadiumModel(Model):
    def __init__(self, width, height, num_fans, gate_service_time=5, gate_width=1):
        super().__init__()
        self.num_fans = num_fans
        self.gate_service_time = gate_service_time
        self.gate_width = gate_width
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Definiujemy środki dwóch bramek
        wall_x = self.grid.width // 2
        gate_centers = [height // 3, 2 * height // 3]

        # Obliczamy wszystkie pola zajmowane przez bramki na podstawie gate_width
        self.gate_positions = []
        for center_y in gate_centers:
            start_y = center_y - (self.gate_width // 2)
            for i in range(self.gate_width):
                y_pos = start_y + i
                if 0 <= y_pos < height:
                    self.gate_positions.append((wall_x, y_pos))

        self._build_walls()

        for _ in range(self.num_fans):
            # Krzesełka co najmniej 2 pola na prawo od bramki (wall_x + 3)
            seat_x = self.random.randrange(wall_x + 3, width)
            seat_y = self.random.randrange(1, height)

            agent = FanAgent(self.next_id(), self, (seat_x, seat_y))

            self.schedule.add(agent)

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
        self.schedule.step()