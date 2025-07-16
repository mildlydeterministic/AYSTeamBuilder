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
6. Each team is seeded with two players, prioritizing players associated with the coach(es).
7. Remaining players are sorted by skill and assigned to the team that:
   - Has the lowest cumulative skill score
   - Has the fewest players
   - Does not already have a sponsored player (if the player is sponsored)
8. Final results are exported to CSV with a team summary and standard deviation of team scores.

---

## 🖥️ Usage

Run the script from the command line:

### 🧾 Syntax

```bash
python3 -m teambuilder_single.py --players path/to/players.csv --coaches path/to/coaches.csv --debug
```

### 📌 Example

```bash
python3 -m teambuilder_single.py\
  --players data/players_6u.csv \
  --coaches data/coaches_6u.csv \
  --debug
```

This will create `team_assignments.csv`, `team_summary.csv`, and `debug_players.csv` in the current working directory and print summary stats. `team_assignments.csv` can be modified or directly uploaded to SportsConnect. 

---

## 📦 Input Expectations

**players.csv** must contain the following columns:

- `PlayerID`: unique ID for the player
- `Player Name`: full name (first and last)
- `Date Of Birth`: MM/DD/YYYY format (used to compute age to 1 decimal place, half-up rounded)
- `Years of Experience`: integer; column may be suffixed (e.g., `:(18643797)`), use the first matching prefix
- `Uniform Size Selection`: text size label; column may be suffixed, use the first matching prefix
- `Player Evaluation Rating`: numeric evaluation score or "No Answer". 
- `sponsor_id`: optional column for sponsor tracking. Expects text for 

**coaches.csv** must contain the following columns:

- `VolunteerID`: unique ID for the coach
- `VolunteerTypeID`: an identifier for the type of volunteer
- `Team Personnel Name`: full name (first and last)
- `Team Personnel Role`: either "Head Coach" or "Assistant Coach" (ignore other roles)
- `associatedPlayers`: will contain the PlayerID if applicable, or a value like "No Answer" if not provided
- `Coach Pair`: VolunteerID of another coach for pairing (both coaches must list each other to be considered paired)

Header names are hardcoded for now but can be updated in future versions.

---

## 📤 Output

- `team_assignments.csv`: player and coach team assignments. Usable for input into SportsConnect.
- Console output includes:
  - Standard deviation of team skill scores
- `team_summary.csv` : Summary of each team: name, number of players, total score, and sponsor (if present)
- `debug_players.csv`: Player data and calculated skill score

---

## 🧊 Platform Notes

Built to run with Python 3.12+ using standard library only.
