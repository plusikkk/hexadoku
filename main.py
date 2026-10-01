import tkinter as tk
from logic import LetterSudoku


class HexadokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hexadoku 16x16")
        self.root.geometry("700x750")

        self.cells = {}

        self.menu_frame = tk.Frame(self.root)
        self.game_frame = tk.Frame(self.root)

        self.show_menu()

    def show_menu(self):
        self.game_frame.pack_forget()
        self.menu_frame.pack(expand=True)

        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        tk.Label(self.menu_frame, text="HEXADOKU 16x16", font=("Arial", 24, "bold")).pack(pady=30)
        tk.Label(self.menu_frame, text="Оберіть рівень складності:", font=("Arial", 14)).pack(pady=10)

        tk.Button(self.menu_frame, text="Легкий", font=("Arial", 14), width=15,
                  command=lambda: self.start_game(100)).pack(pady=5)
        tk.Button(self.menu_frame, text="Середній", font=("Arial", 14), width=15,
                  command=lambda: self.start_game(130)).pack(pady=5)
        tk.Button(self.menu_frame, text="Складний", font=("Arial", 14), width=15,
                  command=lambda: self.start_game(160)).pack(pady=5)

    def start_game(self, empty_cells):
        self.menu_frame.pack_forget()

        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.game_frame.pack(expand=True)

        loading_label = tk.Label(self.game_frame, text="Генерую поле...\nЗачекайте кілька секунд.", font=("Arial", 14))
        loading_label.pack(pady=100)
        self.root.update()

        self.game = LetterSudoku()
        self.game.fill_board()
        self.game.generate_puzzle(empty_cells=empty_cells)

        loading_label.destroy()
        self.create_grid()

        buttons_frame = tk.Frame(self.game_frame)
        buttons_frame.pack(pady=15)

        tk.Button(buttons_frame, text="Розв'язати гру", font=("Arial", 12), command=self.solve_game, bg="#ffff99").grid(
            row=0, column=0, padx=10)
        tk.Button(buttons_frame, text="Повернутися до меню", font=("Arial", 12), command=self.show_menu).grid(row=0, column=1, padx=10)

    def create_grid(self):
        grid_frame = tk.Frame(self.game_frame, bg="black", bd=2)
        grid_frame.pack()

        for block_row in range(4):
            for block_col in range(4):
                block = tk.Frame(grid_frame, bg="black")
                block.grid(row=block_row, column=block_col, padx=2, pady=2)

                for i in range(4):
                    for j in range(4):
                        row = block_row * 4 + i
                        col = block_col * 4 + j
                        val = self.game.board[row][col]

                        entry = tk.Entry(
                            block, width=2, font=("Arial", 16, "bold"),
                            justify="center", bd=0, relief="solid"
                        )
                        entry.grid(row=i, column=j, padx=1, pady=1, ipady=5)

                        if val != '.':
                            entry.insert(0, val)
                            entry.config(state="readonly", readonlybackground="#e8e8e8", fg="#333333")
                        else:
                            entry.config(bg="white", fg="blue")

                        # Прив'язуємо події натискання клавіш та миші до кожної клітинки
                        entry.bind("<KeyRelease>", lambda e, r=row, c=col: self.on_key_release(e, r, c))
                        entry.bind("<FocusIn>", lambda e, r=row, c=col: self.on_focus_in(e, r, c))
                        entry.bind("<Button-1>", lambda e, r=row, c=col: self.on_focus_in(e, r, c))

                        self.cells[(row, col)] = entry

    def on_key_release(self, event, row, col):
        """Обробляє введення тексту в клітинку."""
        entry = self.cells[(row, col)]
        val = entry.get().upper()

        if len(val) > 1:
            val = val[-1]

        if val and val not in self.game.valid_chars:
            val = ""

        current = entry.get()
        if current != val:
            entry.delete(0, tk.END)
            entry.insert(0, val)

        self.highlight_cells(val)

    def on_focus_in(self, event, row, col):
        """Спрацьовує, коли гравець клікає на клітинку."""
        val = self.cells[(row, col)].get().upper()
        self.highlight_cells(val)

    def highlight_cells(self, active_char):
        """Розфарбовує клітинки: червоним — помилки (найвищий пріоритет), зеленим — однакові букви."""
        for (r, c), entry in self.cells.items():
            val = entry.get().upper()
            is_readonly = self.game.board[r][c] != '.'

            if not is_readonly and val and val != self.game.solved_board[r][c]:
                entry.config(bg="#ff9999")

            elif active_char and val == active_char and active_char in self.game.valid_chars:
                if is_readonly:
                    entry.config(readonlybackground="#aaffaa")
                else:
                    entry.config(bg="#aaffaa")

            else:
                if is_readonly:
                    entry.config(readonlybackground="#e8e8e8")
                else:
                    entry.config(bg="white")

    def solve_game(self):
        """Запускає алгоритм розв'язання та ініціює анімацію."""
        self.game.board = [row[:] for row in self.game.start_board]

        self.game.solve_current()

        self.cells_to_solve = []
        for r in range(16):
            for c in range(16):
                if self.game.start_board[r][c] == '.':
                    self.cells_to_solve.append((r, c))

        self.highlight_cells("")

        self.animate_solve(0)

    def animate_solve(self, index):
        """Анімовано виводить букви, які знайшов алгоритм."""
        if index < len(self.cells_to_solve):
            r, c = self.cells_to_solve[index]
            entry = self.cells[(r, c)]

            correct_char = self.game.board[r][c]

            entry.delete(0, tk.END)
            entry.insert(0, correct_char)

            entry.config(fg="#009900", bg="#ffffdd")

            if index > 0:
                prev_r, prev_c = self.cells_to_solve[index - 1]
                self.cells[(prev_r, prev_c)].config(bg="white")

            self.root.after(30, self.animate_solve, index + 1)
        else:
            if self.cells_to_solve:
                last_r, last_c = self.cells_to_solve[-1]
                self.cells[(last_r, last_c)].config(bg="white")

def main():
    root = tk.Tk()
    app = HexadokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()