# AYSTeamBuilder
A helper for building balanced youth soccer teams.

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
2. Each team is initialized with a coach pair (head and assistant).
3. Each coach contributes either their child or a randomly assigned player.
4. Remaining players are sorted by skill and distributed to the lowest-score team that:
   - Has an available slot
   - Does not already have a sponsored player (if the player is sponsored)
   - Does not exceed the size of the smallest team by more than 1
5. Final results are exported to CSV with a team summary and skill statistics.

---

## 📥 Download

You can download the latest executable for your platform from the GitHub Actions **Artifacts** section:

1. Go to the GitHub repo: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Click the **Actions** tab
3. Select the latest **Build Executables** workflow run (triggered by a push to `main`)
4. Download the appropriate artifact:
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

**players.csv** must contain columns:

- `player_id`, `dob`, `experience`, `uniform_size`, `coach_eval`, `sponsor_id`

**coaches.csv** must contain columns:

- `coach_id`, `coach_name`, `coach_role`, `associated_player_id`, `assistant_coach_id`

Header names are hardcoded for now but can be updated in future versions.

---

## 📤 Output

- `team_assignments.csv`: player-to-team assignments with optional skill and sponsor info
- Console output includes:
  - Standard deviation of team scores
  - Summary of each team: name, player count, total score, sponsor (if present)

---

## 🧊 Platform Notes

- macOS and Windows builds are generated via GitHub Actions
- No Python installation required for executables
- Run from Terminal (macOS) or Command Prompt/PowerShell (Windows)

---

For developers: see `spec.md` and module docstrings for implementation details.

