from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agent import FanAgent

class StadiumModel(Model):
    def __init__(self, width, height, num_fans):
        super().__init__()
        self.num_fans = num_fans
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        
        # Brama wejściowa - wszyscy startują w lewym dolnym rogu
        self.gate_pos = (0, 0) 

        for i in range(self.num_fans):
            # Losowanie miejsca docelowego (krzesełka)
            seat_x = self.random.randrange(1, width)
            seat_y = self.random.randrange(1, height)
            
            agent = FanAgent(i, self, (seat_x, seat_y))
            self.schedule.add(agent)
            
            # Umieszczenie agenta w bramie wejściowej
            self.grid.place_agent(agent, self.gate_pos)

    def step(self):
        # Wykonanie kroku symulacji dla wszystkich agentów
        self.schedule.step()