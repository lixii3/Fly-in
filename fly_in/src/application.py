from __future__ import annotations
import pygame as pg
import os
# from PIL import Image
from copy import deepcopy
from fly_in.src.graph import Graph
from fly_in.src.drone import Drone
from fly_in.src.utils import Mode
from fly_in.src.parser import Parser, ParsingException, MultipleParsingExceptions
from fly_in.src.rendering.renderer import Renderer
from fly_in.src.rendering.graphRenderer import GraphRenderer
from fly_in.src.rendering.droneRenderer import DroneRenderer
from fly_in.src.rendering.pngButton import PNGButton


_curr_path = ""
class ApplicationException(Exception):
    def __init__(cls, msg: str="", err_list: list[Exception] | None = None):
        cls.msg = msg
        cls.err_list = err_list if err_list is not None else []
        super().__init__(msg)
        
    def errors(cls):
        out = cls.msg + "["
        for e in cls.err_list:
            out += f"{e.__class__.__name__}: '{str(e)}', "
        out = out.rsplit(",", 1)[0] + " ]"
        return out
    
    def __str__(cls):
        return cls.msg



class Application:
    pg.init()
    SCREEN = pg.display.set_mode()  #renderer
    WIDTH = SCREEN.get_width() #renderer
    HEIGHT = SCREEN.get_height() #renderer
    FPS = 60 #renderer
    CLOCK = pg.time.Clock() #renderer
    MODE: Mode = Mode.NONE
    __running = False
    __active_buttons: pg.sprite.Group[PNGButton] = pg.sprite.Group()
    __active_graph_surface = pg.Surface((1500, 900), flags=pg.SRCALPHA)
    __graph: Graph
    __renderer = Renderer()
    __gr: GraphRenderer = GraphRenderer()
    __dr: DroneRenderer = DroneRenderer("fly_in/src/rendering/resources/sprites/drone.png")
    def __init__(cls):
        
        cls._load_resources()
        
        pg.display.set_caption(f"FLY-IN by lmongili")
        try:
            cls._change_mode(Mode.MENU)
        except ApplicationException as e:
            err_list = list(e.err_list) if isinstance(e.err_list, list) else [e.err_list]
            err_list.append(e)
            raise ApplicationException("init", err_list)
    
    # spostato in renderer
    def _load_resources(cls) -> None:
        cls.fonts: dict[str, pg.font.Font] = {}
        cls.backgrounds: dict[str, pg.Surface] = {}
        cls.buttons: dict[str, PNGButton] = {}

        _font_path = "fly_in/src/rendering/resources/fonts"
        _bg_path = "fly_in/src/rendering/resources/bg"
        _btns_path = "fly_in/src/rendering/resources/buttons"

        # Fonts
        if os.path.exists(_font_path):
            for file in os.listdir(_font_path):
                font = pg.font.Font(os.path.join(_font_path, file), 24)
                name = file.rsplit(".", 1)[0] # Prende il nome senza estensione
                cls.fonts[name] = font

        # Backgrounds
        if os.path.exists(_bg_path):
            for file in os.listdir(_bg_path):
                bg = pg.image.load(os.path.join(_bg_path, file)).convert()
                # Ridimensiona subito il background per evitare di farlo nel loop
                bg = pg.transform.scale(bg, (cls.WIDTH, cls.HEIGHT)) 
                name = file.rsplit(".", 1)[0]
                cls.backgrounds[name] = bg

        # Bottoni
        if os.path.exists(_btns_path):
            for file in os.listdir(_btns_path):
                name = file.rsplit(".", 1)[0]
                button = PNGButton(os.path.join(_btns_path, file),
                                   name=name, font=cls.fonts['pixel'])
                cls.buttons[name] = button

    def run(cls) -> None:
        cls.__running = True
        cls.MODE = Mode.MENU
        
        while cls.__running:
            events = pg.event.get()
            cls._handle_events(events)
            cls._update()
            cls._draw()
            cls.CLOCK.tick(cls.FPS)
        pg.quit()
        

    def _handle_events(cls, events: list) -> None:

        for event in events:
            if event.type == pg.QUIT:
                cls.__running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    cls.__running = False
        # click su bottoni attivi
        btn: PNGButton
        for btn in cls.__active_buttons:
            if btn.is_clicked(events):
                cls._click(btn.name)
                break   
                        
    def _click(cls, event_name: str) -> None:
        _btn_names = [sp.name for sp in cls.__active_buttons]
        try:
            if event_name in ["maps", "about"]:
                cls._change_mode(Mode.get(event_name))
            elif event_name == "back":
                cls._change_mode(cls.MODE.get_back())
            elif event_name == "quit":
                cls.__running = False
                return
            elif cls.MODE == Mode.MAPS and event_name in set(_btn_names) - {"back"}:
                cls._change_mode(Mode.LEVELS, event_name)
            elif cls.MODE == Mode.LEVELS and event_name in set(_btn_names) - {"back"}:
                cls._change_mode(Mode.FLYING, event_name)
        except ApplicationException as e:
            err_list = list(e.err_list) if isinstance(e.err_list, list) else [e.err_list]
            err_list.append(e)
            raise ApplicationException("_click", err_list)
            
    
    def _update(cls) -> None:
        cls.__active_buttons.update()
        
        if cls.MODE == Mode.FLYING:
            if cls.__graph:
                base_step = 1.0 / cls.FPS        
                for drone in cls.__graph.get_drones():
                    drone.update(base_step) # Passiamo il passo base al drone

    def _change_mode(cls, new_mode: Mode,
                     clicked: str="") -> None:
        cls.MODE = new_mode
        cls.__active_buttons.empty() # Rimuove i vecchi bottoni

        if cls.MODE is Mode.NONE:
            cls.__running = False
            return
        # parametri per creazione bottoni base
        _clicked = clicked
        if "menu" in cls.buttons:
            _button: str = cls.buttons["menu"]
        else:
            _button = PNGButton("")
        _maps_path = "fly_in/maps"
        global _curr_path
        titles: list[str] = []
        start_y = cls.HEIGHT // 2 - 100
        spacing_y = 100
        centered= True
        start_x = 150

        
        def create_btns(titles: list[str], button: PNGButton,
                        start_y: int = 0,
                        spacing_y: int = 0,
                        centered: bool = True,
                        start_x: int = 0) -> None:
            for i, t in enumerate(titles):
                if t == "back" and "menu_white" in cls.buttons:
                    btn = deepcopy(cls.buttons["menu_white"])
                else:
                    btn = deepcopy(button)
                btn.name = t
                # Li posiziona in colonna
                if centered:
                    btn.rect.center = (cls.WIDTH // 2, start_y + (i * spacing_y))
                else:
                    btn.rect.center = (start_x, start_y + (i * spacing_y))
                # setto il text
                btn.add_text(t)
                cls.__active_buttons.add(btn)

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
            start_y = start_y + cls.HEIGHT // 3
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
            if "menu_white" in cls.buttons:
                _button = cls.buttons["menu_white"]
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
            start_y = cls.SCREEN.get_height() // 10 * 9 # posizione ad un quarto dalla fine dello schermo
            create_btns(titles, _button, start_y)
            try:
                cls.__graph = Parser.parse_map(os.path.join(_curr_path))
            except (ParsingException, MultipleParsingExceptions) as e:
                err_list = [e]
                raise ApplicationException("__flying_layout", err_list)
            
        # SMISTAMENTO
        try:
            match cls.MODE:
                case Mode.MENU: __menu_layout()
                case Mode.MAPS: __maps_layout()
                case Mode.ABOUT: __about_layout()
                case Mode.LEVELS: __levels_layout()
                case Mode.FLYING: __flying_layout()
                case _: cls._change_mode(Mode.NONE)
        except ApplicationException as e:
            err_list = list(e.err_list) if isinstance(e.err_list, list) else [e.err_list]
            err_list.append(e)
            raise ApplicationException("change_mode", err_list)
        
    def _draw(cls) -> None:
        cls.BG = cls.backgrounds.get(cls.MODE.value)
        if cls.MODE == Mode.LEVELS:
            cls.BG = cls.backgrounds.get(Mode.MAPS.value)
        if cls.BG:
            cls.SCREEN.blit(cls.BG, (0, 0))
        else:
            cls.SCREEN.fill((0, 0, 0))
        if cls.MODE == Mode.FLYING:
            if not cls.__active_graph_surface:
                raise ApplicationException("Unexistent graph to draw")
            cls.__active_graph_surface.fill((0, 0, 0, 0))
            cls.ft_mapping = cls.__gr.drawGraph(cls.__graph, cls.__active_graph_surface)
            cls.__dr.drawDrones(cls.__active_graph_surface, cls.__graph, cls.ft_mapping)
            graph_rect = cls.__active_graph_surface.get_rect()
            graph_rect.center = cls.SCREEN.get_width() // 2, cls.SCREEN.get_height() // 2
            cls.SCREEN.blit(cls.__active_graph_surface, graph_rect)
        # Disegna tutti gli sprite attivi
        cls.__active_buttons.draw(cls.SCREEN)
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
    