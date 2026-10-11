"""Flask API for the Sudoku Solver."""
from flask import Flask, jsonify, render_template, request
from puzzles import example_board
from solver import solve_board
from validator import validate_board

app = Flask(__name__)
MAX_EVENTS = 200_000      # keeps the browser responsive; use /api/solve beyond this


def _get_board():
    """Return (board, error_response). Validates the JSON body."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "board" not in data:
        return None, (jsonify(valid=False, errors=["Request body must be JSON with a 'board' field."]), 400)
    errors = validate_board(data["board"])
    if errors:
        return None, (jsonify(valid=False, errors=errors), 400)
    return data["board"], None


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/example")
def example():
    return jsonify(board=example_board())


@app.post("/api/validate")
def validate():
    board, err = _get_board()
    return err if err else jsonify(valid=True, errors=[])


@app.post("/api/solve")
def solve():
    board, err = _get_board()
    if err:
        return err
    r = solve_board(board)
    return jsonify(valid=True, solvable=r["solvable"], board=r["board"], stats=r["stats"])


@app.post("/api/visualize")
def visualize():
    board, err = _get_board()
    if err:
        return err
    r = solve_board(board)
    if len(r["events"]) > MAX_EVENTS:
        return jsonify(valid=True, errors=[f"Search took {len(r['events'])} events; too many to visualize. Use Solve instead."]), 413
    return jsonify(valid=True, solvable=r["solvable"], initial=board, board=r["board"],
                   events=r["events"], stats=r["stats"])


if __name__ == "__main__":
    app.run(debug=True)
