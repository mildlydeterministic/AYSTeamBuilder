# Team Builder

## 🧾 Overview

Team Builder is a portable tool for assigning balanced youth soccer teams. It uses player data and coaching constraints to build fair teams by:

- Computing a normalized skill score for each player
- Seeding each team with coaches and their associated players (or random fallback players)
- Distributing remaining players to teams to minimize total skill imbalance
- Enforcing sponsor and team size constraints

You can run Team Builder on macOS or Windows using standalone executables built from the Python source.

---

## ⚙️ Team Building Method

1. **Input CSV files** of players and coaches are loaded.
2. Players are parsed first to build the complete player pool.
3. Coaches are parsed and separated into head and assistant coach pools.
4. Reciprocated coach pairs are identified and used to create teams.
5. Remaining unpaired head coaches are matched with available assistant coaches, prioritizing pairings where one coach has an associated player.
6. Each team is seeded with one player per coach (if any); otherwise filled with random unassigned players.
7. Remaining players are sorted by skill and distributed to the lowest-score team that:
   - Has an available slot
   - Does not already have a sponsored player (if the player is sponsored)
   - Does not exceed the size of the smallest team by more than one player
8. Final results are exported to CSV with a team summary and standard deviation of team scores.

---

## 📥 Download

You can download the latest executable for your platform from the GitHub Actions **Artifacts** section:

1. Click the **Actions** tab in this repository
2. Select the latest **Build Executables** workflow run (triggered by a push to `main`)
3. Download the appropriate artifact:
   - `team_builder_windows` → `team_builder.exe`
   - `team_builder_macos` → `team_builder`

---

## 🖥️ Usage

Run the executable from the command line:

### 🧾 Syntax

```bash
./team_builder --players path/to/players.csv --coaches path/to/coaches.csv --team-size 7
```

### 📌 Example

```bash
./team_builder \
  --players data/players_6u.csv \
  --coaches data/coaches_6u.csv \
  --team-size 6
```

This will create `team_assignments.csv` in the current working directory and print summary stats.

---

## 📦 Input Expectations

**players.csv** must contain the following columns:

- `PlayerID`: unique ID for the player
- `Player Name`: full name (first and last)
- `Date Of Birth`: MM/DD/YYYY format (used to compute age to 1 decimal place, half-up rounded)
- `Years of Experience`: integer; column may be suffixed (e.g., `:(18643797)`), use the first matching prefix
- `Uniform Size Selection`: text size label; column may be suffixed, use the first matching prefix
- `Player Evaluation Ranking`: numeric or string evaluation score (format unknown)
- `sponsor_id`: optional column for sponsor tracking

**coaches.csv** must contain the following columns:

- `VolunteerID`: unique ID for the coach
- `VolunteerTypeID`: an identifier for the type of volunteer
- `Team Personnel Name`: full name (first and last)
- `Team Personnel Role`: either "Head Coach" or "Assistant Coach" (ignore other roles)
- `associatedPlayers`: will contain the PlayerID if applicable, or a value like "No Answer" if not provided
- `Coach Pair`: coach ID of a linked coach for pairing (both coaches must list each other to be considered paired)

Header names are hardcoded for now but can be updated in future versions.

---

## 📤 Output

- `team_assignments.csv`: player and coach team assignments. Usable for input into SportsConnect.
- Console output includes:
  - Standard deviation of team skill scores
  - Summary of each team: name, number of players, total score, and sponsor (if present)

---

## 🧊 Platform Notes

- macOS and Windows builds are generated via GitHub Actions
- No Python installation required for executables
- Run from Terminal (macOS) or Command Prompt/PowerShell (Windows)

---

For developers: see `spec.md` and module docstrings for implementation details.

