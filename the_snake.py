from random import choice, randint
from typing import Optional

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
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
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
screen.fill(BOARD_BACKGROUND_COLOR)

# Настройка времени:
clock = pygame.time.Clock()


class GameObject():
    position: tuple[int, int]
    body_color: tuple[int, int, int]

    def __init__(self) -> None:
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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


    def __init__(self, body_color: tuple[int, int, int]) -> None:
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
        new_x_pos = self.positions[0][0] + self.direction[0] * GRID_SIZE
        new_y_pos = self.positions[0][1] + self.direction[1] * GRID_SIZE

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

    def eat_apple(self, apple: GameObject):
        self.positions = [apple.position] + self.positions
        self.draw(screen)

    def can_eat(self, apple: GameObject) -> bool:
        return apple.position == self.new_x_y_pos()
    
    def can_bite_itself(self) -> bool:
        return self.new_x_y_pos() in self.positions
  

class Apple(GameObject):
    def __init__(self, body_color) -> None:
        super().__init__()
        self.body_color = body_color
        self.randomize_position()


def handle_keys(game_object: Snake):
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            quit_game()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def new_position(apple: Apple, distroyed_apple: Apple, snake: Snake):
    apple_pos = apple.position
    old_pos = distroyed_apple.position
    snake_pos = snake.positions

    while apple_pos == old_pos or apple_pos in snake_pos:
        apple.randomize_position()
        apple_pos = apple.position


def quit_game():
    pygame.quit()
    raise SystemExit


def main():
    running = True
    slow = 0
    apple = Apple(APPLE_COLOR)
    distroyed_apple = Apple(BOARD_BACKGROUND_COLOR)
    snake = Snake(SNAKE_COLOR)

    if apple.position == snake.position:
        apple.randomize_position()

    while running:
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        snake.draw(screen)

        if slow == 10:
            handle_keys(snake)
            snake.update_direction()

            if snake.can_eat(apple):
                snake.eat_apple(apple)
                distroyed_apple.position = apple.position
                new_position(apple, distroyed_apple, snake)
                distroyed_apple.draw(screen)
            elif snake.can_bite_itself():
                quit_game()
            else:
                snake.move()
            
            slow = 0
        else:
            slow += 1

        clock.tick(SPEED)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
