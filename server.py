from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa_viz_tornado.UserParam import Slider
from model import StadiumModel
from agent import FanAgent, WallAgent

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
            "Layer": 1,
            "Color": color,
            "r": 0.6
        }

grid = CanvasGrid(agent_portrayal, 30, 30, 600, 600)

model_params = {
    "width": 30,
    "height": 30,
    "num_fans": Slider(
        "Liczba kibiców", 60, 10, 200, 10,
        description="Całkowita liczba kibiców w symulacji"
    ),
    "gate_width": Slider(
        "Szerokość bramek", 1, 1, 5, 1,
        description="Szerokość każdej z dwóch bramek"
    ),
    "gate_service_time": Slider(
        "Czas kontroli biletów", 5, 1, 20, 1,
        description="Liczba kroków potrzebna na przeskanowanie biletu"
    )
}

server = ModularServer(
    StadiumModel,
    [grid],
    "Symulacja Wejścia na Stadion",
    model_params
)
server.port = 8521
