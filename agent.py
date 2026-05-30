from mesa import Agent
import random
import heapq

class WallAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class SeatAgent(Agent):
    def __init__(self, unique_id, model, row_num, seat_num):
        super().__init__(unique_id, model)
        self.row_num = row_num
        self.seat_num = seat_num
        self.is_occupied = False

    def step(self):
        pass

class FanAgent(Agent):
    def __init__(self, unique_id, model, seat_agent, smart_entry):
        super().__init__(unique_id, model)
        self.seat_agent = seat_agent
        self.seat_pos = seat_agent.pos
        self.smart_entry = smart_entry
        
        self.is_seated = False
        self.is_scanning = False
        self.has_scanned = False
        self.scanning_timer = 0
        self.entry_time = None
        
        self.path = []
        self.target_gate = None
        self.path_target = None
        self.blocked_counter = 0

    def find_path(self, target):
        queue = [(0, self.pos, [])]
        visited = {self.pos: 0}

        while queue:
            cost, current_pos, path = heapq.heappop(queue)

            if current_pos == target:
                return path

            neighbors = list(self.model.grid.get_neighborhood(current_pos, moore=True, include_center=False))
            random.shuffle(neighbors)

            for next_pos in neighbors:
                cell_contents = self.model.grid.get_cell_list_contents([next_pos])
                
                is_wall = any(isinstance(obj, WallAgent) for obj in cell_contents)
                if is_wall:
                    continue
                    
                # Jeśli kibic nie wszedł jeszcze, nie pozwalamy mu wejść w obce bramki!
                # Dzięki temu nie traktuje płyty stadionu jako skrótu do innej bramki.
                cx, cy = self.model.grid.width // 2, self.model.grid.height // 2
                d_next = max(abs(next_pos[0] - cx), abs(next_pos[1] - cy))
                
                if not self.has_scanned:
                    if d_next < 18:
                        continue # Zakaz wchodzenia na płytę stadionu bez biletu!
                    if next_pos in self.model.gate_positions:
                        is_my_gate = (abs(next_pos[0] - self.target_gate[0]) + abs(next_pos[1] - self.target_gate[1]) <= self.model.gate_width)
                        if not is_my_gate:
                            continue # Szanujemy obce bramki - nie przebijamy się przez nie
                
                # Zabraniamy kibicom będącym w środku wyjścia z powrotem na zewnątrz (tzw. zjawisko skrotu przez parking)
                if self.has_scanned and d_next > 18:
                    continue
                    
                # Zamiast całkowicie blokować ruch po siedzeniach, 
                # nadajemy im ogromny koszt. Dzięki temu, w przypadku zatorów, 
                # kibice "przecisną się" przez rzędy innych siedzeń by się ominąć.
                is_other_seat = any(isinstance(obj, SeatAgent) and obj.pos != self.seat_pos for obj in cell_contents)
                
                # Wykrywamy tłum na danym kafelku żeby unikać korków
                crowds = sum(1 for obj in cell_contents if isinstance(obj, FanAgent) and not obj.is_seated)
                
                base_cost = 1
                if is_other_seat:
                    base_cost = 15 
                
                new_cost = cost + base_cost + (crowds * 5)
                
                if next_pos not in visited or new_cost < visited[next_pos]:
                    visited[next_pos] = new_cost
                    priority = new_cost + abs(next_pos[0] - target[0]) + abs(next_pos[1] - target[1])
                    heapq.heappush(queue, (priority, next_pos, path + [next_pos]))
                    
        return []

    def step(self):
        if self.pos == self.seat_pos:
            if not self.is_seated:
                self.is_seated = True
                self.is_scanning = False
                self.seat_agent.is_occupied = True
                self.entry_time = self.model.schedule.steps
            return

        if not self.target_gate:
            if int(self.smart_entry) == 1:
                # Kibic świadomie wybiera bramkę najbliższą swojemu krzesełku.
                self.target_gate = min(
                    self.model.gate_centers, 
                    key=lambda g: abs(g[0] - self.seat_pos[0]) + abs(g[1] - self.seat_pos[1])
                )
            else:
                # Kibic domyślnie wybiera bramkę znajdującą się najbliżej miejsca startu.
                self.target_gate = min(
                    self.model.gate_centers, 
                    key=lambda g: abs(g[0] - self.pos[0]) + abs(g[1] - self.pos[1])
                )

        is_at_my_gate = (self.pos in self.model.gate_positions) and (
            abs(self.pos[0] - self.target_gate[0]) + abs(self.pos[1] - self.target_gate[1]) <= self.model.gate_width
        )

        if is_at_my_gate and not self.has_scanned:
            if not self.is_scanning:
                self.is_scanning = True
                self.scanning_timer = self.model.gate_service_time

            if self.is_scanning:
                self.scanning_timer -= 1
                if self.scanning_timer <= 0:
                    self.is_scanning = False
                    self.has_scanned = True
                    self.path = [] 
                else:
                    return

        if not self.has_scanned:
            current_target = self.target_gate
        else:
            current_target = self.seat_pos

        if not self.path or self.path_target != current_target:
            self.path = self.find_path(current_target)
            self.path_target = current_target
            self.blocked_counter = 0

        if self.path:
            next_step = self.path[0]
            cell_contents = self.model.grid.get_cell_list_contents([next_step])
            
            moving_agents = [obj for obj in cell_contents if isinstance(obj, FanAgent) and not obj.is_seated]

            # Zasadniczo trzymamy się zasady: 1 osoba na 1 polu (len == 0).
            # Dzięki temu ładnie i naturalnie ustawiają się w kolejki bez nakładania kroków.
            if len(moving_agents) == 0:
                self.model.grid.move_agent(self, next_step)
                self.path.pop(0)
                self.blocked_counter = 0
            else:
                self.blocked_counter += 1
                if self.blocked_counter == 3:
                    # Jeśli stoją w kolejce ponad 3 iteracje, przeliczą trasę,
                    # co poskutkuje tym, że np. ominą zablokowanego chłopa bokiem.
                    self.path = self.find_path(current_target)
                elif self.blocked_counter > 6:
                    # Desperacja! Stoją twarzą w twarz lub są całkowicie zamurowani
                    # przez 6 iteracji (kompletny deadlock). Zezwalamy na 1 ułamek sekundy 
                    # "przeniknąć" kogoś wchodząc na to samo zajęte pole.
                    if len(moving_agents) < 4:
                        self.model.grid.move_agent(self, next_step)
                        self.path.pop(0)
                        self.blocked_counter = 0
                    else:
                        self.path = self.find_path(current_target)
                        self.blocked_counter = 3
