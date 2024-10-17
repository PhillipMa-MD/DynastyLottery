import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Function to load CSV file
@st.cache_data
def load_data(file_path='Dynasty2024.csv'):
    data = pd.read_csv(file_path)
    return data

# Function to simulate lottery
def simulate_lottery(data, odds, num_simulations=10):
    lottery_teams = data[data['Playoff_Rank'] > 6].sort_values('MaxPF')
    num_lottery_teams = len(lottery_teams)
    
    results = []
    for _ in range(num_simulations):
        lottery_order = np.random.choice(range(num_lottery_teams), size=num_lottery_teams, replace=False, p=odds)
        draft_order = [lottery_teams.index[i] for i in lottery_order]
        draft_order += list(data[data['Playoff_Rank'] <= 6].sort_values('Playoff_Rank', ascending=False).index)
        results.append(draft_order)
    
    return results

# Streamlit app
st.title('Dynasty Fantasy Football Draft Lottery Simulator')

# Load data
data = load_data()

# Display input data
st.subheader("Input Data")
st.dataframe(data)

# Get non-playoff teams sorted by MaxPF
lottery_teams = data[data['Playoff_Rank'] > 6].sort_values('MaxPF')
num_lottery_teams = len(lottery_teams)

# Adjust lottery odds
st.subheader("Adjust Lottery Odds")
st.write("Adjust the odds for each non-playoff team. Team 1 has the lowest MaxPF, Team 6 has the highest.")

odds = []
for i in range(num_lottery_teams):
    default_odds = (num_lottery_teams - i) / sum(range(1, num_lottery_teams + 1))
    odds.append(st.slider(f"Team {i+1} (Relative MaxPF Rank: {i+1})", 0.0, 1.0, default_odds, 0.01))

# Normalize odds
odds = [o / sum(odds) for o in odds]

# Display normalized odds
st.subheader("Normalized Odds")
for i, odd in enumerate(odds):
    st.write(f"Team {i+1}: {odd:.2%}")

# Simulate lottery
if st.button("Run Simulation"):
    simulations = simulate_lottery(data, odds)
    
    st.subheader("Simulation Results")
    for i, result in enumerate(simulations, 1):
        st.write(f"Simulation {i}:")
        for pick, team_index in enumerate(result, 1):
            st.write(f"Pick {pick}: {data.loc[team_index, 'Team']} (MaxPF: {data.loc[team_index, 'MaxPF']})")
        st.write("---")

# Display odds distribution
st.subheader("Odds Distribution")
fig, ax = plt.subplots()
ax.bar(range(1, num_lottery_teams + 1), odds)
ax.set_xlabel("Team (Relative MaxPF Rank)")
ax.set_ylabel("Probability")
ax.set_title("Lottery Odds Distribution")
st.pyplot(fig)

