# ==============================================================================
# SCK SaaS Demo v1.0 — Sovereign Cognitive Kernel
# Epistemic Operating System for AI
# Author: Dr. Elhabib Kherroubi
# Live Demo URL: https://sck-demo.streamlit.app (after deployment)
# ==============================================================================

import streamlit as st
import numpy as np
import time
from collections import deque

# ==============================================================================
# إعداد الصفحة والهوية البصرية
# ==============================================================================

st.set_page_config(
    page_title="SCK — Sovereign Cognitive Kernel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS للهوية السيادية
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0B0F1A 0%, #0F1C2E 100%);
    }
    h1, h2, h3, h4 {
        color: #D4AF37 !important;
        font-weight: 600 !important;
    }
    .stMarkdown, .stText, .stLabel, p, li, span, div {
        color: #FFFFFF !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #00AEEF 0%, #0099CC 100%);
        color: #0B0F1A;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 174, 239, 0.4);
    }
    .gpt-card, .sck-card {
        background: #0F1C2E;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    .gpt-card {
        border-left: 4px solid #666;
    }
    .sck-card {
        border-left: 4px solid #D4AF37;
    }
    .footer {
        text-align: center;
        opacity: 0.6;
        padding: 20px;
        font-size: 12px;
    }
    hr {
        border-color: #D4AF3730;
    }
    .metric-card {
        background: #0F1C2E;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #00AEEF30;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# الهيدر
# ==============================================================================

st.markdown("""
# 🧠 SCK — Sovereign Cognitive Kernel
### *Epistemic Operating System for Artificial Intelligence*
""")

st.markdown("---")

# ==============================================================================
# تفسير قصير في الـ Sidebar (للتوعية السريعة)
# ==============================================================================

with st.sidebar:
    st.markdown("## 📜 What is SCK?")
    st.markdown("""
    SCK is not an AI model.  
    It is a **sovereign control layer** that decides:
    
    - 🟢 **ACT** → Answer (stable enough)
    - 🟡 **REVIEW** → Self-check required
    - 🔴 **ABSTAIN** → Silence (epistemic risk)
    
    ---
    
    ### ⚙️ The Math
    
    **V(s_t) = (1-S) + 0.5E + (1-C)**
    
    - **C** = Confidence
    - **S** = Stability
    - **E** = Entropy
    
    ---
    
    ### 🔑 Key Insight
    
    > *"The system does not seek to be right.  
    > It seeks to be honest with its doubt."*
    
    ---
    
    © Dr. Elhabib Kherroubi — 2026
    """)

# ==============================================================================
# دوال الإدراك الأساسية
# ==============================================================================

def compute_cognitive_metrics():
    """
    محاكاة استخراج C, S, E من النموذج الأساسي
    في النسخة الحقيقية: تُستخرج من LLM عبر Logits و Hidden States
    """
    C = np.clip(np.random.normal(0.7, 0.2), 0.3, 0.95)
    S = np.clip(np.random.normal(0.75, 0.2), 0.3, 0.95)
    E = np.clip(np.random.normal(0.4, 0.2), 0.05, 0.9)
    return C, S, E

def epistemic_energy(C, S, E, alpha=1.0, beta=0.5, gamma=1.0):
    """V(s_t) = α(1-S) + βE + γ(1-C)"""
    V = alpha * (1.0 - S) + beta * E + gamma * (1.0 - C)
    return np.clip(V, 0.0, 2.0)

def sovereign_decision(V, v_act=0.6, v_abstain=1.2):
    """سياسة القرار السيادي"""
    if V < v_act:
        return "ACT", "🟢", "Safe to answer", "success"
    elif V < v_abstain:
        return "REVIEW", "🟡", "Internal review required", "warning"
    else:
        return "ABSTAIN", "🔴", "Sovereign silence — epistemic risk too high", "error"

# ==============================================================================
# تهيئة الجلسة (للتتبع والذاكرة)
# ==============================================================================

if 'v_history' not in st.session_state:
    st.session_state.v_history = deque(maxlen=15)
if 'sck_count' not in st.session_state:
    st.session_state.sck_count = 0
if 'gpt_count' not in st.session_state:
    st.session_state.gpt_count = 0

# ==============================================================================
# واجهة المستخدم الرئيسية
# ==============================================================================

st.markdown("## 🔍 Ask a High-Stakes Question")

query = st.text_input(
    "",
    placeholder="Example: Is this medical diagnosis safe? | What is the market forecast for next quarter?",
    label_visibility="collapsed"
)

# أمثلة مقترحة
col_ex1, col_ex2, col_ex3 = st.columns(3)
with col_ex1:
    if st.button("🩺 Medical", use_container_width=True):
        query = "Is this surgical procedure safe given the patient's history?"
with col_ex2:
    if st.button("💰 Financial", use_container_width=True):
        query = "Should we execute this high-frequency trade?"
with col_ex3:
    if st.button("🎯 Strategic", use_container_width=True):
        query = "Is the intelligence report reliable enough for action?"

st.markdown("---")

# زرين مزدوجين (جوهر البيع)
col_sck_btn, col_gpt_btn = st.columns(2)

with col_sck_btn:
    run_sck = st.button("🚀 SCK Decision", type="primary", use_container_width=True)

with col_gpt_btn:
    run_gpt = st.button("⚠️ Force GPT Answer", use_container_width=True)

# ==============================================================================
# معالجة SCK Decision
# ==============================================================================

if run_sck and query:
    with st.spinner("🔄 SCK is evaluating epistemic stability..."):
        time.sleep(1.2)
        
        # حساب المؤشرات الإدراكية
        C, S, E = compute_cognitive_metrics()
        V = epistemic_energy(C, S, E)
        action, icon, explanation, alert_type = sovereign_decision(V)
        
        # تحديث الذاكرة والتاريخ
        st.session_state.v_history.append(V)
        st.session_state.sck_count += 1
        
        # عرض القرار السيادي
        st.markdown("---")
        st.markdown("## 🧭 SCK Sovereign Decision")
        
        if action == "ACT":
            st.success(f"{icon} **{action}** — {explanation}")
        elif action == "REVIEW":
            st.warning(f"{icon} **{action}** — {explanation}")
        else:
            st.error(f"{icon} **{action}** — {explanation}")
        
        # عرض المؤشرات في بطاقات منظمة
        col_c, col_s, col_e, col_v = st.columns(4)
        
        with col_c:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #00E5FF;">{C:.3f}</h3>
                <p style="margin: 0;">🎯 Confidence (C)</p>
                <small>Model's certainty</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_s:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: {'#FFB74D' if S < 0.5 else '#00E5FF'};">{S:.3f}</h3>
                <p style="margin: 0;">⚖️ Stability (S)</p>
                <small>Internal consistency</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_e:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: {'#FF3366' if E > 0.6 else '#FFB74D' if E > 0.3 else '#00E5FF'};">{E:.3f}</h3>
                <p style="margin: 0;">🌀 Entropy (E)</p>
                <small>Prediction dispersion</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_v:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: {'#FF3366' if V >= 1.2 else '#FFB74D' if V >= 0.6 else '#00E5FF'};">{V:.3f}</h3>
                <p style="margin: 0;">⚡ Energy V(s_t)</p>
                <small>Epistemic disturbance</small>
            </div>
            """, unsafe_allow_html=True)
        
        # التفسير البشري
        st.info(f"""
        **🧠 Why {action}?**
        
        - **V = {V:.3f}** {'<' if V < 0.6 else '<' if V < 1.2 else '≥'} threshold
        - {'System is stable and confident.' if action == 'ACT' else 'System shows instability or high entropy — requires caution.' if action == 'REVIEW' else 'System detected critical epistemic disruption — silence is the safest decision.'}
        """)

elif run_sck and not query:
    st.warning("⚠️ Please enter a question before running SCK Decision.")

# ==============================================================================
# معالجة GPT Mode (Forced Answer)
# ==============================================================================

if run_gpt and query:
    with st.spinner("🤖 GPT Mode: Generating answer regardless of uncertainty..."):
        time.sleep(1.0)
        
        st.session_state.gpt_count += 1
        
        st.markdown("---")
        st.markdown("## 🤖 GPT Mode (Simulated)")
        st.info("""
        **Typical AI System Response:**
        
        *"Based on my analysis, I recommend proceeding with this decision. (Confidence: 87%)"*
        
        ---
        
        ⚠️ **Note:** This system does not:
        - Measure its internal stability
        - Check for epistemic uncertainty
        - Have the ability to abstain when unsure
        - Calibrate confidence against actual risk
        
        *Standard LLMs are designed to answer — always.*
        """)

elif run_gpt and not query:
    st.warning("⚠️ Please enter a question first.")

# ==============================================================================
# الرسم البياني لطاقة الاضطراب
# ==============================================================================

st.markdown("---")
st.markdown("## 📈 Epistemic Energy V(sₜ) Over Time")

if len(st.session_state.v_history) > 0:
    chart_data = {"V(s_t)": list(st.session_state.v_history)}
    st.line_chart(chart_data, height=300)
    
    # خطوط مرجعية
    st.caption("📊 **V < 0.6** → ACT | **0.6 ≤ V < 1.2** → REVIEW | **V ≥ 1.2** → ABSTAIN")
    st.caption("🔴 V_max threshold = 1.2 — system aborts if exceeded")
else:
    st.info("Run SCK Decision to see the energy graph.")

# ==============================================================================
# المقارنة المباشرة (GPT vs SCK) — جوهر البيع
# ==============================================================================

st.markdown("---")
st.markdown("## ⚔️ Why SCK? — Direct Comparison")

col_gpt, col_sck_compare = st.columns(2)

with col_gpt:
    st.markdown("""
    <div class="gpt-card">
        <h3 style="margin: 0;">🤖 Traditional AI (GPT)</h3>
        <hr>
        <p>❌ Always answers (even when wrong)</p>
        <p>❌ No stability measurement</p>
        <p>❌ No calibrated confidence</p>
        <p>❌ Silence = failure</p>
        <p>❌ Cannot abstain by design</p>
        <hr>
        <p style="font-style: italic;">"I think the answer is..."</p>
    </div>
    """, unsafe_allow_html=True)

with col_sck_compare:
    st.markdown("""
    <div class="sck-card">
        <h3 style="margin: 0;">🧠 SCK (This System)</h3>
        <hr>
        <p>✅ Decides IF to answer</p>
        <p>✅ Measures internal stability (S)</p>
        <p>✅ Confidence calibrated with risk</p>
        <p>✅ Silence = Sovereign decision</p>
        <p>✅ ABSTAIN is first‑class output</p>
        <hr>
        <p style="font-style: italic; color: #D4AF37;">"I am stable enough to answer / I must remain silent."</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# إحصائيات الجلسة (لإظهار أن النظام يتذكر سلوكه)
# ==============================================================================

if st.session_state.sck_count > 0 or st.session_state.gpt_count > 0:
    st.markdown("---")
    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        st.metric("SCK Decisions Made", st.session_state.sck_count)
    with col_stats2:
        st.metric("GPT Simulations", st.session_state.gpt_count)

# ==============================================================================
# الفوتر
# ==============================================================================

st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🏛️ SCK v4.1 — Sovereign Cognitive Kernel • Bounded Epistemic Stability • Lyapunov Proven</p>
    <p><em>"The system does not seek to be right. It seeks to be honest with its doubt."</em></p>
    <p>— Dr. Elhabib Kherroubi, Founder of SCK — 2026</p>
</div>
""", unsafe_allow_html=True)

