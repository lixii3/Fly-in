from fly_in.src.zone import Zone
from typing import Callable


def calcola_trasformazione(nodi: list[Zone], width: int,
                               height: int, padding=50) -> Callable:
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
        
        # 3. Funzione di conversione da applicare a Nodi, Archi e Droni
        def world_to_screen(x, y) -> tuple[int, int]:
            screen_x = int(padding + (x - min_x) * scale)
            screen_y = int(padding + (y - min_y) * scale)
            return (screen_x, screen_y)

        return world_to_screen