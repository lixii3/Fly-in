from __future__ import annotations
import pygame as pg
import os
from enum import Enum
from copy import deepcopy
from fly_in.src.graph import Graph
from fly_in.src.rendering.graphRenderer import GraphRenderer
from fly_in.src.rendering.pngButton import PNGButton


class ApplicationException(Exception):
    def __init__(self, msg: str=""):
        self.msg = msg
        super().__init__(msg)
        
    def __str__(self):
         return self.msg

class Mode(Enum):
    NONE = None
    MENU = "menu"
    MAPS = "maps"
    ABOUT = "about"
    LEVELS = "levels"
    
    
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
        self.__active_sprites = pg.sprite.Group()
        
        self._load_resources()
        
        pg.display.set_caption(f"FLY-IN by lmongili")
        self._change_mode(Mode.MENU)
        
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
        for btn in self.__active_sprites:
            if btn.is_clicked(events):
                self._click(btn.name)
                break   
                        
    def _click(self, event_name: str) -> None:
        if event_name in ["maps", "about"]:
            self._change_mode(Mode.get(event_name))
    
        elif event_name == "back":
            self._change_mode(self.MODE.get_back())
        elif event_name == "quit":
            self.__running = False
            return
    
    def _update(self) -> None:
        self.__active_sprites.update()

    def _change_mode(self, new_mode: Mode) -> None:
        """Cambia lo stato del gioco, aggiorna lo sfondo e prepara i bottoni."""
        self.MODE = new_mode
        if self.MODE is Mode.NONE:
            self.__running = False
            return
        self.__active_sprites.empty() # Rimuove i vecchi bottoni
        
        titles: list[str] = []
        start_y = self.HEIGHT // 2 - 100
        spacing_y = 100
        
        def create_btns(titles: list[str], button: PNGButton,
                        start_y: int, spacing_y: int) -> None:
            for i, t in enumerate(titles):
                if "menu" in self.buttons:
                    btn = deepcopy(button)
                    btn.name = t
                    btn.add_text(t)
                    # Li posiziona in colonna al centro
                    btn.rect.center = (self.WIDTH // 2, start_y + (i * spacing_y))
                    self.__active_sprites.add(btn)

        if self.MODE == Mode.MENU:
            titles = ["maps", "about", "quit"]
            # 1. Recupera il bottone 'menu' se esiste
            if "menu" in self.buttons:
                create_btns(titles, self.buttons["menu"], start_y, spacing_y)

        elif self.MODE == Mode.MAPS:
            _maps_path = "fly_in/maps"
            titles = os.listdir(_maps_path)
            titles = [dir for dir in titles if 
                      os.path.isdir(os.path.join(_maps_path, dir))]
            if "menu" in self.buttons:
                create_btns(titles, self.buttons["menu"], start_y, spacing_y)
                
        elif self.MODE == Mode.ABOUT:
            titles = ["back"]
            if "menu" in self.buttons:
                create_btns(titles, self.buttons["menu"], start_y + self.HEIGHT // 3, spacing_y)
        
    def _draw(self) -> None:
        self.BG = self.backgrounds.get(self.MODE.value)
        if self.BG:
            self.SCREEN.blit(self.BG, (0, 0))
        else:
            self.SCREEN.fill((0, 0, 0))

        # Disegna tutti gli sprite attivi
        self.__active_sprites.draw(self.SCREEN)

        pg.display.flip()


if __name__ == '__main__':
    app = Application()
    app.run()