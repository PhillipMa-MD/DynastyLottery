# CLAUDE.md

Streamlit app for running a dynasty fantasy football rookie-draft lottery live, on draft night.

## Entry point

`streamlit.py` (repo root). Run with:

```bash
streamlit run streamlit.py
```

Dependencies: `streamlit`, `pandas`, `numpy`. There is no `requirements.txt` currently.

## Data

Standings live in `Standings/Dynasty{YEAR}.csv`. The newest year is auto-loaded (`find_latest_standings()` matches `Dynasty(\d{4}).csv` and picks the max year). Expected columns:

- `Team` - team name
- `MaxPF` - max possible points, used as the "worst team" ordering (lower is worse)
- A rank column - `load_standings()` flexibly matches `Playoff Standings`, `Playoff_Rank`, `rank`, or `standings`, so both header variants in the repo load.

Ranks 1-6 are playoff teams; ranks 7-12 are the six lottery (non-playoff) teams.

## Core mechanics

- Constants: `TOTAL_BALLS = 200`, `LOTTERY_TEAMS_COUNT = 6`, `PLAYOFF_TEAMS_COUNT = 6`, and a fixed NBA-style probability table `INITIAL_PROBS = [71.98, 16.17, 8.00, 2.67, 0.89, 0.30]`.
- `calculate_initial_distribution()` assigns the 200 balls across lottery teams sorted by ascending `MaxPF` (worst team gets the most). The consolation-bracket winner (sidebar radio) gets +1 ball, taken from the team with the most.
- `draw_lottery_ball()` takes a ball number 1-200, looks up the owning team, awards them the pick, then proportionally redistributes that team's balls to the remaining teams for the next pick. Six picks total; the last remaining team auto-fills pick 6.
- Final order = lottery picks 1-6, then playoff teams as picks 7-12 in reverse standings order (worst playoff team picks 7th).
- Odds display uses `american_odds()` to show American-moneyline lines on the chip cards.

## Presentation

- Dark gold-accent theme in `.streamlit/config.toml`.
- Celebrations (drum roll / air horn / crowd cheer audio, confetti, slot-machine name reveal, fireworks finale) are client-side JS injected via `components.html` in `celebrate_winner()` and `fire_fireworks_barrage()`. Audio samples come from the Google Actions sound library.

## Legacy note

`simulator/streamlit.py` is the original odds-experimentation simulator (odds sliders, an exponential-curve generator, a 6/8-team radio, and 10 Monte Carlo simulation runs). It is NOT the live app and should not be treated as the entry point. The live tool is `streamlit.py` at the repo root.
