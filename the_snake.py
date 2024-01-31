from random import randint
from typing import Optional

import pygame

pygame.init()
"""Настройки экрана и игорового поля."""
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MIDDLE_SCREEN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FIELD_SIZE = GRID_WIDTH * GRID_HEIGHT
NOISE_SIZE = 5
NOISE_STRENGTH = 4
"""Направления движения змейки."""
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
"""Цвета объектов и игрового поля."""
BOARD_BACKGROUND_COLOR = (181, 130, 81)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (255, 100, 55)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (77, 55, 41)
DEFAULT_COLOR = (0, 0, 0)
"""Управление скорость и замедлением игры."""
GAME_SPEED = 20
SLOW_SPEED = 5
"""Количество игровых объектов наполе."""
DEFAULT_COUNT_APPLES = 10
DEFAULT_COUNT_BAD_APPLES = 5
DEFAULT_COUNT_STONES = 5
"""Основной эран игры."""
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
"""Оюъект в котором будет хранится фон для игры."""
background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
"""Создание фона и шума для эмитации сложной поверхности (например песка)."""
background_surface.fill(BOARD_BACKGROUND_COLOR)
for i in range(0, SCREEN_WIDTH, NOISE_SIZE):
    for j in range(0, SCREEN_HEIGHT, NOISE_SIZE):
        rnd_rgb = [0, 0, 0]
        for k in range(3):
            rnd_rgb[k] = randint(
                BOARD_BACKGROUND_COLOR[k] - NOISE_STRENGTH,
                BOARD_BACKGROUND_COLOR[k] + NOISE_STRENGTH
            )
        pygame.draw.rect(
            background_surface,
            (rnd_rgb[0], rnd_rgb[1], rnd_rgb[2]),
            (i, j, NOISE_SIZE, NOISE_SIZE)
        )
"""Отрисовка фона на экране"""
screen.blit(background_surface, (0, 0))
"""Создаем объект для управления заголовком игры."""
game_caption = pygame.display.set_caption
game_caption('Змейка')
"""Объект для управления временем."""
clock = pygame.time.Clock()


class GameObject():
    """Базовый класс от которого наследуются все игровые объекты. Содержит:

    Атрибуты:
        {position} : tuple[int, int]
            Координаты объекта на поле, от которых он отрисовывается.
        {body_color} : tuple[int, int, int]
            Цвет объекта заданный в формате RGB.

    Методы:
        { draw(self, surface) } -> None
            Отрисовывает объект на выбранной поверхност (surface).
        { randomize_position(self) } -> None
            Задаёт случайные координата для объекта.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = DEFAULT_COLOR) -> None:
        """Инициализирует новый экземпляр класса {GameObject}."""
        self.position: tuple[int, int] = MIDDLE_SCREEN
        self.body_color = body_color

    def draw(self, surface) -> None:
        """Отрисовывает на поверхности {surface} фигуру
        заданных, константой {GRID_SIZE}, размеров.
        """
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def randomize_position(self) -> None:
        """Задаёт объекту случайные координаты."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


class Apple(GameObject):
    """Класс описывающий игровой объект Яблоко.
    Наследуется от {GameObject}, обладает одним дополнительным параметром:

        {is_good_apple} : bool
            Параметр отвечающий за игровую логику 'хорошее/плохое яблоко'.
            Если {True} - размер 'Змейки' при взаимодействии увеличится.
            Если {False} - размер 'Змейки' при взаимодействии уменьшится.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = APPLE_COLOR,
                 is_good_apple: bool = True) -> None:
        """Инициализирует экземпляр класса {Apple} и задает ему
        случайные координаты. Наследуясь от {GameObject}.
        """
        super().__init__(body_color)
        self.randomize_position()
        self.is_good_apple = is_good_apple


class Stone(GameObject):
    """Класс описывающий игровой объект Камень. Наследуется от {GameObject}.
    При столкновении с камнем 'Змейка' принимает исходное состояние.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = STONE_COLOR) -> None:
        """Инициализирует экземпляр класса {Stone} и задает ему случайные
        координаты. Наследуется от {GameObject}.
        """
        super().__init__(body_color)
        self.randomize_position()


class Snake(GameObject):
    """Класс описывающий игровой объект 'Змейка'.
    Наследуется от {GameObject}. Содержит:

    Атрибуты:
        {positions} : list
            Содержит список всех позиции всех сегментов тела змейки.
            Начальная позиция — центр экрана.
        {length} : int
            Длина змейки. Изначально змейка имеет длину 1.
        {direction} : tuple[int, int]
            Направление движения змейки. По умолчанию змейка движется вправо.
        {next_direction} : Optional[tuple[int, int]]
            Следующее направление движения, которое будет применено после
            обработки нажатия клавиши. По умолчанию {None}.
        {last} : Optional[tuple[int, int]]
            Используется для хранения позиции последнего сегмента змейки
            перед тем, как он исчезнет (при движении змейки).
    Методы:
        { update_direction() } -> None
            Обновляет направление движения змейки.
        { get_head_position() } -> tuple[int, int]
            Возвращает позицию головы змейки (первый элемент в
            списке {positions}).
        { new_x_y_pos() } -> tuple[int, int]:
            Возвращает позицию в которую будет перемещена змейка
            исходя из направления движения.
        { draw(surface) } -> None
            Принимает на вход поверхность на которой отрисовывает
            змейку, затирая след.
        { move() } -> None
            Расчитывает координаты новой головы методом { new_x_y_pos() } и
            добовляет к ней 'тело змейки' удалив из него крайний элемент.
        { reset() } -> None
            Сбрасывает змейку в начальное состояние после столкновения с собой
            или несъедобным препятствием.
        { eat(apple: Apple) } -> None
            Принимает на вход объект класса {Apple} и в зависимости от его
            атрибута {is_good_apple} либо увеличивается либо уменьшается.
        { can_bite_itself() } -> bool
            Проверяет может ли следующим ходом змейка укусить сама себя.
        { try_bite(this: GameObject) } -> bool
            Принимает на вход объект и проверяет можно ли его укусить.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        """Инициализирует экземпляр класса {Snake}, и записывает стартовую
        позицию в список {positions}. Наследуясь от {GameObject}.
        """
        super().__init__(body_color)
        self.positions = [self.position]
        self.length: int = 1
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: Optional[tuple[int, int]] = None
        self.last: Optional[tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def new_x_y_pos(self) -> tuple[int, int]:
        """Возвращает позицию в которую будет перемещена змейка."""
        new_x_pos, new_y_pos = self.get_head_position()
        new_x_pos = new_x_pos + self.direction[0] * GRID_SIZE
        new_y_pos = new_y_pos + self.direction[1] * GRID_SIZE

        if new_x_pos < 0 or new_x_pos == SCREEN_WIDTH:
            new_x_pos = SCREEN_WIDTH - new_x_pos * self.direction[0]

        if new_y_pos < 0 or new_y_pos == SCREEN_HEIGHT:
            new_y_pos = SCREEN_HEIGHT - new_y_pos * self.direction[1]

        return (new_x_pos, new_y_pos)

    def draw(self, surface) -> None:
        """Отрисовывает на поверхности {surface} змейку заданных списком
        {positions} размеров, где константа {GRID_SIZE} размер сегмента. И
        и если {last} содержит координаты старого сегмента затирает его.
        """
        for position in self.positions:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self) -> None:
        """Сдвигает змейку на одну клетку игрового поля."""
        new_x_pos, new_y_pos = self.new_x_y_pos()
        head_snake = (new_x_pos, new_y_pos)
        self.last = self.positions.pop()
        self.positions = [head_snake] + self.positions

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        Snake.__init__(self)

    def eat(self, apple: Apple) -> None:
        """Принимает на вход объект класса {Apple} и в зависимости от его
        атрибута {is_good_apple} увеличивает или уменьшает змейку.
        """
        if apple.is_good_apple:
            self.positions = [apple.position] + self.positions
        elif self.length > 1:
            self.positions.pop()

        self.length = len(self.positions)

    def can_bite_itself(self) -> bool:
        """Проверяет может ли следующим ходом змейка укусить сама себя."""
        return self.new_x_y_pos() in self.positions

    def try_bite(self, this: GameObject) -> bool:
        """Принимает на вход объект и проверяет можно ли его укусить."""
        return this.position == self.new_x_y_pos()


class GameManager():
    """Класс для управления общей логикой игры. Содержит:

    Атрибуты:
        {__game_is_run} : bool
            Содержит в себе статус игру (включено/выключено)
            в виде True / False
        {__slow_count} : int
            Счетчик для работы метода { slow_mode() }.
    Методы:
        { is_run() } -> bool
            Возвращает статус игры (включено/выключено)
        { game_switch_on() } -> None
            Переключает положение игры в состояние - включено.
        { game_switch_off() } -> None
            Переключает положение игры в состояние - выключено.
        { slow_mode() } -> bool
            Возвращает False пока действует замедление для выбранного
            блока кода, и True в момент когда код должен быть выполнен.
            Работает на протяжении всего игрового цикла.
    """

    def __init__(self) -> None:
        """Инициализирует экземпляр класса
        и базовые атрибуты.
        """
        self.__game_is_run: bool = True
        self.__slow_count: int = 0

    def is_run(self) -> bool:
        """Возвращяет True если игра включена и False если нет."""
        return self.__game_is_run

    def game_switch_on(self) -> None:
        """Переключатель игры в положение - включено."""
        self.__game_is_run = True

    def game_switch_off(self) -> None:
        """Переключатель игры в положение - выключено."""
        self.__game_is_run = False

    def slow_mode(self, how_slow: int = SLOW_SPEED) -> bool:
        """Замедляет часть игровой логики.
        Степень замедления, по умолчанию, определяется константой
        {SLOW_SPEED}, но может быть переопределена в игре. Чем больше
        значение {how_slow}, тем сильнее замедление.
        """
        self.__slow_count += 1
        if self.__slow_count > how_slow:
            self.__slow_count = 0

        return self.__slow_count == how_slow

    def start_game(self):
        """Находится в разработке"""
        pass


def handle_keys(game_obj: Snake) -> None:
    """Отслеживает нажатые клавиши для управления змейкой
    или выходом из игры.
    """
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
    """Завершает игру"""
    pygame.quit()
    raise SystemExit


def get_good_apples(count: int = DEFAULT_COUNT_APPLES) -> list:
    """Создает список хороших яблок. И возвращает его."""
    return [Apple() for _ in range(0, count)]


def get_stones(count: int = DEFAULT_COUNT_STONES) -> list:
    """Создает список камней. И возвращает его."""
    return [Stone() for _ in range(0, count)]


def get_bad_apples(count: int = DEFAULT_COUNT_BAD_APPLES) -> list:
    """Создает список плохих яблок. И возвращает его."""
    return [Apple(BAD_APPLE_COLOR, False) for _ in range(0, count)]


def get_obstacles_position(obstacles: list[GameObject]) -> list:
    """Возвращает список состоящий из координат всех
    созданных объектов, змейка в список не входит.
    """
    return [obstacle.position for obstacle in obstacles]


def set_uniques_positions(obstacles: list[GameObject],
                          snake_position: tuple[int, int]) -> None:
    """Задает всем объектам из списка {obstacles} уникальные координаты."""
    new_obstacles_pos: list = []

    for obstacle in obstacles:
        obstacle.randomize_position()

        while (obstacle.position == snake_position
               or obstacle.position in new_obstacles_pos):
            obstacle.randomize_position()

        new_obstacles_pos += [obstacle.position]


def set_this_new_position(apple: Apple, distroyed_apple: Apple,
                          snake: Snake, obstacles: list[GameObject]) -> None:
    """Задает новые координаты съеденому яблоку а на его месте отрисовыывает
    на мгновение 'поврежденное' яблоко, создавая эффект его поедания.
    """
    obstacles_pos: list = get_obstacles_position(obstacles)
    snake_pos: list = snake.positions
    distroyed_apple.position = apple.position

    while (apple.position in snake_pos or apple.position in obstacles_pos):
        apple.randomize_position()

    distroyed_apple.draw(screen)


def snake_can_move(snake: Snake, obstacles, distroyed_apple) -> bool:
    """Проверяет есть ли на пути препятствия. Если нет то возвращает {True}
    и змейка двигается дальше. Если есть препятствие, возвращется {False}.
    В зависимости от препятсвия змейка вырастет, уменьшится или сбросится
    в начальное состояние.
    """
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
    """Реализует базовую логику игры и инициализацию всех объектов."""
    game = GameManager()
    snake = Snake()
    distroyed_apple = Apple(DEFAULT_COLOR)
    good_apples = get_good_apples()
    bad_apples = get_bad_apples()
    stones = get_stones()
    obstacles = good_apples + bad_apples + stones
    set_uniques_positions(obstacles, snake.position)

    while game.is_run():
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

    quit_game()


if __name__ == '__main__':
    main()
