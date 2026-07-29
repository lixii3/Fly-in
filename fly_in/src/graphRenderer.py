import pygame as pg
from connection import Connection
from zone import Zone
from graph import Graph
from typing import Callable
from utils import calcola_trasformazione


class GraphRenderer:
    def __init__(self, screen: pg.Surface):
        self.screen: pg.Surface = screen
        self.screen.se
        self.font = pg.font.SysFont('Arial', 18)
        
    
        
    def drawConnection(self, conn: Connection,
                       normalizer_funct: Callable | None=None) -> None:
        color = pg.Color(conn.get_color().value)
        xa, ya = conn.get_zoneA().get_coordinates()
        xb, yb = conn.get_zoneB().get_coordinates()
        start = (xa, ya)
        end = (xb, yb)
        if normalizer_funct:
            start = normalizer_funct(xa, ya)
            end = normalizer_funct(xb, yb)
        pg.draw.line(self.screen, color, start, end, 2)
        
    def drawZone(self, zone: Zone,
                 radius: int=5,
                 normalizer_funct: Callable | None=None) -> None:
        color = zone.get_color().value
        x, y = zone.get_coordinates()
        center = (x,y)
        if normalizer_funct:
            center = normalizer_funct(x, y)
        pg.draw.circle(self.screen, color, center, radius, 1)
        
    def drawGraph(self, graph: Graph) -> None:
        to_screen: Callable = calcola_trasformazione(graph.get_zones(),
                                                  self.screen.get_width(),
                                                  self.screen.get_height())
        for c in graph.get_connections():
            self.drawConnection(c, to_screen)
        for z in graph.get_zones():
            self.drawConnection(z, to_screen)
        