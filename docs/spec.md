# Team Builder - Project Specification

## 🧾 Purpose

Create a portable, reproducible Python-based tool to assign balanced youth soccer teams based on skill scores, coach assignments, and team size constraints.

## 🧱 Requirements

### Inputs

- `players.csv`: CSV file with player data.

  - Must include:
    - `PlayerID`: unique player ID
    - `Player Name`: first and last name
    - `Date Of Birth`: MM/DD/YYYY (used to compute age with 1 decimal precision)
    - `Years of Experience`: integer; column header may be suffixed (use the first matching prefix)
    - `Uniform Size Selection`: categorical size value; header may be suffixed (use the first matching prefix)
    - `Player Evaluation Ranking`: skill score (format currently unknown)
    - `sponsor_id`: optional sponsor identifier

- `coaches.csv`: CSV file with coach data.

  - Must include:
    - `VolunteerID`: coach ID
    - `Team Personnel Name`: full name (first and last)
    - `Team Personnel Role`: "Head Coach" or "Assistant Coach" (ignore others)
    - `associatedPlayers`: linked player ID if available; values like "No Answer" mean none
    - `Coach Pair`: ID of paired coach (both coaches must reference each other to form a valid pair)
    - `VolunteerTypeID`:  included in output

### Command-line Arguments

- `--players path/to/players.csv`
- `--coaches path/to/coaches.csv`
- `--team-size 7`

### Outputs

- `team_assignments.csv` written to the current working directory
  - Contains multiple rows per team, one per Coach and Player assigned to that team
    - Coach rows include: `TeamName`, `VolunteerID`, `VolunteerTypeID`, `Team Personnel Name`, `Team Personnel Role`
    - Player rows include: `TeamName`, `PlayerID`, `Player Name`
- `team_summary.csv` written to the current working directory
  - Contains one row per team with: `team name`, `number of players`, `total skill score`, `sponsor_id` (if any)

### Constraints

- Parse players first and build full player pool
- Parse coaches and create head/assistant pools
- Form teams from:
  - Reciprocated pairings (both coaches list each other in `Coach Pair`)
  - Unpaired head coaches, randomly matched with unpaired assistant coaches
    - Prioritize pairing coaches without an associated player with those who do have one
- Each team includes:
  - One required head coach
  - One optional assistant coach
  - One or more players
  - At most one sponsored player
  - Cumulative skill score of all players on the roster
  - Team name format:
    - `<Head Last Name>` (if solo)
    - `<Head Last Name>/<Assistant Last Name>` (if both present)
- Greedy distribution of remaining players:
  - Prioritize teams with lowest skill score
  - Break ties using fewest players, then randomly
  - Skip teams that already have a sponsor when assigning sponsored players
  - Enforce minimum team size before expanding
  - After minimums are met, no team may exceed the smallest team by more than one player

---

## 🧩 Data Models

### `Player`

- `player_id: str`
- `name: str` (full name)
- `dob: str` (MM/DD/YYYY)
- `age: float` (computed from DOB, 1 decimal precision, half-up rounding)
- `experience: int`
- `uniform_size: str`
- `evaluation_score: str` (raw format, possibly numeric)
- `sponsor_id: Optional[str]`

### `Coach`

- `coach_id: str`
- `full_name: str`
- `role: str` ("Head Coach" or "Assistant Coach")
- `associated_player_id: Optional[str]`
- `pair_id: Optional[str]` (referenced `VolunteerID` of intended pair)
- `volunteer_type_id: Optional[str]` (used for output formatting)

### `Team`

- `team_id: str`
- `name: str` (e.g. "Smith/Jones" or "Smith")
- `head_coach: Coach`
- `assistant_coach: Optional[Coach]`
- `players: List[Player]`
- `sponsor_id: Optional[str]`
- `total_score: float`

---

## 📦 Project Structure

```
teambuilder/
├── __main__.py          # Entry point for CLI and PyInstaller
├── cli.py               # Command-line argument parsing
├── models.py            # Data classes: Player, Coach, Team
├── load_data.py         # CSV parsing logic
├── scoring.py           # Skill normalization and scoring logic
├── team_builder.py      # Team seeding and balancing logic
├── output.py            # Final CSV export logic
└── requirements.txt     # (can be empty or list PyInstaller if needed)
```

---

## 🧊 GitHub Actions Build

Located at `.github/workflows/build.yml`:

- Builds both Windows and macOS executables
- Uses PyInstaller to generate:
  - `team_builder.exe` for Windows
  - `team_builder` for macOS
- Artifacts are uploaded for download via GitHub UI

---

## 📘 Module-Level Docstrings

### `__main__.py`

```python
"""
Entrypoint for running team builder from CLI or via PyInstaller.
Delegates to CLI handler.
"""
```

### `cli.py`

```python
"""
Parses command-line arguments and launches team building process.
"""
```

### `models.py`

```python
"""
Contains data models: Player, Coach, and Team.
Encapsulates core data used throughout the build process.
"""
```

### `load_data.py`

```python
"""
Parses players and coaches from CSV files.
Maps header names to expected fields and builds coach pools.
Creates teams based on reciprocated and fallback pairings.
"""
```

### `scoring.py`

```python
"""
Normalizes skill-related features and computes a weighted skill score.
Handles missing data and dynamic min/max normalization per division.
"""
```

### `team_builder.py`

```python
"""
Seeds teams using coach data and assigns players using greedy score balancing.
Tracks total team scores and uses defined tiebreak rules.
Ensures no team has more than one sponsored player.
Enforces balanced team sizes such that no team exceeds another by more than one player after the minimum team size is met.
"""
```

### `output.py`

```python
"""
Exports final team assignments to CSV in the current working directory.
Follows the format of TeamImportSampleFile.csv.
Outputs rows for both players and coaches, tracking VolunteerTypeID for coaches only.
Includes a summary of team compositions and prints standard deviation of total skill scores.
"""
```

