
import streamlit as st
import pandas as pd
import numpy as np
import random

# Function to simulate the draft lottery
def simulate_lottery(teams, ticket_weights, num_simulations=10):
    results = []
    for _ in range(num_simulations):
        hat = []
        for team, weight in zip(teams, ticket_weights):
            hat.extend([team] * weight)
        random.shuffle(hat)
        draft_order = []
        for _ in range(len(teams)):
            pick = random.choice(hat)
            draft_order.append(pick)
            hat = [ticket for ticket in hat if ticket != pick]
        results.append(draft_order)
    return results

# Streamlit app


st.set_page_config(layout="wide")  # Set the layout to wide mode

st.title("Dynasty Football League Lottery Draft Simulator")

st.sidebar.header("Upload CSV")
df = pd.read_csv('Dynasty2024.csv')

if df is not None:

    df = df.sort_values(by='MaxPF', ascending=True).reset_index(drop=True)
    
    # Generate default draft positions based on MaxPF
    df['Default Draft Position'] = df.index + 1
    
    st.write('### Standings and Max Points For (Sorted by Worst to Best)')
    
    teams = df['Team'].tolist()
    st.write("### Enter the number of tickets for each team")
    ticket_weights = []
    for team in teams:
        weight = st.sidebar.number_input(f"{team}", min_value=1, max_value=100, value=1)
        ticket_weights.append(weight)
    
    # Calculate probabilities and odds
    total_tickets = sum(ticket_weights)
    probabilities = [weight / total_tickets * 100 for weight in ticket_weights]
    odds = [f"{round(prob / (100 - prob), 2)}:1" if prob != 100 else "1:0" for prob in probabilities]

    ticket_info_df = pd.DataFrame({
        'Team': teams,
        'Tickets': ticket_weights,
        'Probability (%)': [f"{prob:.2f}%" for prob in probabilities],
        'Odds': odds
    })
    
    # Display original standings and ticket info side by side
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Sorted Standings")
        st.table(df[['Team', 'MaxPF', 'Default Draft Position']].style.hide(axis="index"))
    with col2:
        st.write("### Team Tickets and Lottery Odds")
        st.table(ticket_info_df.style.hide(axis="index"))

    if st.sidebar.button("Simulate Lottery"):
        num_simulations = st.sidebar.number_input("Number of simulations", min_value=1, value=10)
        results = simulate_lottery(teams, ticket_weights, num_simulations)
        
        st.write("### Simulated Lottery Results")
        
        # Create and display dataframes side by side for each simulation
        result_dfs = []
        for i, result in enumerate(results):
            sim_df = pd.DataFrame({
                'Pick': list(range(1, len(result) + 1)),
                'Team': result
            })
            result_dfs.append(sim_df)

        chunked_dfs = [result_dfs[i:i+5] for i in range(0, len(result_dfs), 5)]  # Chunk the dataframes to fit into rows
        
        for chunk in chunked_dfs:
            columns = st.columns(len(chunk))
            for col, result_df in zip(columns, chunk):
                with col:
                    st.table(result_df.style.hide(axis="index"))
