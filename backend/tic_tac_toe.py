import enum
from typing import Optional


class Sign(enum.Enum):
    NONE = None
    NOUGHT = "o"
    CROSS = "x"


def next_turn(turn: Sign) -> Sign:
    if turn == Sign.NOUGHT:
        return Sign.CROSS
    if turn == Sign.CROSS:
        return Sign.NOUGHT
    raise ValueError(f"Unexpected turn value: {turn!r}")


class GameplayError(Exception):
    pass


class UsedFieldError(GameplayError):
    def __init__(self, row: int, col: int):
        super().__init__(f"Field (row={row};col={col}) is used")


class NotPlayersTurnError(GameplayError):
    def __init__(self):
        super().__init__("Wait for second player's move")


class TicTacToe:
    board: list[list[Sign]]
    turn: Sign

    def __init__(self, field=3):
        self.board = [[Sign.NONE for _ in range(field)] for _ in range(field)]
        self.turn = Sign.CROSS

    def move(self, row: int, col: int):
        if self.board[row][col] != Sign.NONE:
            raise UsedFieldError(row, col)
        self.board[row][col] = self.turn
        self.turn = next_turn(self.turn)

    @property
    def state(self) -> list[list[Optional[str]]]:
        return [[cell.value for cell in row] for row in self.board]

    @property
    def game_over(self) -> bool:
        signed = sum(sum(1 for cell in row if cell != Sign.NONE) for row in self.board)
        n = len(self.board)
        return self.winner != Sign.NONE or signed == n ** 2

    @property
    def winner(self) -> Sign:
        n = len(self.board)

        # rows
        for i in range(n):
            p1, p2 = 0, 0
            for j in range(n):
                if self.board[i][j] == Sign.NOUGHT:
                    p1 += 1
                if self.board[i][j] == Sign.CROSS:
                    p2 += 1
            if p1 == n:
                return Sign.NOUGHT
            if p2 == n:
                return Sign.CROSS

        # cols
        for i in range(n):
            p1, p2 = 0, 0
            for j in range(n):
                if self.board[j][i] == Sign.NOUGHT:
                    p1 += 1
                if self.board[j][i] == Sign.CROSS:
                    p2 += 1
            if p1 == n:
                return Sign.NOUGHT
            if p2 == n:
                return Sign.CROSS

        # diagonal 1
        p1, p2 = 0, 0
        for i in range(n):
            if self.board[i][i] == Sign.NOUGHT:
                p1 += 1
            if self.board[i][i] == Sign.CROSS:
                p2 += 1
        if p1 == n:
            return Sign.NOUGHT
        if p2 == n:
            return Sign.CROSS

        # diagonal 2
        p1, p2 = 0, 0
        for i in range(n):
            if self.board[n - i - 1][i] == Sign.NOUGHT:
                p1 += 1
            if self.board[n - i - 1][i] == Sign.CROSS:
                p2 += 1
        if p1 == n:
            return Sign.NOUGHT
        if p2 == n:
            return Sign.CROSS

        return Sign.NONE
