import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
import unicodedata
# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Administrative Pressure Monitoring Dashboard",
    layout="wide"
)

# =====================================================
# CSS — FIXED (TITLE WILL SHOW)
# =====================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0E1117 !important;
    color: #E5E7EB;
}

.block-container {
    max-width: 1200px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* MAIN SECTION CARD */
.section-card {
    background: #FFFFFF;
    color: #111827;
    padding: 18px 24px;          /* ↓ reduced padding */
    margin-bottom: 22px;         /* ↓ reduced spacing */
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.22);
}

/* TITLES */
.section-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 4px;          /* ↓ tighter */
}

/* DESCRIPTIONS */

.section-desc {
    font-size: 17px;              /* ↑ from 15 */
    font-weight: 500;             /* subtle emphasis */
    color: #1F2937;               /* darker for contrast */
    margin-bottom: 14px;
    line-height: 1.65;
}

/* ===== BLUE – interpretation ===== */
.insight-box {
    background: #EFF6FF;
    color: #1E3A8A;
    border-left: 5px solid #2563EB;
    padding: 22px 26px;
    margin-top: 18px;
    font-size: 17px;
    line-height: 1.75;
    border-radius: 10px;
}

/* ===== ORANGE – decision / action ===== */
.action-box {
    background: #FFF7ED;
    color: #7C2D12;
    border-left: 5px solid #F97316;
    padding: 26px 30px;
    margin-top: 26px;
    font-size: 17.5px;
    line-height: 1.8;
    border-radius: 12px;
}

/* ===== CYAN – executive summary ===== */
.summary-box {
    background: #ECFEFF;
    color: #0F172A;
    border-left: 6px solid #0891B2;
    padding: 30px 34px;
    margin-top: 30px;
    font-size: 18.5px;
    line-height: 1.85;
    border-radius: 14px;
}
/* ===== SIGNAL CHIPS ===== */
.signal-chip {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 20px;
    font-weight: 600;
    background: #E5E7EB;
    color: #111827;
}

.signal-chip.severity {
    background: #FFF7ED;
    color: #7C2D12;
}

.signal-chip.confidence {
    background: #ECFEFF;
    color: #0F172A;
}

.signal-chip.anomaly {
    background: #EFF6FF;
    color: #1E3A8A;
}

/* ===== EXEC ACTION ===== */
.exec-action {
    margin-top: 20px;
    padding: 14px 18px;
    background: #FFF7ED;
    border-left: 4px solid #F97316;
    font-weight: 600;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# MATPLOTLIB SETTINGS
# =====================================================
mpl.rcParams.update({
    "figure.figsize": (11, 4),
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
})

# =====================================================
# CANONICALISATION (UNCHANGED)
# =====================================================
STATE_MAP = {
    "west bengal": "West Bengal",
    "westbengal": "West Bengal",
    "West Bangal": "West Bengal",
    "orissa": "Odisha",
    "odisha": "Odisha",

    "uttaranchal": "Uttarakhand",
    "uttarakhand": "Uttarakhand",

    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",

    "nct of delhi": "Delhi",
    "delhi": "Delhi",

    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andaman nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar islands": "Andaman & Nicobar Islands",

    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu":
        "Dadra & Nagar Haveli and Daman & Diu",

    "lakshadweep": "Lakshadweep",
    "laksha dweep": "Lakshadweep",

    "jammu and kashmir": "Jammu & Kashmir",
    "jammu & kashmir": "Jammu & Kashmir",
    "ladakh": "Ladakh",
}

def canon_state(x):
    if not isinstance(x, str):
        return x
    key = x.lower().replace("&", "and").replace(".", "").strip()
    key = " ".join(key.split())
    return STATE_MAP.get(key, key.title())
def hard_clean(s: str) -> str:
    if not isinstance(s, str):
        return s
    return (
        s.replace("\u200b", "")   # zero-width space
         .replace("\ufeff", "")   # BOM
         .replace("\xa0", " ")    # non-breaking space
         .strip()
    )
    return x
def canon_district(x):
    if not isinstance(x, str):
        return x
    return " ".join(x.title().split())


# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    base = Path(__file__).resolve().parent.parent
    d = base / "data" / "processed"

    comp = pd.read_csv(d / "composite_pressure_index.csv")
    typ = pd.read_csv(d / "district_risk_typology.csv")

    comp["month"] = pd.to_datetime(comp["month"])

    # 🔥 CANONICALISE ONCE, OVERWRITE
    comp["state"] = (
    comp["state"]
    .astype(str)
    .apply(hard_clean)
    .apply(canon_state)
    )
    comp["district"] = comp["district"].apply(canon_district)

    typ["state"] = typ["state"].apply(canon_state)
    typ["district"] = typ["district"].apply(canon_district)

    return comp, typ

df, typ = load_data()
df["state"] = df["state"].apply(hard_clean)
typ["state"] = typ["state"].apply(hard_clean)
# =====================================================
# HEADER (THIS WILL NOW SHOW)
# =====================================================
st.markdown(
    "<h1 style='font-size:42px; font-weight:600;'>Administrative Pressure Monitoring Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='font-size:17px;color:#CBD5E1;'>Decision-support view of Aadhaar-related administrative workload using anonymised, aggregated indicators.</p>",
    unsafe_allow_html=True
)
st.divider()

# =====================================================
# CONTROLS (NOW CLEAN)
# =====================================================
c1, c2 = st.columns(2)
# ===== HARD DEDUPLICATION FOR DROPDOWNS =====
state_options = (
    df[["state"]]
    .drop_duplicates()
    .sort_values("state")
    ["state"]
    .tolist()
)
STATE_MASTER = sorted(set(df["state"].tolist()))

state = c1.selectbox("State", STATE_MASTER)
district_options = (
    df[df["state"] == state][["district"]]
    .drop_duplicates()
    .sort_values("district")
    ["district"]
    .tolist()
)

district = c2.selectbox("District", district_options)

sdf = df[df["state"] == state]
ddf = sdf[sdf["district"] == district].sort_values("month")
# =====================================================
# ALERT SIGNAL INTERPRETATION (NON-INTRUSIVE)
# =====================================================
latest_row = ddf.iloc[-1]

early_warning = latest_row.get("early_warning", 0)
sustained_alert = latest_row.get("sustained_alert", 0)

if sustained_alert == 1:
    alert_signal = "Sustained Administrative Stress"
elif early_warning == 1:
    alert_signal = "Early Warning Signal"
else:
    alert_signal = "No Active Alert"
latest = ddf.iloc[-1]
risk_row = typ[(typ["state"] == state) & (typ["district"] == district)]


# =====================================================
# KPI STRIP
# =====================================================
st.markdown("<h2 style='font-size:30px;'>Administrative Situation Overview</h2>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

k1.metric("Current Status", "Elevated" if latest["composite_pressure_index"] > 0 else "Normal")
k2.metric("Recent Trend", "Increasing" if ddf.tail(3)["composite_pressure_index"].mean() > 0 else "Stable")
k3.metric("Latest Index", f"{latest['composite_pressure_index']:.2f}")
k4.metric("Risk Typology", risk_row["risk_category"].iloc[0] if not risk_row.empty else "Not Classified")

# =====================================================
# VISUAL 1 — DISTRICT TREND
# =====================================================
with st.container():
    st.markdown("""
    <div class="section-card">
    <div class="section-title">Is administrative pressure building?</div>
    <div class="section-desc">Monthly composite pressure trend for the selected district.</div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.plot(ddf["month"], ddf["composite_pressure_index"], marker="o", linewidth=2)
    ax.axhline(0)
    ax.set_xlabel("Month")
    ax.set_ylabel("Composite Pressure Index")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    slope = ddf.tail(6)["composite_pressure_index"].diff().mean()
    trend_msg = (
        "Pressure has been rising consistently over recent months."
        if slope > 0.1 else
        "Pressure has been easing over recent months."
        if slope < -0.1 else
        "Pressure has remained broadly stable."
    )

    st.markdown(f"<div class='insight-box'><b>Interpretation:</b> {trend_msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# VISUAL 2 — DISTRICT vs STATE vs NATIONAL
# =====================================================
with st.container():
    st.markdown("""
    <div class="section-card">
    <div class="section-title">Is this pressure local or systemic?</div>
    <div class="section-desc">Comparison with state and national averages.</div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.plot(ddf.groupby("month")["composite_pressure_index"].mean(), label="District", linewidth=3)
    ax.plot(sdf.groupby("month")["composite_pressure_index"].mean(), label="State", linestyle="--")
    ax.plot(df.groupby("month")["composite_pressure_index"].mean(), label="National", linestyle=":")
    ax.axhline(0)
    ax.set_xlabel("Month")
    ax.set_ylabel("Composite Pressure Index")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    st.markdown(
        "<div class='insight-box'><b>Interpretation:</b> Divergence from state and national trends suggests district-specific administrative drivers.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# VISUAL 3 — DRIVERS
# =====================================================
with st.container():
    st.markdown("""
    <div class="section-card">
    <div class="section-title">What is driving the workload?</div>
    <div class="section-desc">Biometric vs demographic pressure components.</div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.plot(ddf["month"], ddf["biometric_pressure_index"], label="Biometric")
    ax.plot(ddf["month"], ddf["demographic_pressure_index"], label="Demographic")
    ax.axhline(0)
    ax.set_xlabel("Month")
    ax.set_ylabel("Normalised Pressure Index")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    driver_msg = (
        "Recent pressure is primarily driven by biometric-related activity."
        if ddf["biometric_pressure_index"].tail(4).mean() >
           ddf["demographic_pressure_index"].tail(4).mean()
        else
        "Recent pressure is primarily driven by demographic update activity."
    )

    st.markdown(f"<div class='insight-box'><b>Interpretation:</b> {driver_msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# VISUAL 4 — RISK TYPOLOGY
# =====================================================
with st.container():
    st.markdown("""
    <div class="section-card">
    <div class="section-title">Is this district stable or shock-prone?</div>
    <div class="section-desc">District position within the state risk landscape.</div>
    """, unsafe_allow_html=True)

    fig, ax = plt.subplots()
    st_typ = typ[typ["state"] == state]
    ax.scatter(st_typ["mean_pressure"], st_typ["volatility"], alpha=0.4)
    if not risk_row.empty:
        ax.scatter(risk_row["mean_pressure"].iloc[0], risk_row["volatility"].iloc[0],
                   s=180, color="red")
    ax.set_xlabel("Average Pressure")
    ax.set_ylabel("Volatility")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    stab_msg = (
        "The district experiences episodic administrative surges."
        if not risk_row.empty and risk_row["volatility"].iloc[0] > 1 else
        "The district operates under stable administrative conditions."
    )

    st.markdown(f"<div class='insight-box'><b>Interpretation:</b> {stab_msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
# =====================================================
# CONFIDENCE LOGIC EXPLANATION (NEW, NON-INTRUSIVE)
# =====================================================
confidence_explainer = (
    "The confidence score reflects consistency and persistence of administrative pressure "
    "over recent months. Higher confidence indicates repeated positive deviations rather "
    "than isolated spikes, improving reliability of the signal."
)


# =====================================================
# DECISION SUPPORT & EXECUTIVE READINESS
# =====================================================
recent = ddf.tail(4)["composite_pressure_index"]
confidence_score = int(((recent > 0).sum() / len(recent)) * 60 + 40)
confidence_label = "High" if confidence_score >= 75 else "Moderate" if confidence_score >= 50 else "Low"

delta = ddf.iloc[-1]["composite_pressure_index"] - ddf.iloc[-2]["composite_pressure_index"] if len(ddf) > 1 else 0
mom_text = (
    "Pressure increased compared to last month." if delta > 0.15 else
    "Pressure decreased compared to last month." if delta < -0.15 else
    "Pressure remained stable compared to last month."
)

positive_months = (recent > 0).sum()
severity = (
    "Normal" if positive_months == 0 else
    "Watch" if positive_months == 1 else
    "Elevated" if positive_months in [2, 3] else
    "Sustained"
)

action = (
    "Consider reinforcing administrative staffing and monitoring."
    if severity in ["Elevated", "Sustained"] else
    "Continue routine monitoring."
)

summary = (
    f"In {district}, {state}, administrative workload shows {confidence_label.lower()} confidence. "
    f"{mom_text} Current severity level is {severity}. Recommended action: {action}"
)

# =====================================================
# EXPLICIT ANOMALY FRAMING (TEXT ONLY)
# =====================================================
district_mean = ddf["composite_pressure_index"].mean()
state_mean = sdf["composite_pressure_index"].mean()
district_vol = ddf["composite_pressure_index"].std()
state_vol = sdf["composite_pressure_index"].std()

if district_mean > state_mean and district_vol > state_vol:
    anomaly_type = "Structural Anomaly"
    anomaly_expl = (
        "The district consistently operates under higher-than-normal administrative load "
        "with elevated volatility, indicating systemic stress rather than isolated events."
    )
elif district_vol > state_vol:
    anomaly_type = "Operational Shock"
    anomaly_expl = (
        "Administrative pressure fluctuates sharply despite a moderate average, "
        "suggesting episodic operational disruptions or short-term surges."
    )
elif sustained_alert == 1:
    anomaly_type = "Chronic Stress Pattern"
    anomaly_expl = (
        "Administrative pressure remains elevated across consecutive months, "
        "indicating sustained workload accumulation."
    )
elif early_warning == 1:
    anomaly_type = "Transient Spike"
    anomaly_expl = (
        "A short-term elevation has been detected, but pressure has not yet persisted."
    )
else:
    anomaly_type = "No Significant Anomaly"
    anomaly_expl = (
        "Administrative pressure aligns closely with state-level patterns and remains stable."
    )
# =====================================================
# WHY THIS DISTRICT IS DIFFERENT — EXECUTIVE CONTEXT
# =====================================================
district_mean = ddf["composite_pressure_index"].mean()
state_mean = sdf["composite_pressure_index"].mean()
district_vol = ddf["composite_pressure_index"].std()
state_vol = sdf["composite_pressure_index"].std()

if district_mean > state_mean and district_vol > state_vol:
    diff_msg = (
        "This district shows both higher average administrative pressure and higher volatility "
        "than the state baseline, indicating recurrent administrative stress surges."
    )
elif district_mean > state_mean:
    diff_msg = (
        "This district consistently operates above the state average, suggesting sustained "
        "administrative demand."
    )
elif district_vol > state_vol:
    diff_msg = (
        "This district aligns with the state average workload but experiences higher volatility, "
        "indicating intermittent pressure spikes."
    )
else:
    diff_msg = (
        "This district closely mirrors state-level administrative patterns with stable workload behaviour."
    )

st.markdown(
f"""
<div class="summary-box">

  <div style="font-size:22px;font-weight:600;margin-bottom:14px;">
    Executive Assessment: Administrative Pressure & Readiness
  </div>

  <div style="display:flex; gap:12px; margin-bottom:18px; flex-wrap:wrap;">
    <div class="signal-chip severity">{severity}</div>
    <div class="signal-chip confidence">Confidence: {confidence_label}</div>
    <div class="signal-chip anomaly">{anomaly_type}</div>
  </div>

  <p>
    The selected district is currently operating under an
    <b>{severity.lower()}</b> level of administrative workload.
    Recent data indicates that pressure has {mom_text.lower()}.
    Overall workload remains above routine thresholds, warranting
    continued administrative attention.
  </p>

  <p>
    The confidence associated with this assessment is
    <b>{confidence_label.lower()}</b>, reflecting repeated elevation
    across recent months rather than a single isolated spike.
    This suggests a meaningful signal, though not yet an entrenched
    structural overload.
  </p>

  <p>
    From an anomaly perspective, the district aligns with a
    <b>{anomaly_type.lower()}</b> pattern. {anomaly_expl}
  </p>

  <p>
    Relative to the state baseline, the district
    {diff_msg.lower()}.
  </p>

  <div class="exec-action">
    Recommended action: {action}
  </div>

</div>
""",
unsafe_allow_html=True
)
st.caption(
    "All insights are derived from anonymised, aggregated administrative data. "
    "No individual-level inference or causal attribution is made."
)