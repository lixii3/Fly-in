import sys
import pygame as pg
import copy


class PNGButton(pg.sprite.Sprite):
    """Interactive pygame sprite backed by a PNG image."""

    def __init__(
        self,
        image_path: str,
        name: str = "",
        x: int = 0,
        y: int = 0,
        text: str = "",
        font: pg.font.Font = None,
        text_color: tuple = (255, 255, 255),
        outline_color: tuple = (0, 0, 0),
        outline_thickness: int = 2,
        glow_color=(255, 255, 0),
        glow_radius=15,
        glow_passes=10
    ):
        """Create a clickable image button with optional text and glow.

        Args:
            image_path (str): Path to the button image.
            name (str, optional): Button name. Defaults to "".
            x (int, optional): Initial horizontal position. Defaults to 0.
            y (int, optional): Initial vertical position. Defaults to 0.
            text (str, optional): Initial label. Defaults to "".
            font (pg.font.Font, optional): Font used for labels.
            text_color (tuple, optional): Label color.
            outline_color (tuple, optional): Label outline color.
            outline_thickness (int, optional): Label outline width.
            glow_color (tuple, optional): Hover glow color.
            glow_radius (int, optional): Glow radius.
            glow_passes (int, optional): Number of glow layers.
        """
        super().__init__()

        # Salviamo i parametri per poterli riutilizzare nel metodo add_text
        self.name = name
        if font:
            self.font = font
        else:
            self.font = pg.font.SysFont("Arial", 35)
        self.text_color = text_color
        self.outline_color = outline_color
        self.outline_thickness = outline_thickness

        try:
            # Carica l'immagine originale
            loaded_image = pg.image.load(image_path).convert_alpha()
            
            # Ricava la lista dei rettangoli dei pixel visibili
            mask = pg.mask.from_surface(loaded_image)
            rects = mask.get_bounding_rects()
            
            if rects:
                # Unisce tutti i rettangoli trovati in un unico rettangolo contenitore
                visible_rect = pg.Rect.unionall(rects[0], rects[1:])
                self.base_image = loaded_image.subsurface(visible_rect).copy()
            else:
                self.base_image = loaded_image
        except FileNotFoundError:
            self.base_image = pg.Surface((150, 50), pg.SRCALPHA)
            pg.draw.rect(
                self.base_image, (200, 50, 50), (0, 0, 150, 50)
            )

        # L'immagine originale di partenza è un clone della base pulita
        self.original_image = self.base_image.copy()

        # Parametri Glow e Sprite
        self.glow_color = glow_color
        self.glow_radius = glow_radius
        self.glow_passes = glow_passes

        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_hovered = False

        # Se viene passato un testo all'avvio
        if text:
            self.add_text(text)
        else:
            self.glow_image = self._create_glow_image()
        self.mask = pg.mask.from_surface(self.original_image)
    
    
    def __deepcopy__(self, memo):
        """Create an independent copy of the button and its surfaces.

        Args:
            memo (dict): Memoization dictionary used by ``deepcopy``.

        Returns:
            PNGButton: Copied button.
        """
        if id(self) in memo:
            return memo[id(self)]

        # Crea una nuova istanza vuota
        cls = self.__class__
        new_btn = cls.__new__(cls)
        memo[id(self)] = new_btn
        
        # Inizializza la parte Sprite
        super(PNGButton, new_btn).__init__()

        # Copia gli attributi di base e i parametri
        new_btn.name = self.name
        new_btn.text_color = self.text_color
        new_btn.outline_color = self.outline_color
        new_btn.outline_thickness = self.outline_thickness
        new_btn.glow_color = self.glow_color
        new_btn.glow_radius = self.glow_radius
        new_btn.glow_passes = self.glow_passes
        new_btn.is_hovered = self.is_hovered
        new_btn.font = self.font

        # Clono le Surfaces con .copy()
        new_btn.base_image = self.base_image.copy()
        new_btn.original_image = self.original_image.copy()
        new_btn.glow_image = self.glow_image.copy()

        # Collega l'immagine visibile corretta
        if self.image is self.original_image:
            new_btn.image = new_btn.original_image
        elif self.image is self.glow_image:
            new_btn.image = new_btn.glow_image
        else:
            new_btn.image = self.image.copy()

        # Clona il rect
        new_btn.rect = self.rect.copy()
        new_btn.mask = pg.mask.from_surface(new_btn.original_image)

        return new_btn

    def _create_glow_image(self) -> pg.Surface:
        """Build the hover image by outlining the button mask.

        Returns:
            pg.Surface: Surface containing the glow and original image.
        """
        mask = pg.mask.from_surface(self.original_image)
        padding = self.glow_radius * 2
        glow_size = (self.rect.width + padding, self.rect.height + padding)
        glow_surface = pg.Surface(glow_size, pg.SRCALPHA)

        # creo il fade del glow strato per strato
        base_alpha = 100
        for p in range(self.glow_passes):
            thickness = int((p + 1) * self.glow_radius / self.glow_passes)
            alpha = int(base_alpha * (1 - p / self.glow_passes))

            if thickness <= 0:
                continue

            points = mask.outline(thickness)
            if not points:
                continue

            contour_surf = pg.Surface(glow_size, pg.SRCALPHA)
            for pt in points:
                pg.draw.circle(
                    contour_surf,
                    (*self.glow_color, alpha),
                    (pt[0] + self.glow_radius, pt[1] + self.glow_radius),
                    1,
                )
            glow_surface.blit(contour_surf, (0, 0))

        glow_surface.blit(
            self.original_image, (self.glow_radius, self.glow_radius)
        )
        return glow_surface
    
    def add_text(self, text: str) -> None:
        """Render a label onto the button and rebuild its glow.

        Args:
            text (str): Label to render.
        """
        # Resetta l'immagine all'originale pulita
        self.original_image = self.base_image.copy()

        # Rendering del testo
        if text and self.font:
            text_surf = self.font.render(text, False, self.text_color)
            outline_surf = self.font.render(text, False, self.outline_color)

            # Crea una superficie per il testo (incluso lo spessore del bordo)
            tw = text_surf.get_width() + self.outline_thickness * 2
            th = text_surf.get_height() + self.outline_thickness * 2
            combined_text_surf = pg.Surface((tw, th), pg.SRCALPHA)

            # Disegna il bordo
            for dx in range(-self.outline_thickness, self.outline_thickness + 1):
                for dy in range(-self.outline_thickness, self.outline_thickness + 1):
                    if dx != 0 or dy != 0:
                        combined_text_surf.blit(
                            outline_surf,
                            (dx + self.outline_thickness, dy + self.outline_thickness),
                        )

            # Disegna il testo principale
            combined_text_surf.blit(
                text_surf, (self.outline_thickness, self.outline_thickness)
            )

            padding = 20
            
            # Se il testo supera la larghezza attuale della base
            if combined_text_surf.get_width() + padding > self.base_image.get_width():
                new_width = combined_text_surf.get_width() + padding
                new_height = self.base_image.get_height()
                
                # Scaliamo sia la base_image che l'original_image per mantenere la coerenza
                self.base_image = pg.transform.scale(self.base_image, (new_width, new_height))
                self.original_image = self.base_image.copy()

            # Aggiorniamo subito il rect con le nuove dimensioni
            topleft_pos = self.rect.topleft if hasattr(self, 'rect') else (0, 0)
            self.rect = self.original_image.get_rect(topleft=topleft_pos)

            # Ricalcolo il centro
            btn_center_x = self.original_image.get_width() // 2
            btn_center_y = self.original_image.get_height() // 2
            text_rect = combined_text_surf.get_rect(
                center=(btn_center_x, btn_center_y)
            )

            # Applico il testo e aggiorno la maschera
            self.original_image.blit(combined_text_surf, text_rect)
            self.mask = pg.mask.from_surface(self.original_image)

        # Rigenera l'effetto glow
        self.glow_image = self._create_glow_image()

        # Imposta l'immagine visibile finale
        if self.is_hovered:
            self.image = self.glow_image
            self.rect = self.image.get_rect(
                topleft=(self.rect.x - self.glow_radius, self.rect.y - self.glow_radius)
            )
        else:
            self.image = self.original_image

    def update(self) -> None:
        """Update hover state using pixel-perfect mouse collision."""
        mouse_pos = pg.mouse.get_pos()
        was_hovered = self.is_hovered
        
        # 1. Controllo base sul rettangolo (molto veloce)
        if self.rect.collidepoint(mouse_pos):
            # 2. Calcola le coordinate relative del mouse all'interno del rettangolo
            rel_x = mouse_pos[0] - self.rect.x
            rel_y = mouse_pos[1] - self.rect.y
            
            # Se stiamo disegnando il glow, il rect attuale è più grande!
            # Dobbiamo sottrarre il raggio per calibrare le coordinate con la maschera originale.
            if self.image is self.glow_image:
                rel_x -= self.glow_radius
                rel_y -= self.glow_radius
            
            # 3. Controllo collisione Pixel-Perfect
            try:
                # get_at ritorna 1 se il pixel non è trasparente, 0 se è trasparente
                self.is_hovered = bool(self.mask.get_at((rel_x, rel_y)))
            except IndexError:
                # Se le coordinate sforano la maschera originale, ignoriamo
                self.is_hovered = False
        else:
            self.is_hovered = False

        # --- LOGICA DEL CAMBIO IMMAGINE (invariata) ---
        if self.is_hovered and not was_hovered:
            self.image = self.glow_image
            actual_x, actual_y = self.rect.topleft
            self.rect = self.image.get_rect(
                topleft=(
                    actual_x - self.glow_radius,
                    actual_y - self.glow_radius,
                )
            )
        elif not self.is_hovered and was_hovered:
            self.image = self.original_image
            actual_x, actual_y = self.rect.topleft
            self.rect = self.image.get_rect(
                topleft=(
                    actual_x + self.glow_radius,
                    actual_y + self.glow_radius,
                )
            )
            
    def is_clicked(self, event_list: list) -> bool:
        """Return whether a left-click occurred while hovered.

        Args:
            event_list (list): Pygame events to inspect.

        Returns:
            bool: Whether this button was clicked.
        """
        if self.is_hovered:
            for event in event_list:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    return True
        return False