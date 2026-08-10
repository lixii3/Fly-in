from fly_in.src.drone import Drone
from fly_in.src.graph import Graph
from typing import Callable
import pygame as pg


class DroneRenderer:
    def __init__(self, img_path: str):
        self.img = pg.image.load(img_path).convert_alpha()
        self.img = pg.transform.scale(self.img, (100, 100))
        self.font = pg.font.SysFont('Arial', 18)
    
    def drawDrones(self, screen: pg.Surface, graph: Graph, ft_mapping: Callable) -> None:
        for d in graph.get_drones():
            x, y = ft_mapping(d.get_where().get_x(), d.get_where().get_y())
            img_rect = self.img.get_rect(x=x, y=y)
            screen.blit(self.img, img_rect)
            