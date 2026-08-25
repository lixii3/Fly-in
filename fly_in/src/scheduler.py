from fly_in.src.graph import Graph
from fly_in.src.drone import Drone
from fly_in.src.zone import Zone
from fly_in.src.connection import Connection
from fly_in.src.utils import Action


class SchedulerException(Exception):
    def __init__(self, msg: str = ""):
        super().__init__(msg)
        self.msg = msg
        
    def __str__(self):
        return "SchedulerException: " + self.msg

class Scheduler:
    def __init__(self, graph: Graph):
        self.__graph = graph
    
    def schedule(self):
        drone: Drone
        resource: Zone | Connection
        for drone in self.__graph.get_drones():
            path = self.__graph.get_min_cost_path(self.__graph.get_start(), self.__graph.get_end(), start_turn=0)
            
            if path:
                # Assegna il percorso al drone
                drone.set_path(path)
                
                # Effettua le prenotazioni fisiche su Zone e Connection per bloccare gli altri
                for _, resource, turn in path:
                    resource.reserve(turn)
            else:
                print(f"Errore: nessun percorso trovato per {drone.ID}")
    
        self.__generate_output_file()
        
    
    def __generate_output_file(self, filename: str = "output.txt") -> None:
        curr_turn = 1
        all_arrived = all(d.at_end() for d in self.__graph.get_drones())
        dest: Zone | Connection
        action: Action
        output: list[str] = []
        while not all_arrived:
            turn_moves = []
            for d in self.__graph.get_drones():
                if d.at_end():
                    continue
                action = d.get_action_at_turn(curr_turn)
                if action == Action.NONE:
                    continue
                dest = action[1]
                if action == Action.MOVE or action == Action.TRANSIT:
                    movement = f"D{d.ID}-{dest.get_name()}"
                    turn_moves.append(movement)
            all_arrived = all(d.at_end() for d in self.__graph.get_drones())
            if len(turn_moves) > 0:
                line = str.join(turn_moves, " ")
                output[curr_turn] = line
                turn_moves.clear()
            curr_turn += 1

        try:
            with open(filename, "w+") as file:
                for l in output:
                    file.write(l + "\n")
        except OSError as e:
            raise SchedulerException(str(e[0]))
                    
                
if __name__ == "__main__":
    from fly_in.src.parser import Parser
    g = Parser.parse_map("fly_in/maps/easy/01_linear_path.txt")
    s = Scheduler(g)
    s.schedule()