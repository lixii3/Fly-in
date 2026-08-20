from fly_in.src.drone import Drone
from fly_in.src.graph import Graph
from typing import Callable
import pygame as pg


class DroneRenderer:
    def __init__(self, img_path: str):
        self.img = pg.image.load(img_path).convert_alpha()
        self.img = pg.transform.scale(self.img, (100, 100))
        self.font = pg.font.SysFont('Arial', 18)
    
    def drawDrone(self, screen: pg.Surface,
                  d: Drone,
                  ft_mapping: Callable[[int, int], tuple[int, int]] = None) -> None:
        x, y = d.get_coordinates()
        if ft_mapping:
            x1, y1 = ft_mapping(x, y)
        img_rect = self.img.get_rect(center=(x1, y1))
        screen.blit(self.img, img_rect)
        print(f"{d.ID} : {x}, {y}")
        
    
    def drawDrones(self, screen: pg.Surface, graph: Graph,
                   ft_mapping: Callable[[int, int], tuple[int, int]] = None) -> None:
        for d in graph.get_drones():
            self.drawDrone(screen, d, ft_mapping)
