# Sudoku Game

This project is a Sudoku game implemented in Python using the Tkinter library. It provides a graphical user interface for playing Sudoku puzzles.

## Features

- **Sudoku Board Logic**: The `SudokuBoard` class handles the core logic of the Sudoku game, including setting and getting cell values, checking for valid moves, solving the board, generating a full board, and creating puzzles by removing numbers.
- **Graphical User Interface**: The `SudokuGUI` class manages the user interface, allowing players to interact with the game, select cells, input numbers, and receive hints.
- **Puzzle Loading**: The game can load Sudoku puzzles from a text file (`sudoku.txt`), which contains a 9x9 grid of numbers.

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)

## How to Run

1. Ensure you have Python installed on your system.
2. Clone the repository or download the project files.
3. Navigate to the project directory in your terminal.
4. Run the game using the following command:
   ```bash
   python sudoku_game.py
   ```

## Game Instructions

- Use the mouse to select a cell on the Sudoku board.
- Input numbers using the keyboard to fill in the cells.
- The game will check if your moves are valid and provide hints if needed.
- Complete the puzzle by filling in all cells correctly.

## File Structure

- `sudoku_game.py`: Contains the main game logic and GUI implementation.
- `sudoku.txt`: A sample Sudoku puzzle in text format.

## Contributing

Feel free to fork the repository and submit pull requests for any improvements or bug fixes.

## License

This project is open-source and available under the MIT License. 