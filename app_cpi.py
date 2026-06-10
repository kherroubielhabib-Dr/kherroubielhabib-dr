"""
مؤشر التلاقح المعرفي - CPI Dashboard
د. الحبيب خروبي · ESU-001
تشغيل على Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="CPI Dashboard - مؤشر التلاقح المعرفي",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص للغة العربية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');
    * {
        font-family: 'IBM Plex Sans Arabic', 'Segoe UI', sans-serif;
    }
    .stApp {
        direction: rtl;
    }
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .cpi-card {
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        color: white;
    }
    .dim-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-right: 4px solid;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# الأبعاد الأربعة
DIMS = {
    'P': {'name': 'الممارسة', 'color': '#2563EB', 'question': 'هل فهمنا أولويات بعضنا البعض في القرارات؟', 'desc': 'مدى استيعاب كل تخصص لأولويات التخصص الآخر'},
    'L': {'name': 'اللغة المشتركة', 'color': '#059669', 'question': 'هل تحدثنا بلغة مشتركة دون سوء فهم؟', 'desc': 'وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال'},
    'G': {'name': 'التوجيه', 'color': '#7C3AED', 'question': 'هل تدفقت الأفكار من الجميع (وليس فقط من القائد)؟', 'desc': 'اتجاه تدفق الأفكار داخل النظام'},
    'EH': {'name': 'التواضع المعرفي', 'color': '#DC2626', 'question': 'هل استمعنا لبعضنا بتواضع وغيرنا مواقفنا؟', 'desc': 'قدرة الأفراد على قبول التصحيح والتعلم من الآخرين'}
}

LEVELS = [
    {'min': 0, 'max': 40, 'label': 'نموذج العبقري المنعزل', 'color': '#EF4444'},
    {'min': 40, 'max': 65, 'label': 'تعاون شكلي', 'color': '#F59E0B'},
    {'min': 65, 'max': 85, 'label': 'ذكاء جماعي واعٍ جزئياً', 'color': '#3B82F6'},
    {'min': 85, 'max': 101, 'label': 'ذكاء جماعي حقيقي — اختفاء الحدود', 'color': '#10B981'}
]

def get_level(cpi):
    for l in LEVELS:
        if l['min'] <= cpi < l['max']:
            return l
    return LEVELS[3]

def calc_cpi(scores):
    vals = [v for v in scores.values() if v > 0]
    if len(vals) < 4:
        return None
    return round((sum(vals) / 16) * 100)

def init_session_state():
    if 'sessions' not in st.session_state:
        st.session_state.sessions = []
    if 'scores' not in st.session_state:
        st.session_state.scores = {k: 0 for k in DIMS.keys()}
    if 'session_label' not in st.session_state:
        st.session_state.session_label = ''

init_session_state()

# ==================== الرأس ====================
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin:0;">🧠 مؤشر التلاقح المعرفي</h1>
        <p style="color: #7DD3FC; margin:0;">Cross-Pollination Index — CPI Dashboard</p>
        <p style="color: #94A3B8; font-size: 0.8rem; margin-top: 0.5rem;">CI = NK × EH — الذكاء الجماعي = المعرفة الشبكية × التواضع المعرفي</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== الشريط الجانبي ====================
with st.sidebar:
    st.markdown("## 📊 لوحة التحكم")
    tab_choice = st.radio("", ["📝 تقييم جلسة", "📈 لوحة القيادة", "📜 السجل"], label_visibility="collapsed")
    
    st.markdown("---")
    st.caption("CPI — د. الحبيب خروبي · ESU-001")

# ==================== تبويب: تقييم جلسة ====================
if tab_choice == "📝 تقييم جلسة":
    st.markdown("## 📝 تقييم جلسة جديدة")
    
    session_label = st.text_input("اسم الجلسة (اختياري)", value=st.session_state.session_label, placeholder="مثال: اجتماع الفريق - يناير 2026")
    st.session_state.session_label = session_label
    
    st.markdown("### قيّم الأبعاد الأربعة")
    st.caption("1 = ضعيف · 2 = مقبول · 3 = جيد · 4 = متقدم (اختفاء الحدود)")
    
    cols = st.columns(2)
    for i, (key, dim) in enumerate(DIMS.items()):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"""
                <div class="dim-card" style="border-right-color: {dim['color']}">
                    <h4 style="color: {dim['color']}; margin:0;">{dim['name']} <span style="font-size:0.8rem;">({key})</span></h4>
                    <p style="font-size:0.8rem; color:#6B7280;">{dim['desc']}</p>
                    <p style="font-style:italic; font-size:0.85rem;">“{dim['question']}”</p>
                </div>
                """, unsafe_allow_html=True)
                
                score = st.select_slider(
                    f"تقييم {dim['name']}",
                    options=[1, 2, 3, 4],
                    value=st.session_state.scores.get(key, 1) if st.session_state.scores.get(key, 0) > 0 else 1,
                    key=f"score_{key}"
                )
                st.session_state.scores[key] = score
    
    cpi_now = calc_cpi(st.session_state.scores)
    
    if cpi_now is not None:
        level = get_level(cpi_now)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="cpi-card">
                <p style="font-size:0.8rem;">CPI المحسوب</p>
                <h1 style="font-size:3rem; margin:0;">{cpi_now}%</h1>
                <p style="margin:0; background:rgba(255,255,255,0.2); border-radius:20px; padding:0.2rem;">{level['label']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # مخطط راداري بسيط باستخدام plotly
            fig = go.Figure()
            values = [st.session_state.scores.get(k, 0) for k in DIMS.keys()]
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=[d['name'] for d in DIMS.values()],
                fill='toself',
                fillcolor='rgba(37,99,235,0.3)',
                line=dict(color='#2563EB', width=2),
                name='التقييم'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 4], tickvals=[1,2,3,4]),
                    angularaxis=dict(direction='clockwise', rotation=90)
                ),
                showlegend=False,
                height=250,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if st.button(f"✅ تسجيل الجلسة — CPI: {cpi_now}%", use_container_width=True):
            new_session = {
                'id': datetime.now().timestamp(),
                'label': session_label or f"جلسة {len(st.session_state.sessions)+1}",
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'scores': st.session_state.scores.copy(),
                'cpi': cpi_now
            }
            st.session_state.sessions.append(new_session)
            st.session_state.scores = {k: 0 for k in DIMS.keys()}
            st.session_state.session_label = ''
            st.success("✓ تم تسجيل الجلسة!")
            st.rerun()
    else:
        st.warning("⚠️ يرجى تقييم جميع الأبعاد الأربعة أولاً.")

# ==================== تبويب: لوحة القيادة ====================
elif tab_choice == "📈 لوحة القيادة":
    st.markdown("## 📈 لوحة القيادة")
    
    if not st.session_state.sessions:
        st.info("📊 لا توجد بيانات بعد. ابدأ بتسجيل أول جلسة في تبويب 'تقييم جلسة'.")
    else:
        last = st.session_state.sessions[-1]
        level = get_level(last['cpi'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="cpi-card">
                <p style="font-size:0.8rem;">آخر CPI مسجل</p>
                <h1 style="font-size:3rem; margin:0;">{last['cpi']}%</h1>
                <p style="margin:0; background:rgba(255,255,255,0.2); border-radius:20px; padding:0.2rem;">{level['label']}</p>
                <p style="margin-top:0.5rem; font-size:0.7rem;">{last['label']} · {last['date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            values = [last['scores'].get(k, 0) for k in DIMS.keys()]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=[d['name'] for d in DIMS.values()],
                fill='toself',
                fillcolor='rgba(37,99,235,0.3)',
                line=dict(color='#2563EB', width=2)
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 4], tickvals=[1,2,3,4]),
                    angularaxis=dict(direction='clockwise', rotation=90)
                ),
                showlegend=False,
                height=250,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # تفصيل الأبعاد
        st.markdown("### تفصيل الأبعاد - آخر جلسة")
        for key, dim in DIMS.items():
            val = last['scores'].get(key, 0)
            pct = (val / 4) * 100
            st.markdown(f"""
            <div style="margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight:600;">{dim['name']} ({key})</span>
                    <span style="color:{dim['color']}; font-weight:700;">{val}/4</span>
                </div>
                <div style="background:#F3F4F6; border-radius:10px; height:8px; overflow:hidden;">
                    <div style="background:{dim['color']}; width:{pct}%; height:100%; border-radius:10px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # مؤشر BDI
        if len(st.session_state.sessions) >= 2:
            last_vals = [st.session_state.sessions[-1]['scores'].get(k, 0) for k in DIMS.keys()]
            mean = sum(last_vals) / 4
            variance = sum((v - mean) ** 2 for v in last_vals) / 4
            bdi = round((1 - variance / 2.25) * 100)
            bdi_color = '#10B981' if bdi >= 75 else '#3B82F6' if bdi >= 50 else '#EF4444'
            st.markdown(f"""
            <div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:12px; padding:0.8rem; margin:1rem 0; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600; color:#7C3AED;">مؤشر اختفاء الحدود (BDI)</div>
                    <div style="font-size:0.7rem; color:#9CA3AF;">كلما اقترب من 100% كلما اقترب الفريق من العقل الجماعي</div>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:{bdi_color};">{bdi}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # مسار التطور
        if len(st.session_state.sessions) >= 2:
            st.markdown("### مسار CPI عبر الزمن")
            sessions_rev = st.session_state.sessions[-10:]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[s['label'] for s in sessions_rev],
                y=[s['cpi'] for s in sessions_rev],
                mode='lines+markers',
                line=dict(color='#2563EB', width=2),
                marker=dict(size=8, color=[get_level(s['cpi'])['color'] for s in sessions_rev]),
                name='CPI'
            ))
            fig.update_layout(
                height=300,
                yaxis=dict(title='CPI (%)', range=[0, 100]),
                xaxis=dict(title='الجلسة'),
                showlegend=False,
                margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # توصيات التحسين
        st.markdown("### 💡 توصيات التحسين")
        weak_dims = [(k, v) for k, v in last['scores'].items() if v <= 2]
        if not weak_dims:
            st.success("✓ جميع الأبعاد في مستوى جيد. استمر في المسار الحالي!")
        else:
            recommendations = {
                'P': 'جلسات «تظليل وظيفي» أسبوعية — يظلل كل تخصص الآخر.',
                'L': 'ورشة بناء «قاموس مشترك» — يوم واحد + تحديثات أسبوعية.',
                'G': 'إلغاء الموافقات الهرمية على الاقتراحات الصغيرة. تفعيل تصويت مرجح بالخبرة.',
                'EH': 'جلسات «مراجعة عمياء» — تقييم الأفكار دون معرفة صاحبها.'
            }
            for key, val in weak_dims:
                dim = DIMS[key]
                st.warning(f"**{dim['name']} — يحتاج تعزيز**\n\n{recommendations.get(key, '')}")

# ==================== تبويب: السجل ====================
else:
    st.markdown("## 📜 سجل الجلسات")
    
    if not st.session_state.sessions:
        st.info("🗂️ لا توجد جلسات مسجلة بعد.")
    else:
        if st.button("🗑️ حذف كل الجلسات", use_container_width=True):
            st.session_state.sessions = []
            st.rerun()
        
        for session in reversed(st.session_state.sessions):
            level = get_level(session['cpi'])
            with st.expander(f"📌 {session['label']} — {session['date']} — {session['cpi']}%"):
                cols = st.columns(4)
                for i, (key, dim) in enumerate(DIMS.items()):
                    val = session['scores'].get(key, 0)
                    with cols[i]:
                        st.markdown(f"""
                        <div style="text-align:center;">
                            <div style="font-size:1.2rem; font-weight:700; color:{dim['color']};">{dim['name']}</div>
                            <div style="font-size:1.5rem; font-weight:800;">{val}/4</div>
                        </div>
                        """, unsafe_allow_html=True)
