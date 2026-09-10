from fly_in.src.zone import Zone
from typing import Callable


def calcola_trasformazione(
    nodi: list[Zone], width: int,
    height: int, padding: int = 50
) -> Callable[[float, float], tuple[float, float]]:
    """Create a function mapping graph coordinates to screen coordinates.

    Args:
        nodi (list[Zone]): Zones whose coordinate bounds define the graph.
        width (int): Target surface width in pixels.
        height (int): Target surface height in pixels.
        padding (int, optional): Minimum edge padding in pixels.
            Defaults to 50.

    Returns:
        Callable: Coordinate conversion function.
    """
    # 1. Trova gli estremi del grafo
    xs = [nodo.get_x() for nodo in nodi]
    ys = [nodo.get_y() for nodo in nodi]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Evitiamo divisioni per zero
    larghezza_grafo = max(max_x - min_x, 1)
    altezza_grafo = max(max_y - min_y, 1)

    # 2. Calcola il fattore di scala
    area_utile_w = width - (padding * 2)
    area_utile_h = height - (padding * 2)

    scale_x = area_utile_w / larghezza_grafo
    scale_y = area_utile_h / altezza_grafo

    # Usiamo la scala minore per non distorcere le proporzioni del grafo
    scale = min(scale_x, scale_y)
    pixel_w = larghezza_grafo * scale
    pixel_h = altezza_grafo * scale
    offset_x = (width - pixel_w) / 2
    offset_y = (height - pixel_h) / 2

    def world_to_screen(x: float, y: float) -> tuple[float, float]:
        """Convert one world-space point to screen-space coordinates.

        Args:
            x (float): World-space horizontal coordinate.
            y (float): World-space vertical coordinate.

        Returns:
            tuple[int, int]: Screen-space pixel coordinates.
        """
        screen_x = int(offset_x + (x - min_x) * scale)
        screen_y = int(offset_y + (y - min_y) * scale)
        return (screen_x, screen_y)

    return world_to_screen
