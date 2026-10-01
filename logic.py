import random


class _Abort(Exception):
    pass

class LetterSudoku:
    def __init__(self):
        self.valid_chars = [chr(i) for i in range(ord('A'), ord('P') + 1)]
        self.board = [['.' for _ in range(16)] for _ in range(16)]

    def is_valid_move(self, row, col, char):
        """Перевіряє, чи можна поставити символ char у клітинку (row, col)."""
        if char in self.board[row]:
            return False

        for i in range(16):
            if self.board[i][col] == char:
                return False

        start_row, start_col = 4 * (row // 4), 4 * (col // 4)
        for i in range(4):
            for j in range(4):
                if self.board[start_row + i][start_col + j] == char:
                    return False

        return True

    def find_empty(self):
        """Знаходить першу порожню клітинку (повертає рядок та стовпець)."""
        for i in range(16):
            for j in range(16):
                if self.board[i][j] == '.':
                    return (i, j)
        return None

    def fill_board(self):
        """Рекурсивно заповнює поле (генератор випадкового судоку)."""
        empty = self.find_empty()
        if not empty:
            return True

        row, col = empty

        chars = self.valid_chars.copy()
        random.shuffle(chars)

        for char in chars:
            if self.is_valid_move(row, col, char):
                self.board[row][col] = char

                if self.fill_board():
                    return True

                self.board[row][col] = '.'

        return False

    def generate_puzzle(self, empty_cells=130):
        """Створює ігрову дошку, приховуючи частину букв."""
        self.solved_board = [row[:] for row in self.board]

        cells_removed = 0
        while cells_removed < empty_cells:
            row = random.randint(0, 15)
            col = random.randint(0, 15)

            if self.board[row][col] != '.':
                self.board[row][col] = '.'
                cells_removed += 1

        self.start_board = [row[:] for row in self.board]

    def solve_current(self):
        """Backtracking + MRV на бітових масках з рандомізованими перезапусками."""
        start = [row[:] for row in self.board]
        limit = 3000

        while True:
            self.board = [row[:] for row in start]
            try:
                if self._solve_attempt(limit):
                    return True
                return False
            except _Abort:
                limit = int(limit * 1.5)

    def _solve_attempt(self, limit):
        FULL = (1 << 16) - 1
        rows = [0] * 16
        cols = [0] * 16
        boxes = [0] * 16
        empties = []

        for r in range(16):
            for c in range(16):
                ch = self.board[r][c]
                if ch == '.':
                    empties.append((r, c))
                else:
                    bit = 1 << (ord(ch) - ord('A'))
                    rows[r] |= bit
                    cols[c] |= bit
                    boxes[(r // 4) * 4 + c // 4] |= bit

        steps = 0

        def search(remaining):
            nonlocal steps
            if not remaining:
                return True

            steps += 1
            if steps > limit:
                raise _Abort()

            best_i, best_mask, best_count = -1, 0, 17
            for i, (r, c) in enumerate(remaining):
                mask = FULL & ~(rows[r] | cols[c] | boxes[(r // 4) * 4 + c // 4])
                cnt = bin(mask).count('1')
                if cnt == 0:
                    return False
                if cnt < best_count:
                    best_count, best_i, best_mask = cnt, i, mask
                    if cnt == 1:
                        break

            r, c = remaining[best_i]
            b = (r // 4) * 4 + c // 4
            remaining[best_i], remaining[-1] = remaining[-1], remaining[best_i]
            remaining.pop()

            bits = [1 << k for k in range(16) if best_mask >> k & 1]
            random.shuffle(bits)

            for bit in bits:
                rows[r] |= bit
                cols[c] |= bit
                boxes[b] |= bit
                self.board[r][c] = chr(ord('A') + bit.bit_length() - 1)

                if search(remaining):
                    return True

                rows[r] ^= bit
                cols[c] ^= bit
                boxes[b] ^= bit
                self.board[r][c] = '.'

            remaining.append((r, c))
            remaining[best_i], remaining[-1] = remaining[-1], remaining[best_i]
            return False

        return search(empties)