import tkinter as tk
from tkinter import messagebox
import random
import copy
import os

class SudokuBoard:
    def __init__(self, size):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.subgrid_rows, self.subgrid_cols = self.get_subgrid_dimensions()

    def get_subgrid_dimensions(self):
        if self.size == 9:
            return 3, 3
        elif self.size == 8:
            return 4, 2
        elif self.size == 6:
            return 3, 2
        return 1, 1

    def set_cell(self, row, col, value):
        if 0 <= row < self.size and 0 <= col < self.size and 0 <= value <= self.size:
            self.grid[row][col] = value
            return True
        return False

    def get_cell(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return None

    def is_valid_move(self, row, col, value):
        if value == 0:
            return True
        for i in range(self.size):
            if i != col and self.grid[row][i] == value:
                return False
        for i in range(self.size):
            if i != row and self.grid[i][col] == value:
                return False
        start_row = (row // self.subgrid_rows) * self.subgrid_rows
        start_col = (col // self.subgrid_cols) * self.subgrid_cols
        for i in range(start_row, start_row + self.subgrid_rows):
            for j in range(start_col, start_col + self.subgrid_cols):
                if (i != row or j != col) and self.grid[i][j] == value:
                    return False
        return True

    def solve(self):
        empty = self.find_empty()
        if not empty:
            return True
        row, col = empty
        for value in range(1, self.size + 1):
            if self.is_valid_move(row, col, value):
                self.set_cell(row, col, value)
                if self.solve():
                    return True
                self.set_cell(row, col, 0)
        return False

    def find_empty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def get_hint(self, row=None, col=None):
        if row is not None and col is not None:
            # If specific cell is provided, get hint for that cell
            if self.grid[row][col] != 0:
                return None
            for value in range(1, self.size + 1):
                if self.is_valid_move(row, col, value):
                    temp_board = copy.deepcopy(self)
                    temp_board.set_cell(row, col, value)
                    if temp_board.solve():
                        return (row, col, value)
            return None
        else:
            # Original behavior for sequential hints
            empty = self.find_empty()
            if not empty:
                return None
            row, col = empty
            for value in range(1, self.size + 1):
                if self.is_valid_move(row, col, value):
                    temp_board = copy.deepcopy(self)
                    temp_board.set_cell(row, col, value)
                    if temp_board.solve():
                        return (row, col, value)
            return None

    def count_solutions(self, max_solutions=2):
        count = [0]
        def solver():
            if count[0] >= max_solutions:
                return
            empty = self.find_empty()
            if not empty:
                count[0] += 1
                return
            row, col = empty
            for value in range(1, self.size + 1):
                if self.is_valid_move(row, col, value):
                    self.set_cell(row, col, value)
                    solver()
                    self.set_cell(row, col, 0)
                    if count[0] >= max_solutions:
                        return
        solver()
        return count[0]

    def generate_full_board(self):
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        numbers = list(range(1, self.size + 1))
        random.shuffle(numbers)
        
        def fill_board(row, col):
            if col >= self.size:
                row += 1
                col = 0
            if row >= self.size:
                return True
                
            if self.grid[row][col] != 0:
                return fill_board(row, col + 1)
                
            random.shuffle(numbers)
            for value in numbers:
                if self.is_valid_move(row, col, value):
                    self.grid[row][col] = value
                    if fill_board(row, col + 1):
                        return True
                    self.grid[row][col] = 0
            return False
            
        return fill_board(0, 0)

    def remove_numbers(self, clues):
        cells = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(cells)
        removed = 0
        total_to_remove = self.size * self.size - clues
        for row, col in cells:
            if removed >= total_to_remove:
                break
            value = self.grid[row][col]
            if value == 0:
                continue
            self.grid[row][col] = 0
            temp_board = copy.deepcopy(self)
            if temp_board.count_solutions() == 1:
                removed += 1
            else:
                self.grid[row][col] = value
        return removed == total_to_remove

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.root.geometry("600x600")
        self.center_window()
        self.board = None
        self.cells = {}
        self.selected_cell = None
        self.original_cells = set()
        self.wrong_count = 3
        self.hint_count = 0
        self.max_hints = 3
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0", width=600, height=600)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.current_content = None
        self.difficulty_var = tk.StringVar(value="Medium")
        self.grid_size_var = tk.StringVar(value="9x9")
        self.load_game_var = tk.BooleanVar(value=False)
        self.wrong_count_label = None
        self.hint_count_label = None
        self.show_welcome_screen()

    def center_window(self):
        self.root.update_idletasks()
        width = 600
        height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def clear_content(self):
        if self.current_content:
            self.current_content.destroy()
        self.current_content = None

    def show_welcome_screen(self):
        self.clear_content()
        # Reset game state
        self.board = None
        self.cells.clear()
        self.selected_cell = None
        self.original_cells.clear()
        self.wrong_count = 3
        self.hint_count = 0
        
        self.current_content = tk.Frame(self.main_frame, bg="#f0f0f0", width=600, height=600)
        self.current_content.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.current_content, text="Welcome to Sudoku!", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)
        tk.Label(self.current_content, text="Difficulty:", bg="#f0f0f0", font=("Arial", 12)).pack()
        difficulty_menu = tk.OptionMenu(self.current_content, self.difficulty_var, "Easy", "Medium", "Hard")
        difficulty_menu.config(bg="#add8e6", font=("Arial", 12))
        difficulty_menu.pack(pady=5)
        tk.Label(self.current_content, text="Grid Size:", bg="#f0f0f0", font=("Arial", 12)).pack()
        grid_size_menu = tk.OptionMenu(self.current_content, self.grid_size_var, "9x9", "8x8", "6x6")
        grid_size_menu.config(bg="#add8e6", font=("Arial", 12))
        grid_size_menu.pack(pady=5)
        tk.Checkbutton(self.current_content, text="Load an existing game from sudoku.txt", variable=self.load_game_var, bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.current_content, text="Start Game", command=self.start_game, bg="#4caf50", fg="white", font=("Arial", 12)).pack(pady=10)
        self.root.update()

    def load_puzzle_from_file(self, filename="sudoku.txt"):
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File {filename} not found.")
            return None
        try:
            with open(filename, 'r') as file:
                lines = [line.strip().split() for line in file if line.strip()]
            size = len(lines)
            if size not in [6, 8, 9] or any(len(row) != size for row in lines):
                messagebox.showerror("Error", "Invalid grid size in sudoku.txt. Must be 6x6, 8x8, or 9x9.")
                return None
            grid = []
            for row in lines:
                grid_row = []
                for val in row:
                    if val == '0' or val == '.':
                        grid_row.append(0)
                    elif val.isdigit() and 1 <= int(val) <= size:
                        grid_row.append(int(val))
                    else:
                        messagebox.showerror("Error", "Invalid value in sudoku.txt. Use 0 or . for empty cells and numbers 1 to grid size.")
                        return None
                grid.append(grid_row)
            board = SudokuBoard(size)
            for i in range(size):
                for j in range(size):
                    board.set_cell(i, j, grid[i][j])
            if board.count_solutions() != 1:
                messagebox.showerror("Error", "Puzzle in sudoku.txt does not have exactly one solution.")
                return None
            return board
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sudoku.txt: {str(e)}")
            return None

    def save_puzzle_to_file(self, filename="sudoku.txt"):
        if not self.board:
            messagebox.showerror("Error", "No active game to save.")
            return
        try:
            with open(filename, 'w') as file:
                for i in range(self.board.size):
                    row = [str(self.board.get_cell(i, j)) for j in range(self.board.size)]
                    file.write(" ".join(row) + "\n")
            messagebox.showinfo("Success", "Game state saved to sudoku.txt.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to sudoku.txt: {str(e)}")

    def start_game(self):
        try:
            self.wrong_count = 3
            self.hint_count = 0
            if self.load_game_var.get():
                board = self.load_puzzle_from_file()
                if not board:
                    return
                self.board = board
                self.grid_size_var.set(f"{board.size}x{board.size}")
            else:
                grid_size = self.grid_size_var.get()
                size_map = {"9x9": 9, "8x8": 8, "6x6": 6}
                self.board = SudokuBoard(size_map[grid_size])
                self.generate_puzzle()
            self.show_game_screen()
            self.update_grid()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {str(e)}")
            self.show_welcome_screen()

    def show_game_screen(self):
        self.clear_content()
        self.current_content = tk.Frame(self.main_frame, bg="#f0f0f0", width=600, height=600)
        self.current_content.place(relx=0.5, rely=0.5, anchor="center")
        grid_frame = tk.Frame(self.current_content, bg="#f0f0f0")
        grid_frame.pack(side=tk.LEFT, padx=20, pady=20)
        cell_size = 50 if self.grid_size_var.get() == "6x6" else 40 if self.grid_size_var.get() == "8x8" else 35
        size = {"9x9": 9, "8x8": 8, "6x6": 6}[self.grid_size_var.get()]
        subgrid_rows, subgrid_cols = (3, 3) if size == 9 else (4, 2) if size == 8 else (3, 2)
        self.cells.clear()
        for i in range(size):
            for j in range(size):
                cell = tk.Entry(
                    grid_frame,
                    width=2,
                    font=("Arial", 16),
                    justify="center",
                    bg="white",
                    fg="black",
                    borderwidth=1,
                    relief="solid"
                )
                cell.grid(row=i, column=j, padx=1, pady=1, ipady=cell_size//4)
                cell.bind("<Button-1>", lambda e, r=i, c=j: self.select_cell(r, c))
                cell.bind("<Key>", self.handle_key)
                self.cells[(i, j)] = cell
        control_frame = tk.Frame(self.current_content, bg="#f0f0f0", width=150)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
        self.wrong_count_label = tk.Label(control_frame, text=f"Wrong Attempts Left: {self.wrong_count}", bg="#f0f0f0", font=("Arial", 12))
        self.wrong_count_label.pack(pady=5)
        self.hint_count_label = tk.Label(control_frame, text=f"Hints Used: {self.hint_count}/{self.max_hints}", bg="#f0f0f0", font=("Arial", 12))
        self.hint_count_label.pack(pady=5)
        buttons = [
            ("Hint", self.get_hint, "#ff9800"),
            ("Clear", self.clear_board, "#f44336"),
            ("Save", self.save_puzzle_to_file, "#2196f3")
        ]
        for text, command, color in buttons:
            btn = tk.Button(control_frame, text=text, command=command, bg=color, fg="white", font=("Arial", 12))
            btn.pack(pady=5, fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#cccccc"))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        self.root.update()

    def select_cell(self, row, col):
        if self.selected_cell:
            self.reset_cell_colors()
        self.selected_cell = (row, col)
        self.cells[(row, col)].config(bg="#add8e6")
        for i in range(self.board.size):
            self.cells[(row, i)].config(bg="#add8e6")
            self.cells[(i, col)].config(bg="#add8e6")
        start_row = (row // self.board.subgrid_rows) * self.board.subgrid_rows
        start_col = (col // self.board.subgrid_cols) * self.board.subgrid_cols
        for i in range(start_row, start_row + self.board.subgrid_rows):
            for j in range(start_col, start_col + self.board.subgrid_cols):
                self.cells[(i, j)].config(bg="#add8e6")
        self.cells[(row, col)].focus_set()

    def reset_cell_colors(self):
        for i in range(self.board.size):
            for j in range(self.board.size):
                self.cells[(i, j)].config(bg="white", fg="black" if (i, j) not in self.original_cells else "black")

    def handle_key(self, event):
        if not self.selected_cell or self.selected_cell in self.original_cells:
            return "break"
        row, col = self.selected_cell
        char = event.char
        if char in [str(i) for i in range(1, self.board.size + 1)]:
            value = int(char)
            if self.board.is_valid_move(row, col, value):
                self.board.set_cell(row, col, value)
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].insert(0, str(value))
                self.cells[(row, col)].config(fg="black")
                if self.is_board_complete():
                    if messagebox.askyesno("Congratulations", "Puzzle Solved! Start a new game?"):
                        self.generate_puzzle()
            else:
                self.wrong_count -= 1
                self.wrong_count_label.config(text=f"Wrong Attempts Left: {self.wrong_count}")
                self.cells[(row, col)].config(fg="red")
                if self.wrong_count <= 0:
                    messagebox.showinfo("Game Over", "No wrong attempts left! Returning to main menu.")
                    self.show_welcome_screen()
        elif char in ["\b", ""]:
            self.board.set_cell(row, col, 0)
            self.cells[(row, col)].delete(0, tk.END)
            self.cells[(row, col)].config(fg="black")
        return "break"

    def update_grid(self):
        if not self.cells or not self.board:
            return
        self.original_cells.clear()
        for i in range(self.board.size):
            for j in range(self.board.size):
                value = self.board.get_cell(i, j)
                self.cells[(i, j)].delete(0, tk.END)
                if value != 0:
                    self.cells[(i, j)].insert(0, str(value))
                    self.cells[(i, j)].config(fg="black", font=("Arial", 16, "bold"))
                    self.original_cells.add((i, j))
                else:
                    self.cells[(i, j)].config(fg="black", font=("Arial", 16))
                self.cells[(i, j)].config(bg="white", state="normal" if (i, j) not in self.original_cells else "readonly")
        if self.selected_cell:
            self.select_cell(*self.selected_cell)

    def generate_puzzle(self):
        if not self.board:
            return
        difficulty = self.difficulty_var.get()
        clue_map = {
            9: {"Easy": 36, "Medium": 30, "Hard": 25},
            8: {"Easy": 30, "Medium": 25, "Hard": 20},
            6: {"Easy": 20, "Medium": 16, "Hard": 12}
        }
        clues = clue_map[self.board.size][difficulty]
        self.board.generate_full_board()
        self.board.remove_numbers(clues)
        self.wrong_count = 3
        self.hint_count = 0
        self.update_grid()
        if self.wrong_count_label:
            self.wrong_count_label.config(text=f"Wrong Attempts Left: {self.wrong_count}")
        if self.hint_count_label:
            self.hint_count_label.config(text=f"Hints Used: {self.hint_count}/{self.max_hints}")
        messagebox.showinfo("Success", f"{difficulty} {self.board.size}x{self.board.size} puzzle generated with {clues} clues.")

    def get_hint(self):
        if not self.board:
            return
        if self.hint_count >= self.max_hints:
            messagebox.showinfo("Hint Limit", f"No more hints available (max {self.max_hints}).")
            return
        if not self.selected_cell:
            messagebox.showinfo("Hint", "Please select a cell first to get a hint.")
            return
        row, col = self.selected_cell
        if (row, col) in self.original_cells:
            messagebox.showinfo("Hint", "Cannot get hint for a pre-filled cell.")
            return
        hint = self.board.get_hint(row, col)
        if hint:
            row, col, value = hint
            self.board.set_cell(row, col, value)
            self.cells[(row, col)].delete(0, tk.END)
            self.cells[(row, col)].insert(0, str(value))
            self.cells[(row, col)].config(fg="black", font=("Arial", 16))
            self.hint_count += 1
            self.hint_count_label.config(text=f"Hints Used: {self.hint_count}/{self.max_hints}")
            if self.is_board_complete():
                if messagebox.askyesno("Congratulations", "Puzzle Solved! Start a new game?"):
                    self.generate_puzzle()
        else:
            messagebox.showinfo("Hint", "No valid hint available for this cell.")

    def clear_board(self):
        if not self.board:
            return
        for i in range(self.board.size):
            for j in range(self.board.size):
                if (i, j) not in self.original_cells:
                    self.board.set_cell(i, j, 0)
        self.wrong_count = 3
        self.hint_count = 0
        self.update_grid()
        self.wrong_count_label.config(text=f"Wrong Attempts Left: {self.wrong_count}")
        self.hint_count_label.config(text=f"Hints Used: {self.hint_count}/{self.max_hints}")
        self.selected_cell = None

    def is_board_complete(self):
        if not self.board:
            return False
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.get_cell(i, j) == 0:
                    return False
                if not self.board.is_valid_move(i, j, self.board.get_cell(i, j)):
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop() 