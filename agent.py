from mesa import Agent

class FanAgent(Agent):
    def __init__(self, unique_id, model, seat_pos):
        super().__init__(unique_id, model)
        self.seat_pos = seat_pos
        self.is_seated = False

    def step(self):
        # Jeśli agent dotarł na miejsce, kończy ruch
        if self.pos == self.seat_pos:
            self.is_seated = True
            return

        # Uproszczony pathfinding (Manhattan) w kierunku celu
        current_x, current_y = self.pos
        target_x, target_y = self.seat_pos

        new_x = current_x + 1 if current_x < target_x else (current_x - 1 if current_x > target_x else current_x)
        new_y = current_y + 1 if current_y < target_y else (current_y - 1 if current_y > target_y else current_y)

        # Przesunięcie agenta na nową pozycję
        self.model.grid.move_agent(self, (new_x, new_y))