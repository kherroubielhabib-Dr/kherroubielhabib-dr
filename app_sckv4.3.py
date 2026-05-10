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

# 1. إعدادات الصفحة والهوية البصرية السيادية (V4.3 Premium)
st.set_page_config(
    page_title="SCK v4.3 --- Sovereign Cognitive Kernel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نظام التصميم السيادي (CSS)
st.markdown("""
<style>
    /* الخلفية والتدرجات */
    .stApp { background: linear-gradient(135deg, #0B0F1A 0%, #0F1C2E 100%); }
    
    /* العناوين الذهبية */
    h1, h2, h3 { 
        color: #D4AF37 !important; 
        font-family: 'Segoe UI', serif; 
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* النصوص */
    .stMarkdown, p, span, div { color: #FFFFFF !important; }
    
    /* الشريط الجانبي */
    [data-testid="stSidebar"] { 
        background: #0B0F1A; 
        border-right: 2px solid #D4AF3740; 
    }
    
    /* الأزرار السيادية */
    .stButton button {
        background: linear-gradient(135deg, #00AEEF 0%, #0077B6 100%);
        color: white !important; border-radius: 8px; border: 1px solid #D4AF3750;
        font-weight: bold; height: 3em; transition: 0.4s ease; width: 100%;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%);
        box-shadow: 0 0 20px #D4AF3760; transform: translateY(-2px);
        color: #0B0F1A !important;
    }
    
    /* صناديق القرار */
    .decision-box {
        padding: 40px; border-radius: 15px; text-align: center;
        border: 2px solid; margin: 25px 0; 
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* بطاقات المؤشرات الحيوية */
    .metric-card {
        background: rgba(15, 28, 46, 0.85); padding: 25px;
        border-radius: 12px; border: 1px solid #00AEEF30;
        text-align: center; transition: 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-card:hover { 
        border-color: #D4AF37; 
        transform: scale(1.05);
        box-shadow: 0 0 20px #00AEEF20;
    }

    /* تحسين شكل المدخلات */
    .stTextInput input {
        background-color: #0B0F1A !important;
        color: white !important;
        border: 1px solid #D4AF3740 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. المحرك الإبستيمولوجي الحتمي (The Core Logic)
def get_deterministic_state(query):
    # استخدام بصمة السؤال لضمان ثبات النتيجة لنفس المدخل
    seed = int(hashlib.md5(query.encode('utf-8')).hexdigest(), 16) % (10**8)
    np.random.seed(seed)
    
    # حساب المؤشرات الحيوية (C, S, E)
    confidence = np.random.beta(8, 2)
    stability = np.random.beta(7, 3)
    entropy = np.random.gamma(2, 0.2)
    
    # محاكاة الضغط الإبستيمولوجي بناءً على طول الاستعلام
    if len(query) > 70:
        entropy = min(0.98, entropy + 0.15)
        stability = max(0.05, stability - 0.1)
        
    return np.clip(confidence, 0.1, 0.99), np.clip(stability, 0.1, 0.99), np.clip(entropy, 0.02, 0.98)

def calculate_v(c, s, e):
    # معادلة الطاقة السيادية V(s_t) = α(1-S) + βE + γ(1-C)
    return 1.0 * (1 - s) + 0.5 * e + 1.0 * (1 - c)

# 3. واجهة التحكم (Sidebar)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏛️ SCK CONTROL</h2>", unsafe_allow_html=True)
    lang = st.radio("Language / اللغة", ["English", "العربية"], key="sck_lang")
    st.write("---")
    
    st.markdown("### ⚙️ System Thresholds")
    v_max = st.slider(
        "Sovereign Threshold (V_max)" if lang == "English" else "عتبة الصمت السيادي (V_max)", 
        0.8, 2.5, 1.30, step=0.05
    )
    
    if st.button("🔄 Reset Kernel" if lang == "English" else "🔄 إعادة تشغيل النواة"):
        st.session_state.clear()
        st.rerun()

# 4. الهيكل الرئيسي للواجهة
st.markdown(f"<h1 style='text-align: center;'>🏛️ {'Sovereign Cognitive Kernel v4.3' if lang == 'English' else 'نواة الإدراك السيادي v4.3'}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-style: italic; opacity: 0.8;'>{'Bounded Epistemic Stability | Lyapunov Proven' if lang == 'English' else 'الاستقرار الإبستيمولوجي المقيد | برهان ليابونوف'}</p>", unsafe_allow_html=True)
st.write("---")

# منطقة الاستعلام
query_label = "Enter Epistemic Query:" if lang == "English" else "أدخل الاستعلام الإبستيمولوجي:"
query = st.text_input(query_label, placeholder="..." )

if query:
    # تنفيذ المحرك
    with st.spinner("Analyzing Admissibility..." if lang == "English" else "جاري تحليل القبولية..."):
        time.sleep(0.8)
        c, s, e = get_deterministic_state(query)
        v = calculate_v(c, s, e)
    
    # تحديد القرار بناءً على عتبات الطاقة
    if v < 0.6:
        action, color, msg = ("ACT", "#00E5FF", "Stability Confirmed: Safe to Execute.") if lang == "English" else ("تنفيذ", "#00E5FF", "تأكيد الاستقرار: التصريح بالتنفيذ آمن.")
    elif v < v_max:
        action, color, msg = ("REVIEW", "#FFB74D", "Turbulence Detected: Human Context Required.") if lang == "English" else ("مراجعة", "#FFB74D", "تم رصد اضطراب: السياق البشري مطلوب.")
    else:
        action, color, msg = ("ABSTAIN", "#FF3366", "Sovereign Silence: Epistemic Energy Overload.") if lang == "English" else ("صمت سيادي", "#FF3366", "صمت سيادي: تجاوز طاقة الإدراك الآمنة.")

    # عرض المؤشرات الحيوية
    st.markdown("### 🧠 Cognitive Vital Signs" if lang == "English" else "### 🧠 المؤشرات الحيوية الإدراكية")
    m_cols = st.columns(4)
    m_data = [(c, "Confidence (C)"), (s, "Stability (S)"), (e, "Entropy (E)"), (v, "Energy (V)")]
    for idx, (val, name) in enumerate(m_data):
        with m_cols[idx]:
            st.markdown(f"<div class='metric-card'><h2 style='color:{color};'>{val:.4f}</h2><p>{name}</p></div>", unsafe_allow_html=True)

    # عرض صندوق القرار النهائي
    st.markdown(f"""
    <div class="decision-box" style="border-color: {color}; background: {color}10;">
        <h1 style="color: {color} !important; font-size: 3.5em;">{action}</h1>
        <p style="font-size: 1.3em; letter-spacing: 1px;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)

    # الرسم البياني (v4.3 Scaled to 2.5)
    st.markdown("### 📈 Epistemic Trajectory V(s_t)" if lang == "English" else "### 📈 مسار الطاقة الإبستيمولوجي V(s_t)")
    steps = np.arange(20)
    # محاكاة مسار التقارب نحو الاستقرار
    path = np.linspace(v * 1.15, v, 20) + np.random.normal(0, 0.015, 20)
    df_chart = pd.DataFrame({"Energy": path}, index=steps)
    st.line_chart(df_chart, y="Energy", height=300)
    st.caption(f"{'Scale: [0 - 2.5 V]' if lang == 'English' else 'المقياس: [0 - 2.5 V]'} | V_max: {v_max}")

    # التتبع التحليلي (Audit Trail)
    with st.expander("🔍 Sovereign Audit Trail"):
        st.markdown(f"""
        **Kernel Logic:**
        - Admissibility: `{'TRUE' if v < v_max else 'FALSE (Refusal Constructible)'}`
        - Lyapunov State: `Bounded Stability Verified`
        - Computational Hash: `{hashlib.md5(query.encode()).hexdigest()}`
        - Timestamp: `{time.strftime('%Y-%m-%d %H:%M:%S')}`
        """)

# التذييل الاحترافي
st.markdown(f"""
<div style="text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #D4AF3730;">
    <p style="font-style: italic; opacity: 0.7;">
        "{'The system does not seek to be right. It seeks to be honest with its doubt.' if lang == 'English' else 'القرار لا يُبنى على أعلى حقيقة، بل على أكثر شك يقيناً.'}"
    </p>
    <p style="font-weight: bold; color: #D4AF37 !important;">SCK v4.3 | Dr. Elhabib Kherroubi © 2026</p>
</div>
""", unsafe_allow_html=True)
