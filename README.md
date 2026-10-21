# Rush Hour

A single-file sliding-block traffic puzzle. Slide the vehicles out of the way and drive the red car through the exit.

- 8x8 board, 40 puzzles in four tiers (the 6x6 version is tagged `v0.1.0-beta`)
- Drag vehicles along their lane, or focus one and use the arrow keys
- Undo, reset, and a hint that names the shortest next move
- Par scores and star ratings; best scores saved on the device
- Light and dark themes
- Works offline: the fonts are embedded, so `index.html` needs no network
- Android app for sideloading (no Google Play), see below

## Files

- `index.html` the built game, open it in a browser
- `template.html` page source (game, styles, solver); board size is a build parameter
- `gen.cpp` puzzle generator: hill-climbs layouts, labels every state with its distance to a solution
- `pick.py` chooses ten puzzles per tier from the generator output
- `build.py` embeds the puzzles and fonts into the template and writes a standalone page
- `check.js` runs the in-page solver on every puzzle and verifies par
- `fetch_fonts.py` downloads Barlow and writes `fonts/fonts.css` (already committed)
- `puzzles-8x8.json`, `puzzles-6x6.json` the puzzle sets
- `android/` the Android project (a WebView that loads the bundled page)
- `build-android.ps1` builds and signs the APK into `dist/`

## Build the web page

    g++ -O2 -std=c++17 -o gen gen.cpp
    ./gen 8 420 15 20 200000 1 > candidates.txt     # N seconds minVehicles maxVehicles stateLimit seed
    python pick.py candidates.txt puzzles-8x8.json 5-9,10-16,18-26,30-45
    python build.py 8 puzzles-8x8.json index.html
    node check.js index.html

## Build the Android app

The app is a single activity with a WebView that loads `index.html` from the APK's assets. It has no
INTERNET permission, so it cannot reach the network. Package id `com.eladkoren.rushhour`, Android 8.0 and up.

Needed once, on Windows:

- JDK 17 at `%LOCALAPPDATA%\Android\jdk-17` (or set `JAVA_HOME`)
- Android SDK at `%LOCALAPPDATA%\Android\Sdk` with `platforms;android-35` and `build-tools;35.0.0` (or set `ANDROID_HOME`)
- Python 3 and Node on `PATH`

Then:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\build-android.ps1

The first run creates a release signing key in `%USERPROFILE%\.rushhour-signing` and records its
password in `android/keystore.properties` (not committed). **Back up that key.** An update only installs
over an existing copy if it is signed with the same key. The script then builds, signs and verifies
`dist/rush-hour-<version>.apk`.

Install it by copying the APK to the phone and opening it (allow "install unknown apps" for the app you
open it from), or with USB debugging on:

    adb install -r dist\rush-hour-0.2.0.apk

To release a new version, raise `versionCode` and `versionName` in `android/app/build.gradle`.

## Fonts

Barlow and Barlow Condensed are by Jeremy Tribby and licensed under the SIL Open Font License 1.1
(<https://openfontlicense.org>). Their Latin subsets are embedded in `fonts/fonts.css`.
