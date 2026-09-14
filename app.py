import streamlit as st
import sqlite3
import re
from datetime import datetime

try:
    from ai_engine import analyze_reasoning, analyze_decision_fingerprint
    from mindmirror_runtime import get_runtime
    AI_AVAILABLE = True
    RUNTIME = get_runtime()
except Exception:
    AI_AVAILABLE = False
    analyze_decision_fingerprint = None
    RUNTIME = None

DB = "mindmirror.db"

st.set_page_config(
    page_title="MindMirror",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Visual system
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 5%, rgba(116, 91, 255, .16), transparent 28%),
        radial-gradient(circle at 90% 12%, rgba(45, 212, 191, .10), transparent 24%),
        linear-gradient(135deg, #080a11 0%, #0c1020 52%, #071316 100%);
    color: #f5f7fb;
}

.block-container {
    max-width: 1420px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0d16 0%, #080a11 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] * {
    color: #e9edf5;
}

.brand {
    padding: 8px 4px 24px 4px;
}

.brand-title {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -.04em;
}

.brand-sub {
    color: #8f98aa;
    font-size: .82rem;
    line-height: 1.5;
    margin-top: 5px;
}

.ai-pill {
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:7px 11px;
    border:1px solid rgba(45,212,191,.35);
    background:rgba(45,212,191,.08);
    color:#77f2df;
    border-radius:999px;
    font-size:.73rem;
    font-weight:700;
    letter-spacing:.04em;
    margin: 8px 0 14px 0;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 28px;
    padding: 42px 44px;
    background:
        radial-gradient(circle at 12% 20%, rgba(124,92,255,.24), transparent 35%),
        radial-gradient(circle at 88% 80%, rgba(45,212,191,.13), transparent 34%),
        rgba(17,22,35,.78);
    box-shadow: 0 24px 70px rgba(0,0,0,.28);
}

.hero-kicker {
    color:#9d91ff;
    font-size:.72rem;
    font-weight:800;
    letter-spacing:.18em;
    margin-bottom:14px;
}

.hero h1 {
    font-size: 3.1rem;
    line-height: 1.05;
    margin:0;
    letter-spacing:-.06em;
    color:#ffffff;
}

.hero h1 span {
    color:#9f93ff;
}

.hero p {
    max-width: 760px;
    color:#b8c0cf;
    font-size:1.04rem;
    line-height:1.7;
    margin-top:18px;
}

.flow {
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:30px;
    flex-wrap:wrap;
}

.flow-step {
    border:1px solid rgba(255,255,255,.09);
    background:rgba(255,255,255,.035);
    border-radius:14px;
    padding:10px 13px;
    color:#dce2ec;
    font-size:.78rem;
    font-weight:600;
}

.flow-arrow {
    color:#687286;
}

.metric {
    border:1px solid rgba(255,255,255,.09);
    border-radius:20px;
    padding:20px 22px;
    background:rgba(17,20,29,.82);
    min-height:112px;
}

.metric-label {
    color:#8f99ab;
    font-size:.76rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:.08em;
}

.metric-value {
    color:#ffffff;
    font-size:2rem;
    font-weight:800;
    letter-spacing:-.05em;
    margin-top:8px;
}

.metric-note {
    color:#717b8e;
    font-size:.72rem;
    margin-top:3px;
}

.section-title {
    color:#ffffff;
    font-size:1.45rem;
    font-weight:800;
    letter-spacing:-.035em;
    margin:30px 0 6px;
}

.section-sub {
    color:#7f899c;
    font-size:.86rem;
    margin-bottom:16px;
}

.card {
    border:1px solid rgba(255,255,255,.085);
    border-radius:20px;
    padding:22px;
    background:rgba(16,19,28,.76);
    box-shadow:0 12px 35px rgba(0,0,0,.14);
    height:100%;
}

.card-title {
    color:#f4f6fb;
    font-size:1rem;
    font-weight:700;
    margin-bottom:7px;
}

.card-text {
    color:#8f99aa;
    font-size:.83rem;
    line-height:1.55;
}

.badge {
    display:inline-block;
    padding:5px 9px;
    border-radius:999px;
    background:rgba(124,92,255,.11);
    border:1px solid rgba(124,92,255,.23);
    color:#b4aaff;
    font-size:.68rem;
    font-weight:700;
    margin-top:12px;
}

.decision-card {
    border:1px solid rgba(255,255,255,.08);
    border-radius:18px;
    padding:18px 20px;
    background:rgba(15,18,27,.75);
    margin-bottom:12px;
}

.decision-number {
    color:#8f82ff;
    font-size:.72rem;
    font-weight:800;
    letter-spacing:.1em;
    text-transform:uppercase;
}

.decision-name {
    color:#f4f6fb;
    font-size:1rem;
    font-weight:700;
    margin-top:5px;
}

.decision-meta {
    color:#778195;
    font-size:.75rem;
    margin-top:7px;
}

.insight {
    border-left:3px solid #8d7cff;
    background:rgba(124,92,255,.07);
    border-radius:0 16px 16px 0;
    padding:16px 18px;
    color:#d9d6f4;
    line-height:1.65;
}

.question {
    border:1px solid rgba(45,212,191,.18);
    background:rgba(45,212,191,.045);
    border-radius:16px;
    padding:16px 18px;
    color:#c8f5ee;
    line-height:1.55;
}

div.stButton > button {
    border-radius:12px;
    border:1px solid rgba(255,255,255,.10);
    background:rgba(255,255,255,.055);
    color:#ffffff;
    font-weight:650;
}

div.stButton > button:hover {
    border-color:rgba(141,124,255,.55);
    color:#ffffff;
}

.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {
    background:#10141e !important;
    color:#f5f7fb !important;
    border:1px solid rgba(255,255,255,.10) !important;
    border-radius:12px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background:#10141e;
    border-radius:12px;
    border-color:rgba(255,255,255,.10);
}

hr {
    border-color:rgba(255,255,255,.07);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Database
# -----------------------------
def db():
    return sqlite3.connect(DB)

def init_db():
    c = db()
    c.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        decision TEXT NOT NULL,
        reasoning TEXT NOT NULL,
        prediction TEXT NOT NULL,
        confidence INTEGER NOT NULL,
        expected_date TEXT,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Locked',
        actual_outcome TEXT,
        outcome_date TEXT
    )
    """)
    c.commit()
    c.close()

init_db()

def all_decisions():
    c = db()
    rows = c.execute(
        "SELECT id, decision, reasoning, prediction, confidence, expected_date, created_at, status, actual_outcome, outcome_date FROM decisions ORDER BY id DESC"
    ).fetchall()
    c.close()
    return rows

def completed():
    c = db()
    rows = c.execute(
        "SELECT id, decision, reasoning, prediction, confidence, expected_date, created_at, status, actual_outcome, outcome_date FROM decisions WHERE status='Completed' ORDER BY id DESC"
    ).fetchall()
    c.close()
    return rows

def add_decision(decision, reasoning, prediction, confidence, expected_date):
    c = db()
    c.execute(
        """INSERT INTO decisions
        (decision, reasoning, prediction, confidence, expected_date, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Locked')""",
        (decision, reasoning, prediction, confidence, expected_date, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    c.commit()
    c.close()

def complete_decision(row_id, actual):
    c = db()
    c.execute(
        "UPDATE decisions SET actual_outcome=?, outcome_date=?, status='Completed' WHERE id=?",
        (actual, datetime.now().strftime("%Y-%m-%d %H:%M"), row_id)
    )
    c.commit()
    c.close()

def first_number(text):
    if not text:
        return None
    m = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(m.group()) if m else None

def prediction_gap(pred, actual):
    p, a = first_number(pred), first_number(actual)
    if p is None or a is None or p == 0:
        return None
    return abs(p-a) / abs(p) * 100

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-title">🪞 MindMirror</div>
      <div class="brand-sub">Your decisions, replayed.<br>Your thinking, evolved.</div>
    </div>
    """, unsafe_allow_html=True)

    runtime_info = RUNTIME.describe() if RUNTIME is not None else {
        "backend": "unavailable",
        "model": "not detected",
        "execution": "Runtime unavailable",
    }

    if AI_AVAILABLE:
        st.markdown(
            '<div class="ai-pill">● LOCAL AI ACTIVE</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="ai-pill">● LOCAL AI READY</div>',
            unsafe_allow_html=True
        )

    backend_label = {
        "ollama": "Ollama",
        "geniex": "Qualcomm / GenieX",
    }.get(runtime_info["backend"], runtime_info["backend"].title())

    st.caption(f"Runtime: {backend_label}")
    st.caption(f"Model: {runtime_info['model']}")
    st.caption(f"{runtime_info['execution']}")
    st.caption("Decision data stays on this device.")

    with st.expander("Runtime diagnostics"):
        st.caption(f"Backend: {runtime_info['backend']}")
        st.caption(f"Model: {runtime_info['model']}")
        st.caption(f"Execution: {runtime_info['execution']}")

        if RUNTIME is not None:
            health = RUNTIME.health_check()
            status = "Available" if health.get("ok") else "Unavailable"
            st.caption(f"Runtime status: {status}")

            if health.get("models"):
                st.caption(
                    "Local models: " + ", ".join(health["models"][:5])
                )

            # Accelerator is intentionally reported conservatively. The Dell
            # development runtime is CPU/fallback; we only claim NPU when the
            # selected Qualcomm runtime explicitly reports it later.
            if runtime_info["backend"] == "geniex":
                st.caption("Accelerator: Qualcomm runtime (verify NPU on target PC)")
            elif runtime_info["backend"] == "ollama":
                st.caption("Accelerator: Development/fallback path")
        else:
            st.caption("Runtime status: Unavailable")

    st.markdown("### Navigate")
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ New Decision", "📚 Decision History",
         "🔄 Decision Replay", "🪞 Reasoning Mirror", "🧠 Decision Fingerprint"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("MindMirror 1.0 • Runtime-aware local AI")

rows = all_decisions()
done = completed()

# -----------------------------
# Dashboard
# -----------------------------
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">PRIVATE • LOCAL • LEARNING</div>
      <h1>Mind<span>Mirror</span></h1>
      <p>
        A private decision-learning system that compares what you believed
        with what reality taught you — then helps you notice how you think.
      </p>
      <div class="flow">
        <div class="flow-step">💭 Think</div><div class="flow-arrow">→</div>
        <div class="flow-step">🎯 Predict</div><div class="flow-arrow">→</div>
        <div class="flow-step">🔒 Lock</div><div class="flow-arrow">→</div>
        <div class="flow-step">📈 Experience</div><div class="flow-arrow">→</div>
        <div class="flow-step">🪞 Reflect</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your decision landscape</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">A quick view of the decisions you have captured so far.</div>', unsafe_allow_html=True)

    awaiting = len([r for r in rows if r[7] != "Completed"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric"><div class="metric-label">Decisions</div><div class="metric-value">{len(rows)}</div><div class="metric-note">captured in your mirror</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric"><div class="metric-label">Awaiting outcomes</div><div class="metric-value">{awaiting}</div><div class="metric-note">still waiting for reality</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric"><div class="metric-label">Replayed</div><div class="metric-value">{len(done)}</div><div class="metric-note">decisions compared with outcomes</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">The idea behind MindMirror</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">It is not trying to tell you what to decide. It is trying to help you understand your own decision process.</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    cards = [
        ("🔒 Lock the moment", "Capture your reasoning and prediction before hindsight changes the story.", "BEFORE"),
        ("🔄 Replay reality", "Come back later and compare what you expected with what actually happened.", "AFTER"),
        ("🧠 Learn the pattern", "Use repeated decisions to surface recurring assumptions and prediction habits.", "OVER TIME")
    ]
    for col, (title, text, badge) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="card"><div class="card-title">{title}</div><div class="card-text">{text}</div><div class="badge">{badge}</div></div>', unsafe_allow_html=True)

    if done:
        st.markdown('<div class="section-title">Recent reflections</div>', unsafe_allow_html=True)
        for r in done[:3]:
            gap = prediction_gap(r[3], r[8])
            gap_text = f"{gap:.1f}% prediction gap" if gap is not None else "qualitative replay"
            st.markdown(f"""
            <div class="decision-card">
              <div class="decision-number">DECISION #{r[0]}</div>
              <div class="decision-name">{r[1]}</div>
              <div class="decision-meta">{gap_text} • confidence {r[4]}%</div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# New Decision
# -----------------------------
elif page == "➕ New Decision":
    st.markdown('<div class="section-title">Capture a decision</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Write down what you genuinely believe now. The point is to preserve the moment before hindsight.</div>', unsafe_allow_html=True)

    with st.form("new_decision"):
        decision = st.text_input("What decision are you making?", placeholder="e.g. Should I launch the premium version?")
        reasoning = st.text_area("Why do you think this is the right decision?", height=150, placeholder="What evidence, assumptions or experiences are influencing you?")
        prediction = st.text_input("What do you expect will happen?", placeholder="e.g. I expect 150 customers in the first month.")
        confidence = st.slider("How confident are you?", 0, 100, 70)
        expected_date = st.date_input("When should we revisit this?", value=datetime.now().date())
        submitted = st.form_submit_button("🔒 Lock this decision", use_container_width=True)

    if submitted:
        if not decision.strip() or not reasoning.strip() or not prediction.strip():
            st.error("Please complete the decision, reasoning and prediction.")
        else:
            add_decision(decision.strip(), reasoning.strip(), prediction.strip(), confidence, str(expected_date))
            st.success("Decision locked. Your future self can now replay it.")
            st.rerun()

# -----------------------------
# History
# -----------------------------
elif page == "📚 Decision History":
    st.markdown('<div class="section-title">Decision History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Every decision stays in your local mirror.</div>', unsafe_allow_html=True)

    if not rows:
        st.info("No decisions yet. Start by capturing your first decision.")
    else:
        for r in rows:
            status = "COMPLETED" if r[7] == "Completed" else "WAITING"
            st.markdown(f"""
            <div class="decision-card">
              <div class="decision-number">#{r[0]} • {status}</div>
              <div class="decision-name">{r[1]}</div>
              <div class="decision-meta">Confidence {r[4]}% • Created {r[6]}</div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Open decision"):
                st.write("**Reasoning**")
                st.write(r[2])
                st.write("**Prediction**")
                st.write(r[3])
                if r[7] == "Completed":
                    st.write("**Actual outcome**")
                    st.write(r[8])
                else:
                    actual = st.text_area("Record the actual outcome", key=f"outcome_{r[0]}", placeholder="What actually happened?")
                    if st.button("Complete replay", key=f"complete_{r[0]}"):
                        if actual.strip():
                            complete_decision(r[0], actual.strip())
                            st.rerun()
                        else:
                            st.warning("Add the actual outcome first.")

# -----------------------------
# Replay
# -----------------------------
elif page == "🔄 Decision Replay":
    st.markdown('<div class="section-title">Decision Replay</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Step back into what you believed — then see what reality changed.</div>', unsafe_allow_html=True)

    if not done:
        st.info("Complete at least one decision to unlock replay.")
    else:
        labels = {f"#{r[0]} — {r[1]}": r for r in done}
        selected = st.selectbox("Choose a completed decision", list(labels.keys()))
        r = labels[selected]

        left, right = st.columns(2)
        with left:
            st.markdown('<div class="card"><div class="card-title">🎯 What you believed</div><div class="card-text">Your original reasoning and prediction.</div></div>', unsafe_allow_html=True)
            st.markdown(f"**Reasoning**  \n{r[2]}")
            st.markdown(f"**Prediction**  \n{r[3]}")
            st.caption(f"Confidence: {r[4]}%")
        with right:
            st.markdown('<div class="card"><div class="card-title">📈 What reality taught you</div><div class="card-text">The outcome you recorded later.</div></div>', unsafe_allow_html=True)
            st.markdown(f"**Actual outcome**  \n{r[8]}")
            gap = prediction_gap(r[3], r[8])
            if gap is not None:
                st.metric("Prediction gap", f"{gap:.1f}%")

        st.divider()
        st.markdown('<div class="section-title">🪞 AI reflection</div>', unsafe_allow_html=True)

        if AI_AVAILABLE:
            try:
                result = analyze_reasoning(r[1], r[2], r[3], r[8], r[4])
                if isinstance(result, dict):
                    a, b = st.columns(2)
                    with a:
                        st.markdown('<div class="insight"><b>Assumption</b><br>' + str(result.get("assumption", "Not identified")) + '</div>', unsafe_allow_html=True)
                        st.write("")
                        st.markdown('<div class="insight"><b>Potential weakness</b><br>' + str(result.get("potential_weakness", "Not identified")) + '</div>', unsafe_allow_html=True)
                    with b:
                        st.markdown('<div class="insight"><b>Reality check</b><br>' + str(result.get("reality_check", "Not identified")) + '</div>', unsafe_allow_html=True)
                        st.write("")
                        st.markdown('<div class="question"><b>Ask yourself next time</b><br>' + str(result.get("next_time_question", "What would I want to verify before making this decision?")) + '</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.warning("The local AI reflection could not be generated right now.")
                st.caption(str(e))
        else:
            st.info("AI engine is not available. The replay still works locally.")

# -----------------------------
# Reasoning Mirror
# -----------------------------
elif page == "🪞 Reasoning Mirror":
    st.markdown('<div class="section-title">Reasoning Mirror</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">The signature idea: instead of predicting your future, MindMirror studies how your decisions are formed.</div>', unsafe_allow_html=True)

    if not done:
        st.info("Complete decisions first. The mirror becomes more useful as your history grows.")
    else:
        st.markdown("""
        <div class="hero" style="padding:28px 32px;">
          <div class="hero-kicker">YOUR REASONING • OVER TIME</div>
          <h1 style="font-size:2rem;">What keeps showing up in your decisions?</h1>
          <p style="font-size:.95rem;">
            MindMirror looks for recurring assumptions, evidence patterns and
            expectation-vs-reality gaps. These are signals, not diagnoses.
          </p>
        </div>
        """, unsafe_allow_html=True)

        results = []
        for r in done:
            if AI_AVAILABLE:
                try:
                    out = analyze_reasoning(r[1], r[2], r[3], r[8], r[4])
                    if isinstance(out, dict):
                        results.append(out)
                except Exception:
                    pass

        if results:
            st.markdown('<div class="section-title">Signals from your recent decisions</div>', unsafe_allow_html=True)

            assumptions = [x.get("assumption") for x in results if x.get("assumption")]
            weaknesses = [x.get("potential_weakness") for x in results if x.get("potential_weakness")]

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="card"><div class="card-title">🔍 Assumptions</div><div class="card-text">What your reasoning appears to rely on.</div></div>', unsafe_allow_html=True)
                for x in assumptions[:5]:
                    st.markdown(f"- {x}")
            with c2:
                st.markdown('<div class="card"><div class="card-title">⚠️ Potential weak points</div><div class="card-text">Where reality may have more uncertainty than the original reasoning suggested.</div></div>', unsafe_allow_html=True)
                for x in weaknesses[:5]:
                    st.markdown(f"- {x}")

            st.markdown('<div class="section-title">The mirror rule</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="question">
            <b>Don't ask: “Was I right?”</b><br>
            Ask: “What did I believe, why did I believe it, and what should I notice next time?”
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Add a few more completed decisions and the AI reflection layer will become more useful.")

# -----------------------------
# Fingerprint
# -----------------------------
elif page == "🧠 Decision Fingerprint":
    st.markdown('<div class="section-title">Decision Fingerprint</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">A lightweight view of how your predictions have behaved — now combined with an AI reading of the reasoning behind them.</div>', unsafe_allow_html=True)

    if len(done) < 3:
        st.info("Complete at least 3 decisions to build your first fingerprint.")
    else:
        gaps = [prediction_gap(r[3], r[8]) for r in done]
        gaps = [g for g in gaps if g is not None]
        avg_gap = sum(gaps)/len(gaps) if gaps else 0
        avg_conf = sum(r[4] for r in done)/len(done)

        over = 0
        under = 0
        matched = 0
        for r in done:
            p, a = first_number(r[3]), first_number(r[8])
            if p is not None and a is not None:
                if p > a:
                    over += 1
                elif p < a:
                    under += 1
                else:
                    matched += 1

        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            ("DECISIONS ANALYSED", len(done)),
            ("AVG PREDICTION GAP", f"{avg_gap:.1f}%"),
            ("AVG CONFIDENCE", f"{avg_conf:.0f}%"),
            ("OVER / UNDER", f"{over} / {under}")
        ]
        for col, (label, value) in zip([c1,c2,c3,c4], metrics):
            with col:
                st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Your current signal</div>', unsafe_allow_html=True)
        if over > under:
            signal_text = "Your recorded predictions currently lean optimistic: expected outcomes have been higher than actual outcomes more often."
        elif under > over:
            signal_text = "Your recorded predictions currently lean conservative: actual outcomes have been higher than predicted more often."
        else:
            signal_text = "Your recorded predictions are currently balanced between over- and under-estimation."

        st.markdown(f'<div class="insight">{signal_text}<br><br><small>MindMirror is showing a pattern in the recorded numbers — it is not labelling your personality.</small></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🧠 AI Decision Fingerprint</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
        <div class="card-text" style="font-size:.9rem;">
        MindMirror now compares your recorded reasoning, confidence, predictions and outcomes
        to surface recurring decision signals. The AI uses only your recorded decisions.
        </div>
        </div>
        """, unsafe_allow_html=True)

        if AI_AVAILABLE:
            if st.button("🧠 Generate AI Fingerprint", use_container_width=True):
                with st.spinner("Comparing your decisions..."):
                    result = analyze_decision_fingerprint(
                        [(r[1], r[2], r[3], r[8], r[4]) for r in done]
                    )
                    st.session_state["fingerprint_ai_result"] = result

            result = st.session_state.get("fingerprint_ai_result")

            if result and not result.get("error"):
                cards = [
                    ("Prediction bias", result.get("prediction_bias", "Not available.")),
                    ("Confidence pattern", result.get("confidence_pattern", "Not available.")),
                    ("Evidence effectiveness", result.get("evidence_effectiveness", "Not available.")),
                    ("Recurring reasoning pattern", result.get("recurring_reasoning_pattern", "Not available.")),
                    ("Reality lesson", result.get("reality_lesson", "Not available.")),
                    ("Practical adjustment", result.get("practical_adjustment", "Not available.")),
                ]

                for i in range(0, len(cards), 2):
                    left, right = st.columns(2)
                    for col, (title, value) in zip([left, right], cards[i:i+2]):
                        with col:
                            st.markdown(
                                f'<div class="insight"><b>{title}</b><br><br>{value}</div>',
                                unsafe_allow_html=True
                            )

                st.markdown(
                    '<div class="question"><b>Ask before your next similar decision</b><br>' +
                    str(result.get("next_decision_question", "What evidence would most change my prediction?")) +
                    '</div>',
                    unsafe_allow_html=True
                )
            elif result and result.get("error"):
                st.warning("The AI fingerprint could not be generated right now.")
                st.caption(str(result["error"]))
        else:
            st.info("AI engine is not available. The numerical fingerprint still works locally.")

        st.markdown('<div class="section-title">Why this matters</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
        <div class="card-text" style="font-size:.9rem;">
        A single decision can be luck. A repeated pattern is more interesting.
        As the history grows, MindMirror can compare prediction accuracy with
        confidence and reasoning signals to help you notice where your decision
        process may consistently drift from reality.
        </div>
        </div>
        """, unsafe_allow_html=True)
