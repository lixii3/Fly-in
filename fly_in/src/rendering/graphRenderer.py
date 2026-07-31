import pygame as pg
from typing import Callable
from fly_in.src.connection import Connection
from fly_in.src.zone import Zone
from fly_in.src.graph import Graph
from fly_in.src.rendering.utils import calcola_trasformazione


class GraphRenderer:
    def __init__(self):
        self.font = pg.font.SysFont('Arial', 18)
        
    def drawConnection(self, conn: Connection,
                       surface: pg.Surface,
                       normalizer_funct: Callable | None=None) -> None:
        color = pg.Color("#000000")
        color.a = 255
        xa, ya = conn.get_zoneA().get_coordinates()
        xb, yb = conn.get_zoneB().get_coordinates()
        start = (xa, ya)
        end = (xb, yb)
        if normalizer_funct:
            start = normalizer_funct(xa, ya)
            end = normalizer_funct(xb, yb)
        pg.draw.line(surface, color, start, end, 2)
        
    def drawZone(self, zone: Zone,
                 surface: pg.Surface,
                 normalizer_funct: Callable | None=None,
                 radius: int=30) -> None:
        color = zone.get_color().value
        x, y = zone.get_coordinates()
        center = (x,y)
        if normalizer_funct:
            center = normalizer_funct(x, y)
        pg.draw.circle(surface, color, center, radius)
        
    def drawGraph(self, graph: Graph, surface: pg.Surface) -> Callable:
        to_screen: Callable = calcola_trasformazione(graph.get_zones(),
                                                  surface.get_width(),
                                                  surface.get_height())
        for c in graph.get_connections():
            self.drawConnection(c, surface, to_screen)
        for z in graph.get_zones():
            self.drawZone(z, surface, to_screen)
        
        #ritorno la funzione di calcolo per poi poter posizionare i droni con le giuste coordinate
        return to_screen
        