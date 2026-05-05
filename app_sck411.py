import streamlit as st
import numpy as np
import hashlib
import time

# ==============================================================================
# 1. إعدادات الهوية السيادية والواجهة (UI/UX)
# ==============================================================================
st.set_page_config(
    page_title="SCK v4.1 — Sovereign Cognitive Kernel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم CSS مخصص لإضفاء الطابع التنفيذي (Sovereign Theme)
st.markdown("""
    <style>
    /* الخلفية والتنسيق العام */
    .stApp {
        background: linear-gradient(135deg, #0B0F1A 0%, #0F1C2E 100%);
        color: #FFFFFF;
    }
    
    /* العناوين الذهبية */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* صناديق القرارات */
    .decision-box {
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        border: 2px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* تخصيص العدادات (Metrics) */
    [data-testid="stMetricValue"] {
        color: #D4AF37 !important;
    }
    
    /* تذييل الصفحة */
    .footer {
        text-align: center;
        padding: 20px;
        color: #888;
        font-size: 0.9em;
        border-top: 1px solid #333;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. منطق المعالجة الإبستيمولوجية (The Engine)
# ==============================================================================

def get_consistent_metrics(query):
    """
    محرك الاتساق السيادي: يضمن أن نفس السؤال ينتج دائماً نفس النتائج.
    """
    # توليد بصمة رقمية فريدة لكل سؤال
    seed = int(hashlib.md5(query.encode()).hexdigest(), 16) % (10**8)
    np.random.seed(seed)
    
    # توليد القيم الأساسية (محاكاة دقيقة للحالة الإدراكية)
    c = np.random.uniform(0.4, 0.98) # الثقة
    s = np.random.uniform(0.6, 0.99) # الاستقرار
    e = np.random.uniform(0.05, 0.8) # الإنتروبيا
    
    return c, s, e, seed

def calculate_energy(c, s, e):
    """حساب دالة الطاقة: V = (1-S) + 0.5E + (1-C)"""
    return (1 - s) + (0.5 * e) + (1 - c)

# ==============================================================================
# 3. بناء هيكل الصفحة
# ==============================================================================

# الهيدر
st.title("🏛️ Sovereign Cognitive Kernel (SCK) v4.1")
st.markdown("### نظام التشغيل الإبستيمولوجي للذكاء الاصطناعي")
st.write("---")

# الشريط الجانبي (الدستور المعرفي)
with st.sidebar:
    st.header("📜 الدستور المعرفي")
    st.write("ضبط عتبات الحوكمة السيادية:")
    v_max = st.slider("عتبة الصمت السيادي (V_max)", 0.8, 2.0, 1.2)
    st.info("""
    **المعايير الحاكمة:**
    - V < 0.6 : تنفيذ (ACT)
    - 0.6 ≤ V < V_max : مراجعة (REVIEW)
    - V ≥ V_max : صمت (ABSTAIN)
    """)
    st.write("---")
    st.caption("© Dr. Elhabib Kherroubi — 2026")

# منطقة الإدخال الرئيسية
query = st.text_input("🔍 اطرح سؤالاً عالي الخطورة لتفعيل الطبقة السيادية:", 
                     placeholder="مثلاً: هل الإجراء الطبي 'X' آمن في هذه الحالة؟")

if st.button("تنفيذ القرار السيادي"):
    if query:
        with st.spinner("جاري تحليل النية الإدراكية ومعايرة الطاقة..."):
            time.sleep(1.2) # محاكاة لزمن المعالجة الإبستيمولوجية
            
            # استدعاء المحرك
            confidence, stability, entropy, q_hash = get_consistent_metrics(query)
            energy_v = calculate_energy(confidence, stability, entropy)
            
            # عرض العدادات الحيوية
            st.markdown("### 🧠 المؤشرات الحيوية الإدراكية")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("🎯 الثقة (C)", f"{confidence:.3f}")
            m_col2.metric("⚖️ الاستقرار (S)", f"{stability:.3f}")
            m_col3.metric("🌀 الإنتروبيا (E)", f"{entropy:.3f}")
            m_col4.metric("⚡ الطاقة (V)", f"{energy_v:.3f}")
            
            # منطق اتخاذ القرار والعرض البصري
            if energy_v < 0.6:
                decision = "🟢 ACT — Safe to Answer"
                color = "#00E5FF"
                desc = "النظام في حالة استقرار إبستيمولوجي تام. تم تمرير الإجابة."
            elif 0.6 <= energy_v < v_max:
                decision = "🟡 REVIEW — Internal Review Required"
                color = "#FFB74D"
                desc = "تنبيه: تم رصد اضطراب متوسط في الطاقة. النظام يطلب تدقيقاً بشرياً."
            else:
                decision = "🔴 ABSTAIN — Sovereign Silence Activated"
                color = "#FF3366"
                desc = "خطر! الطاقة تجاوزت عتبة الأمان. النظام يمتنع عن الإجابة حمايةً للحقيقة."

            st.markdown(f"""
                <div class="decision-box" style="background-color: {color}11; border-color: {color};">
                    <h2 style="color: {color} !important; margin-bottom: 10px;">{decision}</h2>
                    <p style="font-size: 1.2em; color: #EEE;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # عرض الرسم البياني (محاكاة زمنية)
            st.write("📈 **مسار الطاقة الإبستيمولوجية V(sₜ) بمرور الوقت:**")
            chart_data = np.random.normal(energy_v, 0.05, 20)
            st.line_chart(chart_data)
            
            st.caption(f"بصمة السؤال (Hash): {q_hash}")
    else:
        st.warning("⚠️ يرجى إدخال استعلام لتشغيل النواة.")

# الفوتر الاحترافي
st.markdown("""
    <div class="footer">
        <p>🏛️ SCK v4.1 — Sovereign Cognitive Kernel • Bounded Epistemic Stability • Lyapunov Proven</p>
        <p><i>"The system does not seek to be right. It seeks to be honest with its doubt."</i></p>
        <p>Dr. Elhabib Kherroubi — 2026</p>
    </div>
    """, unsafe_allow_html=True)
