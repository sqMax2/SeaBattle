# Sea Battle Game
from random import randint
from random import getrandbits


# Dots properties
class Dot:
    # Initial attributes:
    # x & y - dot position
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def __eq__(self, other):
        return self._x == other.x and self._y == other.y

    def __repr__(self):
        return f'Dot({self._x}, {self._y})'

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if int(value):
            self._x = int(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if int(value):
            self._y = int(value)


# Exceptions
class SBException(Exception):
    pass


class PositionException(SBException):
    def __str__(self):
        return 'Out of board'


class ForbiddenDotException(SBException):
    def __str__(self):
        return 'Wrong dot'


class ShipPlacementException(SBException):
    pass


# Game ships
class Ship:
    def __init__(self, position, length, horizontal):
        # Left upper corner
        self._position = position
        # Ship doesn't store damaged dots. It's only displayed at game field.
        # Ship dies when number of hits is equal to it's health (length)
        self._length = self.health = length
        # Ship rotation
        self._horizontal = horizontal

    # List of all ship's dots
    @property
    def dots(self):
        ship_dots = []
        for i in range(self._length):
            x = self._position.x
            y = self._position.y

            if self._horizontal:
                x += i
            else:
                y += i

            ship_dots.append(Dot(x, y))

        return ship_dots

    def hit_check(self, shot):
        return shot in self.dots


# Game board
class Board:
    def __init__(self, owner, game, size=6):
        self._size = size
        self._owner = owner
        self._game = game
        # Win condition at 7 lost ships
        self.loss_counter = 0
        # List stores game field representation
        self.field = [["O"] * self._size for _ in range(self._size)]
        # List of game field items
        self.content = []
        # List of placed ships
        self.ships = []

    @property
    def size(self):
        return self._size

    def __str__(self):
        output = ''
        output += '  ' + ' '.join([f'| {i+1}' for i in range(self._size)]) + ' |'
        for i, row in enumerate(self.field):
            output += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        # Hides opponent's ships
        if self._owner != self._game.currentPlayer:
            output = output.replace("■", "O")
        return output

    def outbound_check(self, dot):
        return not ((0 <= dot.x < self._size) and (0 <= dot.y < self._size))

    # Draws ship's boundary
    def ship_contour(self, ship, wreckage=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.dots:
            for dx, dy in near:
                test_dot = Dot(dot.x + dx, dot.y + dy)

                if not (self.outbound_check(test_dot)) and test_dot not in self.content:
                    if wreckage:
                        self.field[test_dot.x][test_dot.y] = "."
                    self.content.append(test_dot)

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.outbound_check(dot) or dot in self.content:
                raise ShipPlacementException()

        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.content.append(dot)

        self.ships.append(ship)
        self.ship_contour(ship)

    def shot(self, dot):
        if self.outbound_check(dot):
            raise PositionException()

        if dot in self.content:
            raise ForbiddenDotException()

        self.content.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.health -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.health == 0:
                    self.loss_counter += 1
                    self.ship_contour(ship, True)
                    print("Destruction!")
                    return False
                else:
                    print("Hit!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Miss!")
        return False

    # Cleans board items after ship placing
    def purge(self):
        self.content = []


# Player interface
class IPlayer:
    def __init__(self, board, opponent_board):
        self.board = board
        self.opponent_board = opponent_board

    def request(self):
        # Obligatory to implement by child
        raise NotImplementedError()

    def turn(self):
        while True:
            try:
                target = self.request()
                repeat = self.opponent_board.shot(target)
                return repeat
            except SBException as exception:
                print(exception)


# Human player
class Human(IPlayer):
    def request(self):
        while True:
            cords = input("Make Your shoot: ").split()

            if len(cords) != 2:
                print(" Type in 2 coordinates in 'x y' style ")
                continue

            y, x = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Coordinates must be digits ")
                continue

            x, y = int(x) - 1, int(y) - 1

            return Dot(x, y)


# AI player
class AI(IPlayer):
    def request(self):
        dot = Dot(randint(0, self.board.size - 1), randint(0, self.board.size - 1))
        print(f"Computer turn: {dot.x + 1} {dot.y + 1}")
        return dot


# Main game flow process
class GameFlow:
    def __init__(self, size=6):
        self.size = size
        self.player = None
        self.ai = None
        self.currentPlayer = None
        player_board = self.random_board(self.player)
        computer_board = self.random_board(self.ai)

        self.ai = AI(computer_board, player_board)
        self.player = Human(player_board, computer_board)

    def random_board(self, owner):
        board = None
        while board is None:
            board = self.random_place(owner)
        return board

    def random_place(self, owner):
        ship_types = [3, 2, 2, 1, 1, 1, 1]
        board = Board(owner, self, size=self.size)
        attempts = 0
        for s_len in ship_types:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), s_len, bool(getrandbits(1)))
                try:
                    board.add_ship(ship)
                    break
                except ShipPlacementException:
                    pass
        board.purge()
        return board

    def greeting(self):
        print("--------------------")
        print("       Welcome      ")
        print("    to Sea Battle   ")
        print("        Game        ")
        print("--------------------")
        print("  Shoot by typing:  ")
        print("         x y        ")

    def game_cycle(self):
        num = 0
        while True:
            self.currentPlayer = self.player
            print("-" * 20)
            print("Player board:")
            print(self.player.board)
            print("-" * 20)
            print("Computer board:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Player turn")
                self.currentPlayer = self.player
                repeat = self.player.turn()
            else:
                print("-" * 20)
                print("Computer turn")
                self.currentPlayer = self.ai
                repeat = self.ai.turn()
            if repeat:
                num -= 1

            if self.ai.board.loss_counter == 7:
                print("-" * 20)
                print("Player won!")
                break

            if self.player.board.loss_counter == 7:
                print("-" * 20)
                print("Computer won!")
                break
            num += 1

    def start(self):
        self.greeting()
        self.game_cycle()


the_game = GameFlow()
the_game.start()
