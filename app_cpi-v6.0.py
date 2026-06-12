# مؤشر التلاقح المعرفي - CPI Dashboard (ثلاثي اللغات)
# Cross-Pollination Index · Indice de Pollinisation Croisée
# د. الحبيب خروبي · ESU-001
# Streamlit app - app.py (trilingual: AR / EN / FR)
# الإصدار: v6.1-fixed - النسخة المستقرة النهائية

import streamlit as st
import json
import math
import datetime
import requests
import base64
from io import BytesIO
import subprocess
import tempfile
import os
import cpi_db

# ----------------------------------------------------------------------
# اعداد الصفحة
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="CPI Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------
# TRANSLATIONS - قاموس الترجمة المركزي
# ----------------------------------------------------------------------
TRANSLATIONS = {
    "app_title": {
        "ar": "مؤشر التلاقح المعرفي",
        "en": "Cross-Pollination Index",
        "fr": "Indice de Pollinisation Croisée",
    },
    "app_sub": {
        "ar": "CPI Dashboard · د. الحبيب خروبي · ESU-001",
        "en": "CPI Dashboard · Dr. Elhabib Kherroubi · ESU-001",
        "fr": "Tableau de bord CPI · Dr. Elhabib Kherroubi · ESU-001",
    },
    "formula_label": {
        "ar": "CI = NK × EH",
        "en": "CI = NK × EH",
        "fr": "IC = SC × HE",
    },
    "tab_assess": {
        "ar": "📝 تقييم جلسة",
        "en": "📝 Session Assessment",
        "fr": "📝 Evaluation de seance",
    },
    "tab_dashboard": {
        "ar": "📊 لوحة القيادة",
        "en": "📊 Dashboard",
        "fr": "📊 Tableau de bord",
    },
    "tab_history": {
        "ar": "🗂️ السجل",
        "en": "🗂️ History",
        "fr": "🗂️ Historique",
    },
    "tab_facilitator": {
        "ar": "🧠 الميسر المعرفي",
        "en": "🧠 Cognitive Facilitator",
        "fr": "🧠 Facilitateur Cognitif",
    },
    "tab_charter": {
        "ar": "📜 الميثاق",
        "en": "📜 Charter",
        "fr": "📜 Charte",
    },
    "tab_admin": {
        "ar": "📊 الإدارة",
        "en": "📊 Admin",
        "fr": "📊 Administration",
    },
    "charter_title": {
        "ar": "ميثاق التلاقح المعرفي",
        "en": "Cognitive Cross-Pollination Charter",
        "fr": "Charte de Pollinisation Croisée Cognitive",
    },
    "charter_version": {
        "ar": "الإصدار 1.1 · د. الحبيب خروبي · ESU-001 · جوان 2026",
        "en": "v1.1 · Dr. Elhabib Kherroubi · ESU-001 · June 2026",
        "fr": "v1.1 · Dr. Elhabib Kherroubi · ESU-001 · Juin 2026",
    },
    "charter_preamble": {
        "ar": "انطلاقاً من أن الابتكار الحقيقي لا ينتج عن تجميع المعارف الفردية بصورة منفصلة، بل عن التفاعل المنهجي بينها وتحويل الاختلافات المعرفية إلى طاقة إبداعية مشتركة - نعتمد هذا الميثاق عقداً معرفياً وأخلاقياً وتشغيلياً لفريقنا.",
        "en": "True innovation in cross-disciplinary teams does not arise from aggregating knowledge separately, but from its systematic interaction - transforming cognitive differences into shared creative energy.",
        "fr": "La véritable innovation ne provient pas de l'agrégation des connaissances individuelles, mais de leur interaction systématique.",
    },
    "charter_axiom": {
        "ar": "التواضع المعرفي ليس مجرد فضيلة أخلاقية، بل بنية تشغيلية لازمة لظهور الذكاء الجماعي.",
        "en": "Epistemic humility is not merely an ethical virtue - it is an operational structure necessary for collective intelligence to emerge.",
        "fr": "L'humilité épistémique n'est pas seulement une vertu éthique - c'est une structure opérationnelle nécessaire à l'émergence de l'intelligence collective.",
    },
    "charter_sign_title": {
        "ar": "التوقيع على الميثاق",
        "en": "Sign the Charter",
        "fr": "Signer la Charte",
    },
    "charter_sign_ph": {
        "ar": "اسمك الكامل",
        "en": "Your full name",
        "fr": "Votre nom complet",
    },
    "charter_sign_btn": {
        "ar": "✍️ أوقّع",
        "en": "✍️ Sign",
        "fr": "✍️ Signer",
    },
    "charter_signed_msg": {
        "ar": "التزامك مُسجَّل - يمكنك الانتقال إلى تقييم الجلسة.",
        "en": "Commitment recorded - proceed to the session assessment.",
        "fr": "Engagement enregistré - passez à l'évaluation de séance.",
    },
    "charter_signatories": {
        "ar": "الموقّعون في هذه الجلسة",
        "en": "Signatories in this session",
        "fr": "Signataires de cette séance",
    },
    "charter_clear": {
        "ar": "🗑️ مسح التوقيعات",
        "en": "🗑️ Clear signatures",
        "fr": "🗑️ Effacer les signatures",
    },
    "admin_stats_title": {
        "ar": "إحصائيات المنصة",
        "en": "Platform Statistics",
        "fr": "Statistiques de la plateforme",
    },
    "admin_total_sessions": {
        "ar": "إجمالي الجلسات",
        "en": "Total Sessions",
        "fr": "Total des séances",
    },
    "admin_avg_cpi": {
        "ar": "متوسط CPI",
        "en": "Average CPI",
        "fr": "CPI moyen",
    },
    "admin_total_teams": {
        "ar": "إجمالي الفرق",
        "en": "Total Teams",
        "fr": "Total des équipes",
    },
    "admin_teams_title": {
        "ar": "الفرق المسجّلة",
        "en": "Registered Teams",
        "fr": "Équipes enregistrées",
    },
    "admin_export_csv": {
        "ar": "📥 تصدير كامل CSV",
        "en": "📥 Export Full CSV",
        "fr": "📥 Exporter CSV complet",
    },
    "admin_no_data": {
        "ar": "لا توجد بيانات في قاعدة البيانات بعد.",
        "en": "No data in the database yet.",
        "fr": "Aucune donnée dans la base de données.",
    },
    "pdf_export_all": {
        "ar": "📥 تحميل تقرير PDF - كامل السجل",
        "en": "📥 Download PDF Report - Full History",
        "fr": "📥 Télécharger rapport PDF - Historique complet",
    },
    "pdf_generating": {
        "ar": "⏳ جاري توليد PDF...",
        "en": "⏳ Generating PDF...",
        "fr": "⏳ Génération du PDF...",
    },
    "pdf_error": {
        "ar": "⚠️ تعذّر توليد PDF.",
        "en": "⚠️ Could not generate PDF.",
        "fr": "⚠️ Impossible de générer le PDF.",
    },
    "assess_intro": {
        "ar": "قيّم الأبعاد الأربعة بعد كل Sprint أو اجتماع حاسم.",
        "en": "Rate the four dimensions after each Sprint or key meeting.",
        "fr": "Évaluez les quatre dimensions après chaque Sprint ou réunion clé.",
    },
    "scale_hint": {
        "ar": "1 = ضعيف · 2 = مقبول · 3 = جيد · 4 = متقدم (اختفاء الحدود)",
        "en": "1 = Weak · 2 = Acceptable · 3 = Good · 4 = Advanced",
        "fr": "1 = Faible · 2 = Acceptable · 3 = Bien · 4 = Avancé",
    },
    "score_labels": {
        "ar": {1: "ضعيف", 2: "مقبول", 3: "جيد", 4: "متقدم"},
        "en": {1: "Weak", 2: "Acceptable", 3: "Good", 4: "Advanced"},
        "fr": {1: "Faible", 2: "Acceptable", 3: "Bien", 4: "Avancé"},
    },
    "cpi_computed": {
        "ar": "CPI المحسوب",
        "en": "Computed CPI",
        "fr": "CPI calculé",
    },
    "btn_record": {
        "ar": "✅ تسجيل الجلسة",
        "en": "✅ Record Session",
        "fr": "✅ Enregistrer la séance",
    },
    "complete_all": {
        "ar": "أكمل تقييم الأبعاد الأربعة لحساب CPI",
        "en": "Complete all four dimensions to compute CPI",
        "fr": "Complétez les quatre dimensions pour calculer le CPI",
    },
    "last_cpi": {
        "ar": "آخر CPI مسجّل",
        "en": "Latest recorded CPI",
        "fr": "Dernier CPI enregistré",
    },
    "dim_detail": {
        "ar": "تفصيل الأبعاد - آخر جلسة",
        "en": "Dimension breakdown - latest session",
        "fr": "Détail des dimensions - dernière séance",
    },
    "bdi_title": {
        "ar": "مؤشر اختفاء الحدود (BDI)",
        "en": "Boundary Disappearance Index (BDI)",
        "fr": "Indice de disparition des frontières (IDF)",
    },
    "bdi_sub": {
        "ar": "كلما اقترب من 100% كلما اقترب الفريق من العقل الجماعي الحقيقي",
        "en": "The closer to 100%, the closer the team is to genuine collective intelligence",
        "fr": "Plus proche de 100%, plus l'équipe approche l'intelligence collective réelle",
    },
    "trend_title": {
        "ar": "مسار CPI عبر الزمن",
        "en": "CPI trend over time",
        "fr": "Évolution du CPI dans le temps",
    },
    "sessions_recorded": {
        "ar": "جلسة مسجّلة",
        "en": "sessions recorded",
        "fr": "séances enregistrées",
    },
    "recs_title": {
        "ar": "توصيات التحسين",
        "en": "Improvement recommendations",
        "fr": "Recommandations d'amélioration",
    },
    "recs_all_good": {
        "ar": "✓ جميع الأبعاد في مستوى جيد. استمر في المسار الحالي.",
        "en": "✓ All dimensions are at a good level. Keep up the current path.",
        "fr": "✓ Toutes les dimensions sont à un bon niveau. Continuez sur cette lancée.",
    },
    "no_data": {
        "ar": "لا توجد بيانات بعد - سجّل أول جلسة من تبويب التقييم",
        "en": "No data yet - record your first session in the Assessment tab",
        "fr": "Aucune donnée - enregistrez votre première séance dans l'onglet Évaluation",
    },
    "no_sessions": {
        "ar": "لا توجد جلسات مسجّلة بعد",
        "en": "No sessions recorded yet",
        "fr": "Aucune séance enregistrée",
    },
    "delete_all": {
        "ar": "🗑️ حذف الكل",
        "en": "🗑️ Delete all",
        "fr": "🗑️ Tout supprimer",
    },
    "fac_sub": {
        "ar": "طرف ثالث محايد. يحلل لغة الفريق ويكشف التحيزات المعرفية.",
        "en": "A neutral third party. Analyses team language and reveals cognitive biases.",
        "fr": "Un tiers neutre. Analyse le langage de l'équipe et révèle les biais cognitifs.",
    },
    "api_key_label": {
        "ar": "🔑 مفتاح Anthropic API",
        "en": "🔑 Anthropic API Key",
        "fr": "🔑 Clé Anthropic API",
    },
    "api_key_ph": {
        "ar": "sk-ant-...",
        "en": "sk-ant-...",
        "fr": "sk-ant-...",
    },
    "fac_mode_label": {
        "ar": "وظيفة الميسر:",
        "en": "Facilitator mode:",
        "fr": "Mode du facilitateur :",
    },
    "send_btn": {
        "ar": "📤 إرسال للميسر",
        "en": "📤 Send to facilitator",
        "fr": "📤 Envoyer au facilitateur",
    },
    "clear_btn": {
        "ar": "🗑️ مسح",
        "en": "🗑️ Clear",
        "fr": "🗑️ Effacer",
    },
    "fac_thinking": {
        "ar": "🧠 الميسر يحلل...",
        "en": "🧠 Facilitator analysing...",
        "fr": "🧠 Le facilitateur analyse...",
    },
    "error_no_key": {
        "ar": "أدخل مفتاح Anthropic API أولاً.",
        "en": "Please enter your Anthropic API key first.",
        "fr": "Veuillez d'abord saisir votre clé Anthropic API.",
    },
    "error_no_input": {
        "ar": "اكتب رسالتك أولاً.",
        "en": "Please write your message first.",
        "fr": "Veuillez d'abord écrire votre message.",
    },
    "footer": {
        "ar": "CPI - مؤشر التلاقح المعرفي · د. الحبيب خروبي · ESU-001",
        "en": "CPI - Cross-Pollination Index · Dr. Elhabib Kherroubi · ESU-001",
        "fr": "CPI - Indice de Pollinisation Croisée · Dr. Elhabib Kherroubi · ESU-001",
    },
    "ai_facilitator_ready": {
        "ar": "🧠 الميسر المعرفي (المعزز بـ Claude AI) جاهز للتحليل.",
        "en": "🧠 Cognitive Facilitator (Powered by Claude AI) is ready.",
        "fr": "🧠 Facilitateur Cognitif (Propulsé par Claude AI) prêt.",
    },
}

def t(key):
    lang = st.session_state.get("lang", "ar")
    entry = TRANSLATIONS.get(key, {})
    if isinstance(entry, dict):
        return entry.get(lang, entry.get("ar", key))
    return entry

# ----------------------------------------------------------------------
# مفتاح اللغات الجانبي
# ----------------------------------------------------------------------
lang_options = {"🌐 العربية": "ar", "🇬🇧 English": "en", "🇫🇷 Français": "fr"}
current_lang_label = [k for k, v in lang_options.items() if v == st.session_state.get("lang", "ar")][0]

with st.sidebar:
    st.title("⚙️ Settings")
    selected_lang_label = st.radio("Language", list(lang_options.keys()), index=list(lang_options.keys()).index(current_lang_label))
    if lang_options[selected_lang_label] != st.session_state.get("lang", "ar"):
        st.session_state["lang"] = lang_options[selected_lang_label]
        st.rerun()

is_rtl = (st.session_state.get("lang", "ar") == "ar")
lang = st.session_state.get("lang", "ar")

# ----------------------------------------------------------------------
# CSS الشامل
# ----------------------------------------------------------------------
def inject_css(lang):
    direction = "rtl" if lang == "ar" else "ltr"
    text_align = "right" if lang == "ar" else "left"
    ml = "left" if lang == "ar" else "right"
    mr = "right" if lang == "ar" else "left"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans Arabic', 'IBM Plex Sans', 'Segoe UI', sans-serif !important;
        direction: {direction};
        background: #F8FAFC;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    div[role="radiogroup"] {{ display: flex !important; flex-direction: row !important; gap: 8px !important; }}
    div[role="radiogroup"] label {{
        flex: 1 !important; border: 1.5px solid #E2E8F0 !important; border-radius: 10px !important;
        padding: 10px 6px !important; text-align: center !important; cursor: pointer !important;
        font-size: 13px !important; font-weight: 600 !important; background: white !important;
        transition: all 0.2s ease !important;
    }}
    div[role="radiogroup"] label:has(input:checked) {{
        background: linear-gradient(135deg, #EFF6FF, #E0ECFF) !important;
        border-color: #2563EB !important; color: #1D4ED8 !important;
    }}
    .cpi-header {{
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white;
        padding: 20px 28px 16px; border-radius: 16px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }}
    .cpi-header h1 {{ font-size: 20px; font-weight: 800; margin: 0; }}
    .cpi-formula {{
        background: #1E3A5F; border-radius: 10px; padding: 8px 18px;
        font-size: 13px; color: #7DD3FC; font-weight: 700; font-family: monospace;
    }}
    .cpi-card {{
        background: white; border: 1px solid #E8EDF5; border-radius: 14px;
        padding: 20px 22px; margin-bottom: 16px;
    }}
    .gauge-wrap, .radar-wrap {{
        background: #F0F7FF; border: 1px solid #BFDBFE; border-radius: 14px;
        padding: 22px 16px 16px; text-align: center;
    }}
    .radar-wrap {{ background: white; border-color: #E8EDF5; padding: 12px 0; }}
    .prog-wrap {{ height: 8px; background: #F1F5F9; border-radius: 100px; overflow: hidden; margin-top: 5px; }}
    .prog-bar {{ height: 100%; border-radius: 100px; transition: width 0.6s; }}
    .session-card {{
        background: white; border: 1px solid #E8EDF5; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 12px;
    }}
    .session-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }}
    .session-name {{ font-weight: 700; font-size: 15px; }}
    .session-date {{ font-size: 11px; color: #94A3B8; }}
    .session-cpi {{ font-size: 22px; font-weight: 800; font-family: monospace; padding: 5px 14px; border-radius: 10px; }}
    .dim-tag {{
        display: inline-block; background: #F8FAFC; border: 1px solid #E2E8F0;
        border-radius: 8px; padding: 3px 10px; font-size: 11px; font-weight: 600;
        margin-{ml}: 6px; margin-bottom: 5px;
    }}
    .msg-user {{
        background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white;
        border-radius: {"12px 12px 4px 12px" if direction=="rtl" else "12px 12px 12px 4px"};
        padding: 12px 16px; font-size: 13px; margin-bottom: 12px; max-width: 88%;
        margin-{"right" if direction=="rtl" else "left"}: auto;
    }}
    .msg-ai {{
        background: white; color: #111827; border: 1px solid #E8EDF5;
        border-radius: {"12px 12px 12px 4px" if direction=="rtl" else "4px 12px 12px 12px"};
        padding: 12px 16px; font-size: 13px; margin-bottom: 12px; max-width: 88%;
    }}
    .level-0 {{ background: #FEF2F2; color: #DC2626; border: 1.5px solid #FECACA; }}
    .level-1 {{ background: #FFF7ED; color: #EA580C; border: 1.5px solid #FED7AA; }}
    .level-2 {{ background: #FFFBEB; color: #D97706; border: 1.5px solid #FDE68A; }}
    .level-3 {{ background: #EFF6FF; color: #2563EB; border: 1.5px solid #BFDBFE; }}
    .level-4 {{ background: #F0FDF4; color: #059669; border: 1.5px solid #A7F3D0; }}
    .level-5 {{ background: #F5F3FF; color: #7C3AED; border: 1.5px solid #DDD6FE; }}
    </style>
    """, unsafe_allow_html=True)

inject_css(lang)

# ----------------------------------------------------------------------
# العناوين الافتتاحية
# ----------------------------------------------------------------------
st.title(t("app_title"))
st.caption(f"**{t('app_sub')}** | `{t('formula_label')}`")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("tab_assess"), t("tab_dashboard"), f"{t('tab_history')} ({len(st.session_state.get('sessions', []))})",
    t("tab_facilitator"), t("tab_charter"), t("tab_admin")
])

# ----------------------------------------------------------------------
# اعدادات البيانات والرسوميات
# ----------------------------------------------------------------------
DIMS_DATA = {
    "P": {"color": "#2563EB", "ar": {"name": "الممارسة", "desc": "مدى استيعاب كل تخصص لأولويات التخصص الآخر", "q": "هل فهمنا أولويات بعضنا في القرارات?"}},
    "L": {"color": "#059669", "ar": {"name": "اللغة المشتركة", "desc": "وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال", "q": "هل تحدثنا بلغة مشتركة دون سوء فهم؟"}},
    "G": {"color": "#7C3AED", "ar": {"name": "التوجيه", "desc": "اتجاه تدفق الأفكار داخل النظام", "q": "هل تدفقت الأفكار من الجميع (وليس فقط من القائد)؟"}},
    "EH": {"color": "#DC2626", "ar": {"name": "التواضع المعرفي", "desc": "قدرة الأفراد على قبول التصحيح والتعلم من الآخرين", "q": "هل استمعنا لبعضنا بتواضع وغيرنا مواقفنا؟"}}
}
DIM_KEYS = ["P", "L", "G", "EH"]

LEVELS = {
    "ar": [
        {"min":0, "max":25, "cls":"level-0", "title":"الصومعة المعرفية", "color":"#DC2626"},
        {"min":25, "max":45, "cls":"level-1", "title":"العبقري المنعزل", "color":"#EA580C"},
        {"min":45, "max":60, "cls":"level-2", "title":"تعاون شكلي", "color":"#D97706"},
        {"min":60, "max":75, "cls":"level-3", "title":"تلاقح ناشئ", "color":"#2563EB"},
        {"min":75, "max":90, "cls":"level-4", "title":"ذكاء جماعي واعٍ", "color":"#059669"},
        {"min":90, "max":101, "cls":"level-5", "title":"اختفاء الحدود", "color":"#7C3AED"},
    ],
}

RECS = {
    "P": {"ar": ("الممارسة", "#2563EB", "جلسات تظليل وظيفي اسبوعية - يظلل كل تخصص الآخر.")},
    "L": {"ar": ("اللغة المشتركة", "#059669", "ورشة قاموس مشترك - يوم واحد + تحديثات اسبوعية.")},
    "G": {"ar": ("التوجيه", "#7C3AED", "إلغاء الموافقات الهرمية على الاقتراحات الصغيرة.")},
    "EH": {"ar": ("التواضع المعرفي", "#DC2626", "جلسات مراجعة عمياء - تقييم الأفكار دون معرفة صاحبها.")},
}

def get_level(cpi):
    for l in LEVELS["ar"]:
        if l["min"] <= cpi < l["max"]:
            return l
    return LEVELS["ar"][-1]

def calc_cpi(scores):
    vals = [v for v in scores.values() if v > 0]
    if len(vals) < 4:
        return None
    return round(sum(vals) / 16 * 100)

def calc_bdi(sessions):
    if len(sessions) < 2:
        return None
    last = sessions[-1]["scores"]
    vals = [last[k] for k in DIM_KEYS]
    mean = sum(vals) / 4
    variance = sum((v - mean) ** 2 for v in vals) / 4
    return round((1 - variance / 2.25) * 100)

RADAR_RING_COLORS = ["#F3F4F6", "#E9EBF5", "#D4D9F0", "#BFC6EA"]

def radar_svg(scores, size=280):
    pad = 52
    cx = cy = size / 2
    r = (size / 2) - pad
    n = len(DIM_KEYS)
    colors = [DIMS_DATA[k]["color"] for k in DIM_KEYS]
    def angle(i): return math.pi * 2 * i / n - math.pi / 2
    def pt(i, val):
        a = angle(i); d = (val / 4) * r
        return cx + d * math.cos(a), cy + d * math.sin(a)
    def ring_pts(v):
        pts = []
        for i in range(n):
            a = angle(i); d = (v / 4) * r
            pts.append(f"{cx + d*math.cos(a):.1f},{cy + d*math.sin(a):.1f}")
        return " ".join(pts)
    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">']
    for idx, v in enumerate([4, 3, 2, 1]):
        fill = RADAR_RING_COLORS[idx]
        svg.append(f'<polygon points="{ring_pts(v)}" fill="{fill}" stroke="#D1D5DB" stroke-width="0.8"/>')
    for i in range(n):
        a = angle(i)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + r*math.cos(a):.1f}" y2="{cy + r*math.sin(a):.1f}" stroke="#C7CDE8" stroke-width="1" stroke-dasharray="4 3"/>')
    filled_pts = []
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        filled_pts.append(f"{x:.1f},{y:.1f}")
    svg.append(f'<polygon points="{" ".join(filled_pts)}" fill="rgba(37,99,235,0.18)" stroke="#2563EB" stroke-width="2.5" stroke-linejoin="round"/>')
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        c = colors[i]
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{c}" opacity="0.15"/>')
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{c}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{x:.1f}" y="{y+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="7" font-weight="700" fill="white">{v}</text>')
        a = angle(i)
        lx = cx + (r + 32) * math.cos(a)
        ly = cy + (r + 32) * math.sin(a)
        short_name = {"P":"الممارسة", "L":"اللغة", "G":"التوجيه", "EH":"التواضع"}.get(k, k)
        svg.append(f'<rect x="{lx-28:.1f}" y="{ly-11:.1f}" width="56" height="22" rx="6" fill="{c}" opacity="0.12"/>')
        svg.append(f'<text x="{lx:.1f}" y="{ly+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-weight="700" fill="{c}">{short_name}</text>')
    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="#94A3B8"/></svg>')
    return "\n".join(svg)

def trend_svg(sessions, w=320, h=90):
    if len(sessions) < 2:
        return ""
    vals = [s["cpi"] for s in sessions if s.get("cpi")]
    if len(vals) < 2:
        return ""
    pad = 16
    min_v = max(0, min(vals) - 10)
    max_v = min(100, max(vals) + 10)
    def x(i): return pad + (i / (len(vals) - 1)) * (w - pad * 2)
    def y(v):
        if max_v == min_v: return h / 2
        return h - pad - ((v - min_v) / (max_v - min_v)) * (h - pad * 2)
    area_pts = f"{x(0):.1f},{h} " + " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals)) + f" {x(len(vals)-1):.1f},{h}"
    svg = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;overflow:visible">']
    svg.append('<defs><linearGradient id="tgrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2563EB" stop-opacity="0.2"/><stop offset="100%" stop-color="#2563EB" stop-opacity="0.02"/></linearGradient></defs>')
    for v_ref in [40, 65, 85]:
        yr = y(v_ref)
        if pad <= yr <= h - pad:
            svg.append(f'<line x1="{pad}" y1="{yr:.1f}" x2="{w-pad}" y2="{yr:.1f}" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="4 3"/>')
            svg.append(f'<text x="{w-pad+4}" y="{yr+4:.1f}" font-size="9" fill="#94A3B8" font-family="monospace">{v_ref}%</text>')
    svg.append(f'<polygon points="{area_pts}" fill="url(#tgrad)"/>')
    line_pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    svg.append(f'<polyline points="{line_pts}" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    for i, v in enumerate(vals):
        c = get_level(v)["color"]
        xi, yi = x(i), y(v)
        svg.append(f'<circle cx="{xi:.1f}" cy="{yi:.1f}" r="5" fill="{c}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{xi:.1f}" y="{yi-10:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="{c}" font-family="monospace">{v}%</text>')
    svg.append("</svg>")
    return "\n".join(svg)

def gauge_svg(value):
    if value is None:
        return ""
    level = get_level(value)
    color = level["color"]
    circ = math.pi * 58
    dash = (value / 100) * circ
    angle_deg = 180 - (value / 100) * 180
    needle_x = 88 + 46 * math.cos(math.radians(angle_deg))
    needle_y = 84 - 46 * math.sin(math.radians(angle_deg))
    return f"""
    <svg width="176" height="100" viewBox="0 0 176 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="ggrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#EF4444"/>
          <stop offset="40%" stop-color="#F59E0B"/>
          <stop offset="70%" stop-color="#3B82F6"/>
          <stop offset="100%" stop-color="#10B981"/>
        </linearGradient>
      </defs>
      <path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round"/>
      <path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="url(#ggrad)" stroke-width="14" stroke-linecap="round" opacity="0.25"/>
      <path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/>
      <circle cx="{needle_x:.1f}" cy="{needle_y:.1f}" r="5" fill="{color}" opacity="0.9"/>
      <text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827" font-family="monospace">{value}%</text>
    </svg>"""

def get_api_key():
    try:
        secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if secret_key:
            return secret_key, True
    except Exception:
        pass
    return st.session_state.get("api_key", ""), False

def call_claude(messages, system_prompt, api_key):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": messages,
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=60)
        data = r.json()
        if "content" in data:
            return data["content"][0]["text"]
        elif "error" in data:
            return f"⚠️ API Error: {data['error']['message']}"
        else:
            return "⚠️ Unexpected server response."
    except Exception as e:
        return f"⚠️ Connection error: {str(e)}"

def generate_pdf_bytes(session, all_sessions, lang):
    try:
        mock_pdf_bytes = f"Executive Cross-Pollination Analysis Report - Project: {session.get('label', 'CPI')}".encode()
        return mock_pdf_bytes, None
    except Exception as e:
        return None, str(e)

# ----------------------------------------------------------------------
# تهيئة Session State
# ----------------------------------------------------------------------
if "lang" not in st.session_state: st.session_state.lang = "ar"
if "sessions" not in st.session_state: st.session_state.sessions = []
if "scores" not in st.session_state: st.session_state.scores = {k: 0 for k in DIM_KEYS}
if "fac_msgs" not in st.session_state: st.session_state.fac_msgs = []
if "fac_mode" not in st.session_state: st.session_state.fac_mode = "transcript"
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "signatories" not in st.session_state: st.session_state.signatories = []
if "session_num_counter" not in st.session_state: st.session_state["session_num_counter"] = 1

# ----------------------------------------------------------------------
# TAB 1 - تقييم الجلسة
# ----------------------------------------------------------------------
with tab1:
    st.markdown(f'<div style="font-size:13px; color:#6B7280; margin-bottom:16px;">{t("assess_intro")}<br><strong>{t("scale_hint")}</strong></div>', unsafe_allow_html=True)

    col_t, col_p = st.columns(2)
    with col_t:
        team_name_input = st.text_input("team", placeholder="اسم الفريق *", label_visibility="collapsed", key="team_name_input")
    with col_p:
        project_name_input = st.text_input("project", placeholder="اسم المشروع / الجلسة", label_visibility="collapsed", key="project_name_input")

    col_n, col_d = st.columns(2)
    with col_n:
        if st.session_state["session_num_counter"] == 1 and team_name_input:
            try:
                cpi_db.init_db()
                _existing = cpi_db.load_historical_scores(team_name=team_name_input, limit=999)
                if _existing:
                    st.session_state["session_num_counter"] = len(_existing) + 1
            except Exception:
                pass
        session_num_input = st.number_input("رقم الجلسة (Sprint)", min_value=1, step=1, value=st.session_state["session_num_counter"])
    with col_d:
        session_date_input = st.date_input("التاريخ", value=datetime.date.today(), key="session_date_input")

    session_name = project_name_input or team_name_input or "Session"
    st.markdown("---")

    for k in DIM_KEYS:
        d = DIMS_DATA[k]
        current = st.session_state.scores.get(k, 1)
        name = d["ar"]["name"]
        desc = d["ar"]["desc"]
        q = d["ar"]["q"]
        st.markdown(f"##### {k} - {name}")
        st.caption(desc)
        st.caption(f"*{q}*")
        st.session_state.scores[k] = st.select_slider(
            label=f"S_{k}", options=[1, 2, 3, 4],
            value=current if current > 0 else 1, label_visibility="collapsed"
        )

    p_s, l_s, g_s, eh_s = st.session_state.scores["P"], st.session_state.scores["L"], st.session_state.scores["G"], st.session_state.scores["EH"]
    cpi_score_final = int(((p_s + l_s + g_s + eh_s) / 16.0) * 100)

    if cpi_score_final >= 90: level_title = "المستوى 5: النظام البيئي المتكامل"
    elif cpi_score_final >= 75: level_title = "المستوى 4: النظام التشاركي"
    elif cpi_score_final >= 55: level_title = "المستوى 3: النظام المتعاون"
    elif cpi_score_final >= 40: level_title = "المستوى 2: النظام البيروقراطي"
    elif cpi_score_final >= 25: level_title = "المستوى 1: جزر التخصصات المنعزلة"
    else: level_title = "المستوى 0: العبقري المنعزل"

    st.markdown("---")

    if st.button(f"{t('btn_record')} — CPI: {cpi_score_final}%", type="primary", use_container_width=True):
        entry = {
            "id": datetime.datetime.now().timestamp(),
            "team": team_name_input or "Default",
            "project": project_name_input or session_name,
            "session_number": session_num_input,
            "date": str(session_date_input),
            "scores": dict(st.session_state.scores),
            "cpi": cpi_score_final,
            "level": level_title,
            "color": get_level(cpi_score_final)["color"],
            "cls": get_level(cpi_score_final)["cls"],
        }
        st.session_state.sessions.append(entry)

        try:
            cpi_db.init_db()
            cpi_db.save_cpi_session({
                "team_name": team_name_input or "Default",
                "project_name": project_name_input or session_name,
                "session_number": int(session_num_input),
                "session_date": str(session_date_input),
                "score_eh": float(eh_s), "score_l": float(l_s), "score_p": float(p_s), "score_g": float(g_s),
                "cpi_score_final": float(cpi_score_final),
                "maturity_level": level_title,
                "lang": lang,
            }, signatories=st.session_state.get("signatories", []))
        except Exception as e:
            st.warning(f"تم الحفظ محلياً. تعذر الاتصال بقاعدة البيانات: {e}")

        st.session_state["session_num_counter"] = session_num_input + 1
        st.session_state.scores = {k: 0 for k in DIM_KEYS}
        st.success(f"✓ تم توثيق الجلسة بنجاح! {level_title}")
        st.rerun()

# ----------------------------------------------------------------------
# TAB 2 - لوحة القيادة
# ----------------------------------------------------------------------
with tab2:
    if not st.session_state.sessions:
        st.info(t("no_data"))
    else:
        latest = st.session_state.sessions[-1]
        level = get_level(latest["cpi"])
        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            st.markdown(f'<div class="gauge-wrap">{gauge_svg(latest["cpi"])}<div style="margin-top:12px"><strong>{level["title"]}</strong></div></div>', unsafe_allow_html=True)
        with col_g2:
            st.markdown(f'<div class="radar-wrap">{radar_svg(latest["scores"], 280)}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# TAB 3 - السجل
# ----------------------------------------------------------------------
with tab3:
    if not st.session_state.sessions:
        st.info(t("no_sessions"))
    else:
        if st.button(t("pdf_export_all"), type="primary", use_container_width=True):
            with st.spinner(t("pdf_generating")):
                pdf_bytes, err = generate_pdf_bytes(st.session_state.sessions[-1], st.session_state.sessions, lang)
                if pdf_bytes:
                    st.download_button("⬇️ تحميل التقرير PDF", data=pdf_bytes, file_name="CPI_Report.pdf", mime="application/pdf")
                else:
                    st.error(t("pdf_error"))
        for s in reversed(st.session_state.sessions):
            st.markdown(f"📁 **{s['project']}** ({s['date']}) - {s['team']} | **CPI: {s['cpi']}%** → {s['level']}")

# ----------------------------------------------------------------------
# TAB 4 - الميسر المعرفي
# ----------------------------------------------------------------------
with tab4:
    st.info(t("ai_facilitator_ready"))
    api_key_input = st.text_input("Anthropic API Key", value=st.session_state.api_key, type="password")
    if api_key_input:
        st.session_state.api_key = api_key_input
    transcript_input = st.text_area("أدخل محضر أو نص النقاش الجماعي للتحليل المعرفي:", height=150)
    if st.button("تفعيل التحليل الإستراتيجي للميسر الذكي"):
        if not st.session_state.api_key:
            st.error(t("error_no_key"))
        elif not transcript_input.strip():
            st.warning(t("error_no_input"))
        else:
            with st.spinner(t("fac_thinking")):
                url = "https://api.anthropic.com/v1/messages"
                headers = {"x-api-key": st.session_state.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": f"أنت ميسر معرفي خبير في إطار حوكمة الذكاء الجماعي CPI. قم بتحليل المحضر التالي: 1) رصد لغة الأنا مقابل لغة التلاقح. 2) كشف التحيزات المعرفية. 3) تقييم التواضع المعرفي. قدّم توصيات تنفيذية:\n\n{transcript_input}"}]
                }
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=35)
                    if response.status_code == 200:
                        reply_text = response.json()["content"][0]["text"]
                        st.markdown("### 📝 تقرير الميسر المعرفي:")
                        st.write(reply_text)
                    else:
                        st.error(f"فشل الاتصال. رمز الاستجابة: {response.status_code}")
                except Exception as api_err:
                    st.error(f"⚠️ خطأ في الاتصال: {api_err}")

# ----------------------------------------------------------------------
# TAB 5 - الميثاق
# ----------------------------------------------------------------------
with tab5:
    st.markdown("### 📜 ميثاق التواضع المعرفي وحوكمة الذكاء الجماعي (ESU-001)")
    st.markdown("""
    * **أولا:** ممارسة التواضع المعرفي (Epistemic Humility).
    * **ثانيا:** صياغة وتحديث لغة مشتركة (Shared Language).
    * **ثالثا:** السماح بتدفق الأفكار والتوجيه التشاركي (Guidance).
    """)
    sig_name = st.text_input("وقع اسمك الكريم هنا لإعلان الالتزام:")
    if st.button("تثبيت التوقيع"):
        if sig_name and sig_name not in st.session_state.signatories:
            st.session_state.signatories.append(sig_name)
            st.success(f"✍️ تم تسجيل التوقيع بنجاح.")
            st.rerun()
    if st.session_state.signatories:
        st.markdown("---")
        for sig in st.session_state.signatories:
            st.markdown(f"✓ {sig}")

# ----------------------------------------------------------------------
# TAB 6 - الإدارة
# ----------------------------------------------------------------------
with tab6:
    st.markdown("#### التحكم المركزي بالسجلات")
    if st.button("تصدير البيانات CSV", type="secondary", use_container_width=True):
        csv_output = "ID,Team,Project,SessionNumber,CPI_Score,MaturityLevel\n"
        for s in st.session_state.sessions:
            csv_output += f"{s['id']},{s['team']},{s['project']},{s['session_number']},{s['cpi']},{s['level']}\n"
        st.download_button("📥 تحميل ملف CSV", data=csv_output, file_name="CPI_Data_Export.csv", mime="text/csv")
    if st.button("🚨 إعادة تعيين هياكل الذاكرة المؤقتة بالكامل", type="primary"):
        st.session_state.sessions = []
        st.session_state.signatories = []
        st.session_state.scores = {k: 0 for k in DIM_KEYS}
        st.session_state["session_num_counter"] = 1
        st.success("تم تصفير البيانات بنجاح.")
        st.rerun()

# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
st.markdown(f"""
<div style="text-align:center; margin-top:48px; padding:24px 16px; background:linear-gradient(135deg,#0F172A,#1E293B); border-radius:16px">
    <div style="font-size:13px; font-weight:700; color:#E2E8F0; margin-bottom:6px">🧠 {t('footer')}</div>
    <div style="font-size:11px; color:#64748B; font-family:monospace;">CPI Framework v6.1-fixed · Project Ref: ESU-001 · All Systems Operational</div>
</div>
""", unsafe_allow_html=True)
