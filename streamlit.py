import streamlit as st
import pandas as pd
import numpy as np

# Function to load CSV file
@st.cache_data
def load_data(file_path='Dynasty2024.csv'):
    data = pd.read_csv(file_path)
    return data

# Function to simulate lottery
def simulate_lottery(data, odds, num_simulations=10):
    lottery_teams = data[data['Playoff_Rank'] > (12 - len(odds))].sort_values('MaxPF')
    num_lottery_teams = len(lottery_teams)
    
    results = []
    for _ in range(num_simulations):
        lottery_order = np.random.choice(range(num_lottery_teams), size=num_lottery_teams, replace=False, p=odds)
        draft_order = [lottery_teams.index[i] for i in lottery_order]
        draft_order += list(data[data['Playoff_Rank'] <= (12 - len(odds))].sort_values('Playoff_Rank', ascending=False).index)
        results.append(draft_order)
    
    return results

# Function to calculate exponential odds
def calculate_exp_odds(exp_base, num_teams):
    odds = [exp_base ** (num_teams - i) for i in range(num_teams)]
    return [o / sum(odds) for o in odds]

# Streamlit app
st.title('Dynasty Fantasy Football Draft Lottery Simulator')

# Load data
data = load_data()

# Display input data
st.subheader("Input Data")
st.dataframe(data)

# Select number of lottery teams
num_lottery_teams = st.radio("Number of teams in lottery", (6, 8))

# Get lottery teams sorted by MaxPF
lottery_teams = data[data['Playoff_Rank'] > (12 - num_lottery_teams)].sort_values('MaxPF')

# Adjust lottery odds
st.subheader("Adjust Lottery Odds")

# Add slider for exp_base
exp_base = st.slider("Adjust initial odds distribution (higher value = steeper curve)", 1.1, 2.0, 1.5, 0.1)

# Calculate initial exponential odds
initial_odds = calculate_exp_odds(exp_base, num_lottery_teams)

st.write(f"Adjust the odds for each non-playoff team. Team 1 has the lowest MaxPF, Team {num_lottery_teams} has the highest.")

odds = []
for i in range(num_lottery_teams):
    odds.append(st.slider(f"Team {i+1} (Relative MaxPF Rank: {i+1})", 0.0, 1.0, initial_odds[i], 0.01))

# Consolation bracket winner boost
include_boost = st.radio("Include consolation bracket winner boost?", ('Yes', 'No'))
boost_amount = st.slider("Consolation winner odds boost", 0.0, 0.2, 0.05, 0.01)

# Apply consolation bracket winner boost if selected
if include_boost == 'Yes':
    consolation_winner_index = lottery_teams[lottery_teams['Playoff_Rank'] == 7].index[0]
    consolation_winner_position = lottery_teams.index.get_loc(consolation_winner_index)
    odds[consolation_winner_position] += boost_amount

# Normalize odds
odds = [o / sum(odds) for o in odds]

# Create two columns for normalized odds and odds distribution
col1, col2 = st.columns(2)

# Display normalized odds in the first column
with col1:
    st.subheader("Normalized Odds")
    for i, odd in enumerate(odds):
        team_name = lottery_teams.iloc[i]['Team']
        st.write(f"Team {i+1} ({team_name}): {odd:.2%}")
        if include_boost == 'Yes' and i == consolation_winner_position:
            st.write("(Includes consolation winner boost)")

# Display odds distribution using Streamlit's native chart in the second column
with col2:
    st.subheader("Odds Distribution")
    chart_data = pd.DataFrame({
        'Team': [f"Team {i+1}" for i in range(num_lottery_teams)],
        'Odds': odds
    })
    st.bar_chart(chart_data.set_index('Team'))

# Simulate lottery
if st.button("Run Simulation"):
    simulations = simulate_lottery(data, odds)
    
    st.subheader("Simulation Results")
    
    # Create two rows of five columns each
    row1 = st.columns(5)
    row2 = st.columns(5)
    
    for i, result in enumerate(simulations, 1):
        # Determine which row and column to use
        col = row1[i-1] if i <= 5 else row2[i-6]
        
        with col:
            st.write(f"Simulation {i}:")
            for pick, team_index in enumerate(result, 1):
                st.write(f"Pick {pick}: {data.loc[team_index, 'Team']} (MaxPF: {data.loc[team_index, 'MaxPF']})")
            st.write("---")



