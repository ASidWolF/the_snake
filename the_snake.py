from random import randint
from typing import Optional
from time import time

import pygame

pygame.init()
"""Настройки экрана, игорового поля и меню."""
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MENU_WIDTH, MENU_HEIGHT = 200, 200
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
MAIN_MENU_COLOR = (200, 200, 200)
MENU_BORDER_COLOR = (25, 25, 25)
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (255, 100, 55)
SNAKE_COLOR = (0, 255, 0)
STONE_COLOR = (107, 99, 92)
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
"""Меню игры."""
main_menu = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
main_menu_rect = main_menu.get_rect()
main_menu_rect.center = MIDDLE_SCREEN
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
"""Создаем объект текст."""
font = pygame.font.Font(None, 30)
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
            Отрисовывает объект на выбранной поверхност {surface}.
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
        случайные координаты. Наследуется от {GameObject}.
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
            Содержит в себе статус игры (включено/выключено)
            в виде True / False
        {__slow_count} : int
            Счетчик для работы метода { slow_mode() }.
        {__snake_length}: int
            Хранит длину змейки.
        {__snake_speed}: float
            Хранит скорость змейки (измеряется в клетках в минуту)
        {__start_time}: Optional[float]
            Переменная для расчета скорости в методе { update_snake_speed() }
        {__eaten_apples}: int
            Хранит количество съеденных яблок за всю игру.
        {__reset_count}: int
            Хранит количество столкновений за всю игру.
    Методы:
        { is_run() } -> bool
            Возвращает статус игры (включено/выключено)
        { game_switch_on() } -> None
            Переключает положение игры в состояние - включено.
        { game_switch_off() } -> None
            Переключает положение игры в состояние - выключено.
        { menu_is_open() } -> bool
            Отображает статус меню (активно / не активно).
        { slow_mode() } -> bool
            Возвращает {False} пока действует замедление для выбранного
            блока кода, и {True} в момент когда код должен быть выполнен.
            Работает по принципу пропуска кадров, количество пропущенных
            кадров определяется константой {SLOW_SPEED}.
        { update_snake_speed(self, end_time: float) } -> None
            Вычесляет сколько клеток за минут пройдет змейка. И записывет
            результат в переменную {__snake_speed}.
        { update_eaten_apples(self) } -> None
            При каждом вызове увеличиывет значение {__eaten_apples} на 1.
        { update_reset_count(self) } -> None
            При каждом вызове увеличиывет значение {__reset_count} на 1.
        { update_snake_length(self, length: int) } -> None
            При каждом вызове обновляет значение переменной {__snake_length}.
        { info() } -> str:
            Выводит информацию об игре.
    """

    def __init__(self) -> None:
        """Инициализирует экземпляр класса
        и базовые атрибуты.
        """
        self.reset: bool = False
        self.new_game: bool = True
        self.__game_is_run: bool = True
        self.__slow_count: int = 0
        self.__snake_length: int = 1
        self.__snake_speed: float = 0
        self.__start_time: Optional[float] = None
        self.__eaten_apples: int = 0
        self.__reset_count: int = 0
        self.__status_menu: bool = True
        self.__menu_value: int = 0
        self.__menu_sections: list = [
            'Новая игра',
            'Продолжить',
            'Выход'
        ]

    def is_run(self) -> bool:
        """Возвращяет {True} если игра включена и {False} если нет."""
        return self.__game_is_run

    def switch_on(self) -> None:
        """Переключатель игры в положение - включено."""
        self.__game_is_run = True

    def switch_off(self) -> None:
        """Переключатель игры в положение - выключено."""
        self.__game_is_run = False

    def menu_is_open(self) -> bool:
        """Отображает статус меню (активно / не активно)."""
        return self.__status_menu

    def close_menu(self) -> None:
        self.__status_menu = False

    def open_menu(self) -> None:
        self.__status_menu = True

    def menu_up(self) -> None:
        self.__menu_value -= 1 if self.__menu_value > 0 else 0

    def menu_down(self) -> None:
        x = len(self.__menu_sections) - 1
        if self.__menu_value < x:
            self.__menu_value += 1
        else:
            self.__menu_value = x

    def menu_title(self) -> str:
        return self.__menu_sections[self.__menu_value]

    def get_menu_step(self) -> int:
        return (MENU_HEIGHT // (len(self.__menu_sections) + 1))

    def get_menu_list(self) -> list:
        return self.__menu_sections

    def slow_mode(self, how_slow: int = SLOW_SPEED) -> bool:
        """Возвращает {False} пока действует замедление для выбранного
        блока кода, и {True} в момент когда код должен быть выполнен.
        Работает по принципу пропуска кадров, количество пропущенных
        кадров по умолчанию = {SLOW_SPEED}. Чем больше значение
        тем сильнее замедление.
        """
        self.__slow_count += 1
        if self.__slow_count > how_slow:
            self.__slow_count = 0

        return self.__slow_count == how_slow

    def update_snake_speed(self, end_time: float) -> None:
        """Обновляет скорость движения змейки."""
        if self.__start_time:
            self.__snake_speed = round(60 / (end_time - self.__start_time))

        self.__start_time = end_time

    def update_eaten_apples(self) -> None:
        """Обновляет количество съеденных яблок."""
        self.__eaten_apples += 1

    def update_count_of_resets(self) -> None:
        """Обновляет количество врезаний в препятствие."""
        self.__reset_count += 1

    def update_snake_length(self, length: int) -> None:
        """Обновляет значение длины зъмейки."""
        self.__snake_length = length

    def reset_info(self) -> None:
        self.__snake_length = 1
        self.__eaten_apples = 0
        self.__reset_count = 0

    def info(self) -> str:
        """Выводит информацию об игре."""
        info = (
            f'Длина змейки: {self.__snake_length} || '
            f'Яблок съедено: {self.__eaten_apples} || '
            f'Врезаний: {self.__reset_count} || '
            f'Скорость {self.__snake_speed} клеток в минуту!'
        )
        return info


"""Инициализируем для возможнисти управлять всей логикой."""
game = GameManager()


def handle_keys(game_obj: Snake) -> None:
    """Отслеживает нажатые клавиши для управления змейкой"""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and game_obj.direction != DOWN:
        game_obj.next_direction = UP
    elif keys[pygame.K_DOWN] and game_obj.direction != UP:
        game_obj.next_direction = DOWN
    elif keys[pygame.K_LEFT] and game_obj.direction != RIGHT:
        game_obj.next_direction = LEFT
    elif keys[pygame.K_RIGHT] and game_obj.direction != LEFT:
        game_obj.next_direction = RIGHT


def handle_keys_menu() -> None:
    """Отслеживает нажатые клавиши для управления в меню"""
    keys = pygame.key.get_pressed()

    if keys[13] and game.menu_title() == 'Новая игра':
        if game.new_game:
            game.new_game = False
        else:
            game.reset = True
        game.close_menu()
    elif keys[13] and game.menu_title() == 'Продолжить' and not game.new_game:
        game.close_menu()
    elif keys[13] and game.menu_title() == 'Выход':
        game.switch_off()
        game.close_menu()

    elif game.slow_mode(1):
        if keys[pygame.K_UP]:
            game.menu_up()
        elif keys[pygame.K_DOWN]:
            game.menu_down()


def quit_game() -> None:
    """Завершает игру."""
    pygame.quit()
    raise SystemExit

def quit_pressed() -> bool:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            if game.new_game:
                game.switch_off()
            else:
                return True

    return False


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


def reset_game(snake: Snake, obstacles: list[GameObject],
               new_game: bool = False) -> None:
    snake.reset()
    set_uniques_positions(obstacles, snake.position)

    if new_game:
        game.reset_info()
    else:
        game.update_snake_length(snake.length)
        game.update_count_of_resets()


def snake_can_move(snake: Snake, obstacles, distroyed_apple) -> bool:
    """Проверяет есть ли на пути препятствия. Если нет то возвращает {True}
    и змейка двигается дальше. Если есть препятствие, возвращется {False}.
    В зависимости от препятсвия змейка вырастет, уменьшится или сбросится
    в начальное состояние.
    """

    if snake.can_bite_itself():
        game.reset = True

    for this in obstacles:

        if snake.try_bite(this) and type(this) is Apple:
            snake.eat(this)
            game.update_snake_length(snake.length)
            game.update_eaten_apples()

            if snake.length + len(obstacles) <= FIELD_SIZE:
                set_this_new_position(this, distroyed_apple,
                                      snake, obstacles)
                return False
            else:
                game.reset = True

        elif snake.try_bite(this) and type(this) is Stone:
            game.reset = True

        if game.reset:
            reset_game(snake, obstacles)
            game.reset = False
            return False

    return True


def draw_menu():
    main_menu.fill(MAIN_MENU_COLOR)
    rect = (0, 0, MENU_WIDTH, MENU_HEIGHT)
    step = game.get_menu_step()

    pygame.draw.rect(main_menu, MENU_BORDER_COLOR, rect, 4)
    y_tmp = step

    for item in game.get_menu_list():
        text = font.render(item, True, 'Black')
        text_rect = text.get_rect()
        text_rect.center = (MENU_WIDTH // 2, y_tmp)
        main_menu.blit(text, text_rect)

        if game.menu_title() == item:
            text_rect.inflate_ip(15, 15)
            pygame.draw.rect(main_menu, SNAKE_COLOR, text_rect, 5)

        y_tmp += step

    screen.blit(main_menu, main_menu_rect)


def main():
    """Реализует базовую логику игры и инициализацию всех объектов."""
    snake = Snake()
    distroyed_apple = Apple(DEFAULT_COLOR)
    good_apples = get_good_apples()
    bad_apples = get_bad_apples()
    stones = get_stones()
    obstacles = good_apples + bad_apples + stones
    set_uniques_positions(obstacles, snake.position)

    while game.is_run():
        screen.blit(background_surface, (0, 0))

        if game.menu_is_open():
            game_caption('Змейка || Основное меню')
            if quit_pressed():
                game.close_menu()

            draw_menu()
            handle_keys_menu()
            if game.reset:
                reset_game(snake, obstacles, True)
                game.reset = False
        else:
            if quit_pressed():
                game.open_menu()

            snake.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)

            handle_keys(snake)

            if game.slow_mode():
                snake.update_direction()

                if snake_can_move(snake, obstacles, distroyed_apple):
                    snake.move()

                game.update_snake_speed(time())

            game_caption(game.info())

        clock.tick(GAME_SPEED)
        pygame.display.update()

    quit_game()


if __name__ == '__main__':
    main()
