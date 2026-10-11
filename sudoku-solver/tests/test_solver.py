import copy
from puzzles import example_board
from solver import SudokuSolver, solve_board

def blank(): return [["."] * 9 for _ in range(9)]

def assert_complete(b):
    full = set("123456789")
    for i in range(9):
        assert set(b[i]) == full
        assert {b[r][i] for r in range(9)} == full
        r, c = (i // 3) * 3, (i % 3) * 3
        assert {b[r + a][c + k] for a in range(3) for k in range(3)} == full

def test_solves_example_and_keeps_clues():
    puzzle = example_board()
    original = copy.deepcopy(puzzle)
    res = solve_board(puzzle)
    assert res["solvable"] and puzzle == original      # input not mutated
    assert_complete(res["board"])
    for i in range(9):
        for j in range(9):
            if original[i][j] != ".":
                assert res["board"][i][j] == original[i][j]

def test_empty_board_solves():
    assert_complete(solve_board(blank())["board"])

def test_already_solved_board():
    solved = solve_board(example_board())["board"]
    res = solve_board(solved)
    assert res["solvable"] and res["board"] == solved
    assert res["events"] == [{"type": "solved"}] and res["stats"]["recursive_calls"] == 1

def test_unsolvable_immediately_restores_board():
    b = blank()
    b[0] = list("12345678.")
    b[1][8] = "9"                      # valid, but cell (0,8) has no candidate
    res = solve_board(b)
    assert not res["solvable"] and res["board"] == b
    assert res["events"][-1] == {"type": "unsolvable"}

def test_unsolvable_after_deep_search_rolls_back_everything():
    b = example_board()
    b[0][2] = "1"                      # valid-looking clue that contradicts the unique solution
    s = SudokuSolver(b)
    assert not s.solve()
    assert s.board == b                # every placement was undone
    assert s.stats["backtracks"] > 0
    assert s.stats["placements_attempted"] == s.stats["backtracks"]
    fresh = SudokuSolver(b)            # sets must equal their initial (clue-only) state
    assert (s.rows, s.cols, s.boxes) == (fresh.rows, fresh.cols, fresh.boxes)

def test_sets_consistent_with_board_after_solve():
    s = SudokuSolver(example_board())
    assert s.solve()
    for i in range(9):
        assert s.rows[i] == set(s.board[i])
        assert s.cols[i] == {s.board[r][i] for r in range(9)}
        r, c = (i // 3) * 3, (i % 3) * 3
        assert s.boxes[i] == {s.board[r + a][c + k] for a in range(3) for k in range(3)}

def test_stats_are_consistent():
    r = solve_board(example_board())
    st = r["stats"]
    assert st["empty_cells"] == 51
    assert st["events"] == len(r["events"])
    assert st["successful_placements"] == st["empty_cells"]
    assert st["placements_attempted"] == st["backtracks"] + st["successful_placements"]
    assert st["recursive_calls"] == st["placements_attempted"] + 1
