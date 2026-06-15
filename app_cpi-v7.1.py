# ═══════════════════════════════════════════════════════════════════
# مؤشر التلاقح المعرفي — CPI Dashboard v7.1 (ثلاثي اللغات)
# Cross-Pollination Index · Indice de Pollinisation Croisée
# د. الحبيب خروبي · ESU-001
# Streamlit app — app.py (trilingual: AR / EN / FR)
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import datetime
import cpi_db

# ── إعداد الصفحة ────────────────────────────────────────────────────
st.set_page_config(
    page_title="CPI Dashboard v7.1",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── القواميس والبيانات الأساسية ─────────────────────────────────────
DIM_KEYS = ["P", "L", "G", "EH"]

TRANSLATIONS = {
    "app_title": {"ar": "مؤشر التلاقح المعرفي", "en": "Cross-Pollination Index", "fr": "Indice de Pollinisation Croisée"},
    "app_sub": {"ar": "CPI Dashboard v7.1 · د. الحبيب خروبي · ESU-001", "en": "CPI Dashboard v7.1 · Dr. Elhabib Kherroubi · ESU-001", "fr": "Tableau de bord CPI v7.1 · Dr. Elhabib Kherroubi"},
    "tab_assess": {"ar": "📝 تقييم جلسة", "en": "📝 Assessment", "fr": "📝 Évaluation"},
    "tab_dashboard": {"ar": "📊 لوحة القيادة", "en": "📊 Dashboard", "fr": "📊 Tableau de bord"},
    "tab_history": {"ar": "🗂️ السجل", "en": "🗂️ History", "fr": "🗂️ Historique"},
    "btn_record": {"ar": "✅ تسجيل الجلسة", "en": "✅ Record Session", "fr": "✅ Enregistrer"},
    "no_data": {"ar": "لا توجد بيانات مسجلة بعد.", "en": "No data recorded yet.", "fr": "Aucune donnée enregistrée."},
}

DIMS_DATA = {
    "P":  {"color": "#2563EB", "ar": {"name": "الممارسة"}, "en": {"name": "Practice"}, "fr": {"name": "Pratique"}},
    "L":  {"color": "#059669", "ar": {"name": "اللغة المشتركة"}, "en": {"name": "Shared Language"}, "fr": {"name": "Langage commun"}},
    "G":  {"color": "#7C3AED", "ar": {"name": "التوجيه"}, "en": {"name": "Guidance"}, "fr": {"name": "Orientation"}},
    "EH": {"color": "#DC2626", "ar": {"name": "التواضع المعرفي"}, "en": {"name": "Epistemic Humility"}, "fr": {"name": "Humilité épistémique"}},
}

LEVELS = {
    "ar": [
        {"min":0,  "max":25,  "title":"الصومعة المعرفية", "color":"#DC2626"},
        {"min":25, "max":45,  "title":"العبقري المنعزل", "color":"#EA580C"},
        {"min":45, "max":60,  "title":"تعاون شكلي", "color":"#D97706"},
        {"min":60, "max":75,  "title":"تلاقح ناشئ", "color":"#2563EB"},
        {"min":75, "max":90,  "title":"ذكاء جماعي واعٍ", "color":"#059669"},
        {"min":90, "max":101, "title":"اختفاء الحدود", "color":"#7C3AED"},
    ],
    "en": [
        {"min":0,  "max":25,  "title":"Knowledge Silo", "color":"#DC2626"},
        {"min":25, "max":45,  "title":"Isolated Genius", "color":"#EA580C"},
        {"min":45, "max":60,  "title":"Formal Cooperation", "color":"#D97706"},
        {"min":60, "max":75,  "title":"Emerging Cross-Pollination", "color":"#2563EB"},
        {"min":75, "max":90,  "title":"Aware Collective Intelligence", "color":"#059669"},
        {"min":90, "max":101, "title":"Boundary Disappearance", "color":"#7C3AED"},
    ],
    "fr": [
        {"min":0,  "max":25,  "title":"Silo cognitif", "color":"#DC2626"},
        {"min":25, "max":45,  "title":"Génie isolé", "color":"#EA580C"},
        {"min":45, "max":60,  "title":"Coopération formelle", "color":"#D97706"},
        {"min":60, "max":75,  "title":"Pollinisation émergente", "color":"#2563EB"},
        {"min":75, "max":90,  "title":"Intelligence collective consciente", "color":"#059669"},
        {"min":90, "max":101, "title":"Disparition des frontières", "color":"#7C3AED"},
    ],
}

def t(key):
    lang = st.session_state.get("lang", "ar")
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("ar", key))

def get_level(cpi):
    lang = st.session_state.get("lang", "ar")
    for l in LEVELS[lang]:
        if l["min"] <= cpi < l["max"]:
            return l
    return LEVELS[lang][-1]

# ── SESSION STATE وتهيئة قاعدة البيانات ──────────────────────────────
if "lang" not in st.session_state: 
    st.session_state.lang = "ar"

# تحميل البيانات من قاعدة البيانات عند بدء التشغيل
if "sessions" not in st.session_state:
    try:
        cpi_db.init_db()
        db_sessions = cpi_db.load_historical_scores(limit=500)
        formatted_sessions = []
        for row in db_sessions:
            formatted_sessions.append({
                "id": row.get("id"),
                "label": row.get("project_name", "جلسة غير مسماة"),
                "team": row.get("team_name", "فريق غير مسمى"),
                "date": row.get("session_date", str(datetime.date.today())),
                "cpi": float(row.get("cpi_score_final", 0)),
                "alignment_index": row.get("alignment_index"),
                "scores": {
                    "EH": float(row.get("score_eh", 1)),
                    "L": float(row.get("score_l", 1)),
                    "P": float(row.get("score_p", 1)),
                    "G": float(row.get("score_g", 1))
                },
                "maturity_level": row.get("maturity_level", "مستوى غير محدد"),
                "session_number": row.get("session_number", 0)
            })
        st.session_state.sessions = formatted_sessions
    except Exception as e:
        st.session_state.sessions = []

if "scores" not in st.session_state: 
    st.session_state.scores = {k: 2 for k in DIM_KEYS}  # قيمة افتراضية 2

# ── واجهة التطبيق الرئيسية ───────────────────────────────────────────
col_head, col_lang = st.columns([5, 1])
with col_head:
    st.markdown(f"## 🧠 {t('app_title')}\n<small>{t('app_sub')}</small>", unsafe_allow_html=True)
with col_lang:
    lang_choice = st.radio("🌐", ["ar", "en", "fr"], horizontal=True, label_visibility="collapsed")
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

lang = st.session_state.lang

# ── التبويبات ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    t("tab_assess"), 
    t("tab_dashboard"), 
    f"{t('tab_history')} ({len(st.session_state.sessions)})"
])

# ════════════════════════════════════════════════════════════════════
# TAB 1: تقييم الجلسة
# ════════════════════════════════════════════════════════════════════
with tab1:
    team_name = st.text_input("🏢 اسم الفريق", value="فريق الابتكار")
    project_name = st.text_input("📋 اسم المشروع/الجلسة", value="Sprint 1")
    
    st.markdown("---")
    
    for k in DIM_KEYS:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{k}**")
        with col2:
            val = st.slider(
                f"{DIMS_DATA[k][lang]['name']}", 
                1, 4, 
                value=st.session_state.scores.get(k, 2),
                key=f"slider_{k}",
                label_visibility="collapsed"
            )
            st.session_state.scores[k] = val

    # حساب CPI
    total = sum(st.session_state.scores.values())
    cpi_now = (total / 16) * 100
    level = get_level(cpi_now)
    
    st.markdown("---")
    st.markdown(f"### 📊 CPI المحسوب: **{cpi_now:.1f}%**")
    st.markdown(f"#### 🏆 مستوى النضج: **{level['title']}**")
    st.markdown(f"<span style='color:{level['color']};background:{level['color']}20;padding:4px 12px;border-radius:20px;font-size:14px;'>{level['title']}</span>", unsafe_allow_html=True)

    if st.button(t("btn_record"), type="primary", use_container_width=True):
        try:
            # حفظ في قاعدة البيانات
            cpi_db.init_db()
            new_session_number = len(st.session_state.sessions) + 1
            
            cpi_db.save_cpi_session({
                "team_name": team_name,
                "project_name": project_name,
                "session_number": new_session_number,
                "session_date": str(datetime.date.today()),
                "score_eh": float(st.session_state.scores.get("EH", 1)),
                "score_l": float(st.session_state.scores.get("L", 1)),
                "score_p": float(st.session_state.scores.get("P", 1)),
                "score_g": float(st.session_state.scores.get("G", 1)),
                "cpi_score_final": float(cpi_now),
                "alignment_index": 100.0,
                "std_deviation": 0.0,
                "participant_count": 1,
                "maturity_level": level["title"],
                "lang": lang,
            }, signatories=[])
            
            # تحديث البيانات المحلية من قاعدة البيانات
            db_sessions = cpi_db.load_historical_scores(limit=500)
            formatted_sessions = []
            for row in db_sessions:
                formatted_sessions.append({
                    "id": row.get("id"),
                    "label": row.get("project_name", "جلسة غير مسماة"),
                    "team": row.get("team_name", "فريق غير مسمى"),
                    "date": row.get("session_date", str(datetime.date.today())),
                    "cpi": float(row.get("cpi_score_final", 0)),
                    "alignment_index": row.get("alignment_index"),
                    "scores": {
                        "EH": float(row.get("score_eh", 1)),
                        "L": float(row.get("score_l", 1)),
                        "P": float(row.get("score_p", 1)),
                        "G": float(row.get("score_g", 1))
                    },
                    "maturity_level": row.get("maturity_level", "مستوى غير محدد"),
                    "session_number": row.get("session_number", 0)
                })
            st.session_state.sessions = formatted_sessions
            
            st.success(f"✅ تم حفظ الجلسة بنجاح! (إجمالي الجلسات: {len(formatted_sessions)})")
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ فشل الحفظ في قاعدة البيانات: {e}")

# ════════════════════════════════════════════════════════════════════
# TAB 2: لوحة القيادة
# ════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.sessions:
        st.info(t("no_data"))
    else:
        last_session = st.session_state.sessions[-1]
        c_lvl = get_level(last_session["cpi"])
        
        st.markdown(f"### 📌 آخر جلسة: **{last_session['label']}** ({last_session['date']})")
        st.markdown(f"👥 فريق: **{last_session['team']}**")
        
        col_cpi, col_cai = st.columns(2)
        with col_cpi:
            st.metric("🎯 CPI الجماعي", f"{last_session['cpi']:.1f}%", delta=c_lvl["title"])
        with col_cai:
            cai_val = last_session.get('alignment_index', 100)
            delta_cai = "عالٍ" if cai_val >= 75 else ("متوسط" if cai_val >= 50 else "منخفض")
            st.metric("📐 مؤشر الانسجام (CAI)", f"{cai_val}%", delta=delta_cai)
            
        st.markdown("---")
        st.markdown("#### 📊 تفصيل الأبعاد للجلسة الأخيرة:")
        
        cols = st.columns(4)
        for i, k in enumerate(DIM_KEYS):
            with cols[i]:
                score = last_session['scores'][k]
                color = DIMS_DATA[k]["color"]
                st.markdown(f"""
                <div style='text-align:center; padding:12px; border-radius:10px; background:{color}10; border:1px solid {color}30;'>
                    <div style='font-size:11px; color:{color}; font-weight:600;'>{DIMS_DATA[k][lang]['name']}</div>
                    <div style='font-size:28px; font-weight:800; color:{color};'>{score}/4</div>
                </div>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3: السجل التاريخي
# ════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.sessions:
        st.info(t("no_data"))
    else:
        st.markdown(f"#### 📋 إجمالي الجلسات المسجلة: **{len(st.session_state.sessions)}**")
        st.markdown("---")
        
        for session in reversed(st.session_state.sessions):
            lvl = get_level(session["cpi"])
            with st.expander(f"📌 {session['label']} — {session['date']} (CPI: {session['cpi']:.1f}%)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🏢 الفريق:** {session['team']}")
                    st.markdown(f"**🏆 المستوى:** {session.get('maturity_level', lvl['title'])}")
                    st.markdown(f"**📐 الانسجام (CAI):** {session.get('alignment_index', 'غير محدد')}%")
                with col2:
                    st.markdown(f"**📊 CPI:** {session['cpi']:.1f}%")
                    st.markdown(f"**🎨 اللون:** <span style='background:{lvl['color']}; width:20px; height:20px; display:inline-block; border-radius:50%;'></span>", unsafe_allow_html=True)
                
                st.markdown("**تفصيل الأبعاد:**")
                cols = st.columns(4)
                for i, k in enumerate(DIM_KEYS):
                    with cols[i]:
                        score = session['scores'][k]
                        color = DIMS_DATA[k]["color"]
                        st.markdown(f"<div style='text-align:center;'><span style='color:{color};font-weight:800;'>{score}</span><br><span style='font-size:10px;'>{DIMS_DATA[k][lang]['name']}</span></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# Footer
# ════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center; font-size:12px; color:#94A3B8;'>"
    f"🧠 CPI Framework v7.1 · د. الحبيب خروبي · ESU-001 · {datetime.datetime.now().year}<br>"
    f"<span style='font-family:monospace;'>CI = NK × EH</span> | "
    f"<a href='https://kherroubielhabib-dr-dtviynu5d5yxbqrcicytdr.streamlit.app/' target='_blank'>التطبيق المباشر</a>"
    f"</div>",
    unsafe_allow_html=True
)
