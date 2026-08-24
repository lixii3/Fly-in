from fly_in.src.graph import Graph
from fly_in.src.drone import Drone
from fly_in.src.zone import Zone
from fly_in.src.connection import Connection


class Scheduler:
    def __init__(self, graph: Graph):
        self.__graph = graph
    
    def schedule(cls):
        drone: Drone
        for drone in cls.__graph.get_drones():
            path = cls.__graph.get_min_cost_path(cls.__graph.get_start(), cls.__graph.get_end(), start_turn=0)
            
            if path:
                # Assegna il percorso al drone
                drone.set_path(path)
                
                # Effettua le prenotazioni fisiche su Zone e Connection per bloccare gli altri!
                for action, resource, turn in path:
                    if action in ("MOVE", "WAIT", "TRANSIT"):
                        resource.reserve(turn)
            else:
                print(f"Errore: nessun percorso trovato per {drone.ID}")