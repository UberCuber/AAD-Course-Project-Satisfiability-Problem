#!/usr/bin/env python3
"""
Backtracking Sudoku Solver using
- Constraint satisfaction formulation
- MRV heuristic (Minimum Remaining Values)
- Forward checking
"""

import time
import copy


# ---------------------- Utility functions ----------------------

def print_board(board):
    """Pretty print Sudoku board"""
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("| ", end="")
            print(board[i][j] if board[i][j] != 0 else ".", end=" ")
        print()
    print()


def find_unassigned_mrv(board, domains):
    """
    Select unassigned cell using MRV heuristic:
    the one with the fewest remaining possible values.
    """
    min_len = 10
    best_cell = None
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                domain_size = len(domains[(i, j)])
                if domain_size < min_len:
                    min_len = domain_size
                    best_cell = (i, j)
    return best_cell


def is_valid(board, row, col, val):
    """Check Sudoku constraints for placing val at (row, col)."""
    # Row
    if val in board[row]:
        return False
    # Column
    for i in range(9):
        if board[i][col] == val:
            return False
    # 3x3 block
    start_r, start_c = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_r, start_r + 3):
        for c in range(start_c, start_c + 3):
            if board[r][c] == val:
                return False
    return True


def forward_check(board, domains, row, col, val):
    """
    Forward checking:
    After assigning val to (row, col), remove val from domains of
    related unassigned cells (same row, col, and block).
    Returns new_domains or None if any domain becomes empty.
    """
    new_domains = copy.deepcopy(domains)
    new_domains[(row, col)] = {val}
    board[row][col] = val  # <-- FIX: assign before propagation

    for k in range(9):
        # Row
        if board[row][k] == 0 and val in new_domains[(row, k)]:
            new_domains[(row, k)].discard(val)
            if not new_domains[(row, k)]:
                board[row][col] = 0  # undo before returning
                return None
        # Column
        if board[k][col] == 0 and val in new_domains[(k, col)]:
            new_domains[(k, col)].discard(val)
            if not new_domains[(k, col)]:
                board[row][col] = 0
                return None

    # 3x3 block
    start_r, start_c = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_r, start_r + 3):
        for c in range(start_c, start_c + 3):
            if board[r][c] == 0 and val in new_domains[(r, c)]:
                new_domains[(r, c)].discard(val)
                if not new_domains[(r, c)]:
                    board[row][col] = 0
                    return None

    board[row][col] = 0  # <-- restore before returning
    return new_domains


def solve_sudoku(board, domains):
    """Recursive backtracking solver with MRV + forward checking."""
    cell = find_unassigned_mrv(board, domains)
    if cell is None:
        return True  # Solved

    row, col = cell
    for val in sorted(domains[(row, col)]):
        if is_valid(board, row, col, val):
            new_domains = forward_check(board, domains, row, col, val)
            if new_domains is None:
                continue  # invalid move
            board[row][col] = val
            if solve_sudoku(board, new_domains):
                return True
            board[row][col] = 0  # backtrack
    return False


def initialize_domains(board):
    """Initialize domains for each variable based on current board."""
    domains = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                domains[(i, j)] = {board[i][j]}
            else:
                domains[(i, j)] = {v for v in range(1, 10) if is_valid(board, i, j, v)}
    return domains


# ---------------------- Main entry ----------------------

if __name__ == "__main__":
    # Example test case (easy Sudoku)
    board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]





    print("Initial Sudoku:")
    print_board(board)

    start_time = time.perf_counter()
    domains = initialize_domains(board)
    solved = solve_sudoku(board, domains)
    end_time = time.perf_counter()

    if solved:
        print("Solved Sudoku:")
        print_board(board)
    else:
        print("No solution found.")

    print(f"Time taken: {end_time - start_time:.4f} seconds")
