from __future__ import annotations
import pygame as pg
from fly_in.src.utils import Mode
from fly_in.src.parser import ParsingException, MultipleParsingExceptions
from fly_in.src.rendering.renderer import Renderer, RenderException
from fly_in.src.rendering.pngButton import PNGButton


class ApplicationException(Exception):
    def __init__(cls, msg: str=""):
        cls.msg = msg
        super().__init__(msg)
    
    def __str__(cls):
        return cls.msg


class Application:
    MODE: Mode = Mode.NONE
    __running = False
    __renderer = Renderer()

    def run(cls) -> None:
        cls.MODE = Mode.MENU
        try:
            cls._change_mode(cls.MODE)
        except (RenderException, ApplicationException):
            raise ApplicationException("init")
        # application loop
        cls.__running = True
        while cls.__running:
            events = pg.event.get()
            cls._handle_events(events)
            cls.__renderer._update(cls.MODE)
            cls.__renderer._draw(cls.MODE)
            cls.__renderer.update_frame()
        pg.quit()

    def schedule(cls):
        # Esempio di utilizzo (pseudo-codice per il tuo main loop):
        for drone in cls.__graph.get_drones():
            path = cls.__graph.get_min_cost_path(cls.__graph.get_start(), cls.__graph.get_end(), start_turn=0)
            
            if path:
                # Assegna il percorso al drone
                drone.set_path(path)
                
                # Effettua le prenotazioni fisiche su Zone e Connection per bloccare gli altri!
                for action, resource, turn in path:
                    if action in ("MOVE", "WAIT", "TRANSIT"):
                        resource.reserve(turn)
            else:
                print(f"Errore: nessun percorso trovato per {drone.ID}")
    def _handle_events(cls, events: list) -> None:
        for event in events:
            if event.type == pg.QUIT:
                cls.__running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    cls.__running = False
        # click su bottoni attivi
        btn: PNGButton
        for btn in cls.__renderer.get_active_buttons():
            if btn.is_clicked(events):
                try:
                    cls._click(btn.name)
                    break
                except ApplicationException:
                    cls.__running = False
                        
    def _click(cls, event_name: str) -> None:
        _btn_names = [sp.name for sp in cls.__renderer.get_active_buttons()]
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
        except ApplicationException:
            raise ApplicationException("_click")
        

    def _change_mode(cls, new_mode: Mode,
                     clicked: str="") -> None:
        cls.MODE = new_mode
        try:
           cls.__renderer.render_mode(cls.MODE, clicked)
        except (RenderException, ParsingException, MultipleParsingExceptions) as e:
            raise ApplicationException("change_mode")
        

if __name__ == '__main__':
    try:
        app = Application()
        app.run()
    except ApplicationException as e:
        print(e.errors())
    