"""Validates board shape, characters and initial Sudoku constraints."""
DIGITS = "123456789"

def validate_board(board) -> list[str]:
    """Return a list of error messages (empty list = valid board)."""
    if not isinstance(board, list) or len(board) != 9:
        return ["Board must have exactly 9 rows."]
    errors = []
    for i, row in enumerate(board):
        if not isinstance(row, list) or len(row) != 9:
            errors.append(f"Row {i + 1} must have exactly 9 cells.")
    if errors:
        return errors
    for i in range(9):
        for j in range(9):
            v = board[i][j]
            if not (isinstance(v, str) and len(v) == 1 and (v == "." or v in DIGITS)):
                errors.append(f"Invalid value {v!r} at row {i + 1}, column {j + 1}.")
    if errors:
        return errors
    units = {}
    for i in range(9):
        units[f"row {i + 1}"] = [(i, j) for j in range(9)]
        units[f"column {i + 1}"] = [(j, i) for j in range(9)]
        r, c = (i // 3) * 3, (i % 3) * 3
        units[f"box {i + 1}"] = [(r + a, c + b) for a in range(3) for b in range(3)]
    for name, cells in units.items():
        seen = set()
        for r, c in cells:
            d = board[r][c]
            if d == ".":
                continue
            if d in seen:
                errors.append(f"Duplicate {d} in {name}.")
            seen.add(d)
    return errors
