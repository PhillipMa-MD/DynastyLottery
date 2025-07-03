import streamlit as st
import pandas as pd
import numpy as np
import random

st.title("Draft Lottery Ball Distribution")

# Set up the sidebar for inputs
st.sidebar.header("Team Information")

# Create containers for lottery teams and playoff teams
lottery_container = st.sidebar.expander("Lottery Teams", expanded=True)
playoff_container = st.sidebar.expander("Playoff Teams", expanded=True)

# Initialize lottery teams
lottery_teams = []
for i in range(6):
    with lottery_container:
        col1, col2 = st.columns(2)
        team_name = col1.text_input(f"Lottery Team {i+1} Name", key=f"lottery_team_{i}")
        max_pf = col2.number_input(f"MaxPF", key=f"max_pf_{i}", value=0.0, step=0.1)
        
        if team_name:  # Only add if team name is provided
            lottery_teams.append({"Team": team_name, "MaxPF": max_pf, "Type": "Lottery"})

# Initialize playoff teams
playoff_teams = []
for i in range(6):
    with playoff_container:
        col1, col2 = st.columns(2)
        team_name = col1.text_input(f"Playoff Team {i+1} Name", key=f"playoff_team_{i}")
        rank = col2.number_input(f"Playoff Rank", key=f"rank_{i}", min_value=1, max_value=6, step=1)
        
        if team_name:  # Only add if team name is provided
            playoff_teams.append({"Team": team_name, "Rank": rank, "Type": "Playoff"})

# Combine all teams
all_teams = lottery_teams + playoff_teams

# Consolation prize selection
st.sidebar.header("Consolation Prize")
consolation_teams = [team["Team"] for team in all_teams if team["Team"]]
if consolation_teams:
    consolation_team = st.sidebar.selectbox("Select team to receive consolation ball:", 
                                          options=consolation_teams)
else:
    consolation_team = None

# Calculate ball distribution when button is pressed
if st.sidebar.button("Calculate Ball Distribution"):
    if len(lottery_teams) == 6:
        # Sort lottery teams by MaxPF (ascending)
        lottery_teams_sorted = sorted(lottery_teams, key=lambda x: x["MaxPF"])
        
        # Probability distribution
        probabilities = [0.7198, 0.1617, 0.08, 0.0267, 0.0089, 0.003]
        
        # Calculate initial ball counts (out of 200)
        total_balls = 200
        ball_counts = [round(prob * total_balls) for prob in probabilities]
        
        # Adjust if total doesn't equal 200
        while sum(ball_counts) != total_balls:
            if sum(ball_counts) < total_balls:
                # Add to the team with the lowest MaxPF
                ball_counts[0] += 1
            else:
                # Remove from the team with the lowest MaxPF
                ball_counts[0] -= 1
        
        # Apply consolation prize if selected
        if consolation_team and consolation_team != lottery_teams_sorted[0]["Team"]:
            # Find the index of the consolation team in the sorted list
            consolation_idx = next((i for i, team in enumerate(lottery_teams_sorted) 
                                  if team["Team"] == consolation_team), None)
            
            if consolation_idx is not None:
                ball_counts[0] -= 1  # Take from worst team
                ball_counts[consolation_idx] += 1  # Give to consolation team
        
        # Assign ball counts to teams
        for i, team in enumerate(lottery_teams_sorted):
            team["Balls"] = ball_counts[i]
            
        # Assign ball numbers to teams
        all_balls = list(range(1, total_balls + 1))
        random.shuffle(all_balls)
        
        for team in lottery_teams_sorted:
            team["Ball Numbers"] = all_balls[:team["Balls"]]
            all_balls = all_balls[team["Balls"]:]
        
        # Display lottery teams with ball distribution
        st.header("Lottery Ball Distribution")
        
        lottery_df = pd.DataFrame([
            {
                "Team": team["Team"],
                "MaxPF": team["MaxPF"],
                "Balls": team["Balls"],
                "Percentage": f"{(team['Balls']/total_balls)*100:.2f}%"
            } for team in lottery_teams_sorted
        ])
        
        st.dataframe(lottery_df)
        
        # Display ball numbers for each team
        st.header("Ball Number Assignments")
        
        for team in lottery_teams_sorted:
            st.subheader(f"{team['Team']}")
            # Display ball numbers in a grid format
            ball_numbers = team["Ball Numbers"]
            ball_numbers.sort()  # Sort ball numbers for better readability
            
            # Create rows of 10 balls each
            rows = [ball_numbers[i:i+10] for i in range(0, len(ball_numbers), 10)]
            
            # Display as a table
            ball_table = ""
            for row in rows:
                ball_table += "| " + " | ".join([str(ball) for ball in row]) + " |\n"
                
            st.markdown(ball_table)
        
        # Display playoff teams in reverse order
        st.header("Draft Order for Playoff Teams")
        
        # Sort playoff teams by rank (descending)
        playoff_teams_sorted = sorted(playoff_teams, key=lambda x: x["Rank"])
        
        playoff_df = pd.DataFrame([
            {
                "Pick Order": i + 7,  # Start after the 6 lottery teams
                "Team": team["Team"],
                "Playoff Rank": team["Rank"]
            } for i, team in enumerate(playoff_teams_sorted)
        ])
        
        st.dataframe(playoff_df)
        
    else:
        st.error("Please enter all 6 lottery teams before calculating.")

# Add some instructions
st.sidebar.markdown("""
## Instructions
1. Enter all 6 lottery teams with their MaxPF values
2. Enter all 6 playoff teams with their rankings
3. Select a team for the consolation prize (optional)
4. Click "Calculate Ball Distribution"
""")
