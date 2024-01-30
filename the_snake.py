from random import randint
from typing import Optional

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MIDDLE_SCREEN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FIELD_SIZE = GRID_WIDTH * GRID_HEIGHT
NOISE_SIZE = 5

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BACKGROUND_COLOR = (176, 128, 83)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (255, 100, 55)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (77, 55, 41)
DEFAULT_COLOR = (0, 0, 0)

# Скорость движения змейки:
GAME_SPEED = 20
SNAKE_SPEED = 5
DEFAULT_COUNT_APPLES = 10
DEFAULT_COUNT_BAD_APPLES = 5
DEFAULT_COUNT_STONES = 5

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Создание поверхности для фона
background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Заполнение поверхности цветом песка
background_surface.fill(BACKGROUND_COLOR)
for i in range(0, SCREEN_WIDTH, NOISE_SIZE):
    for j in range(0, SCREEN_HEIGHT, NOISE_SIZE):
        rnd_r = randint(BACKGROUND_COLOR[0] - 2, BACKGROUND_COLOR[0] + 2)
        rnd_g = randint(BACKGROUND_COLOR[1] - 2, BACKGROUND_COLOR[1] + 2)
        rnd_b = randint(BACKGROUND_COLOR[2] - 2, BACKGROUND_COLOR[2] + 2)
        pygame.draw.rect(
            background_surface,
            (rnd_r, rnd_g, rnd_b),
            (i, j, NOISE_SIZE, NOISE_SIZE)
        )

# Отрисовка поверхности на экране
screen.blit(background_surface, (0, 0))

game_caption = pygame.display.set_caption
game_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject():

    def __init__(self,
                 body_color: tuple[int, int, int] = DEFAULT_COLOR) -> None:
        self.position: tuple[int, int] = MIDDLE_SCREEN
        self.body_color = body_color

    def draw(self, surface) -> None:
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def randomize_position(self) -> None:
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


class Apple(GameObject):

    def __init__(self,
                 body_color: tuple[int, int, int] = APPLE_COLOR,
                 is_good_apple: bool = True) -> None:
        super().__init__(body_color)
        self.randomize_position()
        self.is_good_apple = is_good_apple


class Stone(GameObject):

    def __init__(self,
                 body_color: tuple[int, int, int] = STONE_COLOR) -> None:
        super().__init__(body_color)
        self.randomize_position()


class Snake(GameObject):

    def __init__(self,
                 body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        self.positions = [self.position]
        self.length: int = 1
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        self.last: Optional[tuple[int, int]] = None

    def update_direction(self) -> None:
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> tuple[int, int]:
        return self.positions[0]

    def new_x_y_pos(self) -> tuple[int, int]:
        new_x_pos, new_y_pos = self.get_head_position()
        new_x_pos = new_x_pos + self.direction[0] * GRID_SIZE
        new_y_pos = new_y_pos + self.direction[1] * GRID_SIZE

        if new_x_pos < 0 or new_x_pos == SCREEN_WIDTH:
            new_x_pos = SCREEN_WIDTH - new_x_pos * self.direction[0]

        if new_y_pos < 0 or new_y_pos == SCREEN_HEIGHT:
            new_y_pos = SCREEN_HEIGHT - new_y_pos * self.direction[1]

        return (new_x_pos, new_y_pos)

    def draw(self, surface) -> None:
        for position in self.positions:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BACKGROUND_COLOR, last_rect)

    def move(self) -> None:
        new_x_pos, new_y_pos = self.new_x_y_pos()
        head_snake = (new_x_pos, new_y_pos)
        self.last = self.positions.pop()
        self.positions = [head_snake] + self.positions

    def reset(self) -> None:
        Snake.__init__(self)

    def eat(self, apple: Apple) -> None:
        if apple.is_good_apple:
            self.positions = [apple.position] + self.positions
        elif self.length > 1:
            self.positions.pop()

        self.length = len(self.positions)

    def can_bite_itself(self) -> bool:
        return self.new_x_y_pos() in self.positions

    def try_bite(self, this: GameObject) -> bool:
        return this.position == self.new_x_y_pos()


class GameManager():

    def __init__(self) -> None:
        self.is_run: bool = True
        self.__slow_count: int = SNAKE_SPEED

    def run(self) -> bool:
        return self.is_run

    def slow_mode(self) -> bool:
        self.__slow_count -= 1
        if self.__slow_count < 1:
            self.__slow_count = SNAKE_SPEED

        return self.__slow_count == SNAKE_SPEED

    def start_game(self):
        pass


def handle_keys(game_obj: Snake) -> None:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            quit_game()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_obj.direction != DOWN:
                game_obj.next_direction = UP
            elif event.key == pygame.K_DOWN and game_obj.direction != UP:
                game_obj.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_obj.direction != RIGHT:
                game_obj.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_obj.direction != LEFT:
                game_obj.next_direction = RIGHT


def quit_game() -> None:
    pygame.quit()
    raise SystemExit


def get_good_apples(count: int) -> list:
    return [Apple() for _ in range(0, count)]


def get_stones(count: int) -> list:
    return [Stone() for _ in range(0, count)]


def get_bad_apples(count: int) -> list:
    return [Apple(BAD_APPLE_COLOR, False) for _ in range(0, count)]


def get_obstacles_position(obstacles: list[GameObject]) -> list:
    return [obstacle.position for obstacle in obstacles]


def set_uniques_positions(obstacles: list[GameObject],
                          snake_position: tuple[int, int]) -> None:
    new_obstacles_pos: list = []

    for obstacle in obstacles:
        obstacle.randomize_position()

        while (obstacle.position == snake_position
               or obstacle.position in new_obstacles_pos):
            obstacle.randomize_position()

        new_obstacles_pos += [obstacle.position]


def set_this_new_position(apple: Apple, distroyed_apple: Apple,
                          snake: Snake, obstacles: list[GameObject]) -> None:
    obstacles_pos: list = get_obstacles_position(obstacles)
    snake_pos: list = snake.positions
    distroyed_apple.position = apple.position

    while (apple.position in snake_pos or apple.position in obstacles_pos):
        apple.randomize_position()

    distroyed_apple.draw(screen)


def snake_can_move(snake: Snake, obstacles, distroyed_apple) -> bool:
    reset: bool = False

    if snake.can_bite_itself():
        reset = True

    for this in obstacles:

        if snake.try_bite(this) and type(this) is Apple:
            snake.eat(this)

            if snake.length + len(obstacles) <= FIELD_SIZE:
                set_this_new_position(this, distroyed_apple,
                                      snake, obstacles)
                return False
            else:
                reset = True

        elif snake.try_bite(this) and type(this) is Stone:
            reset = True

        if reset:
            snake.reset()
            set_uniques_positions(obstacles, snake.position)
            return False

    return True


def main():
    game = GameManager()
    snake = Snake()
    distroyed_apple = Apple(DEFAULT_COLOR)
    good_apples = get_good_apples(DEFAULT_COUNT_APPLES)
    bad_apples = get_bad_apples(DEFAULT_COUNT_BAD_APPLES)
    stones = get_stones(DEFAULT_COUNT_STONES)
    obstacles = good_apples + bad_apples + stones
    set_uniques_positions(obstacles, snake.position)

    while game.run():
        screen.blit(background_surface, (0, 0))
        snake.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)

        handle_keys(snake)

        if game.slow_mode():
            snake.update_direction()

            if snake_can_move(snake, obstacles, distroyed_apple):
                snake.move()

        clock.tick(GAME_SPEED)
        free_cell = FIELD_SIZE - snake.length - len(obstacles)
        game_caption(f'{snake.length = },  {free_cell = }, {FIELD_SIZE = }')
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
