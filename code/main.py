from settings import *
from sys import exit
from os import path
from random import choice

# components
from game import Game
from preview import Preview
from score import Score


class Main:
    def __init__(self) -> None:
        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Tetris")

        # shapes
        self.next_shapes = [choice(list(TETROMINOS.keys())) for shape in range(3)]

        # components
        self.game = Game(self.get_next_shape, self.update_score)
        self.preview = Preview()
        self.score = Score()

        # audio
        self.music = pygame.mixer.Sound(path.join(".", "sounds", "music.wav"))
        self.music.set_volume(0.05)
        self.music.play(-1)

    def update_score(self, lines, score, level) -> None:
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

    def get_next_shape(self) -> str:
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETROMINOS.keys())))
        return next_shape

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # display
            self.display_surface.fill(GRAY)

            self.game.run()
            self.preview.run(self.next_shapes)
            self.score.run()

            # updating the game
            pygame.display.update()
            self.clock.tick(FRAME_RATE)


if __name__ == "__main__":
    main = Main()
    main.run()
