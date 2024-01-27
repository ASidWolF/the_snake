from random import choice, randint
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

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (255, 100, 55)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20
DEFAULT_COUNT_APPLES = 1
DEFAULT_COUNT_BAD_APPLES = 1
DEFAULT_COUNT_ROCKS = 0

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
screen.fill(BOARD_BACKGROUND_COLOR)

# Настройка времени:
clock = pygame.time.Clock()


class GameObject():
    position: tuple[int, int]
    body_color: Optional[tuple[int, int, int]] = None

    def __init__(self):
        self.position = MIDDLE_SCREEN

    def draw(self, surface):
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


class Snake(GameObject):
    length: int = 1
    direction: tuple[int, int] = RIGHT
    next_direction: Optional[tuple[int, int]] = None

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR):
        super().__init__()
        self.body_color = body_color
        self.positions: list[tuple[int, int]] = [self.position]
        self.last: Optional[tuple[int, int]] = None

    def update_direction(self):
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

    def draw(self, surface):
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
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self):
        new_x_pos, new_y_pos = self.new_x_y_pos()
        head_snake = (new_x_pos, new_y_pos)
        self.last = self.positions.pop()
        self.positions = [head_snake] + self.positions

    def reset(self):
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [MIDDLE_SCREEN]
        self.last = None

    def eat(self, apple: GameObject):
        if apple.is_good_apple:
            self.positions = [apple.position] + self.positions
        elif self.length > 1:
            self.positions.pop()
            
        self.length = len(self.positions)
        
        

    def can_eat(self, apple: GameObject) -> bool:
        return apple.position == self.new_x_y_pos()

    def can_bite_itself(self) -> bool:
        return self.new_x_y_pos() in self.positions


class Apple(GameObject):
    def __init__(self, body_color: tuple[int, int, int] = APPLE_COLOR,
                 is_good_apple: bool = True):
        super().__init__()
        self.body_color = body_color
        self.randomize_position()
        self.is_good_apple = is_good_apple


def handle_keys(game_obj: Snake):
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


def quit_game():
    pygame.quit()
    raise SystemExit


def get_good_apples(count: int) -> list:
    return [Apple() for _ in range(0, count)]


def get_bad_apples(count: int) -> list:
    return [Apple(BAD_APPLE_COLOR, False) for _ in range(0, count)]


def get_obstacles_position(obstacles: list[GameObject]) -> list:
    return [obstacle.position for obstacle in obstacles]


def set_uniques_positions(obstacles: list[GameObject],
                          snake_position: tuple[int, int]):
    obstacles_pos = get_obstacles_position(obstacles)
    new_obstacles_pos = []

    for obstacle in obstacles:
        while (obstacle.position == snake_position
               or obstacle.position in obstacles_pos
               or obstacle.position in new_obstacles_pos):
            obstacle.randomize_position()

        new_obstacles_pos += [obstacle.position]


def set_this_new_position(apple: Apple, distroyed_apple: Apple,
                       snake: Snake, obstacles) -> None:
    obstacles_pos = get_obstacles_position(obstacles)
    snake_pos = snake.positions
    distroyed_apple.position = apple.position

    while (apple.position in snake_pos or apple.position in obstacles_pos):
        apple.randomize_position()

    distroyed_apple.draw(screen)


def main():
    running = True
    slow = 0
    move = True

    snake = Snake()
    distroyed_apple = Apple(BOARD_BACKGROUND_COLOR)
    good_apples = get_good_apples(DEFAULT_COUNT_APPLES)
    bad_apples = get_bad_apples(DEFAULT_COUNT_BAD_APPLES)
    obstacles = good_apples + bad_apples
    set_uniques_positions(obstacles, snake.position)

    while running:
        move = True
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)

        handle_keys(snake)

        if slow == 5:
            slow = 0
            snake.update_direction()

            if snake.can_bite_itself():
                snake.reset()
                set_uniques_positions(obstacles, snake.position)
                move = False
                continue

            for this in obstacles:
                if snake.can_eat(this):
                    snake.eat(this)
                    set_this_new_position(this, distroyed_apple,
                                           snake, obstacles)
                    move = False
                    break

            if move:
                snake.move()

        else:
            slow += 1

        clock.tick(SPEED)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
