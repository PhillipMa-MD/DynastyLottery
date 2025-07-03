import streamlit as st
import pandas as pd
import numpy as np
import random

# --- Configuration & Initial Setup ---
st.set_page_config(layout="wide", page_title="Draft Lottery Simulator")
st.title("Draft Lottery Simulator")

TOTAL_BALLS = 200
LOTTERY_TEAMS_COUNT = 6
PLAYOFF_TEAMS_COUNT = 6
INITIAL_PROBS = [71.98, 16.17, 8.00, 2.67, 0.89, 0.30]

# Initialize session states
if 'app_started' not in st.session_state:
    st.session_state.app_started = False
    st.session_state.lottery_teams = [{"name": "", "max_pf": 1000.0} for _ in range(LOTTERY_TEAMS_COUNT)]
    st.session_state.playoff_teams = [{"name": "", "rank": i + 1} for i in range(PLAYOFF_TEAMS_COUNT)]
    # These will be DYNAMIC and change after each draw
    st.session_state.ball_distribution = {}
    st.session_state.ball_owner_map = {}
    st.session_state.draft_order = []
    st.session_state.consolation_applied = False
    st.session_state.error_message = ""
    st.session_state.last_winner = None

def calculate_initial_distribution():
    """Calculates the initial number of balls for each team based on MaxPF"""
    try:
        valid_teams = [team for team in st.session_state.lottery_teams if team['name'].strip()]
        if len(valid_teams) != LOTTERY_TEAMS_COUNT:
            st.session_state.error_message = f"Please enter names for all {LOTTERY_TEAMS_COUNT} lottery teams."
            return

        sorted_teams = sorted(valid_teams, key=lambda x: x['max_pf'])
        distribution = {}
        total_assigned_balls = 0
        
        for i, team in enumerate(sorted_teams):
            prob = INITIAL_PROBS[i] / 100
            num_balls = round(TOTAL_BALLS * prob)
            distribution[team['name']] = int(num_balls)
            total_assigned_balls += int(num_balls)
            
        if total_assigned_balls != TOTAL_BALLS:
            diff = TOTAL_BALLS - total_assigned_balls
            worst_team_name = sorted_teams[0]['name']
            distribution[worst_team_name] += diff
            
        st.session_state.ball_distribution = distribution
        st.session_state.app_started = True
        st.session_state.consolation_applied = False
        st.session_state.error_message = ""
        assign_ball_numbers(distribution)
    except Exception as e:
        st.session_state.error_message = f"An error occurred: {e}"

def assign_ball_numbers(distribution):
    """Re assigns ball numbers to teams based on the distribtuion as if the selecte team's balls were removed"""
    ball_numbers = list(range(1, TOTAL_BALLS + 1))
    random.shuffle(ball_numbers)
    
    owner_map = {}
    current_ball_index = 0
    for team, count in distribution.items():
        for _ in range(count):
            if current_ball_index < len(ball_numbers):
                ball_num = ball_numbers[current_ball_index]
                owner_map[ball_num] = team
                current_ball_index += 1
    st.session_state.ball_owner_map = owner_map

def apply_consolation_prize(consolation_winner):
    """Winner of the consolation prize gets 1 extra ball, taken from the team with the worst MaxPF."""
    if not st.session_state.ball_distribution:
        st.session_state.error_message = "Calculate initial distribution first."
        return

    valid_teams = [team for team in st.session_state.lottery_teams if team['name'].strip()]
    sorted_teams = sorted(valid_teams, key=lambda x: x['max_pf'])
    worst_team_name = sorted_teams[0]['name']

    if worst_team_name == consolation_winner:
        st.session_state.error_message = "The team with the worst MaxPF cannot win the consolation prize."
        return

    st.session_state.ball_distribution[worst_team_name] -= 1
    st.session_state.ball_distribution[consolation_winner] += 1
    st.session_state.consolation_applied = True
    st.session_state.error_message = ""
    # Re-assign ball numbers after the change
    assign_ball_numbers(st.session_state.ball_distribution)


def draw_lottery_ball(drawn_ball_number):
    """
    1. Draw a ball number.
    2. Find the winner from the current owner list
    3. Add the winner to the draft order
    4. Redistribute the balls of the winner to the remaining teams
    5. Update the ball owner map and distribution
    """
    if not 1 <= drawn_ball_number <= TOTAL_BALLS:
        st.error(f"Invalid ball number. Please enter a number between 1 and {TOTAL_BALLS}.")
        return

    # Find the winner from the CURRENT owner map
    winner = st.session_state.ball_owner_map.get(drawn_ball_number)
    if not winner:
        # This case should ideally not happen if all balls are assigned
        st.error(f"Ball #{drawn_ball_number} has no owner. This is an error.")
        return

    st.session_state.last_winner = winner
    
    # Add winner to the draft order (top-down picks)
    current_pick = len(st.session_state.draft_order) + 1
    st.session_state.draft_order.append({"pick": current_pick, "team": winner})

    # --- Start Redistribution ---
    if len(st.session_state.draft_order) < LOTTERY_TEAMS_COUNT:
        # 1. Get balls to redistribute
        balls_to_redistribute = [b for b, owner in st.session_state.ball_owner_map.items() if owner == winner]
        
        # 2. Remove winner from distribution and get remaining teams
        del st.session_state.ball_distribution[winner]
        remaining_teams = st.session_state.ball_distribution
        
        # 3. Calculate proportions of the remaining teams
        total_remaining_balls = sum(remaining_teams.values())
        if total_remaining_balls > 0:
            proportions = {team: count / total_remaining_balls for team, count in remaining_teams.items()}
            
            # 4. Determine how many extra balls each remaining team gets
            extra_balls_assignment = {team: 0 for team in remaining_teams}
            balls_assigned = 0
            for team, prop in proportions.items():
                num_extra = round(len(balls_to_redistribute) * prop)
                extra_balls_assignment[team] = num_extra
                balls_assigned += num_extra

            # 5. Adjust for rounding errors
            diff = len(balls_to_redistribute) - balls_assigned
            if diff != 0:
                # Give remainder/take deficit from the team with the highest proportion
                sorted_by_prop = sorted(proportions.items(), key=lambda item: item[1], reverse=True)
                for i in range(abs(diff)):
                    team_to_adjust = sorted_by_prop[i % len(sorted_by_prop)][0]
                    extra_balls_assignment[team_to_adjust] += np.sign(diff)

            # 6. Update the main ball distribution and re-assign the actual ball numbers
            ball_pool = iter(balls_to_redistribute)
            for team, num_extra in extra_balls_assignment.items():
                st.session_state.ball_distribution[team] += num_extra
                for _ in range(num_extra):
                    try:
                        ball_to_reassign = next(ball_pool)
                        st.session_state.ball_owner_map[ball_to_reassign] = team
                    except StopIteration:
                        break # Should not happen if counts are correct

def reset_app():
    """Resets the entire application state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Streamlit things
with st.sidebar:
    st.header("Team Setup")
    if st.button("Reset Full Application", type="primary"): reset_app()
    with st.expander("**Lottery Teams**", expanded=True):
        for i in range(LOTTERY_TEAMS_COUNT):
            cols = st.columns([2, 1])
            st.session_state.lottery_teams[i]['name'] = cols[0].text_input(f"Team {i+1} Name", st.session_state.lottery_teams[i].get('name', ''), key=f"lt_name_{i}")
            st.session_state.lottery_teams[i]['max_pf'] = cols[1].number_input(f"Team {i+1} MaxPF", value=st.session_state.lottery_teams[i].get('max_pf', 1000.0), key=f"lt_maxpf_{i}", format="%.2f", step=0.01)
    with st.expander("**Playoff Teams**"):
        for i in range(PLAYOFF_TEAMS_COUNT):
            cols = st.columns([2, 1])
            st.session_state.playoff_teams[i]['name'] = cols[0].text_input(f"P. Team {i+1}", st.session_state.playoff_teams[i].get('name', ''), key=f"pt_name_{i}")
            st.session_state.playoff_teams[i]['rank'] = cols[1].number_input(f"P. Rank {i+1}", min_value=1, max_value=PLAYOFF_TEAMS_COUNT, value=st.session_state.playoff_teams[i].get('rank', i + 1), key=f"pt_rank_{i}")
    st.button("1. Calculate Initial Ball Distribution", on_click=calculate_initial_distribution)
    if st.session_state.get('error_message'): st.error(st.session_state.error_message)

if not st.session_state.get('app_started'):
    st.info("⬅️ Please set up the teams in the sidebar and click 'Calculate' to begin.")
else:
    # Consolation Winner
    if not st.session_state.consolation_applied and len(st.session_state.draft_order) == 0:
        st.subheader("Consolation Prize (Optional)")
        lottery_team_names = [team['name'] for team in st.session_state.lottery_teams if team['name']]
        consolation_choice = st.selectbox("Select a team to receive 1 extra ball:", options=lottery_team_names, index=None)
        if consolation_choice and st.button("Apply Consolation Prize"):
            apply_consolation_prize(consolation_choice)
            st.rerun()

    # Lottery Draw Steps
    if len(st.session_state.draft_order) < LOTTERY_TEAMS_COUNT:
        next_pick = len(st.session_state.draft_order) + 1
        st.header(f"Step 2: Drawing for Pick #{next_pick}")

        if st.session_state.last_winner:
            st.success(f"**{st.session_state.last_winner}** has won Pick #{next_pick-1}! Their balls have been redistributed below.")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Draw a Ball")
            drawn_ball = st.number_input("Enter Drawn Ball Number", min_value=1, max_value=TOTAL_BALLS, step=1, key="drawn_ball_input")
            if st.button("Submit Drawn Ball"):
                draw_lottery_ball(drawn_ball)
                st.rerun()

            st.subheader("Draft Order (So Far)")
            if st.session_state.draft_order:
                draft_df = pd.DataFrame(st.session_state.draft_order).sort_values("pick")
                st.dataframe(draft_df.set_index("pick"), use_container_width=True)

        with col2:
            st.subheader("Current State for Next Pick")
            if st.session_state.ball_distribution:
                current_total_balls = sum(st.session_state.ball_distribution.values())
                data = []
                for team, count in st.session_state.ball_distribution.items():
                    prob = (count / current_total_balls) * 100 if current_total_balls > 0 else 0
                    data.append({"Team": team, "Ball Count": count, f"Probability for Pick #{next_pick}": f"{prob:.2f}%"})
                
                state_df = pd.DataFrame(data)
                st.dataframe(state_df, use_container_width=True, hide_index=True)

                with st.expander("Click to see current ball number assignments"):
                    team_balls = {team: [] for team in st.session_state.ball_distribution}
                    for ball, team in st.session_state.ball_owner_map.items():
                        if team in team_balls: team_balls[team].append(ball)
                    for team, balls in sorted(team_balls.items()):
                        balls.sort()
                        st.markdown(f"**{team} ({len(balls)} balls):**")
                        st.text(', '.join(map(str, balls)))

    # Display final draft order
    else:
        st.header("Final Draft Order")
        # Add remaining teams to draft order. Last team gets last available pick.
        if len(st.session_state.draft_order) == LOTTERY_TEAMS_COUNT - 1:
            last_team = list(st.session_state.ball_distribution.keys())[0]
            st.session_state.draft_order.append({"pick": LOTTERY_TEAMS_COUNT, "team": last_team})

        final_order = st.session_state.draft_order.copy()
        valid_playoff_teams = [pt for pt in st.session_state.playoff_teams if pt['name'].strip()]
        sorted_playoff_teams = sorted(valid_playoff_teams, key=lambda x: x['rank'], reverse=True)
        for i, team_info in enumerate(sorted_playoff_teams):
            final_order.append({"pick": LOTTERY_TEAMS_COUNT + i + 1, "team": team_info['name']})
        
        final_df = pd.DataFrame(final_order).sort_values("pick", ascending=True)
        st.table(final_df.set_index("pick"))
        st.balloons()

