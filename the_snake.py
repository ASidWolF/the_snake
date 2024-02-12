"""Игра змейка.
Суть игры:
    - Игрок управляет змейкой, которая движется по игровому полю, разделённому
    на клетки.
Цель игры:
    - Увеличивать длину змейки, 'съедая' хорошие яблоки и избегать камней.
Правила игры:
    - Змейка движется в одном из направлений - вверх, вниз, влево или вправо.
    - Игрок управляет направлением движения, но змейка не может остановиться
    или двигаться назад.
    - Каждый раз, когда змейка съедает яблоко, она увеличивается в длину на
    один сегмент.
    - Змейка может проходить сквозь одну стену и появляться с противоположной
    стороны поля.
    - Если змейка съест 'плохое яблоко' - змейка уменьшится на 1 сегмент.
    - Если змейка столкнётся сама с собой или с камнем — змейка уменьшится
    до 1 сегмента игра начнется заново.
Реализация игры:
    - Игра реализована с помощью библиотеки { pygame }.
    - В игре реализовано 'игровое меню' позволяющее: начать 'Новую игру',
    'Продолжить' текущюю или 'Выйти' из игры.
    - Все настройки игры осуществляются через блок констант.
В игре реализованны:
    Классы:
        {GameObject} - базовый класс описывающий все объекты в игре.
        {Apple} - наследуются от {GameObject} и описывают объект яблоко.
        {Stone} - наследуются от {GameObject} и описывают объект камень.
        {Snake} - наследуются от {GameObject} и описывает змейку.
        {GameManger} - класс нужный для управления основной логикой игры.
    Методы:
        { handle_keys }
            Отслеживает нажатые клавиши для управления змейкой.
        { handle_keys_menu }
            Отслеживает нажатые клавиши для управления в меню.
        { quit_game }
            Завершает игру.
        { quit_pressed }
            Реализует логику нажатия на клавишу ESCAPE в игре.
        { get_good_apples }
            Создает список хороших яблок. И возвращает его.
        { get_stones }
            Создает список хороших камней. И возвращает его.
        { get_bad_apples }
            Создает список хороших плохих яблок. И возвращает его.
        { get_obstacles_position }
            Возвращает список из координат всех объектов за исключением змейки.
        { reset_game }
            Сбрасывает игру. Все объекты возвращаются к стартовым значениям.
        { snake_can_move }
            Реализует логику движения змейки и встречи её с препятствиями.
        { draw_menu }
            Отрисовывает стартовое игровое меню.
        { main }
            Содержит главный игровой цикл. Реализует основную логику игры.
"""
from random import choice, randint
from typing import Optional
from time import time

import pygame as pg

pg.init()
"""Настройки экрана, игорового поля и меню."""
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
MENU_WIDTH, MENU_HEIGHT = 200, 200
TITLE_MENU_WIDTH, TITLE_MENU_HEIGHT = MENU_WIDTH, 50
MIDDLE_SCREEN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
MENU_FONT_SIZE = 35
TITLE_FONT_SIZE = 60
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
GAME_SPEED = 60
SLOW_SPEED = 10
"""Количество игровых объектов на поле."""
DEFAULT_COUNT_APPLES = 20
DEFAULT_COUNT_BAD_APPLES = 20
DEFAULT_COUNT_STONES = 20
"""Клавиши."""
KEY_ENTER = 13
"""Основной эран игры."""
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
"""Меню игры."""
main_menu = pg.Surface((MENU_WIDTH, MENU_HEIGHT))
main_menu_rect = main_menu.get_rect(center=MIDDLE_SCREEN)
"""    """
title_menu = pg.Surface((TITLE_MENU_WIDTH, TITLE_MENU_HEIGHT))
title_menu_rect = main_menu.get_rect(
    center=(SCREEN_WIDTH // 2, main_menu_rect.y + TITLE_MENU_HEIGHT)
)
"""Оюъект в котором будет хранится фон для игры."""
background_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        pg.draw.rect(
            background_surface,
            (rnd_rgb[0], rnd_rgb[1], rnd_rgb[2]),
            (i, j, NOISE_SIZE, NOISE_SIZE)
        )
"""Отрисовка фона на экране"""
screen.blit(background_surface, (0, 0))
"""Создаем объект для управления заголовком игры."""
game_caption = pg.display.set_caption
game_caption('Змейка')
"""Создаем объект текст."""
menu_font = pg.font.Font(None, MENU_FONT_SIZE)
title_font = pg.font.Font(None, TITLE_FONT_SIZE)
"""Объект для управления временем."""
clock = pg.time.Clock()


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

    def draw(self) -> None:
        """Базовый метод рисования объектов. Определяется для
        каждого подкласса отдельно.
        """
        pass

    def draw_cell(self, position: tuple[int, int],
                  color: Optional[tuple[int, int, int]] = None,
                  tail: bool = False) -> None:
        """Отрисовывает ячейку заданых размеров."""
        if color:
            self.body_color = color

        rect = pg.Rect(
            position,
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, self.body_color, rect)
        if not tail:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self,
                           obstacles_pos: list[tuple[int, int]] = [],
                           snake_pos: list[tuple[int, int]] = []) -> None:
        """Задаёт объекту случайные координаты."""
        while (self.position in snake_pos
               or self.position in obstacles_pos):
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
                 is_good_apple: bool = True,
                 obstacles_pos: list = [],
                 snake_pos: list = []) -> None:
        """Инициализирует экземпляр класса {Apple} и задает ему
        случайные координаты. Наследуется от {GameObject}.
        """
        super().__init__(body_color)
        self.randomize_position(obstacles_pos, snake_pos)
        self.is_good_apple = is_good_apple

    def draw(self) -> None:
        self.draw_cell(self.position)


class Stone(GameObject):
    """Класс описывающий игровой объект Камень. Наследуется от {GameObject}.
    При столкновении с камнем 'Змейка' принимает исходное состояние.
    """

    def __init__(self,
                 body_color: tuple[int, int, int] = STONE_COLOR,
                 obstacles_pos: list = [],
                 snake_pos: list = []) -> None:
        """Инициализирует экземпляр класса {Stone} и задает ему случайные
        координаты. Наследуется от {GameObject}.
        """
        super().__init__(body_color)
        self.randomize_position(obstacles_pos, snake_pos)

    def draw(self) -> None:
        self.draw_cell(self.position)


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
        {last} : Optional[tuple[int, int]]
            Используется для хранения позиции последнего сегмента змейки
            перед тем, как он исчезнет (при движении змейки).
    Методы:
        { update_direction() } -> None
            Обновляет направление движения змейки.
        { get_head_position() } -> tuple[int, int]
            Возвращает позицию головы змейки (первый элемент в
            списке {positions}).
        { new_head() } -> tuple[int, int]:
            Возвращает позицию в которую будет перемещена змейка
            исходя из направления движения.
        { draw() } -> None
            Метод отрисовки змейки.
        { move() } -> None
            Расчитывает координаты новой головы методом { new_x_y_pos() } и
            добовляет к ней 'тело змейки' удалив из него крайний элемент.
        { reset() } -> None
            Сбрасывает змейку в начальное состояние после столкновения с собой
            или несъедобным препятствием.
        { eat(apple: Apple) } -> None
            Принимает на вход объект класса {Apple} и в зависимости от его
            атрибута {is_good_apple} либо увеличивает либо уменьшает змейку.
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
        self.reset()
        self.direction: tuple[int, int] = RIGHT

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [self.position]
        self.length: int = 1
        self.last: Optional[tuple[int, int]] = None
        self.direction = choice([RIGHT, LEFT, UP, DOWN])

    def update_direction(self, direction: tuple[int, int]) -> None:
        """Обновляет направление движения змейки."""
        self.direction = direction

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def draw(self) -> None:
        """Отрисовывает на поверхности {surface} змейку заданных списком
        {positions} размеров, где константа {GRID_SIZE} размер сегмента. И
        и если {last} содержит координаты старого сегмента затирает его.
        """
        for position in self.positions:
            self.draw_cell(position, SNAKE_COLOR)

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, True)

    def move(self, new_head: tuple[int, int]) -> None:
        """Сдвигает змейку на одну клетку игрового поля."""
        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def can_bite_itself(self, new_head: tuple[int, int]) -> bool:
        """Проверяет может ли следующим ходом змейка укусить сама себя."""
        return new_head in self.positions

    def try_bite(self, new_head: tuple[int, int], object: GameObject) -> bool:
        """Принимает на вход объект и проверяет можно ли его укусить."""
        return object.position == new_head


class GameManager():
    """Класс для управления общей логикой игры. Содержит:

    Атрибуты:
        {reset} : bool
            Атрибут для управления перезапуском игры.
        {new_game} : bool
            До первого запуска 'Новая игра' = {True}, далее {False}.
        {__game_is_run} : bool
            Содержит в себе статус игры (включено/выключено)
            в виде True / False
        {__slow_count} : int
            Счетчик для работы метода { slow_mode() }.
        {__snake_length} : int
            Хранит длину змейки.
        {__snake_speed} : float
            Хранит скорость змейки (измеряется в клетках в минуту)
        {__start_time} : Optional[float]
            Переменная для расчета скорости в методе { update_snake_speed() }
        {__eaten_apples} : int
            Хранит количество съеденных яблок за всю игру.
        {__reset_count} : int
            Хранит количество столкновений за всю игру.
        {__status_menu} : bool
            Хранит статус меню, где {True} меню активно, {False} меню скрыто.
        {__menu_value} : int
            Хранит номер активного пункта меню. (Считается от 0).
        {__menu_sections} : list
            Хранит список стартовых меню.
    Методы:
        { is_run() } -> bool
            Возвращает статус игры (включено/выключено)
        { game_switch_on() } -> None
            Переключает положение игры в состояние - включено.
        { game_switch_off() } -> None
            Переключает положение игры в состояние - выключено.
        { menu_is_open() } -> bool
            Отображает статус меню (активно / не активно).
        { close_menu(self) } -> None
            Закрывает меню.
        { open_menu(self) } -> None
            Открывет меню.
        { menu_up(self) } -> None
            Передвижение по меню вверх.
        { menu_down(self) } -> None
            Передвижение по меню вниз.
        { menu_title(self) } -> str
            Возвращает название выбранного пункта меню.
        { get_menu_step(self) } -> int
            Возвращает расстояние между пунктами меню исходя из размеров
            высоты меню, заданных константой {MENU_HEIGHT}, и их количества.
        { get_menu_list(self) } -> list
            Возвращает списо из пунктов меню.
        { slow_mode() } -> bool
            Возвращает {False} пока действует замедление для выбранного
            блока кода, и {True} в момент когда код должен быть выполнен.
        { update_snake_speed(self, end_time: float) } -> None
            Вычесляет сколько клеток за минут пройдет змейка. И записывет
            результат в переменную {__snake_speed}.
        { update_eaten_apples(self) } -> None
            При каждом вызове увеличиывет значение {__eaten_apples} на 1.
        { update_reset_count(self) } -> None
            При каждом вызове увеличиывет значение {__reset_count} на 1.
        { update_snake_length(self, length: int) } -> None
            При каждом вызове обновляет значение переменной {__snake_length}.
        { reset_info(self) } -> None
            Сбрасывает информаци о текущей игре.
        { info() } -> str:
            Выводит информацию об игре.
    """

    def __init__(self) -> None:
        """Инициализирует экземпляр класса
        и базовые атрибуты.
        """
        self.reset: bool = False
        self.new_game: bool = True
        self.__game_is_run: bool = False
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
        """Закрывает меню."""
        self.__status_menu = False

    def open_menu(self) -> None:
        """Открывает меню."""
        self.__status_menu = True

    def menu_up(self) -> None:
        """Передвижение по меню вверх."""
        self.__menu_value -= 1 if self.__menu_value > 0 else 0

    def menu_down(self) -> None:
        """Передвижение по меню вниз."""
        x = len(self.__menu_sections) - 1
        if self.__menu_value < x:
            self.__menu_value += 1
        else:
            self.__menu_value = x

    def menu_title(self) -> str:
        """Возвращает название выбранного пункта меню."""
        return self.__menu_sections[self.__menu_value]

    def get_menu_step(self) -> int:
        """Возвращает расстояние между пунктами меню исходя из размеров
        высоты меню, заданных константой {MENU_HEIGHT}, и их количества.
        """
        return (MENU_HEIGHT // (len(self.__menu_sections) + 1))

    def get_menu_list(self) -> list:
        """Возвращает списо из пунктов меню."""
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
        """Сбрасывает информаци о текущей игре."""
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


"""Инициализируем {GameManager} для возможнисти управлять всей логикой."""
game = GameManager()


def handle_keys(snake: Snake) -> None:
    """Отслеживает нажатые клавиши для управления змейкой."""
    keys = pg.key.get_pressed()
    direction: Optional[tuple[int, int]] = None

    if keys[pg.K_UP] and snake.direction != DOWN:
        direction = UP
    elif keys[pg.K_DOWN] and snake.direction != UP:
        direction = DOWN
    elif keys[pg.K_LEFT] and snake.direction != RIGHT:
        direction = LEFT
    elif keys[pg.K_RIGHT] and snake.direction != LEFT:
        direction = RIGHT

    if direction:
        snake.update_direction(direction)


def handle_keys_menu() -> None:
    """Отслеживает нажатые клавиши для управления в меню."""
    keys = pg.key.get_pressed()

    if keys[KEY_ENTER] and game.menu_title() == 'Новая игра':
        if game.new_game:
            game.new_game = False
        else:
            game.reset = True
        game.close_menu()
    elif (keys[KEY_ENTER] and game.menu_title() == 'Продолжить'
          and not game.new_game):
        game.close_menu()
    elif keys[KEY_ENTER] and game.menu_title() == 'Выход':
        game.switch_off()
        game.close_menu()

    if game.slow_mode(1):
        if keys[pg.K_UP]:
            game.menu_up()
        elif keys[pg.K_DOWN]:
            game.menu_down()


def quit_game() -> None:
    """Завершает игру."""
    pg.quit()
    raise SystemExit


def quit_pressed() -> bool:
    """Реализует логику нажатия на клавишу ESCAPE."""
    keys = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
            if game.new_game:
                game.switch_off()
            else:
                return True

    return False


def get_good_apples(count: int = DEFAULT_COUNT_APPLES,
                    obstacles_pos: list = [],
                    snake_pos: list = []) -> tuple[list, list]:
    """Создает список хороших яблок. И возвращает его."""
    obstacles_pos = obstacles_pos
    apples = []
    for _ in range(0, count):
        apple = Apple(obstacles_pos=obstacles_pos, snake_pos=snake_pos)
        apples += [apple]
        obstacles_pos += [apple.position]

    return apples, obstacles_pos


def get_stones(count: int = DEFAULT_COUNT_STONES,
               obstacles_pos: list = [],
               snake_pos: list = []) -> tuple[list, list]:
    """Создает список хороших яблок. И возвращает его."""
    obstacles_pos = obstacles_pos
    stones = []
    for _ in range(0, count):
        stone = Stone(obstacles_pos=obstacles_pos, snake_pos=snake_pos)
        stones += [stone]
        obstacles_pos += [stone.position]

    return stones, obstacles_pos


def get_bad_apples(count: int = DEFAULT_COUNT_BAD_APPLES,
                   obstacles_pos: list = [],
                   snake_pos: list = []) -> tuple[list, list]:
    """Создает список плохих яблок. И возвращает его."""
    obstacles_pos = obstacles_pos
    bad_apples = []
    for _ in range(0, count):
        bad_apple = Apple(BAD_APPLE_COLOR, False, obstacles_pos, snake_pos)
        bad_apples += [bad_apple]
        obstacles_pos += [bad_apple.position]

    return bad_apples, obstacles_pos


def get_obstacles_position(obstacles: list[GameObject]) -> list:
    """Возвращает список состоящий из координат всех
    созданных объектов, змейка в список не входит.
    """
    return [obstacle.position for obstacle in obstacles]


def init_game_obgects() -> tuple[Snake, list[GameObject]]:
    snake = Snake()
    obstacles_pos: list = []
    good_apples, obstacles_pos = get_good_apples(
        obstacles_pos=obstacles_pos, snake_pos=snake.positions
    )
    bad_apples, obstacles_pos = get_bad_apples(
        obstacles_pos=obstacles_pos, snake_pos=snake.positions
    )
    stones, obstacles_pos = get_stones(
        obstacles_pos=obstacles_pos, snake_pos=snake.positions
    )
    obstacles = good_apples + bad_apples + stones

    return snake, obstacles


def reset_game(new_game: bool = False) -> tuple[Snake, list[GameObject]]:
    """Сбрасывает змейку к исходному состоянию и задаёт ей случайное
    направление. Всем препятствиям задаются новые координаты. Если
    {new_game} = {True} информация об игре будет сброшена. Если
    {new_game} = {False} информация об игре будет обновлена.
    """
    if new_game:
        game.reset_info()
    else:
        game.update_snake_length(1)
        game.update_count_of_resets()

    return init_game_obgects()


def snake_can_move(new_head: tuple[int, int], snake: Snake,
                   obstacles) -> bool:
    """Проверяет есть ли на пути препятствия. Если нет то возвращает {True}
    и змейка двигается дальше. Если есть препятствие, возвращется {False}.
    В зависимости от препятсвия змейка вырастет, уменьшится или сбросится
    в начальное состояние.
    """
    if snake.can_bite_itself(new_head):
        game.reset = True
        return False

    for obstacle in obstacles:

        if snake.try_bite(new_head, obstacle) and type(obstacle) is Apple:
            if obstacle.is_good_apple:
                snake.positions.insert(0, obstacle.position)
            elif snake.length > 1:
                snake.positions.pop()

            snake.length = len(snake.positions)
            game.update_snake_length(snake.length)
            game.update_eaten_apples()

            if snake.length + len(obstacles) <= FIELD_SIZE:
                obstacles_pos = get_obstacles_position(obstacles)
                obstacle.randomize_position(obstacles_pos, snake.positions)
                return False
            else:
                game.reset = True
                return False

        elif snake.try_bite(new_head, obstacle) and type(obstacle) is Stone:
            game.reset = True
            return False

    return True


def draw_menu():
    """Отрисовывает главное меню."""
    title_menu.fill('Black')
    text = title_font.render('Змейка', True, 'White')
    txt_x, txt_y = TITLE_MENU_WIDTH // 2, TITLE_MENU_HEIGHT // 2
    text_rect = text.get_rect(center=(txt_x, txt_y))
    title_menu.blit(text, text_rect)

    main_menu.fill(MAIN_MENU_COLOR)
    rect = (0, 0, MENU_WIDTH, MENU_HEIGHT)
    step = game.get_menu_step()

    pg.draw.rect(main_menu, MENU_BORDER_COLOR, rect, 4)
    y_tmp = step

    for item in game.get_menu_list():
        if item == 'Продолжить' and game.new_game:
            text = menu_font.render(item, True, 'DarkGray')
        else:
            text = menu_font.render(item, True, 'Black')

        text_rect = text.get_rect(center=(MENU_WIDTH // 2, y_tmp))
        main_menu.blit(text, text_rect)

        if game.menu_title() == item:
            text_rect.inflate_ip(MENU_FONT_SIZE // 2, MENU_FONT_SIZE // 2)
            pg.draw.rect(main_menu, SNAKE_COLOR, text_rect, 5)

        y_tmp += step

    screen.blit(main_menu, main_menu_rect)
    screen.blit(title_menu, title_menu_rect)


def main():
    """Реализует базовую логику игры и инициализацию всех объектов."""
    snake, obstacles = init_game_obgects()
    game.switch_on()

    while game.is_run():
        screen.blit(background_surface, (0, 0))

        if game.menu_is_open():
            game_caption('Змейка || Основное меню')
            if quit_pressed():
                game.close_menu()

            draw_menu()
            handle_keys_menu()
            if game.reset:
                snake, obstacles = reset_game(True)
                game.reset = False
        else:
            if quit_pressed():
                game.open_menu()

            snake.draw()
            for obstacle in obstacles:
                obstacle.draw()

            handle_keys(snake)

            if game.slow_mode():
                x_pos, y_pos = snake.get_head_position()
                new_head = (
                    (x_pos + snake.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
                    (y_pos + snake.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
                )

                if snake_can_move(new_head, snake, obstacles):
                    snake.move(new_head)
                elif game.reset:
                    snake, obstacles = reset_game()
                    game.reset = False

                game.update_snake_speed(time())

            game_caption(game.info())

        clock.tick(GAME_SPEED)
        pg.display.update()

    quit_game()


if __name__ == '__main__':
    main()
