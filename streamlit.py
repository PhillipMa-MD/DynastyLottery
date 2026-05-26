import streamlit as st
import pandas as pd
import numpy as np
import random
import re
import glob
import os
import json
import streamlit.components.v1 as components

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(layout="wide", page_title="Dynasty Draft Lottery", page_icon="🏈")

# ── Constants ─────────────────────────────────────────────────────────────────
TOTAL_BALLS = 200
LOTTERY_TEAMS_COUNT = 6
PLAYOFF_TEAMS_COUNT = 6
INITIAL_PROBS = [71.98, 16.17, 8.00, 2.67, 0.89, 0.30]
STANDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Standings")
CHIP_COLORS = ["#FFB627", "#4ECDC4", "#45B7D1", "#96CEB4", "#F7B2BD", "#C5A8FF"]

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0d1426 0%, #1a2545 55%, #0d1426 100%);
    border: 1px solid rgba(255,182,39,0.45);
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 50px rgba(255,182,39,0.1), inset 0 0 100px rgba(255,182,39,0.03);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -60%; left: -60%;
    width: 220%; height: 220%;
    background: radial-gradient(ellipse at center, rgba(255,182,39,0.07) 0%, transparent 60%);
    animation: bgshimmer 5s ease-in-out infinite alternate;
}
@keyframes bgshimmer {
    from { transform: translateX(-8%) translateY(-8%); }
    to   { transform: translateX(8%) translateY(8%); }
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    color: #FFB627;
    letter-spacing: 3px;
    text-transform: uppercase;
    text-shadow: 0 0 35px rgba(255,182,39,0.65);
    position: relative;
}
.hero-subtitle {
    font-size: 0.88rem;
    color: #7a8fa8;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 0.35rem;
    position: relative;
}
.hero-caption {
    font-size: 0.78rem;
    color: rgba(255,182,39,0.55);
    margin-top: 0.55rem;
    position: relative;
}

/* ── Winner banner ── */
.winner-banner {
    background: linear-gradient(135deg, #192040, #222d50);
    border: 2px solid #FFB627;
    border-radius: 14px;
    padding: 1.75rem;
    text-align: center;
    animation: pickReveal 0.55s cubic-bezier(0.34,1.56,0.64,1);
    box-shadow: 0 0 70px rgba(255,182,39,0.28);
    margin-bottom: 1.25rem;
}
@keyframes pickReveal {
    from { opacity: 0; transform: scale(0.72) translateY(-18px); }
    to   { opacity: 1; transform: scale(1)    translateY(0); }
}
.winner-label {
    font-size: 0.72rem;
    color: #FFB627;
    letter-spacing: 5px;
    text-transform: uppercase;
    font-weight: 600;
}
.winner-name {
    font-size: 2.8rem;
    font-weight: 700;
    color: #F2F4FA;
    margin-top: 0.2rem;
    text-shadow: 0 2px 20px rgba(255,255,255,0.12);
    opacity: 0;
    animation: nameReveal 0.5s ease-out 1.2s forwards;
}
@keyframes nameReveal {
    from { opacity: 0; transform: scale(0.72) translateY(12px); }
    to   { opacity: 1; transform: scale(1)    translateY(0); }
}
.winner-pick {
    font-size: 0.88rem;
    color: rgba(255,182,39,0.65);
    margin-top: 0.2rem;
}

/* ── Card wrapper ── */
.card {
    background: #111928;
    border-radius: 12px;
    border-left: 3px solid #FFB627;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 28px rgba(0,0,0,0.38);
}

/* ── Pick header ── */
.pick-header {
    font-size: 1.55rem;
    font-weight: 700;
    color: #FFB627;
    letter-spacing: 1px;
    margin-bottom: 0.75rem;
}

/* ── Ball pool chips ── */
.ball-pool {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin: 0.6rem 0 1rem;
}
.team-chip {
    border-radius: 8px;
    padding: 0.5rem 0.7rem;
    min-width: 96px;
    flex: 1 1 96px;
    max-width: 180px;
}
.chip-team  { font-weight: 700; font-size: 0.8rem;  color: #0d1426; display: block; }
.chip-pct   { font-size: 1.05rem; font-weight: 700; color: #0d1426; display: block; }
.chip-balls { font-size: 0.7rem;  color: rgba(13,20,38,0.72); display: block; }

/* ── Final banner ── */
.final-banner {
    background: linear-gradient(135deg, #192040, #222d50);
    border: 2px solid #FFB627;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 60px rgba(255,182,39,0.25);
}
.final-banner-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FFB627;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* ── Footer ── */
.footer-note {
    text-align: center;
    color: rgba(122,143,168,0.45);
    font-size: 0.72rem;
    margin-top: 3rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255,255,255,0.05);
}

/* ── Slot-machine name reveal ── */
.ball-spin {
    font-family: 'Inter', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    color: #FFB627;
    letter-spacing: 0.05em;
    text-shadow: 0 0 24px rgba(255,182,39,0.55);
    margin: 0.4rem 0 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}
.ball-spin.locked {
    animation: ballLock 0.45s ease-out forwards;
}
@keyframes ballLock {
    0%   { transform: scale(1.0); color: #FFB627; }
    40%  { transform: scale(1.35); color: #FFFFFF; }
    100% { transform: scale(1.0); color: #FFB627; }
}

/* ── Streamlit component overrides ── */
section[data-testid="stSidebar"] {
    background: #0a1020 !important;
    border-right: 1px solid rgba(255,182,39,0.12) !important;
}

/* Metrics */
[data-testid="stMetricValue"]  { color: #FFB627 !important; font-size: 1.7rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"]  { color: #7a8fa8 !important; text-transform: uppercase; letter-spacing: 2px; font-size: 0.68rem !important; }
[data-testid="metric-container"],
[data-testid="stMetric"] {
    background: #111928 !important;
    border-radius: 10px !important;
    padding: 0.85rem 1rem !important;
    border: 1px solid rgba(255,182,39,0.14) !important;
}

/* Primary button */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #FFB627, #f5a000) !important;
    color: #0d1426 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    letter-spacing: 0.4px !important;
    box-shadow: 0 4px 16px rgba(255,182,39,0.3) !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 22px rgba(255,182,39,0.5) !important;
}

/* Secondary button */
div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stButton"] > button[data-testid="stBaseButton-secondary"] {
    border: 1px solid rgba(255,182,39,0.4) !important;
    color: #FFB627 !important;
    background: transparent !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Dataframe borders */
[data-testid="stDataFrameResizable"] {
    border: 1px solid rgba(255,182,39,0.14) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)


# ── Celebration effects (canvas-confetti CDN + real audio samples, all client-side) ──
def celebrate_winner(drawn_ball, candidates, winner_name):
    """Per-pick celebration: drum-roll sample (1.2s) → airhorn + cymbal + cheer + confetti + sparks.
    Slot machine cycles through candidate names during the roll, locks to winner_name at reveal.
    Streamlit serves on localhost so the iframe can access window.parent."""
    candidates_js = json.dumps(candidates if candidates else [winner_name])
    winner_js = json.dumps(winner_name)
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
        <script>
        (function() {{
            var CANDIDATES = {candidates_js};
            var WINNER = {winner_js};

            // ── Audio (real samples from Google Actions Sound Library) ─────────
            try {{
                var ROLL  = new Audio('https://actions.google.com/sounds/v1/cartoon/drum_roll.ogg');
                var HORN  = new Audio('https://actions.google.com/sounds/v1/transportation/air_horn_in_close_hall_series.ogg');
                var CRASH = new Audio('https://actions.google.com/sounds/v1/cartoon/crash_layer_cymbals.ogg');
                var CHEER = new Audio('https://actions.google.com/sounds/v1/crowds/team_cheer.ogg');
                ROLL.volume = 0.9; HORN.volume = 1.0; CRASH.volume = 0.8; CHEER.volume = 0.6;

                ROLL.play().catch(function() {{}});

                setTimeout(function() {{
                    try {{ ROLL.pause(); ROLL.currentTime = 0; }} catch(_) {{}}
                }}, 1180);
                setTimeout(function() {{
                    HORN.play().catch(function() {{}});
                    CRASH.play().catch(function() {{}});
                    CHEER.play().catch(function() {{}});
                    setTimeout(function() {{
                        try {{ HORN.pause();  HORN.currentTime  = 0; }} catch(_) {{}}
                        try {{ CHEER.pause(); CHEER.currentTime = 0; }} catch(_) {{}}
                    }}, 15000);
                }}, 1200);
            }} catch(audioErr) {{}}

            // ── Slot-machine name cycling (setInterval so names are readable) ──
            var span = window.parent.document.getElementById('lottery-ball-spin');
            var idx = 0;
            var spinTimer = null;
            if (span && CANDIDATES.length > 0) {{
                spinTimer = setInterval(function() {{
                    span.textContent = CANDIDATES[idx % CANDIDATES.length];
                    idx++;
                }}, 100);
            }}

            setTimeout(function() {{
                if (spinTimer) clearInterval(spinTimer);
                if (span) {{
                    span.textContent = WINNER;
                    span.classList.add('locked');
                }}
            }}, 1180);

            // ── Visuals at 1200ms (synced with airhorn) ────────────────────
            setTimeout(function() {{
                try {{
                    var confCanvas = window.parent.document.createElement('canvas');
                    confCanvas.style.cssText =
                        'position:fixed;top:0;left:0;width:100%;height:100%;'
                        + 'pointer-events:none;z-index:99999;';
                    window.parent.document.body.appendChild(confCanvas);
                    var burst = confetti.create(confCanvas, {{ resize: true, useWorker: true }});
                    burst({{
                        particleCount: 220,
                        spread: 110,
                        origin: {{ y: 0.22 }},
                        colors: ['#FFB627', '#F2F4FA', '#4ECDC4', '#45B7D1', '#f5a000'],
                        ticks: 320,
                    }});
                    setTimeout(function() {{ confCanvas.remove(); }}, 6000);

                    var sparksCanvas = window.parent.document.createElement('canvas');
                    sparksCanvas.style.cssText =
                        'position:fixed;top:0;left:0;width:100%;height:100%;'
                        + 'pointer-events:none;z-index:99998;';
                    window.parent.document.body.appendChild(sparksCanvas);
                    var sparkBurst = confetti.create(sparksCanvas, {{ resize: true, useWorker: false }});
                    var sparkEnd = Date.now() + 3000;
                    (function sparkFrame() {{
                        sparkBurst({{
                            particleCount: 5, angle: 75, spread: 22, startVelocity: 65,
                            origin: {{ x: 0, y: 1 }},
                            colors: ['#FFB627', '#FFE082', '#FFFFFF', '#f5a000'],
                            scalar: 0.65, gravity: 1.2, ticks: 220,
                        }});
                        sparkBurst({{
                            particleCount: 5, angle: 105, spread: 22, startVelocity: 65,
                            origin: {{ x: 1, y: 1 }},
                            colors: ['#FFB627', '#FFE082', '#FFFFFF', '#f5a000'],
                            scalar: 0.65, gravity: 1.2, ticks: 220,
                        }});
                        if (Date.now() < sparkEnd) {{
                            requestAnimationFrame(sparkFrame);
                        }} else {{
                            setTimeout(function() {{ sparksCanvas.remove(); }}, 2000);
                        }}
                    }})();
                }} catch(visErr) {{}}
            }}, 1200);
        }})();
        </script>
        """,
        height=0,
    )


def fire_fireworks_barrage():
    """8-second fireworks show for the final draft order reveal."""
    components.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
        <script>
        (function() {
            try {
                var fwCanvas = window.parent.document.createElement('canvas');
                fwCanvas.style.cssText =
                    'position:fixed;top:0;left:0;width:100%;height:100%;'
                    + 'pointer-events:none;z-index:99999;';
                window.parent.document.body.appendChild(fwCanvas);
                var fwBurst = confetti.create(fwCanvas, { resize: true, useWorker: true });

                function rnd(min, max) { return Math.random() * (max - min) + min; }

                var duration = 8000;
                var animEnd  = Date.now() + duration;
                var colors   = ['#FFB627','#F2F4FA','#4ECDC4','#FF6B6B','#C5A8FF','#f5a000'];

                var interval = setInterval(function() {
                    var timeLeft = animEnd - Date.now();
                    if (timeLeft <= 0) {
                        clearInterval(interval);
                        setTimeout(function() { fwCanvas.remove(); }, 2000);
                        return;
                    }
                    var pc = Math.max(10, Math.floor(55 * (timeLeft / duration)));
                    fwBurst({
                        particleCount: pc,
                        startVelocity: rnd(22, 38),
                        spread: 360, ticks: 80,
                        origin: { x: rnd(0.1, 0.3), y: rnd(-0.1, 0.15) },
                        colors: colors,
                    });
                    fwBurst({
                        particleCount: pc,
                        startVelocity: rnd(22, 38),
                        spread: 360, ticks: 80,
                        origin: { x: rnd(0.7, 0.9), y: rnd(-0.1, 0.15) },
                        colors: colors,
                    });
                }, 250);
            } catch(e) { /* ignore */ }
        })();
        </script>
        """,
        height=0,
    )


# ── CSV helpers ───────────────────────────────────────────────────────────────
def find_latest_standings(standings_dir=STANDINGS_DIR):
    pattern = re.compile(r"Dynasty(\d{4})\.csv$", re.IGNORECASE)
    candidates = []
    for path in glob.glob(os.path.join(standings_dir, "*.csv")):
        m = pattern.search(os.path.basename(path))
        if m:
            candidates.append((int(m.group(1)), path))
    if not candidates:
        return None, None
    return max(candidates, key=lambda x: x[0])


def load_standings(path):
    try:
        df = pd.read_csv(path)
        rank_col = next(
            (c for c in df.columns
             if c.strip().lower().replace("_", " ")
             in ("playoff rank", "playoff standings", "rank", "standings")),
            None,
        )
        if rank_col is None:
            return None
        df = df.rename(columns={rank_col: "Rank"})
        df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
        return df.dropna(subset=["Rank"]).sort_values("Rank")
    except Exception:
        return None


# ── Core lottery logic ────────────────────────────────────────────────────────
def calculate_initial_distribution():
    try:
        valid_teams = [t for t in st.session_state.lottery_teams if t['name'].strip()]
        if len(valid_teams) != LOTTERY_TEAMS_COUNT:
            st.session_state.error_message = f"Please enter names for all {LOTTERY_TEAMS_COUNT} lottery teams."
            return
        sorted_teams = sorted(valid_teams, key=lambda x: x['max_pf'])
        distribution = {}
        total_assigned = 0
        for i, team in enumerate(sorted_teams):
            num_balls = round(TOTAL_BALLS * INITIAL_PROBS[i] / 100)
            distribution[team['name']] = int(num_balls)
            total_assigned += int(num_balls)
        if total_assigned != TOTAL_BALLS:
            distribution[sorted_teams[0]['name']] += TOTAL_BALLS - total_assigned
        st.session_state.ball_distribution = distribution
        st.session_state.app_started = True
        st.session_state.consolation_applied = False
        st.session_state.error_message = ""
        assign_ball_numbers(distribution)
    except Exception as e:
        st.session_state.error_message = f"An error occurred: {e}"


def assign_ball_numbers(distribution):
    ball_numbers = list(range(1, TOTAL_BALLS + 1))
    random.shuffle(ball_numbers)
    owner_map = {}
    idx = 0
    for team, count in distribution.items():
        for _ in range(count):
            if idx < len(ball_numbers):
                owner_map[ball_numbers[idx]] = team
                idx += 1
    st.session_state.ball_owner_map = owner_map


def apply_consolation_prize(consolation_winner):
    if not st.session_state.ball_distribution:
        st.session_state.error_message = "Calculate initial distribution first."
        return
    valid_teams = [t for t in st.session_state.lottery_teams if t['name'].strip()]
    worst = sorted(valid_teams, key=lambda x: x['max_pf'])[0]['name']
    if worst == consolation_winner:
        st.session_state.error_message = "The team with the worst MaxPF cannot win the consolation prize."
        return
    st.session_state.ball_distribution[worst] -= 1
    st.session_state.ball_distribution[consolation_winner] += 1
    st.session_state.consolation_applied = True
    st.session_state.error_message = ""
    assign_ball_numbers(st.session_state.ball_distribution)


def draw_lottery_ball(drawn_ball_number):
    if not 1 <= drawn_ball_number <= TOTAL_BALLS:
        st.error(f"Invalid ball number. Enter a number between 1 and {TOTAL_BALLS}.")
        return
    winner = st.session_state.ball_owner_map.get(drawn_ball_number)
    if not winner:
        st.error(f"Ball #{drawn_ball_number} has no owner. This is an error.")
        return

    st.session_state.last_winner = winner
    st.session_state.last_drawn_ball = drawn_ball_number
    st.session_state.last_draw_candidates = list(st.session_state.ball_distribution.keys())
    current_pick = len(st.session_state.draft_order) + 1
    st.session_state.draft_order.append({"pick": current_pick, "team": winner})

    if len(st.session_state.draft_order) < LOTTERY_TEAMS_COUNT:
        balls_to_redistribute = [b for b, o in st.session_state.ball_owner_map.items() if o == winner]
        del st.session_state.ball_distribution[winner]
        remaining = st.session_state.ball_distribution
        total_remaining = sum(remaining.values())
        if total_remaining > 0:
            proportions = {t: c / total_remaining for t, c in remaining.items()}
            extra = {t: 0 for t in remaining}
            assigned = 0
            for t, p in proportions.items():
                n = round(len(balls_to_redistribute) * p)
                extra[t] = n
                assigned += n
            diff = len(balls_to_redistribute) - assigned
            if diff != 0:
                by_prop = sorted(proportions.items(), key=lambda x: x[1], reverse=True)
                for i in range(abs(diff)):
                    extra[by_prop[i % len(by_prop)][0]] += int(np.sign(diff))
            ball_pool = iter(balls_to_redistribute)
            for t, n in extra.items():
                st.session_state.ball_distribution[t] += n
                for _ in range(n):
                    try:
                        st.session_state.ball_owner_map[next(ball_pool)] = t
                    except StopIteration:
                        break


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# ── Session state init (only on first load) ───────────────────────────────────
if 'app_started' not in st.session_state:
    st.session_state.app_started = False
    st.session_state.lottery_teams = [{"name": "", "max_pf": 1000.0} for _ in range(LOTTERY_TEAMS_COUNT)]
    st.session_state.playoff_teams = [{"name": "", "rank": i + 1} for i in range(PLAYOFF_TEAMS_COUNT)]
    st.session_state.ball_distribution = {}
    st.session_state.ball_owner_map = {}
    st.session_state.draft_order = []
    st.session_state.consolation_applied = False
    st.session_state.error_message = ""
    st.session_state.last_winner = None
    st.session_state.last_drawn_ball = None
    st.session_state.last_draw_candidates = []
    st.session_state.last_celebrated = None
    st.session_state.final_celebrated = False
    st.session_state.standings_year = None

    year, path = find_latest_standings()
    if path:
        df = load_standings(path)
        if df is not None:
            lottery_rows = df[df["Rank"] > PLAYOFF_TEAMS_COUNT].sort_values("Rank")
            playoff_rows = df[df["Rank"] <= PLAYOFF_TEAMS_COUNT].sort_values("Rank")
            for i, (_, row) in enumerate(lottery_rows.iterrows()):
                if i < LOTTERY_TEAMS_COUNT:
                    st.session_state.lottery_teams[i] = {
                        "name": str(row["Team"]),
                        "max_pf": float(row["MaxPF"]),
                    }
            for i, (_, row) in enumerate(playoff_rows.iterrows()):
                if i < PLAYOFF_TEAMS_COUNT:
                    st.session_state.playoff_teams[i] = {
                        "name": str(row["Team"]),
                        "rank": int(row["Rank"]),
                    }
            st.session_state.standings_year = year


# ── Hero banner ───────────────────────────────────────────────────────────────
yr = st.session_state.standings_year
caption_html = (
    f"<div class='hero-caption'>Season {yr} &nbsp;·&nbsp; auto-loaded from Dynasty{yr}.csv</div>"
    if yr else ""
)
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">🏈 Dynasty Draft Lottery</div>
    <div class="hero-subtitle">Live Weighted Ball Draw System</div>
    {caption_html}
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Team Setup")
    if yr:
        st.caption(f"Pre-filled from Dynasty{yr}.csv — edit any field below.")

    with st.expander("**Lottery Teams** (Non-Playoff)", expanded=True):
        hc1, hc2 = st.columns([2, 1])
        hc1.markdown("<small style='color:#7a8fa8;'>Name</small>", unsafe_allow_html=True)
        hc2.markdown("<small style='color:#7a8fa8;'>MaxPF</small>", unsafe_allow_html=True)
        for i in range(LOTTERY_TEAMS_COUNT):
            cols = st.columns([2, 1])
            st.session_state.lottery_teams[i]['name'] = cols[0].text_input(
                f"lt_name_{i}",
                value=st.session_state.lottery_teams[i].get('name', ''),
                key=f"lt_name_{i}",
                label_visibility="collapsed",
                placeholder=f"Team {i+1}",
            )
            st.session_state.lottery_teams[i]['max_pf'] = cols[1].number_input(
                f"lt_maxpf_{i}",
                value=st.session_state.lottery_teams[i].get('max_pf', 1000.0),
                key=f"lt_maxpf_{i}",
                format="%.2f",
                step=0.01,
                label_visibility="collapsed",
            )

    with st.expander("**Playoff Teams**"):
        hc1, hc2 = st.columns([2, 1])
        hc1.markdown("<small style='color:#7a8fa8;'>Name</small>", unsafe_allow_html=True)
        hc2.markdown("<small style='color:#7a8fa8;'>Rank</small>", unsafe_allow_html=True)
        for i in range(PLAYOFF_TEAMS_COUNT):
            cols = st.columns([2, 1])
            st.session_state.playoff_teams[i]['name'] = cols[0].text_input(
                f"pt_name_{i}",
                value=st.session_state.playoff_teams[i].get('name', ''),
                key=f"pt_name_{i}",
                label_visibility="collapsed",
                placeholder=f"Playoff Team {i+1}",
            )
            st.session_state.playoff_teams[i]['rank'] = cols[1].number_input(
                f"pt_rank_{i}",
                min_value=1,
                max_value=PLAYOFF_TEAMS_COUNT,
                value=st.session_state.playoff_teams[i].get('rank', i + 1),
                key=f"pt_rank_{i}",
                label_visibility="collapsed",
            )

    st.button(
        "🎱  Calculate Initial Distribution",
        on_click=calculate_initial_distribution,
        type="primary",
        use_container_width=True,
    )
    if st.session_state.get('error_message'):
        st.error(st.session_state.error_message)

    st.divider()
    if st.button("🔄  Reset Application", use_container_width=True):
        reset_app()


# ── Main body ─────────────────────────────────────────────────────────────────
if not st.session_state.get('app_started'):
    st.markdown("""
    <div class="card" style="text-align:center; padding:3rem 2rem;">
        <div style="font-size:2.5rem; margin-bottom:0.75rem;">⬅️</div>
        <div style="font-size:1.05rem; color:#7a8fa8;">
            Set up your teams in the sidebar and click
            <strong style="color:#FFB627;">Calculate Initial Distribution</strong>
            to begin.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Status strip ──────────────────────────────────────────────────────────
    picks_done = len(st.session_state.draft_order)
    next_pick = picks_done + 1
    teams_left = len(st.session_state.ball_distribution)

    m1, m2 = st.columns(2)
    m1.metric("Next Pick", f"#{next_pick}" if picks_done < LOTTERY_TEAMS_COUNT else "Done")
    m2.metric("Teams Remaining", teams_left)
    st.markdown("<div style='margin-bottom:1.1rem;'></div>", unsafe_allow_html=True)

    # ── Per-pick winner celebration ───────────────────────────────────────────
    last_w = st.session_state.last_winner
    if last_w and last_w != st.session_state.get('last_celebrated'):
        completed = picks_done
        st.markdown(f"""
        <div class="winner-banner">
            <div class="winner-label">🏆 Pick #{completed} Winner</div>
            <div class="ball-spin" id="lottery-ball-spin">--</div>
            <div class="winner-pick">Selects with the #{completed} overall pick</div>
        </div>
        """, unsafe_allow_html=True)
        celebrate_winner(
            st.session_state.last_drawn_ball or 1,
            st.session_state.get('last_draw_candidates', []),
            last_w,
        )
        st.session_state.last_celebrated = last_w

    # ── Consolation prize ─────────────────────────────────────────────────────
    if not st.session_state.consolation_applied and picks_done == 0:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Consolation Prize (Optional)")
        lottery_names = [t['name'] for t in st.session_state.lottery_teams if t['name']]
        consolation_choice = st.selectbox(
            "Select consolation bracket winner — receives 1 extra ball:",
            options=lottery_names,
            index=None,
            placeholder="Choose a team...",
        )
        if consolation_choice and st.button("Apply Consolation Prize", type="primary"):
            apply_consolation_prize(consolation_choice)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Drawing phase ─────────────────────────────────────────────────────────
    if picks_done < LOTTERY_TEAMS_COUNT:
        st.markdown(f'<div class="pick-header">Drawing for Pick #{next_pick}</div>', unsafe_allow_html=True)

        col_draw, col_state = st.columns([1, 2])

        with col_draw:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**Draw a Ball**")
            drawn_ball = st.number_input(
                "Ball Number (1–200)",
                min_value=1,
                max_value=TOTAL_BALLS,
                step=1,
                key="drawn_ball_input",
            )
            if st.button(f"Submit Ball #{int(drawn_ball)}", type="primary", use_container_width=True):
                draw_lottery_ball(drawn_ball)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.draft_order:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("**Draft Order So Far**")
                draft_df = pd.DataFrame(st.session_state.draft_order).sort_values("pick")
                st.dataframe(draft_df.set_index("pick"), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col_state:
            if st.session_state.ball_distribution:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"**Current Odds — Pick #{next_pick}**")

                current_total = sum(st.session_state.ball_distribution.values())
                chips_html = '<div class="ball-pool">'
                for idx, (team, count) in enumerate(st.session_state.ball_distribution.items()):
                    pct = count / current_total * 100
                    color = CHIP_COLORS[idx % len(CHIP_COLORS)]
                    chips_html += (
                        f'<div class="team-chip" style="background:{color};">'
                        f'<span class="chip-team">{team}</span>'
                        f'<span class="chip-pct">{pct:.1f}%</span>'
                        f'<span class="chip-balls">{count} balls</span>'
                        f'</div>'
                    )
                chips_html += '</div>'
                st.markdown(chips_html, unsafe_allow_html=True)

                odds_data = [
                    {"Team": t, "Balls": c, f"P(Pick #{next_pick})": f"{c/current_total*100:.2f}%"}
                    for t, c in st.session_state.ball_distribution.items()
                ]
                st.dataframe(pd.DataFrame(odds_data), use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)

                with st.expander("Ball Number Assignments"):
                    team_balls: dict = {t: [] for t in st.session_state.ball_distribution}
                    for ball, team in st.session_state.ball_owner_map.items():
                        if team in team_balls:
                            team_balls[team].append(ball)
                    for team, balls in sorted(team_balls.items()):
                        balls.sort()
                        st.markdown(f"**{team} ({len(balls)} balls):**")
                        st.text(', '.join(map(str, balls)))

    # ── Final draft order ─────────────────────────────────────────────────────
    else:
        if picks_done == LOTTERY_TEAMS_COUNT - 1:
            last_team = list(st.session_state.ball_distribution.keys())[0]
            st.session_state.draft_order.append({"pick": LOTTERY_TEAMS_COUNT, "team": last_team})

        st.markdown("""
        <div class="final-banner">
            <div class="final-banner-title">🏆 Final Draft Order</div>
        </div>
        """, unsafe_allow_html=True)

        final_order = st.session_state.draft_order.copy()
        valid_playoff = [pt for pt in st.session_state.playoff_teams if pt['name'].strip()]
        for i, team_info in enumerate(sorted(valid_playoff, key=lambda x: x['rank'], reverse=True)):
            final_order.append({"pick": LOTTERY_TEAMS_COUNT + i + 1, "team": team_info['name']})

        st.table(pd.DataFrame(final_order).sort_values("pick").set_index("pick"))

        if not st.session_state.get('final_celebrated'):
            fire_fireworks_barrage()
            st.session_state.final_celebrated = True


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer-note">Dynasty Fantasy Football League &nbsp;·&nbsp; Lottery Simulator</div>',
    unsafe_allow_html=True,
)
