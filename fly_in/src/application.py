import pygame as pg
import os
from fly_in.src.graph import Graph
from fly_in.src.rendering.graphRenderer import GraphRenderer
from fly_in.src.rendering.pngButton import PNGButton


class ApplicationException(Exception):
    def __init__(self, msg: str=""):
        self.msg = msg
        super().__init__(msg)
        
    def __str__(self):
         return self.msg


class Application:
    def __init__(self):
        pg.init()
        self.SCREEN = pg.display.set_mode()
        self.WIDTH = self.SCREEN.get_width()
        self.HEIGHT = self.SCREEN.get_height()
        self.FPS = 60
        self.CLOCK = pg.time.Clock()
        self.MODE = None
        self.running = False
        self.active_sprites = pg.sprite.Group()
        
        self._load_resources()
        
        pg.display.set_caption(f"FLY-IN by lmongili")
        self._change_mode("menu")
        
    def _load_resources(self) -> None:
        self.fonts = {}
        self.backgrounds = {}
        self.buttons = {}

        _font_path = "fly_in/src/rendering/resources/fonts"
        _bg_path = "fly_in/src/rendering/resources/bg"
        _btns_path = "fly_in/src/rendering/resources/buttons"

        # Fonts
        if os.path.exists(_font_path):
            for file in os.listdir(_font_path):
                font = pg.font.Font(f"{_font_path}/{file}", 24)
                name = file.rsplit(".", 1)[0] # Prende il nome senza estensione
                self.fonts[name] = font

        # Backgrounds
        if os.path.exists(_bg_path):
            for file in os.listdir(_bg_path):
                bg = pg.image.load(f"{_bg_path}/{file}").convert()
                # Ridimensiona subito il background per evitare di farlo nel loop
                bg = pg.transform.scale(bg, (self.WIDTH, self.HEIGHT)) 
                name = file.rsplit(".", 1)[0]
                self.backgrounds[name] = bg

        # Bottoni
        if os.path.exists(_btns_path):
            for file in os.listdir(_btns_path):
                name = file.rsplit(".", 1)[0]
                button = PNGButton(f"{_btns_path}/{file}", text=name, font=self.fonts['pixel'])
                self.buttons[name] = button

    def run(self) -> None:
        self.running = True
        self.MODE = 'menu'
        
        while self.running:
            events = pg.event.get()
            self._handle_events(events)
            self._update()
            self._draw()
            self.CLOCK.tick(self.FPS)
        pg.quit()
        
    def _change_mode(self, new_mode: str) -> None:
        """Cambia lo stato del gioco, aggiorna lo sfondo e prepara i bottoni."""
        self.MODE = new_mode
        self.active_sprites.empty() # Rimuove i vecchi bottoni

        if self.MODE == "menu":
            # 1. Recupera il bottone 'maps' se esiste
            if "maps" in self.buttons:
                btn_maps = self.buttons["maps"]
                # Lo centra
                btn_maps.rect.center = (self.WIDTH // 2, self.HEIGHT // 2)
                # Lo aggiunge agli sprite visibili
                self.active_sprites.add(btn_maps)

        elif self.MODE == "map_list":
            map_keys = ["easy", "medium", "hard", "challenger"]
            start_y = self.HEIGHT // 2 - 100
            spacing_y = 80
            
            for i, key in enumerate(map_keys):
                if key in self.buttons:
                    btn = self.buttons[key]
                    # Li posiziona in colonna al centro
                    btn.rect.center = (self.WIDTH // 2, start_y + (i * spacing_y))
                    self.active_sprites.add(btn)
                    

    def _handle_events(self, events: list) -> None:
        for event in events:
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
        # click su bottoni attivi
        for btn in self.active_sprites:
            if btn.is_clicked(events):
                for name, ref in self.buttons.items():
                    if ref == btn:
                        self._click(name)
                        break   
                        
    def _click(self, event_name: str) -> None:
        if event_name == "maps":
            self._change_mode("map_list")
            
        elif event_name == "documentation":
            self._change_mode("documentation")
            
        # Ritorno al menu da una mappa
        elif event_name in ["map1", "map2", "map3", "map4"]:
            print(f"Hai selezionato {event_name}!")
    
    
    def _update(self) -> None:
        self.active_sprites.update()
        
    def _draw(self) -> None:
        self.BG = self.backgrounds.get(self.MODE)
        if self.BG:
            self.SCREEN.blit(self.BG, (0, 0))
        else:
            self.SCREEN.fill((0, 0, 0))

        # 2. Disegna tutti gli sprite attivi
        self.active_sprites.draw(self.SCREEN)

        pg.display.flip()


if __name__ == '__main__':
    app = Application()
    app.run()