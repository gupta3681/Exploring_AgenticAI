from dataclasses import dataclass
from typing import List, Tuple



@dataclass
class ConnectFourBoard:
    """Represents the Connect Four board state and provides utility methods"""

    def __init__(self):
        # Simple representation: "R" for Red, "Y" for Yellow, "." for Empty
        self.rows = 4
        self.cols = 4
        self.board = [["." for _ in range(self.cols)] for _ in range(self.rows)]

    def get_board_state(self) -> list:
        """Returns the current board state as a list of lists"""
        return self.board

    
    def drop_piece(self, board: List[List[str]], col: int, piece: str) -> List[List[str]]:

        # Check if the column index is within the valid range
        if not (0 <= col < self.cols):
            return board  # Illegal move: column index out of range

        # Iterate from the bottom row upward to find the first empty slot ('.')
        for row in reversed(board):
            if row[col] == ".":
                row[col] = piece  # Place the piece
                return board     # Return the updated board

        # If no empty cell is found, the column is full.
        return board  # Illegal move: column is full, board remains unchanged
 

    def is_valid_move(self, col: int) -> bool:
        """Checks if a move (dropping a piece in a column) is valid."""
        return 0 <= col < self.cols and self.board[0][col] == "."

    def check_winner(self) -> str:
        """Checks the board for a winner. Returns 'R', 'Y', or '' if there's no winner."""
        # Check horizontal, vertical, and diagonal (both directions)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Right, Down, Down-Right, Down-Left

        for row in range(self.rows):
            for col in range(self.cols):
                current_piece = self.board[row][col]
                if current_piece == ".":
                    continue

                for dr, dc in directions:
                    count = 1
                    for i in range(1, 4):
                        r, c = row + dr * i, col + dc * i
                        if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == current_piece:
                            count += 1
                        else:
                            break
                    if count == 4:
                        return current_piece

        return ""  # No winner yet

    def is_full(self) -> bool:
        """Checks if the board is full, indicating a draw."""
        return all(cell != "." for cell in self.board[0])

    def reset_board(self) -> None:
        """Resets the board to its initial empty state."""
        self.board = [["." for _ in range(self.cols)] for _ in range(self.rows)]
