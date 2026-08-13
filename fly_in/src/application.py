from __future__ import annotations
import pygame as pg
import os
# from PIL import Image
from enum import Enum
from copy import deepcopy
from fly_in.src.graph import Graph
from fly_in.src.drone import Drone
from fly_in.src.parser import Parser, ParsingException, MultipleParsingExceptions
from fly_in.src.rendering.graphRenderer import GraphRenderer
from fly_in.src.rendering.droneRenderer import DroneRenderer
from fly_in.src.rendering.pngButton import PNGButton


_curr_path = ""
class ApplicationException(Exception):
    def __init__(self, msg: str="", err_list: list[Exception] | None = None):
        self.msg = msg
        self.err_list = err_list if err_list is not None else []
        super().__init__(msg)
        
    def errors(self):
        out = self.msg + "["
        for e in self.err_list:
            out += f"{e.__class__.__name__}: '{str(e)}', "
        out = out.rsplit(",", 1)[0] + " ]"
        return out
    
    def __str__(self):
        return self.msg

class Mode(Enum):
    NONE = None
    MENU = "menu"
    MAPS = "maps"
    ABOUT = "about"
    LEVELS = "levels"
    FLYING = "flying"
    
    
    def get_back(self) -> Mode:
        match self:
            case Mode.LEVELS: return Mode.MAPS
            case _: return self.MENU
    
    @classmethod
    def get(cls, mode: str):
        return cls.__members__.get(mode.upper(), Mode.NONE)


class Application:
    def __init__(self):
        pg.init()
        self.SCREEN = pg.display.set_mode()
        self.WIDTH = self.SCREEN.get_width()
        self.HEIGHT = self.SCREEN.get_height()
        self.FPS = 60
        self.CLOCK = pg.time.Clock()
        self.MODE: Mode = Mode.NONE
        self.__running = False
        self.__active_buttons: pg.sprite.Group[PNGButton] = pg.sprite.Group()
        self.__active_graph_surface = pg.Surface((1500, 900), flags=pg.SRCALPHA)
        self.__graph: Graph
        self.__gr: GraphRenderer = GraphRenderer()
        self.__dr: DroneRenderer = DroneRenderer("fly_in/src/rendering/resources/sprites/drone.png")
        
        self._load_resources()
        
        pg.display.set_caption(f"FLY-IN by lmongili")
        try:
            self._change_mode(Mode.MENU)
        except ApplicationException as e:
            err_list = list(e.err_list) if isinstance(e.err_list, list) else [e.err_list]
            err_list.append(e)
            raise ApplicationException("init", err_list)
        
    def _load_resources(self) -> None:
        self.fonts: dict[str, pg.font.Font] = {}
        self.backgrounds: dict[str, pg.Surface] = {}
        self.buttons: dict[str, PNGButton] = {}

        _font_path = "fly_in/src/rendering/resources/fonts"
        _bg_path = "fly_in/src/rendering/resources/bg"
        _btns_path = "fly_in/src/rendering/resources/buttons"

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

    def run(self) -> None:
        self.__running = True
        self.MODE = Mode.MENU
        
        while self.__running:
            events = pg.event.get()
            self._handle_events(events)
            self._update()
            self._draw()
            self.CLOCK.tick(self.FPS)
        pg.quit()
        

    def _handle_events(self, events: list) -> None:

        for event in events:
            if event.type == pg.QUIT:
                self.__running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.__running = False
        # click su bottoni attivi
        btn: PNGButton
        for btn in self.__active_buttons:
            if btn.is_clicked(events):
                self._click(btn.name)
                break   
                        
    def _click(self, event_name: str) -> None:
        _btn_names = [sp.name for sp in self.__active_buttons]
        try:
            if event_name in ["maps", "about"]:
                self._change_mode(Mode.get(event_name))
            elif event_name == "back":
                self._change_mode(self.MODE.get_back())
            elif event_name == "quit":
                self.__running = False
                return
            elif self.MODE == Mode.MAPS and event_name in set(_btn_names) - {"back"}:
                self._change_mode(Mode.LEVELS, event_name)
            elif self.MODE == Mode.LEVELS and event_name in set(_btn_names) - {"back"}:
                self._change_mode(Mode.FLYING, event_name)
        except ApplicationException as e:
            err_list = list(e.err_list) if isinstance(e.err_list, list) else [e.err_list]
            err_list.append(e)
            raise ApplicationException("_click", err_list)
            
    
    def _update(self) -> None:
        self.__active_buttons.update()
        
        if self.MODE == Mode.FLYING:
            if self.__graph:
                base_step = 1.0 / self.FPS        
                for drone in self.__graph.get_drones():
                    drone.update(base_step) # Passiamo il passo base al drone

    def _change_mode(self, new_mode: Mode,
                     clicked: str="") -> None:
        self.MODE = new_mode
        self.__active_buttons.empty() # Rimuove i vecchi bottoni

        if self.MODE is Mode.NONE:
            self.__running = False
            return
        # parametri per creazione bottoni base
        _clicked = clicked
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

        
        def create_btns(titles: list[str], button: PNGButton,
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

        def __menu_layout() -> None:
            titles = ["maps", "about", "quit"]
            create_btns(titles, _button,
                        start_y, spacing_y,
                        centered, start_x)
            
        def __maps_layout() -> None:
            titles = os.listdir(_maps_path)
            titles = [dir for dir in titles if 
                        os.path.isdir(os.path.join(_maps_path, dir))]
            titles.append("back")
            centered = False
            start_y = 150
            create_btns(titles, _button, start_y, spacing_y,
                        centered, start_x)
            
        def __about_layout() -> None:
            nonlocal start_y
            titles = ["back"]
            start_y = start_y + self.HEIGHT // 3
            create_btns(titles, _button, start_y,
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
            create_btns(titles, _button,
                        start_y, spacing_y,
                        centered, start_x)
        
        def __flying_layout() -> None:
            global _curr_path
            _curr_path = os.path.join(_curr_path, _clicked + ".txt")
            print(_curr_path)
            titles = ["back"]
            start_y = self.SCREEN.get_height() // 10 * 9 # posizione ad un quarto dalla fine dello schermo
            create_btns(titles, _button, start_y)
            try:
                self.__graph = Parser.parse_map(os.path.join(_curr_path))
            except (ParsingException, MultipleParsingExceptions) as e:
                err_list = [e]
                raise ApplicationException("__flying_layout", err_list)
            
        # SMISTAMENTO
        try:
            match self.MODE:
                case Mode.MENU: __menu_layout()
                case Mode.MAPS: __maps_layout()
                case Mode.ABOUT: __about_layout()
                case Mode.LEVELS: __levels_layout()
                case Mode.FLYING: __flying_layout()
                case _: self._change_mode(Mode.NONE)
        except ApplicationException as e:
            err_list = list(e.err_list) if isinstance(e.err_list, list) else [e.err_list]
            err_list.append(e)
            raise ApplicationException("change_mode", err_list)
        
    def _draw(self) -> None:
        self.BG = self.backgrounds.get(self.MODE.value)
        if self.MODE == Mode.LEVELS:
            self.BG = self.backgrounds.get(Mode.MAPS.value)
        if self.BG:
            self.SCREEN.blit(self.BG, (0, 0))
        else:
            self.SCREEN.fill((0, 0, 0))
        if self.MODE == Mode.FLYING:
            if not self.__active_graph_surface:
                raise ApplicationException("Unexistent graph to draw")
            self.__active_graph_surface.fill((0, 0, 0, 0))
            self.ft_mapping = self.__gr.drawGraph(self.__graph, self.__active_graph_surface)
            self.__dr.drawDrones(self.__active_graph_surface, self.__graph, self.ft_mapping)
            graph_rect = self.__active_graph_surface.get_rect()
            graph_rect.center = self.SCREEN.get_width() // 2, self.SCREEN.get_height() // 2
            self.SCREEN.blit(self.__active_graph_surface, graph_rect)
        # Disegna tutti gli sprite attivi
        self.__active_buttons.draw(self.SCREEN)
        pg.display.flip()

if __name__ == '__main__':
    #pg.init()
    #img = pg.image.load("fly_in/src/rendering/resources/buttons/menu.png")
    #img = pg.transform.scale(img, (150, img.get_height()))
    #img_rect = pg.Surface.get_rect(img)
    #screen = pg.display.set_mode()
    #c = pg.time.Clock()
    #r = True
    #while r:
    #    screen.blit(img, img_rect)
    #    pg.display.flip()
    #    c.tick(60)
    #    for event in pg.event.get():
    #        if event.type == pg.QUIT:
    #            r = False
    #pg.quit()
    try:
        app = Application()
        app.run()
    except ApplicationException as e:
        print(e.errors())
    