import sys
import pygame


class PNGButton(pygame.sprite.Sprite):

    def __init__(
        self,
        image_path: str,
        x: int = 0,
        y: int = 0,
        text: str = "",
        font: pygame.font.Font = None,
        text_color: tuple = (255, 255, 255),
        outline_color: tuple = (0, 0, 0),
        outline_thickness: int = 2,
        glow_color=(255, 255, 0),
        glow_radius=15,
        glow_passes=10,
    ):
        super().__init__()

        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            self.original_image = pygame.Surface((150, 50), pygame.SRCALPHA)
            pygame.draw.rect(
                self.original_image, (200, 50, 50), (0, 0, 150, 50)
            )

        # Rendering del testo
        if text and font:
            text_surf = font.render(text, False, text_color)
            outline_surf = font.render(text, False, outline_color)

            # Crea una superficie per il testo
            tw = text_surf.get_width() + outline_thickness * 2
            th = text_surf.get_height() + outline_thickness * 2
            combined_text_surf = pygame.Surface((tw, th), pygame.SRCALPHA)

            # Disegna il bordo nero
            for dx in range(-outline_thickness, outline_thickness + 1):
                for dy in range(-outline_thickness, outline_thickness + 1):
                    if dx != 0 or dy != 0:
                        combined_text_surf.blit(
                            outline_surf,
                            (dx + outline_thickness, dy + outline_thickness),
                        )

            # Disegna il testo principale centrato
            combined_text_surf.blit(
                text_surf, (outline_thickness, outline_thickness)
            )

            # Stampa il testo completo con bordo al centro del bottone
            btn_center_x = self.original_image.get_width() // 2
            btn_center_y = self.original_image.get_height() // 2
            text_rect = combined_text_surf.get_rect(
                center=(btn_center_x, btn_center_y)
            )

            self.original_image.blit(combined_text_surf, text_rect)

        # 3. Parametri Glow e Sprite
        self.glow_color = glow_color
        self.glow_radius = glow_radius
        self.glow_passes = glow_passes

        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_hovered = False

        # Genera il bagliore attorno all'immagine (che ora include anche il testo)
        self.glow_image = self._create_glow_image()

    def _create_glow_image(self) -> pygame.Surface:
        mask = pygame.mask.from_surface(self.original_image)
        padding = self.glow_radius * 2
        glow_size = (self.rect.width + padding, self.rect.height + padding)
        glow_surface = pygame.Surface(glow_size, pygame.SRCALPHA)

        base_alpha = 100
        for p in range(self.glow_passes):
            thickness = int((p + 1) * self.glow_radius / self.glow_passes)
            alpha = int(base_alpha * (1 - p / self.glow_passes))

            if thickness <= 0:
                continue

            points = mask.outline(thickness)
            if not points:
                continue

            contour_surf = pygame.Surface(glow_size, pygame.SRCALPHA)
            for pt in points:
                pygame.draw.circle(
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

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)

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
        if self.is_hovered:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return True
        return False