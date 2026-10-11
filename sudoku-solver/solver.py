"""Set-based recursive backtracking Sudoku solver (instrumented).

This is the author's second LeetCode attempt. Changes: wrapped in a class so
events/statistics can be recorded, and candidates are iterated in sorted order
so runs are deterministic (plain set order can change between Python runs).
"""
import time

Board = list[list[str]]
ALL_DIGITS = set("123456789")


class SudokuSolver:
    def __init__(self, board: Board):
        self.board = [row[:] for row in board]          # working copy
        self.rows = [set() for _ in range(9)]
        self.cols = [set() for _ in range(9)]
        self.boxes = [set() for _ in range(9)]
        self.empty: list[tuple[int, int]] = []
        self.events: list[dict] = []
        self.stats = {"recursive_calls": 0, "placements_attempted": 0,
                      "successful_placements": 0, "backtracks": 0,
                      "empty_cells": 0, "events": 0, "time_ms": 0.0}
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == ".":
                    self.empty.append((i, j))
                else:
                    num = self.board[i][j]
                    self.rows[i].add(num)
                    self.cols[j].add(num)
                    self.boxes[(i // 3) * 3 + (j // 3)].add(num)
        self.stats["empty_cells"] = len(self.empty)

    def _log(self, type_: str, row=None, col=None, digit=None, depth=None) -> None:
        event = {"type": type_}
        if row is not None:
            event.update(row=row, col=col, digit=digit, depth=depth)
        self.events.append(event)

    def _dfs(self, idx: int) -> bool:
        self.stats["recursive_calls"] += 1               # every call to dfs
        if idx == len(self.empty):
            self._log("solved")                          # base case: stop, no backtracking
            return True

        x, y = self.empty[idx]
        b = (x // 3) * 3 + (y // 3)
        possible = ALL_DIGITS - self.rows[x] - self.cols[y] - self.boxes[b]

        for num in sorted(possible):
            self.board[x][y] = num                       # place + update the 3 sets
            self.rows[x].add(num)
            self.cols[y].add(num)
            self.boxes[b].add(num)
            self.stats["placements_attempted"] += 1
            self._log("place", x, y, num, idx + 1)

            if self._dfs(idx + 1):
                return True

            self.rows[x].remove(num)                     # undo sets + board
            self.cols[y].remove(num)
            self.boxes[b].remove(num)
            self.board[x][y] = "."
            self.stats["backtracks"] += 1
            self._log("backtrack", x, y, num, idx + 1)

        return False

    def solve(self) -> bool:
        start = time.perf_counter()
        solved = self._dfs(0)
        if not solved:
            self._log("unsolvable")
        self.stats["time_ms"] = round((time.perf_counter() - start) * 1000, 3)
        self.stats["events"] = len(self.events)
        # placements that were never undone = placements kept in the final board
        self.stats["successful_placements"] = (
            self.stats["placements_attempted"] - self.stats["backtracks"])
        return solved


def solve_board(board: Board) -> dict:
    """Solve a (validated) board. On failure the initial board is returned unchanged."""
    solver = SudokuSolver(board)
    solved = solver.solve()
    return {"solvable": solved, "board": solver.board, "events": solver.events,
            "stats": solver.stats}
