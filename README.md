# Dynasty Lottery Simulator
## Live draw tool for a dynasty fantasy football rookie draft

This is a Streamlit app I wrote to run the annual rookie draft lottery, live, for a dynasty fantasy football league that I am the commissioner for.

For the uninitiated, in dynasty football you keep your roster year to year, so each offseason the only draft is a rookie draft for the newly drafted NFL players. I wanted a lottery system that achieved the following:

1. More frequently than not, give the worst performing teams the best odds at the top picks
2. Reward the winner of the consolation bracket (the teams that missed the playoffs)
3. Add some element of randomness for fun

This started life as an odds simulator with sliders. It has since turned into an actual draw tool that we run on draft night, complete with an NBA style ping-pong ball draw, a slot machine name reveal, and way too many sound effects.

## How it works

1. **Standings load automatically.** The app reads the newest `Standings/Dynasty{YEAR}.csv` and pre-fills the sidebar. Ranks 1-6 are the playoff teams, ranks 7-12 are the six lottery (non-playoff) teams. You can edit any name or number by hand before starting.
2. **Odds are fixed, worst team gets the most balls.** There are 200 balls total, spread across the six lottery teams using a fixed NBA style probability table. The team with the lowest MaxPF (max possible points, our tiebreaker for "worst") gets the biggest share.
3. **The consolation bracket winner gets a bonus.** Pick them in the sidebar and they get +1 ball, taken from whichever team currently has the most.
4. **You draw a ball live.** Enter a ball number from 1 to 200 and the app reveals which team owns it. That team takes the pick. Their remaining balls are then redistributed proportionally to everyone left, and you draw again for the next pick. This repeats for all six lottery picks, then the playoff teams fill picks 7-12 in reverse standings order (worst playoff team picks 7th).
5. **It is loud and jazzy on purpose.** Each pick gets a drum roll, air horn, crowd cheer, confetti, and a slot machine name reveal, and the final draft order sets off a fireworks finale. That is the "randomness for fun" goal, delivered.

## Running it

```bash
pip install streamlit pandas numpy
streamlit run streamlit.py
```

Drop your standings in `Standings/` as `Dynasty{YEAR}.csv` with `Team`, `MaxPF`, and a playoff rank column. The newest year is loaded automatically.

Only a handful of my friends ever even opened the original simulator (being commissioner is a thankless job), but running the live draw on draft night has turned out to be a lot more fun.
