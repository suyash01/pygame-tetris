from settings import *
from os import path


class Preview:
    def __init__(self) -> None:
        # general
        self.surface = pygame.Surface(
            (SIDEBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION)
        )
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topright=(WINDOW_WIDTH - PADDING, PADDING))

        # shapes
        self.shape_surfaces = {
            shape: pygame.image.load(
                path.join(".", "graphics", f"{shape}.png")
            ).convert_alpha()
            for shape in TETROMINOS.keys()
        }

        # image positions
        self.fragment_height = self.surface.get_height() / 3

    def display_pieces(self, shapes) -> None:
        for i, shape in enumerate(shapes):
            shape_surface = self.shape_surfaces[shape]
            x = self.surface.get_width() / 2
            y = self.fragment_height / 2 + i * self.fragment_height
            shape_rect = shape_surface.get_rect(center = (x, y))
            self.surface.blit(shape_surface, shape_rect)

    def run(self, next_shapes) -> None:
        self.surface.fill(GRAY)
        self.display_pieces(next_shapes)
        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)
