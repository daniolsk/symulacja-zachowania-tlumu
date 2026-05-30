from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer, TextElement
from mesa_viz_tornado.UserParam import Slider
from model import StadiumModel
from agent import FanAgent, WallAgent, SeatAgent

class Spacer(TextElement):
    def render(self, model):
        return "<br>"

def agent_portrayal(agent):
    if isinstance(agent, WallAgent):
        return {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": "grey",
            "w": 1,
            "h": 1
        }
        
    if isinstance(agent, SeatAgent):
        return {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "Color": "lightblue",
            "w": 0.8,
            "h": 0.8,
            "Siedzenie": f"Rząd {agent.row_num}, Miejsce {agent.seat_num}"
        }

    if isinstance(agent, FanAgent):
        if agent.is_seated:
            color = "green"
        elif agent.is_scanning:
            color = "yellow"
        else:
            color = "red"

        return {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": color,
            "r": 0.6,
            "Bilet": f"Rząd {agent.seat_agent.row_num}, Miejsce {agent.seat_agent.seat_num}"
        }

grid = CanvasGrid(agent_portrayal, 50, 50, 700, 700)

spacer = Spacer()

chart_throughput = ChartModule([{"Label": "Przepustowość", "Color": "Blue"}])
chart_entry_time = ChartModule([{"Label": "Średni czas wejścia", "Color": "Green"}])
chart_queue = ChartModule([{"Label": "Długość kolejki", "Color": "Red"}])

model_params = {
    "width": 50,
    "height": 50,
    "num_fans": Slider(
        "Liczba kibiców", 100, 10, 336, 10,
        description="Całkowita liczba kibiców w symulacji (max to liczba dostępnych krzesełek)"
    ),
    "num_gates": Slider(
        "Liczba bramek", 4, 1, 12, 1,
        description="Liczba równomiernie rozmieszczonych bramek"
    ),
    "gate_width": Slider(
        "Szerokość bramek", 2, 1, 5, 1,
        description="Szerokość każdej z bramek"
    ),
    "gate_service_time": Slider(
        "Czas kontroli biletów", 5, 1, 20, 1,
        description="Liczba kroków potrzebna na przeskanowanie biletu"
    ),
    "smart_entry": Slider(
        "Świadome wejście (1=Tak, 0=Nie)", 1, 0, 1, 1,
        description="Czy kibice kierują się do bramki najbliższej ich miejsca"
    )
}

server = ModularServer(
    StadiumModel,
    [grid, spacer, chart_throughput, spacer, chart_entry_time, spacer, chart_queue],
    "Symulacja Wejścia na Stadion",
    model_params
)
server.port = 8521
