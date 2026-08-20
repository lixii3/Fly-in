from fly_in.src.rendering.pngButton import PNGButton
from fly_in.src.rendering.utils import calcola_trasformazione
from fly_in.src.connection import Connection
from fly_in.src.graph import Graph
from fly_in.src.zone import Zone
from fly_in.src.drone import Drone
import os
import pygame as pg
from typing import Callable

class Renderer:
    def __init__(self):
        pg.init()
        self.SCREEN = pg.display.set_mode()
        self.WIDTH = self.SCREEN.get_width()
        self.HEIGHT = self.SCREEN.get_height()
        self.FPS = 60
        self.CLOCK = pg.time.Clock()
        self.__active_buttons: pg.sprite.Group[PNGButton] = pg.sprite.Group()
        self.__graph_surface = pg.Surface((1500, 900), flags=pg.SRCALPHA)
        self._load_resources()

    def _load_resources(self) -> None:
            self.fonts: dict[str, pg.font.Font] = {}
            self.backgrounds: dict[str, pg.Surface] = {}
            self.buttons: dict[str, PNGButton] = {}
            self.sprites: dict[str, pg.Surface] = {}
    
            _font_path = "fly_in/src/rendering/resources/fonts"
            _bg_path = "fly_in/src/rendering/resources/bg"
            _btns_path = "fly_in/src/rendering/resources/buttons"
            _sprites_path = "fly_in/src/rendering/resources/sprites"
    
            # Fonts
            if os.path.exists(_font_path):
                for file in os.listdir(_font_path):
                    font = pg.font.Font(os.path.join(_font_path, file), 24)
                    name = file.rsplit(".", 1)[0] # Prende il nome senza estensione
                    self.fonts[name] = font
    
            # Backgrounds
            if os.path.exists(_bg_path):
                for file in os.listdir(_bg_path):
                    bg = pg.image.load(os.path.join(_bg_path, file)).convert()
                    # Ridimensiona subito il background per evitare di farlo nel loop
                    bg = pg.transform.scale(bg, (self.WIDTH, self.HEIGHT)) 
                    name = file.rsplit(".", 1)[0]
                    self.backgrounds[name] = bg
    
            # Bottoni
            if os.path.exists(_btns_path):
                for file in os.listdir(_btns_path):
                    name = file.rsplit(".", 1)[0]
                    button = PNGButton(os.path.join(_btns_path, file),
                                       name=name, font=self.fonts['pixel'])
                    self.buttons[name] = button
                    
            # Sprites
            if os.path.exists(_sprites_path):
                for file in os.listdir(_sprites_path):
                    name = file.rsplit(".", 1)[0]
                    sprite = pg.image.load(os.path.join(_sprites_path, file)).convert_alpha()
                    sprite = pg.transform.scale(sprite, (50, 50))
                    self.sprites[name] = sprite
                    
                    
                    
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
            
        def drawGraph(self, graph: Graph,
                    surface: pg.Surface) -> Callable[[int, int],
                                                    tuple[int, int]]:
            to_screen: Callable = calcola_trasformazione(graph.get_zones(),
                                                         surface.get_width(),
                                                         surface.get_height())
            for c in graph.get_connections():
                self.drawConnection(c, surface, to_screen)
            for z in graph.get_zones():
                self.drawZone(z, surface, to_screen)
            
            #ritorno la funzione di calcolo per poi poter posizionare i droni con le giuste coordinate
            return to_screen
        
    
    class DroneRenderer:
        def __init__(self, img: pg.Surface):
            self.img = img
        
        def drawDrone(self, screen: pg.Surface,
                    d: Drone,
                    ft_mapping: Callable[[int, int], tuple[int, int]] = None) -> None:
            x, y = d.get_coordinates()
            if ft_mapping:
                x, y = ft_mapping(x, y)
            img_rect = self.img.get_rect(center=(x, y))
            screen.blit(self.img, img_rect)
            print(f"{d.ID} : {x}, {y}")
            
        
        def drawDrones(self, screen: pg.Surface, graph: Graph,
                    ft_mapping: Callable[[int, int], tuple[int, int]] = None) -> None:
            for d in graph.get_drones():
                self.drawDrone(screen, d, ft_mapping)