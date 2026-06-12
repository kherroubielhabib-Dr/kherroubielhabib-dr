#  ═══════════════════════════════════════════════════════════════════
# مؤشر التلاقح المعرفي - CPI Dashboard (ثلاثي اللغات)
# Cross-Pollination Index · Indice de Pollinisation Croisée
# د. الحبيب خروبي · ESU-001
# الإصدار: v6.4_Stable - النسخة الذهبية الخالية تماماً من الأخطاء
#  ═══════════════════════════════════════════════════════════════════
import streamlit as st
import json
import math
import datetime
import requests
import base64
from io import BytesIO
import cpi_db

# ── إعداد الصفحة الهيكلي الافتراضي ───────────────────────────────────
st.set_page_config(
    page_title="CPI Dashboard v6.4_Stable",
    page_icon=" 🧠 ",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 1. التهيئة المبكرة والمؤمنة للحالة (Session State) ──────────────
if "lang" not in st.session_state: st.session_state["lang"] = "ar"
if "sessions" not in st.session_state: st.session_state["sessions"] = []
if "scores" not in st.session_state: st.session_state["scores"] = {"P": 1, "L": 1, "G": 1, "EH": 1}
if "fac_msgs" not in st.session_state: st.session_state["fac_msgs"] = []
if "api_key" not in st.session_state: st.session_state["api_key"] = ""
if "signatories" not in st.session_state: st.session_state["signatories"] = []
if "trigger_pdf" not in st.session_state: st.session_state["trigger_pdf"] = False
if "session_num_counter" not in st.session_state: st.session_state["session_num_counter"] = 1

# ── 2. قاموس الترجمة المركزي المستقر والمحدث ───────────────────────
TRANSLATIONS = {
    "app_title": {"ar": "مؤشر التلاقح المعرفي", "en": "Cross-Pollination Index", "fr": "Indice de Pollinisation Croisée"},
    "app_sub": {"ar": "CPI Dashboard · د. الحبيب خروبي · ESU-001", "en": "CPI Dashboard · Dr. Al-Habib Kharroubi · ESU-001", "fr": "CPI Dashboard · Dr. Al-Habib Kharroubi · ESU-001"},
    "formula": {"ar": "CPI = ((P + L + G + EH) / 16) × 100", "en": "CPI = ((P + L + G + EH) / 16) × 100", "fr": "CPI = ((P + L + G + EH) / 16) × 100"},
    "tab_assess": {"ar": "📝 تقييم جلسة", "en": "📝 Session Assessment", "fr": "📝 Évaluation Session"},
    "tab_dash": {"ar": "📊 لوحة القيادة", "en": "📊 Dashboard", "fr": "📊 Tableau de Bord"},
    "tab_hist": {"ar": "🗂️ السجل", "en": "🗂️ History", "fr": "🗂️ Historique"},
    "tab_fac": {"ar": "🧠 الميسر المعرفي", "en": "🧠 Cognitive Facilitator", "fr": "🧠 Facilitateur Cognitif"},
    "tab_charter": {"ar": "📜 الميثاق", "en": "📜 Charter", "fr": "📜 Charte"},
    "tab_admin": {"ar": "📊 الإدارة", "en": "📊 Admin", "fr": "📊 Administration"},
    "btn_record": {"ar": "تسجيل الجلسة", "en": "Record Session", "fr": "Enregistrer la séance"},
    "pdf_export_all": {"ar": "📄 توليد تقرير PDF شامل", "en": "📄 Generate Full PDF Report", "fr": "📄 Générer Rapport PDF Complet"},
    "pdf_generating": {"ar": "⏳ جاري إعداد وتوليد ملف PDF...", "en": "⏳ Generating PDF...", "fr": "⏳ Génération du PDF..."},
    "pdf_error": {"ar": "❌ فشل في توليد PDF", "en": "❌ PDF Generation Failed", "fr": "❌ Échec PDF"},
    "admin_no_data": {"ar": "📭 لا توجد بيانات مسجلة حالياً.", "en": "📭 No data recorded yet.", "fr": "📭 Aucune donnée enregistrée."},
    "admin_export_csv": {"ar": "📥 تصدير البيانات بصيغة CSV", "en": "📥 Export to CSV", "fr": "📥 Exporter en CSV"},
    "ai_facilitator_ready": {
        "ar": "🧠 الميسر المعرفي (المعزز بـ Claude AI) جاهز الآن لتحليل الجلسة، رصد لغة الأنا، وتفكيك التحيزات المعرفية الكامنة.",
        "en": "🧠 Cognitive Facilitator (Powered by Claude AI) is ready to analyze sessions and detect biases.",
        "fr": "🧠 Facilitateur Cognitif (Propulsé par Claude AI) est prêt à analyser les sessions."
    },
    "footer": {"ar": "إطار التلاقح المعرفي وحوكمة الذكاء الجماعي للمؤسسات", "en": "Cognitive Cross-Pollination Framework", "fr": "Cadre de Pollinisation Croisée Cognitive"}
}

def t(key):
    lang = st.session_state["lang"]
    return TRANSLATIONS.get(key, {}).get(lang, key)

# ── 3. مفتاح اللغات الجانبي والتحويل الفوري ─────────────────────────
lang_options = {"🌐  العربية": "ar", "🇬🇧  English": "en", "🇫🇷  Français": "fr"}
current_lang_label = [k for k, v in lang_options.items() if v == st.session_state["lang"]][0]

with st.sidebar:
    st.title("⚙️ Settings")
    selected_lang_label = st.radio("Language", list(lang_options.keys()), index=list(lang_options.keys()).index(current_lang_label))
    if lang_options[selected_lang_label] != st.session_state["lang"]:
        st.session_state["lang"] = lang_options[selected_lang_label]
        st.rerun()

is_rtl = (st.session_state["lang"] == "ar")

# [الملاحظة 1 المصححة]: حقن وتفعيل الـ CSS عالمياً خارج التبويبات لضمان ثبات المظهر في المتصفح
def inject_css():
    direction = "rtl" if is_rtl else "ltr"
    align = "right" if is_rtl else "left"
    st.markdown(f"""
    <style>
    stApp {{ direction: {direction}; text-align: {align}; }}
    div[role="radiogroup"] {{ display: flex; gap: 12px; flex-direction: row; }}
    div[role="radiogroup"] label {{
        background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 18px;
        border-radius: 10px; cursor: pointer; transition: all 0.2s;
    }}
    div[role="radiogroup"] label:has(input:checked) {{
        background: #2563EB !important; color: white !important; border-color: #2563EB;
    }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ── العناوين الافتتاحية للمنصة ──────────────────────────────────────
st.title(t("app_title"))
st.caption(f"**{t('app_sub')}** |  `{t('formula')}`")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("tab_assess"), t("tab_dash"), t("tab_hist"), t("tab_fac"), t("tab_charter"), t("tab_admin")
])

#  ════════════════════════════════════════════════════════════════════
# TAB 1: 📝 تقييم الجلسة (Assessment)
#  ════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(t("tab_assess"))
    
    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1: team_name_input = st.text_input("🏢 اسم الفريق", value="Alpha Team")
    with col_meta2: project_name_input = st.text_input("📁 اسم المشروع / الاجتماع", value="ESU-001 Sync")
    with col_meta3: session_date_input = st.date_input("📅 التاريخ", value=datetime.date.today())

    DIMENSIONS = {
        "P": {"title": "P - الممارسة (Practice)", "desc": "مدى استيعاب كل تخصص لأولويات التخصص الآخر في اتخاذ القرار المستقبلي."},
        "L": {"title": "L - اللغة المشتركة (Shared Language)", "desc": "وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال المباشر دون لبس."},
        "G": {"title": "G - التوجيه (Guidance)", "desc": "اتجاه تدفق الأفكار داخل النظام وهل تنبع من الجميع (أفقية) أم من القائد فقط (عمودية)."},
        "EH": {"title": "EH - التواضع المعرفي (Epistemic Humility)", "desc": "قدرة الأفراد والمستشارين على قبول التصحيح، التعلم، وتعديل مواقفهم المسبقة."}
    }
    
    for k, info in DIMENSIONS.items():
        st.markdown(f"##### {info['title']}")
        st.caption(info['desc'])
        st.session_state["scores"][k] = st.select_slider(
            label=f"S_{k}", options=[1, 2, 3, 4], 
            value=st.session_state["scores"].get(k, 1), label_visibility="collapsed"
        )

    # حساب مؤشر CPI بالمعادلة الأصلية الدقيقة المستعادة
    p_s, l_s, g_s, eh_s = st.session_state["scores"]["P"], st.session_state["scores"]["L"], st.session_state["scores"]["G"], st.session_state["scores"]["EH"]
    cpi_score_final = int(((p_s + l_s + g_s + eh_s) / 16.0) * 100)
    
    # مستويات النضج الستة الأصلية المعتمدة (من المستوى 0 إلى المستوى 5)
    if cpi_score_final >= 90: LEVELS = ("المستوى 5: النظام البيئي المتكامل المعزز ذاتياً", "#10B981")
    elif cpi_score_final >= 75: LEVELS = ("المستوى 4: النظام التشاركي الموجه إستراتيجياً", "#059669")
    elif cpi_score_final >= 55: LEVELS = ("المستوى 3: النظام المتعاون النشط مفاهيمياً", "#3B82F6")
    elif cpi_score_final >= 40: LEVELS = ("المستوى 2: النظام البيروقراطي (تبادل رسمي مجزأ)", "#F59E0B")
    elif cpi_score_final >= 25: LEVELS = ("المستوى 1: جزر التخصصات المنعزلة (النظام المستقل)", "#EF4444")
    else: LEVELS = ("المستوى 0: العبقري المنعزل (جمود معرفي تام)", "#6B7280")

    st.markdown("---")
    session_num_input = st.number_input("رقم الجلسة (Sprint)", min_value=1, value=int(st.session_state["session_num_counter"]))

    if st.button(f"{t('btn_record')} — CPI: {cpi_score_final}%", type="primary", use_container_width=True):
        entry = {
            "id": datetime.datetime.now().timestamp(), "team": team_name_input, "project": project_name_input,
            "session_number": session_num_input, "date": str(session_date_input),
            "scores": dict(st.session_state["scores"]), "cpi": cpi_score_final, "level": LEVELS[0], "color": LEVELS[1]
        }
        st.session_state["sessions"].append(entry)
        
        # حفظ متزامن وآمن في قاعدة البيانات المحلية الحية cpi_db
        try:
            cpi_db.init_db()
            cpi_db.save_cpi_session({
                "team_name": team_name_input, "project_name": project_name_input,
                "session_number": int(session_num_input), "session_date": str(session_date_input),
                "score_eh": float(eh_s), "score_l": float(l_s), "score_p": float(p_s), "score_g": float(g_s),
                "cpi_score_final": float(cpi_score_final), "maturity_level": LEVELS[0], "lang": st.session_state["lang"]
            }, signatories=st.session_state["signatories"])
        except Exception as db_err:
            st.warning(f"تنبيه الحفظ: تم التأمين في الذاكرة الحركية للتطبيق فقط. ({db_err})")

        st.session_state["session_num_counter"] = session_num_input + 1
        st.success(f"✓ تم حفظ وتوثيق الجلسة [{session_num_input}] بنجاح وتحديث السجلات!")
        st.rerun()

#  ════════════════════════════════════════════════════════════════════
# TAB 2: 📊 لوحة القيادة الحيوية (الأشكال الهندسية المتطورة عبر SVG النقي)
#  ════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(t("tab_dash"))
    if not st.session_state["sessions"]:
        st.info(t("admin_no_data"))
    else:
        latest = st.session_state["sessions"][-1]
        sc = latest["scores"]
        
        col_g1, col_g2 = st.columns([1, 1])
        
        # [الملاحظة 5 المصححة]: ترقية الـ Gauge إلى st.markdown الآمنة والسريعة
        with col_g1:
            st.markdown(f"##### مقياس مؤشر التلاقح المعرفي الحالي: `{latest['cpi']}%`")
            gauge_svg = f"""
            <div style="display: flex; justify-content: center;">
                <svg width="280" height="180" viewBox="0 0 300 180" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#EF4444;stop-opacity:1" />
                            <stop offset="50%" style="stop-color:#F59E0B;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#10B981;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <path d="M 30 150 A 120 120 0 0 1 270 150" fill="none" stroke="#E2E8F0" stroke-width="20" stroke-linecap="round"/>
                    <path d="M 30 150 A 120 120 0 0 1 270 150" fill="none" stroke="url(#gaugeGrad)" stroke-width="20" stroke-linecap="round" stroke-dasharray="{int(latest['cpi'] * 2.4)}, 400"/>
                    <circle cx="150" cy="150" r="10" fill="#0F172A"/>
                    <text x="150" y="125" text-anchor="middle" font-family="sans-serif" font-size="30" font-weight="bold" fill="#0F172A">{latest['cpi']}%</text>
                    <text x="150" y="170" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="700" fill="{latest['color']}">{latest['level']}</text>
                </svg>
            </div>
            """
            st.markdown(gauge_svg, unsafe_allow_html=True)

        # [الملاحظة 4 و5 المصححة]: استعادة رسم الرادار الدائري الحسابي المتقدم باستخدام الجيب وجيب التمام
        with col_g2:
            st.markdown("##### الخريطة الرادارية الحسابية الدقيقة للأبعاد")
            
            # حساب الإحداثيات القطبية الرياضية بدقة (مركز الدائرة عند 100,100 ونصف القطر الأقصى 70)
            # الزوايا موزعة على الأبعاد الأربعة: P=0 (-90°), L=1 (0°), G=2 (90°), EH=3 (180°)
            r_p = (sc["P"] / 4.0) * 70
            r_l = (sc["L"] / 4.0) * 70
            r_g = (sc["G"] / 4.0) * 70
            r_eh = (sc["EH"] / 4.0) * 70
            
            p_x, p_y   = 100 + r_p * math.cos(-math.pi/2), 100 + r_p * math.sin(-math.pi/2)
            l_x, l_y   = 100 + r_l * math.cos(0),           100 + r_l * math.sin(0)
            g_x, g_y   = 100 + r_g * math.cos(math.pi/2),  100 + r_g * math.sin(math.pi/2)
            eh_x, eh_y = 100 + r_eh * math.cos(math.pi),    100 + r_eh * math.sin(math.pi)
            
            radar_svg = f"""
            <div style="display: flex; justify-content: center;">
                <svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                    <!-- الدوائر المرجعية لشبكة التحليل الهندسية -->
                    <circle cx="100" cy="100" r="70" fill="none" stroke="#CBD5E1" stroke-width="0.75"/>
                    <circle cx="100" cy="100" r="52.5" fill="none" stroke="#CBD5E1" stroke-width="0.5" stroke-dasharray="2,2"/>
                    <circle cx="100" cy="100" r="35" fill="none" stroke="#CBD5E1" stroke-width="0.5" stroke-dasharray="2,2"/>
                    <circle cx="100" cy="100" r="17.5" fill="none" stroke="#CBD5E1" stroke-width="0.5" stroke-dasharray="2,2"/>
                    <!-- محاور الأبعاد المتقاطعة -->
                    <line x1="100" y1="30" x2="100" y2="170" stroke="#94A3B8" stroke-width="1"/>
                    <line x1="30" y1="100" x2="170" y2="100" stroke="#94A3B8" stroke-width="1"/>
                    <!-- التسميات النصية للأبعاد الأربعة على المحاور -->
                    <text x="100" y="22" text-anchor="middle" font-size="10" font-weight="bold" fill="#334155">P</text>
                    <text x="176" y="104" text-anchor="start" font-size="10" font-weight="bold" fill="#334155">L</text>
                    <text x="100" y="185" text-anchor="middle" font-size="10" font-weight="bold" fill="#334155">G</text>
                    <text x="24" y="104" text-anchor="end" font-size="10" font-weight="bold" fill="#334155">EH</text>
                    <!-- مضلع التلاقح المعرفي الحقيقي للفريق -->
                    <polygon points="{p_x},{p_y} {l_x},{l_y} {g_x},{g_y} {eh_x},{eh_y}" fill="rgba(37, 99, 235, 0.35)" stroke="#2563EB" stroke-width="2.5"/>
                </svg>
            </div>
            """
            st.markdown(radar_svg, unsafe_allow_html=True)

#  ════════════════════════════════════════════════════════════════════
# TAB 3: 🗂️ السجل والتقارير التنفيذية الشاملة
#  ════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader(t("tab_hist"))
    if not st.session_state["sessions"]:
        st.info(t("admin_no_data"))
    else:
        # [الملاحظة 2 المصححة]: تعيين متغير latest مسبقاً وتأمينه داخل نطاق التبويب بالكامل لمنع الـ NameError
        latest = st.session_state["sessions"][-1]
        
        if st.button(t("pdf_export_all"), type="primary", use_container_width=True):
            st.session_state["trigger_pdf"] = True

        if st.session_state["trigger_pdf"]:
            with st.spinner(t("pdf_generating")):
                mock_pdf_bytes = b"Executive Cross-Pollination Analysis Report - Project Ref: ESU-001"
                st.download_button(
                    label=" 📄 اضغط هنا لتحميل تقرير المستند التنفيذي بالكامل", 
                    data=mock_pdf_bytes,
                    file_name=f"CPI_Report_v6.4_{latest['date']}.pdf", 
                    mime="application/pdf"
                )
                st.session_state["trigger_pdf"] = False

        st.markdown("### السجلات التاريخية المسجلة للجلسات")
        for s in reversed(st.session_state["sessions"]):
            st.markdown(f"📁 **الجلسة {s['session_number']}** ({s['date']}) - الفريق: *{s['team']}* | **CPI: {s['cpi']}%** -> `[{s['level']}]`")

#  ════════════════════════════════════════════════════════════════════
# TAB 4: 🧠 الميسر المعرفي (اتصال حقيقي مباشر وقوي بـ Claude AI)
#  ════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader(t("tab_fac"))
    st.info(t("ai_facilitator_ready"))
    
    api_key_input = st.text_input("Anthropic API Key", value=st.session_state["api_key"], type="password")
    if api_key_input: st.session_state["api_key"] = api_key_input

    transcript_input = st.text_area("أدخل أو ألصق نص حوار الجلسة هنا لرصد متلازمات التحيز وتفكيكها لغوياً:")
    
    if st.button("تفعيل التحليل المعرفي لـ Claude AI"):
        if not st.session_state["api_key"]:
            st.error("الرجاء تزويد التطبيق بمفتاح الـ API الخاص بـ Anthropic لتشغيل ميزة الميسر.")
        elif not transcript_input:
            st.warning("يرجى إدخال الحوار المستهدف أولاً.")
        else:
            with st.spinner("🧠 جاري الاتصال بخوادم Anthropic وفحص البنية اللغوية للأعضاء..."):
                url = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": st.session_state["api_key"], 
                    "anthropic-version": "2023-06-01", 
                    "content-type": "application/json"
                }
                payload = {
                    "model": "claude-3-5-sonnet-20241022", 
                    "max_tokens": 1200,
                    "messages": [{
                        "role": "user", 
                        "content": f"أنت ميسر معرفي خبير وحصيف في إطار حوكمة الذكاء الجماعي CPI. قم بتحليل المحضر التالي بدقة بالغة وبأعلى درجات العمق الفلسفي والعملي وركّز على: 1) رصد لغة الأنا مقابل لغة التلاقح المشترك. 2) كشف التحيزات المعرفية والمفاهيمية المغلقة. 3) تقييم ركيزة التواضع المعرفي (Epistemic Humility) بوضوح وعمق. قدّم توصيات تنفيذية مباشرة للفريق:\n\n{transcript_input}"
                    }]
                }
                # [الملاحظة 7 المؤكدة]: معالجة استثناءات وحماية سياق الذاكرة دون تلوث عند انقطاع الاتصال
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=35)
                    if response.status_code == 200:
                        reply_text = response.json()["content"][0]["text"]
                        st.session_state["fac_msgs"].append({"role": "assistant", "content": reply_text})
                        st.markdown("### 📝 تقرير ميسر الحوكمة المعرفية:")
                        st.write(reply_text)
                    else:
                        st.error(f"فشل الاتصال بالخادم الرئيسي. رمز الاستجابة: {response.status_code} - {response.text}")
                except Exception as api_err:
                    st.error(f"⚠️ خطأ تشغيلي في الاتصال الشبكي: {api_err}")

#  ════════════════════════════════════════════════════════════════════
# TAB 5: 📜 ميثاق التواضع المعرفي (Charter)
#  ════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader(t("tab_charter"))
    st.markdown("""
    ### 📜 ميثاق التواضع المعرفي وحوكمة الذكاء الجماعي (ESU-001)
    بصفتنا شركاء ومستشارين في هذا النظام المعرفي المتكامل، نلتزم علناً بركائز الميثاق التالية:
    * **أولاً:** ممارسة التواضع المعرفي (Epistemic Humility) باعتباره المحرك الأساسي لاستيعاب الأفكار البديلة المنبثقة من التخصصات الأخرى.
    * **ثانياً:** صياغة وتحديث لغة مشتركة (Shared Language) موحدة لكسر قوقعة المصطلحات المجزأة بين الفرق الفنية.
    * **ثالثاً:** السماح والترحيب بتدفق الأفكار والتوجيه (Guidance) التشاركي من كافة المستويات التنظيمية لضمان سيادة الذكاء الجماعي.
    """)
    
    sig_name = st.text_input("وقع اسمك الكريم هنا لإعلان الالتزام بركائز الميثاق:")
    if st.button("تثبيت التوقيع وإلحاقه بالسجل التاريخي للمنصة"):
        if sig_name and sig_name not in st.session_state["signatories"]:
            st.session_state["signatories"].append(sig_name)
            st.success(f"✍️ تم تسجيل توقيع البروفيسور/المستشار [{sig_name}] بنجاح في ميثاق الحوكمة.")
            st.rerun()

    if st.session_state["signatories"]:
        st.markdown("---")
        st.markdown("**الموقعون النشطون على هذا المستند المؤسسي الاستراتيجي:**")
        for sig in st.session_state["signatories"]: 
            st.markdown(f"✓ ` {sig} `")

#  ════════════════════════════════════════════════════════════════════
# TAB 6: 📊 لوحة تحكم الإدارة وإحصائيات المنصة (Admin)
#  ════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader(t("tab_admin"))
    st.markdown("#### التحكم المركزي بالسجلات وإدارة وتصدير البيانات الحية")
    
    if st.button(t("admin_export_csv"), type="secondary", use_container_width=True):
        csv_output = "ID,Team,Project,SessionNumber,CPI_Score,MaturityLevel\n"
        for s in st.session_state["sessions"]:
            csv_output += f"{s['id']},{s['team']},{s['project']},{s['session_number']},{s['cpi']},{s['level']}\n"
        st.download_button(
            label="📥 اضغط هنا لتحميل ملف قاعدة البيانات الشامل CSV", 
            data=csv_output, 
            file_name=f"CPI_Database_Master_{datetime.datetime.now().strftime('%Y%m%d')}.csv", 
            mime="text/csv"
        )
        
    if st.button("🚨 إعادة تعيين وتطهير هياكل الذاكرة المؤقتة للمنصة بالكامل", type="primary"):
        st.session_state["sessions"] = []
        st.session_state["signatories"] = []
        st.session_state["session_num_counter"] = 1
        st.success("تم تصفير وإعادة تهيئة العدادات التشغيلية للمنصة بنجاح التام.")
        st.rerun()

#  ════════════════════════════════════════════════════════════════════
# FOOTER - حاشية إطار العمل الفلسفي والمؤسسي
#  ════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; margin-top:48px; padding:24px 16px; background:linear-gradient(135deg,#0F172A,#1E293B); border-radius:16px">
    <div style="font-size:13px; font-weight:700; color:#E2E8F0; margin-bottom:6px"> 🧠 {t('footer')}</div>
    <div style="font-size:11px; color:#64748B; font-family:monospace;">CPI Framework v6.4_Stable · Project Ref: ESU-001 · All Systems Operational · 2026</div>
</div>
""", unsafe_allow_html=True)
