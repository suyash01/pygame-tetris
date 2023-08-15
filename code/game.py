from settings import *
from random import choice
from sys import exit
from os import path
from timer import Timer


class Game:
    def __init__(self, get_next_shape, update_score) -> None:
        # general
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft=(PADDING, PADDING))
        self.sprite = pygame.sprite.Group()

        self.get_next_shape = get_next_shape
        self.update_score = update_score

        # grid
        self.grid_surface = self.surface.copy()
        self.grid_surface.fill((0, 255, 0))
        self.grid_surface.set_colorkey((0, 255, 0))
        self.grid_surface.set_alpha(120)

        # sprite
        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),
            self.sprite,
            self.create_new_tetromino,
            self.field_data,
        )

        # timer
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.3
        self.down_pressed = False
        self.timers = {
            "vertical_move": Timer(self.down_speed, True, self.move_down),
            "horizontal_move": Timer(MOVE_WAIT_TIME),
            "rotate": Timer(ROTATE_WAIT_TIME),
        }
        self.timers["vertical_move"].activate()

        # score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

        # audio
        self.landing_sound = pygame.mixer.Sound(path.join(".", "sounds", "landing.wav"))
        self.landing_sound.set_volume(0.1)

    def calculate_score(self, num_lines) -> None:
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level
        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.3
            self.timers["vertical_move"].duration = self.down_speed
        self.update_score(self.current_lines, self.current_score, self.current_level)

    def check_game_over(self) -> None:
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                exit()

    def create_new_tetromino(self) -> None:
        self.landing_sound.play()
        self.check_game_over()
        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(),
            self.sprite,
            self.create_new_tetromino,
            self.field_data,
        )

    def timer_update(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def move_down(self) -> None:
        self.tetromino.move_down()

    def draw_grid(self) -> None:
        for col in range(1, COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(
                self.grid_surface, LINE_COLOR, (x, 0), (x, self.surface.get_height()), 1
            )
        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(
                self.grid_surface, LINE_COLOR, (0, y), (self.surface.get_width(), y), 1
            )
        self.surface.blit(self.grid_surface, (0, 0))

    def input(self) -> None:
        keys = pygame.key.get_pressed()

        # checking horizontal movement
        if not self.timers["horizontal_move"].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers["horizontal_move"].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers["horizontal_move"].activate()

        # checking rotation
        if not self.timers["rotate"].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate(-1)
                self.timers["rotate"].activate()

        # down speedup
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers["vertical_move"].duration = self.down_speed_faster
        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers["vertical_move"].duration = self.down_speed

    def check_finished_rows(self) -> None:
        # get full rows
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)
        if delete_rows:
            for delete_row in delete_rows:
                # delete full rows
                for block in self.field_data[delete_row]:
                    block.kill()
                # move blocks down
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            # rebuild field data
            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
            for block in self.sprite:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            # update score
            self.calculate_score(len(delete_rows))

    def run(self) -> None:
        # update
        self.input()
        self.timer_update()
        self.sprite.update()

        # drawing
        self.surface.fill(GRAY)
        self.sprite.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)


class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data) -> None:
        # setup
        self.shape = shape
        self.block_positions = TETROMINOS[shape]["shape"]
        self.color = TETROMINOS[shape]["color"]
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        # create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    # collision
    def next_move_horizontal_collide(self, block, amount) -> bool:
        collision_list = [
            block.horizontal_collide(int(block.pos.x + amount), self.field_data)
            for block in self.blocks
        ]
        return True if any(collision_list) else False

    def next_move_vertical_collide(self, block, amount) -> bool:
        collision_list = [
            block.vertical_collide(int(block.pos.y + amount), self.field_data)
            for block in self.blocks
        ]
        return True if any(collision_list) else False

    # movement
    def move_horizontal(self, amount) -> None:
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount

    def move_down(self) -> None:
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.create_new_tetromino()

    # rotate
    def rotate(self, direction) -> None:
        if self.shape != "O":
            pivot_pos = self.blocks[0].pos
            new_block_pos = [
                block.rotate(pivot_pos, direction) for block in self.blocks
            ]
            # collision check
            for pos in new_block_pos:
                if pos.x < 0 or pos.x >= COLUMNS:
                    return
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return
                if pos.y > ROWS:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_block_pos[i]


class Block(pygame.sprite.Sprite):
    def __init__(self, groups, pos, color) -> None:
        # general
        super().__init__(groups)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        # position
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft=self.pos * CELL_SIZE)

    def rotate(self, pivot_pos, direction) -> pygame.Vector2:
        return pivot_pos + (self.pos - pivot_pos).rotate(90 * direction)

    def horizontal_collide(self, x, field_data) -> bool:
        if not 0 <= x < COLUMNS:
            return True
        if field_data[int(self.pos.y)][x]:
            return True
        return False

    def vertical_collide(self, y, field_data) -> bool:
        if y >= ROWS:
            return True
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True
        return False

    def update(self) -> None:
        self.rect.topleft = self.pos * CELL_SIZE
