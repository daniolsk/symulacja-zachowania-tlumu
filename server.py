from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import StadiumModel

def agent_portrayal(agent):
    # Czerwony szuka miejsca, zielony już siedzi
    color = "green" if agent.is_seated else "red"
    
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "Color": color,
        "r": 0.6
    }
    return portrayal

# Siatka 20x20 rysowana na płótnie 500x500 pikseli
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

server = ModularServer(
    StadiumModel,
    [grid],
    "Symulacja Wejścia na Stadion",
    {"width": 20, "height": 20, "num_fans": 15} # Parametry początkowe
)
server.port = 8521