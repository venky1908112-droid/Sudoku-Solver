import copy
from app import app
from puzzles import example_board
from solver import solve_board

def forward(values, e):
    if e["type"] == "place":
        r, c, d = e["row"], e["col"], e["digit"]
        assert values[r][c] == "."                         # only into an empty cell
        assert d not in values[r] and d not in [values[i][c] for i in range(9)]
        br, bc = (r // 3) * 3, (c // 3) * 3
        assert all(values[br + a][bc + k] != d for a in range(3) for k in range(3))
        values[r][c] = d
    elif e["type"] == "backtrack":
        assert values[e["row"]][e["col"]] == e["digit"]    # removes what was placed
        values[e["row"]][e["col"]] = "."

def backward(values, e):                                    # mirrors step(-1) in visualizer.js
    if e["type"] == "place":
        values[e["row"]][e["col"]] = "."
    elif e["type"] == "backtrack":
        values[e["row"]][e["col"]] = e["digit"]

def test_events_valid_and_replay_reaches_solution():
    puzzle = example_board()
    res = solve_board(puzzle)
    vals = copy.deepcopy(puzzle)
    for e in res["events"]:
        forward(vals, e)
    assert vals == res["board"]
    assert res["events"][-1]["type"] == "solved"
    assert [e["type"] for e in res["events"]].count("solved") == 1

def test_backward_restores_every_state_and_initial():
    puzzle = example_board()
    res = solve_board(puzzle)
    vals, snaps = copy.deepcopy(puzzle), []
    for e in res["events"]:
        snaps.append(copy.deepcopy(vals)); forward(vals, e)
    for e, snap in zip(reversed(res["events"]), reversed(snaps)):
        backward(vals, e)
        assert vals == snap
    assert vals == puzzle

def test_has_real_backtracking():
    assert solve_board(example_board())["stats"]["backtracks"] > 0

def test_api():
    c = app.test_client()
    b = c.get("/api/example").get_json()["board"]
    assert c.post("/api/validate", json={"board": b}).status_code == 200
    r = c.post("/api/visualize", json={"board": b}).get_json()
    assert r["solvable"] and r["initial"] == b and r["events"][-1]["type"] == "solved"
    s = c.post("/api/solve", json={"board": b}).get_json()
    assert s["board"] == r["board"] and s["stats"]["events"] == len(r["events"])
    bad = copy.deepcopy(b); bad[0][2] = "5"
    assert c.post("/api/solve", json={"board": bad}).status_code == 400
    assert c.post("/api/solve", data="x").status_code == 400
    assert c.get("/").status_code == 200
