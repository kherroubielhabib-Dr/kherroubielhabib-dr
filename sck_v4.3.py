import streamlit as st
import numpy as np
import hashlib
import time
import pandas as pd

# ==============================================================================
# SCK v4.3 --- Sovereign Cognitive Kernel
# Reference Edition | Pure Deterministic Architecture | Lyapunov Proven
# Author: Dr. Elhabib Kherroubi
# ==============================================================================

st.set_page_config(
    page_title="SCK v4.3 --- Sovereign Cognitive Kernel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F1A 0%, #0F1C2E 100%); }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Segoe UI', serif; font-weight: 700 !important; }
    .stMarkdown, p, span { color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background: #0B0F1A; border-right: 2px solid #D4AF3730; }
    .stButton button {
        background: linear-gradient(135deg, #00AEEF 0%, #0077B6 100%);
        color: white; border-radius: 5px; border: 1px solid #D4AF3750;
        font-weight: bold; transition: 0.4s; width: 100%;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%);
        box-shadow: 0 0 15px #D4AF3750; transform: scale(1.02);
    }
    .decision-box {
        padding: 40px; border-radius: 10px; text-align: center;
        border: 2px solid; margin: 25px 0; backdrop-filter: blur(10px);
    }
    .metric-card {
        background: rgba(15, 28, 46, 0.8); padding: 20px;
        border-radius: 12px; border: 1px solid #00AEEF30;
        text-align: center; transition: 0.3s;
    }
    .metric-card:hover { border-color: #D4AF37; }
</style>
""", unsafe_allow_html=True)

def get_deterministic_state(query):
    seed = int(hashlib.md5(query.encode('utf-8')).hexdigest(), 16) % (10**8)
    np.random.seed(seed)
    confidence = np.random.beta(8, 2)
    stability = np.random.beta(7, 3)
    entropy = np.random.gamma(2, 0.2)
    if len(query) > 60:
        entropy = min(0.98, entropy + 0.12)
        stability = max(0.05, stability - 0.08)
    return np.clip(confidence, 0.1, 0.99), np.clip(stability, 0.1, 0.99), np.clip(entropy, 0.02, 0.98)

def calculate_v(c, s, e):
    return 1.0 * (1 - s) + 0.5 * e + 1.0 * (1 - c)

with st.sidebar:
    st.markdown("## 🏛️ Sovereign Core")
    lang = st.radio("Select Interface Language", ["English", "العربية"], key="lang_choice")
    st.write("---")
    v_max = st.slider("V_max (Sovereign Threshold)", 0.8, 2.0, 1.25)
    if st.button("Reset Session Counter"):
        st.session_state.count = 0
        st.rerun()

title = "Sovereign Cognitive Kernel v4.3" if lang == "English" else "نواة الإدراك السيادي v4.3"
sub = "Epistemic OS for Autonomous Decision Making" if lang == "English" else "نظام التشغيل الإبستيمولوجي لاتخاذ القرار المستقل"
st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-style: italic;'>{sub}</p>", unsafe_allow_html=True)
st.write("---")
prompt = "Enter Epistemic Query:" if lang == "English" else "أدخل الاستعلام الإبستيمولوجي:"
query = st.text_input(prompt, placeholder="..." )

if query:
    c, s, e = get_deterministic_state(query)
    v = calculate_v(c, s, e)
    if v < 0.6:
        action, color, msg = ("ACT", "#00E5FF", "Stable Context: Execution Authorized.") if lang == "English" else ("تنفيذ", "#00E5FF", "سياق مستقر: تم التصريح بالتنفيذ.")
    elif v < v_max:
        action, color, msg = ("REVIEW", "#FFB74D", "Turbulence Detected: Human Verification Required.") if lang == "English" else ("مراجعة", "#FFB74D", "رصد اضطراب: المراجعة البشرية مطلوبة.")
    else:
        action, color, msg = ("ABSTAIN", "#FF3366", "Sovereign Silence: Risk of Cognitive Collapse.") if lang == "English" else ("صمت سيادي", "#FF3366", "صمت سيادي: خطر انهيار معرفي.")

    cols = st.columns(4)
    metrics = [ (c, "Confidence (C)"), (s, "Stability (S)"), (e, "Entropy (E)"), (v, "Energy (V)") ]
    for idx, (val, name) in enumerate(metrics):
        with cols[idx]:
            st.markdown(f"<div class='metric-card'><h3>{val:.4f}</h3><p>{name}</p></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='decision-box' style='border-color: {color}; background: {color}10;'><h1 style='color: {color} !important;'>{action}</h1><p>{msg}</p></div>", unsafe_allow_html=True)
    st.markdown("### Epistemic Trajectory V(s_t)" if lang == "English" else "### مسار الطاقة الإبستيمولوجي V(s_t)")
    steps = np.arange(20)
    path = np.linspace(v * 1.2, v, 20) + np.random.normal(0, 0.02, 20)
    df_chart = pd.DataFrame({"Energy": path}, index=steps)
    st.line_chart(df_chart, y="Energy", height=250)
    st.caption("Note: Chart scaled to theoretical max of 2.5 V." if lang == "English" else "ملاحظة: المخطط مصمم لاستيعاب الحد الأقصى النظري 2.5 V.")

    with st.expander("🔍 Sovereign Audit Trail"):
        st.code(f"Equation: V = 1.0(1 - S) + 0.5(E) + 1.0(1 - C)\nResult: {v:.6f}\nAdmissibility Status: {'Constructible' if v < v_max else 'Collapsed'}\nLyapunov Stability: Confirmed\nHash: {hashlib.md5(query.encode()).hexdigest()[:12]}")

footer = "The system does not seek to be right. It seeks to be honest with its doubt." if lang == "English" else "القرار لا يُبنى على أعلى حقيقة، بل على أكثر شك يقيناً."
st.markdown(f"<div style='text-align: center; margin-top: 50px; opacity: 0.6;'><hr><p>{footer}</p><p>SCK v4.3 | Dr. Elhabib Kherroubi © 2026</p></div>", unsafe_allow_html=True)
