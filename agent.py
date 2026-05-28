from mesa import Agent
import collections
import random

class WallAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class FanAgent(Agent):
    def __init__(self, unique_id, model, seat_pos):
        super().__init__(unique_id, model)
        self.seat_pos = seat_pos
        self.is_seated = False

    def find_path(self):
        queue = collections.deque([(self.pos, [])])
        visited = {self.pos}

        while queue:
            current_pos, path = queue.popleft()

            if current_pos == self.seat_pos:
                return path

            # Włączamy ruch po przekątnych (moore=True)
            neighbors = list(self.model.grid.get_neighborhood(current_pos, moore=True, include_center=False))
            
            # Przełamujemy determinizm - tłum zacznie zachowywać się naturalnie
            random.shuffle(neighbors)
            
            for next_pos in neighbors:
                if next_pos not in visited:
                    cell_contents = self.model.grid.get_cell_list_contents([next_pos])
                    is_wall = any(isinstance(obj, WallAgent) for obj in cell_contents)
                    
                    if not is_wall:
                        visited.add(next_pos)
                        queue.append((next_pos, path + [next_pos]))
        return []

    def step(self):
        if self.pos == self.seat_pos:
            self.is_seated = True
            return

        path = self.find_path()

        if path:
            next_step = path[0]
            
            cell_contents = self.model.grid.get_cell_list_contents([next_step])
            
            # UWAGA: Omijamy tylko tych kibiców, którzy są w ruchu. 
            # Przez siedzących (is_seated=True) można się "przecisnąć".
            is_occupied = any(isinstance(obj, FanAgent) and not obj.is_seated for obj in cell_contents)
            
            if not is_occupied:
                self.model.grid.move_agent(self, next_step)