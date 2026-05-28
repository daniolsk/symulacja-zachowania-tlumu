from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import StadiumModel
from agent import FanAgent, WallAgent

def agent_portrayal(agent):
    if isinstance(agent, WallAgent):
        return {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0, # Warstwa tła
            "Color": "grey",
            "w": 1,
            "h": 1
        }
    
    if isinstance(agent, FanAgent):
        color = "green" if agent.is_seated else "red"
        return {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1, # Kibice na wierzchu
            "Color": color,
            "r": 0.6
        }

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

server = ModularServer(
    StadiumModel,
    [grid],
    "Symulacja Wejścia na Stadion",
    # Zwiększamy liczbę kibiców do 30, żeby lepiej zaobserwować zator
    {"width": 20, "height": 20, "num_fans": 30} 
)
server.port = 8521