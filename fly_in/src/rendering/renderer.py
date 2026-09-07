from __future__ import annotations
from fly_in.src.rendering.pngButton import PNGButton
from copy import deepcopy
from fly_in.src.rendering.utils import calcola_trasformazione
from fly_in.src.utils import Tag, ZoneType
from fly_in.src.connection import Connection
from fly_in.src.graph import Graph
from fly_in.src.zone import Zone
from fly_in.src.drone import Drone
from fly_in.src.utils import Mode, FlyInException
from fly_in.src.scheduler import Scheduler, SchedulerException
from fly_in.src.parser import Parser, ParsingException, MultipleParsingExceptions
import os
import pygame as pg
from typing import Callable


_curr_path = ""

class RenderException(Exception):
    def __init__(self, msg: str = "") -> None:
        self.msg = msg
        super().__init__(msg)
        
    def __str__(self) -> str:
        return "Renderer Exception: " + self.msg

class Renderer:
    def __init__(self) -> None:
        self.name = "lixi"
        pg.init()
        self.SCREEN = pg.display.set_mode()
        pg.display.set_caption(f"FLY-IN by lmongili")
        self.WIDTH = self.SCREEN.get_width()
        self.HEIGHT = self.SCREEN.get_height()
        self.FPS = 60
        self.CLOCK = pg.time.Clock()
        self.__graph_surface = pg.Surface((1500, 900), flags=pg.SRCALPHA)
        self.__active_buttons: pg.sprite.Group[PNGButton] = pg.sprite.Group()
        self.__graph_surface = pg.Surface((1600, 1200), flags=pg.SRCALPHA)
        self.fonts: dict[str, pg.font.Font] = {}
        self.backgrounds: dict[str, pg.Surface] = {}
        self.buttons: dict[str, PNGButton] = {}
        self.sprites: dict[str, pg.Surface] = {}
        self.__graph: Graph
        self.__dr: DroneRenderer = DroneRenderer("fly_in/src/rendering/resources/sprites/drone.png")
        self.__scheduler: Scheduler
        self._load_resources()

    def _load_resources(self) -> None:
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
                if file.endswith("png") or file.endswith("jpg"):
                    name = file.rsplit(".", 1)[0]
                    button = PNGButton(os.path.join(_btns_path, file),
                                        name=name, font=self.fonts['pixel'])
                    self.buttons[name] = button
                
        # Sprites
        if os.path.exists(_sprites_path):
            for file in os.listdir(_sprites_path):
                if file.endswith("png") or file.endswith("jpg"):
                    name = file.rsplit(".", 1)[0]
                    sprite = pg.image.load(os.path.join(_sprites_path, file)).convert_alpha()
                    sprite = pg.transform.scale(sprite, (50, 50))
                    self.sprites[name] = sprite
    
    def get_active_buttons(self) -> pg.sprite.Group[PNGButton]:
        return self. __active_buttons
    
    def get_graph_surface(self) -> pg.Surface:
        return self. __graph_surface
                    
    def create_btns(self, titles: list[str],
                    button: PNGButton,
                    start_y: int = 0,
                    spacing_y: int = 0,
                    centered: bool = True,
                    start_x: int = 0) -> None:
        for i, t in enumerate(titles):
            if t == "back" and "menu_white" in self.buttons:
                btn = deepcopy(self.buttons["menu_white"])
            else:
                btn = deepcopy(button)
            btn.name = t
            # Li posiziona in colonna
            if centered:
                btn.rect.center = (self.WIDTH // 2, start_y + (i * spacing_y))
            else:
                btn.rect.center = (start_x, start_y + (i * spacing_y))
            # setto il text
            btn.add_text(t)
            self.__active_buttons.add(btn)

    def render_mode(self, mode: Mode,
                    _clicked: str) -> None:
        self.__active_buttons.empty() # Rimuove i vecchi bottoni
        if mode is None:
            raise RenderException("Invalid mode to render")
        
        if "menu" in self.buttons:
                _button: str = self.buttons["menu"]
        else:
            _button = PNGButton("")
        _maps_path = "fly_in/maps"
        global _curr_path
        titles: list[str] = []
        start_y = self.HEIGHT // 2 - 100
        spacing_y = 100
        centered= True
        start_x = 150

        def __menu_layout() -> None:
            self.__graph = None
            titles = ["maps", "about", "quit"]
            self.create_btns(titles, _button,
                        start_y, spacing_y,
                        centered, start_x)
            
        def __maps_layout() -> None:
            titles = os.listdir(_maps_path)
            titles = [dir for dir in titles if 
                        os.path.isdir(os.path.join(_maps_path, dir))]
            titles.append("back")
            centered = False
            start_y = 150
            self.create_btns(titles, _button, start_y, spacing_y,
                        centered, start_x)
            
        def __about_layout() -> None:
            nonlocal start_y
            titles = ["back"]
            start_y = start_y + self.HEIGHT // 3
            self.create_btns(titles, _button, start_y,
                        spacing_y, centered, start_x)
            
        def __levels_layout() -> None:
            global _curr_path
            _curr_path = os.path.join(_maps_path, _clicked)
            for filename in os.listdir(_curr_path):
                if os.path.isfile(os.path.join(_curr_path, filename)) and filename.endswith(".txt"):
                    name = filename.rsplit(".")[0]
                    titles.append(name)
            titles.append("back")
            if "menu_white" in self.buttons:
                _button = self.buttons["menu_white"]
            else:
                _button = PNGButton("")
            start_y = 150
            centered = False
            self.create_btns(titles, _button,
                        start_y, spacing_y,
                        centered, start_x)
        
        def __flying_layout() -> None:
            global _curr_path
            _curr_path = os.path.join(_curr_path, _clicked + ".txt")
            titles  = ["back"]
            start_y = self.SCREEN.get_height() // 10 * 9 # posizione ad un quarto dalla fine dello schermo
            self.create_btns(titles, _button, start_y)
            if not self.__graph:
                try:
                    Drone.zeroCounter()
                    self.__graph = Parser.parse_map(os.path.join(_curr_path))
                except (ParsingException, MultipleParsingExceptions) as e:
                    raise e

            self.__scheduler = Scheduler(self.__graph)
            try:
                self.__scheduler.schedule()
            except SchedulerException as e:
                raise RenderException(str(e))
            self.__turn_timer = 0
            self.__current_turn = 1

        # SMISTAMENTO
        try:
            match mode:
                case Mode.MENU: __menu_layout()
                case Mode.MAPS: __maps_layout()
                case Mode.ABOUT: __about_layout()
                case Mode.LEVELS: __levels_layout()
                case Mode.FLYING: __flying_layout()
                case _: self.render_mode(Mode.NONE, "")
        except RenderException as e:
            raise e

    def _draw(self, mode: Mode) -> None:
        self.BG = self.backgrounds.get(mode.value)
        if mode == Mode.LEVELS:
            self.BG = self.backgrounds.get(Mode.MAPS.value)
        if self.BG:
            self.SCREEN.blit(self.BG, (0, 0))
        else:
            self.SCREEN.fill((0, 0, 0))
        if mode == Mode.FLYING:
            if not self.__graph_surface:
                raise RenderException("Unexistent graph to draw")
            self.__graph_surface.fill((0, 0, 0, 0))
            self.ft_mapping = GraphRenderer.drawGraph(self.__graph, self.__graph_surface, self.sprites)
            self.__dr.drawDrones(self.__graph_surface, self.__graph, self.ft_mapping)
            graph_rect = self.__graph_surface.get_rect()
            graph_rect.center = self.SCREEN.get_width() // 2, self.SCREEN.get_height() // 2
            self.SCREEN.blit(self.__graph_surface, graph_rect)

            # rendering info testo info mappa
            try:
                font = self.fonts["pixel"]
            except KeyError:
                font = pg.font.Font("Arial")
            text = font.render(f"Total drones: {self.__graph.get_nb_drones()} --- "
                                      f"Total Turns: {self.__scheduler.TURNS} --- "
                                      f"Current Turn: {self.__current_turn - 1}",
                                      True, (255, 255, 255))
            text_rect = text.get_rect(topleft=(50, 50))
            self.SCREEN.blit(text, text_rect)

        # Disegna tutti gli sprite attivi
        self.__active_buttons.draw(self.SCREEN)
        
    def _update(self, mode: Mode) -> None:
        self.__active_buttons.update()
        
        if mode == Mode.FLYING:
           if self.__graph and self.__scheduler:
                if not hasattr(self, '_Renderer__turn_timer'):
                    self.__turn_timer = 0
                    self.__current_turn = 1

                    for drone in self.__graph.get_drones():
                        target_res = drone.get_action_at_turn(self.__current_turn)[1]
                        if target_res is not None:
                            drone.set_where(target_res)
                        else:
                            # Se un drone è in WAIT al turno 1, deve rimanere fermo
                            drone.set_where(drone.get_where())

                    # Inizializza i target del primo turno
                    for drone in self.__graph.get_drones():
                        target_res = drone.get_action_at_turn(self.__current_turn)[1]
                        if target_res is not None:
                            drone.set_where(target_res)
                        else:
                            # se un drone non ha azioni (es. percorso vuoto), lo teniamo fermo
                            drone.set_where(drone.get_where())
                
                # Calcola il progresso basato sui frame correnti
                progress = self.__turn_timer / self.FPS
                for drone in self.__graph.get_drones():
                    drone.progress = progress

                # Scatta un frame
                self.__turn_timer += 1
                
                # Quando il timer raggiunge gli FPS, il turno è finito
                if self.__turn_timer >= self.FPS:
                    self.__turn_timer = 0
                    if self.__current_turn <= self.__scheduler.TURNS:
                        self.__current_turn += 1
                    
                    # Carica le mosse per il nuovo turno
                    for drone in self.__graph.get_drones():
                        target_res = drone.get_action_at_turn(self.__current_turn)[1]
                        if target_res is not None:
                            drone.set_where(target_res)
                        else:
                            # il drone ha finito il suo percorso per questo livello.
                            drone.set_where(drone.get_where())

    def update_frame(self) -> None:
        pg.display.flip()
        self.CLOCK.tick(60)
                    
class GraphRenderer:
    @classmethod
    def drawConnection(cls, conn: Connection,
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
    
    @classmethod
    def drawZone(cls, zone: Zone,
                surface: pg.Surface,
                normalizer_funct: Callable | None=None,
                img: pg.Surface | None = None,
                radius: int=30) -> None:
        color = zone.get_color().value
        x, y = zone.get_coordinates()
        center = (x,y)
        if normalizer_funct:
            center = normalizer_funct(x, y)
        if img is None:
            pg.draw.circle(surface, color, center, radius)
        else:
            img_rect = img.get_rect(center=center)
            surface.blit(img, img_rect)
    
    @classmethod
    def drawGraph(cls, graph: Graph,
                surface: pg.Surface,
                sprites: dict[str, pg.Surface] | None = None) -> Callable[[int, int],
                                                            tuple[int, int]]:
        to_screen: Callable = calcola_trasformazione(graph.get_zones(),
                                                        surface.get_width(),
                                                        surface.get_height())
        for c in graph.get_connections():
            cls.drawConnection(c, surface, to_screen)
        img: pg.Surface
        for z in graph.get_zones():
            if sprites is not None:
                if z._tag == Tag.START_HUB and "start" in sprites:
                    img = sprites["start"]
                elif z._tag == Tag.END_HUB and "end" in sprites:
                    img = sprites["end"]
                else:
                    img = sprites.get(z.get_type().getName())
            cls.drawZone(z, surface, to_screen, img)
        
        #ritorno la funzione di calcolo per poi poter posizionare i droni con le giuste coordinate
        return to_screen
    

class DroneRenderer:
    def __init__(self, img: pg.Surface):
        self.img = pg.image.load(img).convert_alpha()
        self.img = pg.transform.scale(self.img, (80, 50))
    
import math # Ricordati di aggiungere questo import in cima al file renderer.py

class DroneRenderer:
    def __init__(self, img: pg.Surface):
        self.img = pg.image.load(img).convert_alpha()
        # Se i droni distanziati sembrano troppo grandi, potresti voler ridurre leggermente la scala
        self.img = pg.transform.scale(self.img, (80, 50)) 
    
    def drawDrone(self, screen: pg.Surface,
                d: Drone,
                ft_mapping: Callable[[int, int], tuple[int, int]] = None) -> None:

        x, y = DroneRenderer._get_render_coordinates(d)
        
        if ft_mapping:
            x1, y1 = ft_mapping(x, y)
        else:
            x1, y1 = x, y

        try:
            drone_index = int(d.ID[1:])
        except ValueError:
            drone_index = 0
            
        # Parametri dell'offset
        offset_radius = 15 # Distanza in pixel dal vero centro
        angle = drone_index * 1.5
        
        offset_x = math.cos(angle) * offset_radius
        offset_y = math.sin(angle) * offset_radius

        final_x = x1 + offset_x
        final_y = y1 + offset_y

        img_rect = self.img.get_rect(center=(final_x, final_y))
        screen.blit(self.img, img_rect)
    
    def drawDrones(self, screen: pg.Surface, graph: Graph,
                ft_mapping: Callable[[int, int], tuple[int, int]] = None) -> None:
        for d in graph.get_drones():
            self.drawDrone(screen, d, ft_mapping)


    @staticmethod
    def _get_render_coordinates(drone: Drone) -> tuple[float, float]:
        if not drone.get_where():
            return (0.0, 0.0)
            
        end_x, end_y = drone.get_where().get_coordinates()
        
        # Se il drone è fermo o non ha una posizione precedente
        if not drone.get_last_pos() or drone.get_where() == drone.get_last_pos():
            return (end_x, end_y)

        start_x, start_y = drone.get_last_pos().get_coordinates()

        # Interpolazione lineare
        curr_x = start_x + (end_x - start_x) * drone.progress
        curr_y = start_y + (end_y - start_y) * drone.progress
        
        return (curr_x, curr_y)
