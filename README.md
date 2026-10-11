# Sudoku Solver – Visualize Recursion and Backtracking

A Flask + vanilla JS website that solves Sudoku with my set-based recursive DFS (LeetCode attempt #2) and replays the solver's *real* execution events step by step.

## Run
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py            # open http://127.0.0.1:5000
python -m pytest -q      # tests
```

## Architecture
- `solver.py` – the algorithm + event/statistics recording
- `validator.py` – shape, character, duplicate checks
- `app.py` – Flask routes; `puzzles.py` – example puzzle
- `templates/`, `static/` – UI; `static/js/visualizer.js` replays the event log in the browser
- `tests/` – pytest suite

## Algorithm
`rows/cols/boxes` are lists of 9 sets; `empty` lists the blank cells. `dfs(idx)` takes the cell `empty[idx]`, computes `candidates = {1..9} - rows[x] - cols[y] - boxes[b]`, places each candidate (board + 3 sets), recurses, and on failure undoes all four changes. Returning `True` at `idx == len(empty)` ends the search without undoing anything.
Differences from the LeetCode version: wrapped in a class for recording, and candidates are tried in `sorted()` order so event logs are reproducible. No MRV/other optimizations.
Complexity: time O(9^k) worst case (k = empty cells), space O(k) recursion + O(1) sets.

## Events and statistics
Events: `place`, `backtrack`, `solved`, `unsolvable` (`{type,row,col,digit,depth}`; depth = index of the empty cell, 1-based).
Stats: `recursive_calls` (every `dfs` call), `placements_attempted` (every candidate placed), `backtracks` (every placement undone), `successful_placements` (attempted − backtracks = placements kept in the final board), `empty_cells`, `events`, `time_ms` (solver only).
Backward stepping: undoing `place` clears the cell; undoing `backtrack` restores the removed digit.

## API
`GET /api/example` · `POST /api/validate` · `POST /api/solve` · `POST /api/visualize` – body `{"board": [["5","3",".",...], ...]}`. Invalid boards return 400 with `errors`; valid-but-unsolvable boards return 200 with `solvable:false` and the unchanged board; visualizations over 200,000 events return 413.

## Push to GitHub
```bash
git init && git add . && git commit -m "Sudoku solver with backtracking visualizer"
git branch -M main && git remote add origin https://github.com/<you>/sudoku-solver.git && git push -u origin main
```
Then replace the placeholder GitHub link in `templates/index.html`.
