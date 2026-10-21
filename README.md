# Rush Hour

A single-file sliding-block traffic puzzle. Slide the vehicles out of the way and drive the red car through the exit.

- Drag vehicles along their lane, or focus one and use the arrow keys
- Undo, reset, and a hint that names the shortest next move
- Levels in four tiers with par scores and star ratings; best scores saved in the browser
- Light and dark themes

## Files

- `template.html` page source (game, styles, solver)
- `gen.py` puzzle generator (finds layouts by shortest-solution length)
- `build.py` embeds the puzzles into the template and writes `index.html`
- `check.js` runs the in-page solver against every puzzle and verifies par

## Build

    python3 gen.py 150 puzzles-6x6.json
    python3 build.py
    node check.js

Open `index.html` in a browser.
