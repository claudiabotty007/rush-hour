# Rush Hour

A single-file sliding-block traffic puzzle. Slide the vehicles out of the way and drive the red car through the exit.

- 8x8 board, 40 puzzles in four tiers (the 6x6 version is tagged `v0.1.0-beta`)
- Drag vehicles along their lane, or focus one and use the arrow keys
- Undo, reset, and a hint that names the shortest next move
- Par scores and star ratings; best scores saved in the browser
- Light and dark themes

## Files

- `index.html` the built game, open it in a browser
- `template.html` page source (game, styles, solver); board size is a build parameter
- `gen.cpp` puzzle generator: hill-climbs layouts, labels every state with its distance to a solution
- `pick.py` chooses ten puzzles per tier from the generator output
- `build.py` embeds the puzzles into the template
- `check.js` runs the in-page solver on every puzzle and verifies par
- `puzzles-8x8.json`, `puzzles-6x6.json` the puzzle sets

## Build

    g++ -O2 -std=c++17 -o gen gen.cpp
    ./gen 8 420 15 20 200000 1 > candidates.txt     # N seconds minVehicles maxVehicles stateLimit seed
    python3 pick.py candidates.txt puzzles-8x8.json 5-9,10-16,18-26,30-45
    python3 build.py 8 puzzles-8x8.json index.html
    node check.js index.html
