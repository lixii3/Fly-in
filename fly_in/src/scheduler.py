from fly_in.src.graph import Graph
from fly_in.src.drone import Drone
from fly_in.src.zone import Zone, ZoneException
from fly_in.src.connection import Connection, ConnectionException
from fly_in.src.utils import Action


class SchedulerException(Exception):
    """Exception raised when a schedule cannot be generated."""

    def __init__(self, msg: str = ""):
        """Initialize a scheduling exception.

        Args:
            msg (str, optional): Error message. Defaults to "".
        """
        super().__init__(msg)
        self.msg = msg

    def __str__(self) -> str:
        """Return the formatted exception message."""
        return "SchedulerException: " + self.msg


class Scheduler:
    """Assign capacity-aware paths and produce turn output."""

    def __init__(self, graph: Graph) -> None:
        """Create a scheduler for a graph.

        Args:
            graph (Graph): Graph whose drones should be routed.
        """
        self.__graph = graph
        self.TURNS = -1

    def schedule(self) -> None:
        """Route every drone and write the resulting turn output.

        Returns:
            int: Number of turns in the generated schedule.

        Raises:
            SchedulerException: If a drone cannot be routed or output fails.
        """
        drone: Drone
        resource: Zone | Connection
        for drone in self.__graph.get_drones():
            path = self.__graph.get_min_cost_path(
                self.__graph.get_start(), self.__graph.get_end(), start_turn=0
            )

            if path:
                # Assegna il percorso al drone
                drone.set_path(path)

                # Effettua le prenotazioni fisiche su Zone e Connection
                # per bloccare gli altri
                for _, resource, turn in path:
                    try:
                        resource.reserve(turn)
                    except (ConnectionException, ZoneException) as e:
                        raise SchedulerException(str(e))
            else:
                raise SchedulerException(
                    f"Errore: nessun percorso trovato per {drone.ID}"
                )

        self.TURNS = self.__generate_output_file()
        print(f"Total turns: {self.TURNS}")

    def __generate_output_file(self, filename: str = "output.txt") -> int:
        """both writes scheduled moves to a turn-by-turn output file
        and prints it to terminal.

        Args:
            filename (str, optional): Destination file path. Defaults to
                "output.txt".

        Returns:
            int: Number of output turns written.
        """
        curr_turn = 1
        dest: Zone | Connection | None
        action: tuple[Action, Zone | Connection | None, int]
        output: list[str] = []
        all_done: bool
        while True:
            turn_moves = []
            all_done = True
            for d in self.__graph.get_drones():
                if d.at_end():
                    continue
                action = d.get_action_at_turn(curr_turn)
                if action[0] != Action.NONE:
                    all_done = False

                if action[0] == Action.NONE or action[0] == Action.WAIT:
                    continue
                if action[0] == Action.MOVE or action[0] == Action.TRANSIT:
                    dest = action[1]
                    dstr = dest.get_name() if dest is not None else 'None'
                    movement = f"D{d.ID}-{dstr}"
                    turn_moves.append(movement)
            if all_done:
                break
            if len(turn_moves) > 0:
                line = " ".join(turn_moves)
                output.append(line + "\n")
                print(line)
            curr_turn += 1
        try:
            with open(filename, "w") as file:
                file.writelines(output)
            with open(filename, "r") as file:
                lines = sum(1 for _ in file)
        except OSError as e:
            raise SchedulerException(str(e))
        return lines


# if __name__ == "__main__":
#    from fly_in.src.parser import Parser
#    dir_path = "fly_in/maps/hard/01_maze_nightmare.txt"
#
#    g = Parser.parse_map(dir_path)
#    s = Scheduler(g)
#    s.schedule()
