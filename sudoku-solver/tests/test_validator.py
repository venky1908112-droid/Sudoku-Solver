from puzzles import example_board
from validator import validate_board

def blank(): return [["."] * 9 for _ in range(9)]

def test_valid_cases():
    assert validate_board(blank()) == []
    assert validate_board(example_board()) == []

def test_duplicates():
    b = blank(); b[0][0] = b[0][5] = "4"
    assert any("row 1" in e for e in validate_board(b))
    b = blank(); b[0][0] = b[7][0] = "4"
    assert any("column 1" in e for e in validate_board(b))
    b = blank(); b[0][0] = b[2][2] = "4"
    assert any("box 1" in e for e in validate_board(b))

def test_bad_shape_and_chars():
    assert validate_board([["."] * 9] * 8)
    b = blank(); b[3] = ["."] * 8
    assert validate_board(b)
    b = blank(); b[1][1] = "0"
    assert validate_board(b)
    b[1][1] = "ab"
    assert validate_board(b)
    assert validate_board("nope")
