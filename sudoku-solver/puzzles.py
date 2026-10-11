"""Sample puzzles ('.' = empty cell)."""
EXAMPLE = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1",
           "7...2...6", ".6....28.", "...419..5", "....8..79"]

def example_board() -> list[list[str]]:
    return [list(row) for row in EXAMPLE]
