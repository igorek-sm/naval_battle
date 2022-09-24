from random import randint

# Описание класса "точка":

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


# Описание классов исключений:

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за пределы доски!'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку!'


class BoardWrongShipException(BoardException):
    pass


# Описание класса "корабль":

class Ship:
    def __init__(self, bow, length, orient):
        self.bow = bow
        self.length = length
        self.orient = orient
        self.lives = length

    @property
    def parts(self):    # Определение длины и направления корабля
        ship_parts = []
        for i in range(self.length):
            horisontal = self.bow.x
            vertical = self.bow.y

            if self.orient == 0:
                horisontal += i
            elif self.orient == 1:
                vertical += i

            ship_parts.append(Dot(horisontal, vertical))

        return ship_parts

    def shooten(self, shot):    # Возврат True, если попали в корабль
        return shot in self.parts


# Описание класса "Игровое поле":

class Board:
    def __init__(self, hidden = False, size = 6):
        self.hidden = hidden
        self.size = size
        self.count = 0
        self.field = [['O']*size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):  # Собственно отрисовка игрового поля
        draw = ''
        draw += '   | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, sym in enumerate(self.field):
            draw += f'\n {i+1} | ' + ' | '.join(sym) + ' |'

        if self.hidden:
            draw = draw.replace('■', 'O')
        return draw

    def out(self, d):   # Возврат True, если попали за пределы поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):  # Отрисовка точек вокруг корабля, если verb == True
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)]

        for d in ship.parts:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.parts:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.parts:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):  # Описание стрельбы по доске
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.parts:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True
        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self):    # Очистка списка занятых клеток
        self.busy = []


# Описание класса "игрок":

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as err:
                print(err)


# Описание класса "AI":

class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0,5))
        print(f'Ход компьютера: {d.x+1} {d.y+1}')
        return d


# Описание класса "игрок":

class User(Player):
    def ask(self):
        while True:
            coords = input('Ваш ход: ').split()

            if len(coords) != 2:
                print('Введите 2 координаты!')
                continue

            x, y = coords

            if not (x.isdigit()) and not (y.isdigit()):
                print('Введите числа!')
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


# Описание класса "игра":

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print('-'*57)
        print('Приветствуем Вас в игре Морской Бой!'.center(57))
        print('-'*57)
        print('Формат ввода: две координаты через пробел'.center(57))
        print('(x y, где x - номер строки, y - номер столбца)'.center(57))
        
    def board_split(self):
        us_split = str(self.us.board).splitlines()
        ai_split = str(self.ai.board).splitlines()
        common_board = '      Доска пользователя:' + ' '*13 + 'Доска компьютера: \n'
        
        for i in range(self.size + 1):
            common_board += us_split[i] + '   ' + ai_split[i] + '\n'

        return common_board


    def loop(self):
        num = 0
        while True:
            print('-'*57)
            print()
            print(self.board_split())
            print('-' * 57)
            if num % 2 == 0:
                print('Ходит пользователь!'.center(57))
                repeat = self.us.move()
            else:
                print('Ходит компьютер!'.center(57))
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('-' * 57)
                print('Пользователь выиграл!'.center(57)+'\n')
                print(self.board_split())
                break

            if self.us.board.count == 7:
                print('-' * 57)
                print('Компьютер выиграл!'.center(57)+'\n')
                print(self.board_split())
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()