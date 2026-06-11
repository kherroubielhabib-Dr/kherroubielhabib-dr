# ═══════════════════════════════════════════════════════════════════
#  مؤشر التلاقح المعرفي — CPI Dashboard  (ثلاثي اللغات)
#  Cross-Pollination Index · Indice de Pollinisation Croisée
#  د. الحبيب خروبي · ESU-001
#  Streamlit app — app.py  (trilingual: AR / EN / FR)
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import json
import math
import datetime
import requests
import base64
from io import BytesIO

# ── إعداد الصفحة ────────────────────────────────────────────────────
st.set_page_config(
    page_title="CPI Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
#  TRANSLATIONS — قاموس الترجمة المركزي
# ════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    # ── App shell ──────────────────────────────────────────────────
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
    # ── Tabs ───────────────────────────────────────────────────────
    "tab_assess": {
        "ar": "📝 تقييم جلسة",
        "en": "📝 Session Assessment",
        "fr": "📝 Évaluation de séance",
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
    # ── Assessment tab ─────────────────────────────────────────────
    "assess_intro": {
        "ar": "قيّم الأبعاد الأربعة بعد كل Sprint أو اجتماع حاسم.",
        "en": "Rate the four dimensions after each Sprint or key meeting.",
        "fr": "Évaluez les quatre dimensions après chaque Sprint ou réunion clé.",
    },
    "scale_hint": {
        "ar": "1 = ضعيف · 2 = مقبول · 3 = جيد · 4 = متقدم (اختفاء الحدود)",
        "en": "1 = Weak · 2 = Acceptable · 3 = Good · 4 = Advanced (boundary disappearance)",
        "fr": "1 = Faible · 2 = Acceptable · 3 = Bien · 4 = Avancé (disparition des frontières)",
    },
    "session_name_ph": {
        "ar": "اسم الجلسة (اختياري) — مثال: اجتماع التخطيط يوليو 2026",
        "en": "Session name (optional) — e.g. Planning Meeting July 2026",
        "fr": "Nom de séance (optionnel) — ex. Réunion de planification juillet 2026",
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
    # ── Dashboard tab ──────────────────────────────────────────────
    "last_cpi": {
        "ar": "آخر CPI مسجّل",
        "en": "Latest recorded CPI",
        "fr": "Dernier CPI enregistré",
    },
    "dim_detail": {
        "ar": "تفصيل الأبعاد — آخر جلسة",
        "en": "Dimension breakdown — latest session",
        "fr": "Détail des dimensions — dernière séance",
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
        "ar": "لا توجد بيانات بعد — سجّل أول جلسة من تبويب التقييم",
        "en": "No data yet — record your first session in the Assessment tab",
        "fr": "Aucune donnée — enregistrez votre première séance dans l'onglet Évaluation",
    },
    # ── History tab ────────────────────────────────────────────────
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
    "export_all": {
        "ar": "📄 تصدير تقرير كامل (HTML)",
        "en": "📄 Export full report (HTML)",
        "fr": "📄 Exporter rapport complet (HTML)",
    },
    "export_session": {
        "ar": "📄 تصدير هذه الجلسة",
        "en": "📄 Export this session",
        "fr": "📄 Exporter cette séance",
    },
    # ── Facilitator tab ────────────────────────────────────────────
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
    # ── Footer ─────────────────────────────────────────────────────
    "footer": {
        "ar": "CPI — مؤشر التلاقح المعرفي · د. الحبيب خروبي · ESU-001",
        "en": "CPI — Cross-Pollination Index · Dr. Elhabib Kherroubi · ESU-001",
        "fr": "CPI — Indice de Pollinisation Croisée · Dr. Elhabib Kherroubi · ESU-001",
    },
}

def t(key):
    """استرجاع نص حسب اللغة الحالية."""
    lang = st.session_state.get("lang", "ar")
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("ar", key))

# ════════════════════════════════════════════════════════════════════
#  DATA — الأبعاد والمستويات والتوصيات
# ════════════════════════════════════════════════════════════════════
DIMS_DATA = {
    "P": {
        "color": "#2563EB",
        "ar": {"name": "الممارسة",        "desc": "مدى استيعاب كل تخصص لأولويات التخصص الآخر", "q": "هل فهمنا أولويات بعضنا في القرارات؟"},
        "en": {"name": "Practice",         "desc": "How much each discipline grasps the other's priorities", "q": "Did we understand each other's priorities in decisions?"},
        "fr": {"name": "Pratique",         "desc": "Dans quelle mesure chaque discipline comprend les priorités de l'autre", "q": "Avons-nous compris les priorités de chacun dans les décisions ?"},
    },
    "L": {
        "color": "#059669",
        "ar": {"name": "اللغة المشتركة",  "desc": "وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال", "q": "هل تحدثنا بلغة مشتركة دون سوء فهم؟"},
        "en": {"name": "Shared Language",  "desc": "A unified conceptual vocabulary enabling effective communication", "q": "Did we speak a common language without misunderstanding?"},
        "fr": {"name": "Langage commun",   "desc": "Un vocabulaire conceptuel unifié permettant une communication efficace", "q": "Avons-nous parlé un langage commun sans malentendus ?"},
    },
    "G": {
        "color": "#7C3AED",
        "ar": {"name": "التوجيه",          "desc": "اتجاه تدفق الأفكار داخل النظام", "q": "هل تدفقت الأفكار من الجميع (وليس فقط من القائد)؟"},
        "en": {"name": "Guidance",          "desc": "Direction of idea flow within the system", "q": "Did ideas flow from everyone (not just the leader)?"},
        "fr": {"name": "Orientation",       "desc": "Direction du flux d'idées au sein du système", "q": "Les idées ont-elles circulé de tous (pas seulement du leader) ?"},
    },
    "EH": {
        "color": "#DC2626",
        "ar": {"name": "التواضع المعرفي", "desc": "قدرة الأفراد على قبول التصحيح والتعلم من الآخرين", "q": "هل استمعنا لبعضنا بتواضع وغيرنا مواقفنا؟"},
        "en": {"name": "Epistemic Humility","desc": "Individuals' capacity to accept correction and learn from others", "q": "Did we listen humbly and change our positions?"},
        "fr": {"name": "Humilité épistémique","desc": "Capacité des individus à accepter la correction et apprendre des autres", "q": "Avons-nous écouté humblement et changé nos positions ?"},
    },
}

DIM_KEYS = ["P", "L", "G", "EH"]

LEVELS = {
    "ar": [
        {"min": 0,  "max": 40,  "label": "نموذج العبقري المنعزل",             "color": "#EF4444", "cls": "level-0"},
        {"min": 40, "max": 65,  "label": "تعاون شكلي",                         "color": "#F59E0B", "cls": "level-1"},
        {"min": 65, "max": 85,  "label": "ذكاء جماعي واعٍ جزئياً",            "color": "#3B82F6", "cls": "level-2"},
        {"min": 85, "max": 101, "label": "ذكاء جماعي حقيقي — اختفاء الحدود", "color": "#10B981", "cls": "level-3"},
    ],
    "en": [
        {"min": 0,  "max": 40,  "label": "Isolated Genius Model",              "color": "#EF4444", "cls": "level-0"},
        {"min": 40, "max": 65,  "label": "Formal Cooperation",                  "color": "#F59E0B", "cls": "level-1"},
        {"min": 65, "max": 85,  "label": "Partially Aware Collective",          "color": "#3B82F6", "cls": "level-2"},
        {"min": 85, "max": 101, "label": "True Collective Intelligence",        "color": "#10B981", "cls": "level-3"},
    ],
    "fr": [
        {"min": 0,  "max": 40,  "label": "Modèle du génie isolé",              "color": "#EF4444", "cls": "level-0"},
        {"min": 40, "max": 65,  "label": "Coopération formelle",                "color": "#F59E0B", "cls": "level-1"},
        {"min": 65, "max": 85,  "label": "Intelligence collective partielle",   "color": "#3B82F6", "cls": "level-2"},
        {"min": 85, "max": 101, "label": "Intelligence collective réelle",      "color": "#10B981", "cls": "level-3"},
    ],
}

RECS = {
    "P": {
        "ar": ("الممارسة",         "#2563EB", "جلسات «تظليل وظيفي» أسبوعية — يظلل كل تخصص الآخر."),
        "en": ("Practice",          "#2563EB", "Weekly 'job shadowing' sessions — each discipline shadows the other."),
        "fr": ("Pratique",          "#2563EB", "Séances hebdomadaires d'«observation de poste» — chaque discipline observe l'autre."),
    },
    "L": {
        "ar": ("اللغة المشتركة",   "#059669", "ورشة «قاموس مشترك» — يوم واحد + تحديثات أسبوعية."),
        "en": ("Shared Language",   "#059669", "'Shared Glossary' workshop — one day + weekly updates."),
        "fr": ("Langage commun",    "#059669", "Atelier «glossaire commun» — une journée + mises à jour hebdomadaires."),
    },
    "G": {
        "ar": ("التوجيه",           "#7C3AED", "إلغاء الموافقات الهرمية على الاقتراحات الصغيرة."),
        "en": ("Guidance",           "#7C3AED", "Remove hierarchical approval requirements for small proposals."),
        "fr": ("Orientation",        "#7C3AED", "Supprimer les approbations hiérarchiques pour les petites propositions."),
    },
    "EH": {
        "ar": ("التواضع المعرفي",  "#DC2626", "جلسات «مراجعة عمياء» — تقييم الأفكار دون معرفة صاحبها."),
        "en": ("Epistemic Humility", "#DC2626", "'Blind review' sessions — evaluate ideas without knowing their author."),
        "fr": ("Humilité épistémique","#DC2626", "Séances de «révision à l'aveugle» — évaluer les idées sans connaître leur auteur."),
    },
}

FAC_MODES = {
    "transcript": {
        "ar": {"label": "📋 تحليل محضر اجتماع", "ph": "الصق هنا نص محضر الاجتماع..."},
        "en": {"label": "📋 Meeting transcript analysis", "ph": "Paste the meeting minutes or summary here..."},
        "fr": {"label": "📋 Analyse de compte rendu", "ph": "Collez ici le compte rendu de la réunion..."},
        "system_ar": """أنت ميسر معرفي محايد متخصص في نظرية CPI (مؤشر التلاقح المعرفي) وضعه د. الحبيب خروبي.
نظريتك: CI = NK × EH. مهمتك تحليل المحضر وإرجاع: مؤشر تقديري لكل بُعد مع تبرير، المصطلحات التي تحتاج تفسيراً، أبرز لحظة تواضع وأبرز لحظة أنا مرتفعة، وتوصية واحدة للجلسة القادمة. الرد بالعربية.""",
        "system_en": """You are a neutral cognitive facilitator specialising in CPI theory (Cross-Pollination Index) by Dr. Elhabib Kherroubi.
Formula: CI = NK × EH. Your task: analyse the transcript and return: an estimated score for each dimension with brief justification, terms needing cross-disciplinary clarification, the standout moment of humility vs. ego, and one actionable recommendation for the next session. Reply in English.""",
        "system_fr": """Vous êtes un facilitateur cognitif neutre spécialisé dans la théorie CPI (Indice de Pollinisation Croisée) du Dr. Elhabib Kherroubi.
Formule : IC = SC × HE. Votre tâche : analyser le compte rendu et fournir : un score estimé pour chaque dimension avec justification, les termes nécessitant une clarification interdisciplinaire, le moment clé d'humilité vs. ego, et une recommandation actionnable pour la prochaine séance. Répondre en français.""",
    },
    "glossary": {
        "ar": {"label": "📖 فك الاشتباك المعرفي", "ph": "اكتب مصطلحاً تقنياً تريد تبسيطه..."},
        "en": {"label": "📖 Cognitive detangling", "ph": "Enter a technical term you want simplified..."},
        "fr": {"label": "📖 Démêlage cognitif", "ph": "Saisissez un terme technique à simplifier..."},
        "system_ar": "أنت ميسر معرفي. اشرح المصطلح بثلاث طبقات: تعريف بسيط، مثال واقعي، ولماذا هذا المصطلح مهم للفريق متعدد التخصصات. الرد بالعربية.",
        "system_en": "You are a cognitive facilitator. Explain the term in three layers: simple definition, real-world example, and why this term matters for a cross-disciplinary team. Reply in English.",
        "system_fr": "Vous êtes un facilitateur cognitif. Expliquez le terme en trois couches : définition simple, exemple concret, et pourquoi ce terme est important pour une équipe interdisciplinaire. Répondre en français.",
    },
    "ego": {
        "ar": {"label": "🔍 رصد الأنا", "ph": "الصق مقتطفات من حوار الفريق أو رسائل المجموعة..."},
        "en": {"label": "🔍 Ego monitoring", "ph": "Paste excerpts from team conversations or group messages..."},
        "fr": {"label": "🔍 Surveillance de l'ego", "ph": "Collez des extraits de conversations ou messages d'équipe..."},
        "system_ar": "أنت ميسر معرفي محايد. حلل نسبة لغة الأنا مقابل النحن، أعطِ تقييم EH من 1 إلى 4، وأرسل جملة تغذية راجعة محايدة للفريق. الرد بالعربية.",
        "system_en": "You are a neutral cognitive facilitator. Analyse the ratio of 'I' vs 'We' language, give an EH score from 1 to 4, and provide one neutral feedback sentence for the team. Reply in English.",
        "system_fr": "Vous êtes un facilitateur cognitif neutre. Analysez le ratio de langage «je» vs «nous», donnez un score HE de 1 à 4, et formulez une phrase de feedback neutre pour l'équipe. Répondre en français.",
    },
    "bias": {
        "ar": {"label": "⚖️ كشف التحيزات", "ph": "صف ما جرى في الاجتماع أو القرار الذي اتُّخذ..."},
        "en": {"label": "⚖️ Bias detection", "ph": "Describe what happened in the meeting or the decision made..."},
        "fr": {"label": "⚖️ Détection des biais", "ph": "Décrivez ce qui s'est passé lors de la réunion ou la décision prise..."},
        "system_ar": "أنت ميسر معرفي محايد. ارصد التحيزات المعرفية (تأكيد، سلطة، ثقة مفرطة، إجماع)، حدد السؤال الذي لم يُطرح، وأعطِ توصية واحدة. الرد بالعربية.",
        "system_en": "You are a neutral cognitive facilitator. Identify cognitive biases (confirmation, authority, overconfidence, consensus), pinpoint the question that wasn't asked, and give one recommendation. Reply in English.",
        "system_fr": "Vous êtes un facilitateur cognitif neutre. Identifiez les biais cognitifs (confirmation, autorité, excès de confiance, consensus), repérez la question qui n'a pas été posée, et donnez une recommandation. Répondre en français.",
    },
}

# ── CSS ──────────────────────────────────────────────────────────────
def inject_css(lang):
    direction = "rtl" if lang == "ar" else "ltr"
    text_align = "right" if lang == "ar" else "left"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans Arabic', 'IBM Plex Sans', 'Segoe UI', sans-serif !important;
    direction: {direction};
}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
div[role="radiogroup"] {{
    display: flex !important; flex-direction: row !important;
    gap: 8px !important; flex-wrap: nowrap !important;
}}
div[role="radiogroup"] label {{
    flex: 1 !important; border: 1.5px solid #D1D5DB !important;
    border-radius: 8px !important; padding: 10px 6px !important;
    text-align: center !important; cursor: pointer !important;
    font-size: 13px !important; font-weight: 600 !important;
    background: white !important; transition: all 0.15s !important;
}}
div[role="radiogroup"] label:has(input:checked) {{
    background: #EFF6FF !important; border-color: #2563EB !important; color: #2563EB !important;
}}
div[role="radiogroup"] input[type="radio"] {{ display: none !important; }}
.cpi-header {{
    background: #0F172A; color: white; padding: 18px 28px 14px;
    border-radius: 12px; margin-bottom: 8px;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 2px solid #1E3A5F;
}}
.cpi-header h1 {{ font-size: 20px; font-weight: 700; margin: 0; }}
.cpi-header p  {{ font-size: 11px; color: #94A3B8; margin: 4px 0 0; }}
.lang-bar {{
    background: #1E293B; border-radius: 8px; padding: 6px 12px;
    display: flex; gap: 6px; align-items: center;
}}
.cpi-formula {{
    background: #1E3A5F; border-radius: 8px;
    padding: 6px 16px; font-size: 13px; color: #7DD3FC;
    font-weight: 600; font-family: monospace; letter-spacing: 1px;
}}
.cpi-card {{
    background: white; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}
.dim-card {{
    border-radius: 10px; padding: 16px 18px;
    margin-bottom: 14px; border: 1.5px solid #E5E7EB; background: #FAFAFA;
}}
.dim-title {{ font-size: 17px; font-weight: 700; }}
.dim-desc  {{ font-size: 12px; color: #9CA3AF; margin: 3px 0 8px; }}
.dim-q     {{ font-size: 13px; color: #374151; font-style: italic; margin-bottom: 10px; }}
.cpi-badge {{
    border-radius: 10px; padding: 16px 24px;
    text-align: center; font-family: monospace;
}}
.cpi-value  {{ font-size: 42px; font-weight: 800; }}
.cpi-label  {{ font-size: 13px; font-weight: 600; margin-top: 4px; }}
.level-0 {{ background:#FEF2F2; color:#EF4444; border:1.5px solid #FECACA; }}
.level-1 {{ background:#FFFBEB; color:#F59E0B; border:1.5px solid #FDE68A; }}
.level-2 {{ background:#EFF6FF; color:#3B82F6; border:1.5px solid #BFDBFE; }}
.level-3 {{ background:#F0FDF4; color:#10B981; border:1.5px solid #A7F3D0; }}
div[data-testid="stSlider"] > div > div > div {{ direction: ltr !important; }}
div[data-testid="stSlider"] > label {{ direction: {direction} !important; }}
.rec-card {{
    background: #FFF7ED; border: 1px solid #FED7AA;
    border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 13px;
}}
.session-card {{
    background: white; border: 1px solid #E5E7EB;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
}}
.session-header {{ display:flex; justify-content:space-between; margin-bottom:8px; }}
.session-name   {{ font-weight:700; font-size:14px; }}
.session-date   {{ font-size:11px; color:#9CA3AF; }}
.session-cpi    {{ font-size:20px; font-weight:800; font-family:monospace; padding:4px 12px; border-radius:8px; }}
.dim-tag {{
    display:inline-block; background:#F9FAFB; border-radius:6px;
    padding:3px 10px; font-size:11px; font-weight:600;
    margin-{"left" if direction=="ltr" else "right"}:6px; margin-bottom:4px;
}}
.msg-user {{
    background: #2563EB; color: white;
    border-radius: 12px 12px {"4px 12px" if direction=="rtl" else "12px 4px"};
    padding: 10px 14px; font-size: 13px; line-height: 1.7;
    margin-bottom: 10px; max-width: 88%; margin-{"right" if direction=="rtl" else "left"}: auto;
}}
.msg-ai {{
    background: white; color: #111827; border: 1px solid #E5E7EB;
    border-radius: 12px 12px {"12px 4px" if direction=="rtl" else "4px 12px"};
    padding: 10px 14px; font-size: 13px; line-height: 1.7;
    margin-bottom: 10px; max-width: 88%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.msg-ai-label {{ font-size:10px; color:#7C3AED; font-weight:700; margin-bottom:5px; }}
.radar-wrap {{ display:flex; justify-content:center; padding:10px 0; }}
.prog-wrap {{ height:8px; background:#F3F4F6; border-radius:4px; overflow:hidden; margin-top:4px; }}
.prog-bar  {{ height:100%; border-radius:4px; transition: width 0.5s ease; }}
.bdi-card {{
    background:#F5F3FF; border:1px solid #DDD6FE;
    border-radius:12px; padding:16px 20px;
    display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;
}}
.bdi-val {{ font-size:32px; font-weight:800; font-family:monospace; }}
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────
def get_level(cpi):
    lang = st.session_state.get("lang", "ar")
    for l in LEVELS[lang]:
        if l["min"] <= cpi < l["max"]:
            return l
    return LEVELS[lang][-1]

def dim_field(key, field):
    lang = st.session_state.get("lang", "ar")
    return DIMS_DATA[key][lang][field]

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

def radar_svg(scores, size=220):
    cx = cy = size / 2
    r = size * 0.36
    n = len(DIM_KEYS)
    lang = st.session_state.get("lang", "ar")

    def angle(i): return math.pi * 2 * i / n - math.pi / 2
    def pt(i, val):
        a = angle(i)
        d = (val / 4) * r
        return cx + d * math.cos(a), cy + d * math.sin(a)
    def ring_points(v):
        pts = []
        for i in range(n):
            a = angle(i)
            d = (v / 4) * r
            pts.append(f"{cx + d*math.cos(a):.1f},{cy + d*math.sin(a):.1f}")
        return " ".join(pts)

    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']
    for v in [1, 2, 3, 4]:
        svg.append(f'<polygon points="{ring_points(v)}" fill="none" stroke="#E5E7EB" stroke-width="1"/>')
    for i in range(n):
        a = angle(i)
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
    filled_pts = []
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        filled_pts.append(f"{x:.1f},{y:.1f}")
    svg.append(f'<polygon points="{" ".join(filled_pts)}" fill="rgba(37,99,235,0.15)" stroke="#2563EB" stroke-width="2" stroke-linejoin="round"/>')
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        color = DIMS_DATA[k]["color"]
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
    for i, k in enumerate(DIM_KEYS):
        a = angle(i)
        lx = cx + (r + 26) * math.cos(a)
        ly = cy + (r + 26) * math.sin(a)
        name = DIMS_DATA[k][lang]["name"]
        svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" '
                   f'font-size="10" font-weight="600" fill="#374151" '
                   f'font-family="IBM Plex Sans Arabic, IBM Plex Sans, sans-serif">{name}</text>')
    svg.append("</svg>")
    return "\n".join(svg)

def trend_svg(sessions, w=320, h=70):
    if len(sessions) < 2:
        return ""
    vals = [s["cpi"] for s in sessions if s.get("cpi")]
    if len(vals) < 2:
        return ""
    pad = 12
    min_v = max(0, min(vals) - 8)
    max_v = min(100, max(vals) + 8)
    def x(i): return pad + (i / (len(vals) - 1)) * (w - pad * 2)
    def y(v): return h - pad - ((v - min_v) / (max_v - min_v)) * (h - pad * 2) if max_v != min_v else h / 2
    svg = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">']
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#2563EB" stroke-width="2" stroke-linejoin="round"/>')
    for i, v in enumerate(vals):
        c = get_level(v)["color"]
        svg.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="4" fill="{c}"/>')
        svg.append(f'<text x="{x(i):.1f}" y="{y(v)-10:.1f}" text-anchor="middle" font-size="9" fill="#6B7280">{v}%</text>')
    svg.append("</svg>")
    return "\n".join(svg)

def gauge_svg(value):
    if value is None:
        return ""
    level = get_level(value)
    circ = math.pi * 54
    dash = (value / 100) * circ
    return f"""
<svg width="160" height="90" viewBox="0 0 160 90" xmlns="http://www.w3.org/2000/svg">
  <path d="M 16 78 A 64 64 0 0 1 144 78" fill="none" stroke="#E5E7EB" stroke-width="12" stroke-linecap="round"/>
  <path d="M 16 78 A 64 64 0 0 1 144 78" fill="none" stroke="{level['color']}" stroke-width="12"
        stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/>
  <text x="80" y="76" text-anchor="middle" font-size="24" font-weight="700" fill="#111827"
        font-family="IBM Plex Sans Arabic, IBM Plex Sans, monospace">{value}%</text>
</svg>"""

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

def generate_report_html(session, all_sessions, lang):
    s = session
    lvl = get_level(s["cpi"])
    dim_rows = ""
    for k in DIM_KEYS:
        v = s["scores"].get(k, 0)
        pct = (v / 4) * 100
        color = DIMS_DATA[k]["color"]
        name = DIMS_DATA[k][lang]["name"]
        icon = "🔴" if v <= 2 else ("🔵" if v == 3 else "🟢")
        bar = f'<div style="height:8px;background:#F3F4F6;border-radius:4px;overflow:hidden;margin-top:4px"><div style="height:100%;width:{pct}%;background:{color};border-radius:4px"></div></div>'
        dim_rows += f'<tr><td style="padding:10px 14px;font-weight:700;color:{color}">{k}</td><td style="padding:10px 14px;font-weight:600">{name}</td><td style="padding:10px 14px;font-family:monospace;font-weight:700;color:{color}">{v}/4 {icon}</td><td style="padding:10px 14px;width:160px">{bar}</td></tr>'

    weak = [k for k in DIM_KEYS if s["scores"].get(k, 0) <= 2]
    recs_html = ""
    if not weak:
        ok_msgs = {"ar": "✓ جميع الأبعاد في مستوى جيد.", "en": "✓ All dimensions at a good level.", "fr": "✓ Toutes les dimensions à un bon niveau."}
        recs_html = f'<p style="color:#10B981;font-weight:600">{ok_msgs[lang]}</p>'
    else:
        for k in weak:
            name, color, rec_text = RECS[k][lang]
            recs_html += f'<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;padding:10px 14px;margin-bottom:8px"><strong style="color:{color}">{name}</strong><br><span style="color:#92400E;font-size:13px">{rec_text}</span></div>'

    history_rows = ""
    for hs in all_sessions:
        hl = get_level(hs["cpi"])
        history_rows += f'<tr><td style="padding:8px 12px">{hs["label"]}</td><td style="padding:8px 12px;color:#6B7280">{hs["date"]}</td><td style="padding:8px 12px;font-weight:800;font-family:monospace;color:{hl["color"]}">{hs["cpi"]}%</td><td style="padding:8px 12px;font-size:12px;color:{hl["color"]}">{hl["label"]}</td></tr>'

    direction = "rtl" if lang == "ar" else "ltr"
    titles = {
        "ar": {"title": "تقرير مؤشر التلاقح المعرفي", "dim": "تفصيل الأبعاد", "rec": "توصيات التحسين", "hist": "مسار CPI عبر الزمن", "ses": "اسم الجلسة", "date": "التاريخ"},
        "en": {"title": "CPI Assessment Report", "dim": "Dimension breakdown", "rec": "Improvement recommendations", "hist": "CPI trend over time", "ses": "Session", "date": "Date"},
        "fr": {"title": "Rapport d'évaluation CPI", "dim": "Détail des dimensions", "rec": "Recommandations d'amélioration", "hist": "Évolution CPI", "ses": "Séance", "date": "Date"},
    }[lang]

    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CPI Report — {s['label']}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;600;700&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
* {{margin:0;padding:0;box-sizing:border-box;}}
body {{font-family:"IBM Plex Sans Arabic","IBM Plex Sans","Segoe UI",sans-serif;background:#F8FAFC;color:#111827;direction:{direction};padding:24px;}}
.header {{background:#0F172A;color:white;border-radius:12px;padding:20px 28px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;}}
.header h1 {{font-size:20px;font-weight:700;}}
.header p {{font-size:11px;color:#94A3B8;margin-top:4px;}}
.formula {{background:#1E3A5F;border-radius:8px;padding:8px 16px;font-size:13px;color:#7DD3FC;font-family:monospace;}}
.card {{background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.04);}}
.card h2 {{font-size:14px;font-weight:700;margin-bottom:14px;color:#374151;}}
table {{width:100%;border-collapse:collapse;}}
td,th {{text-align:{"right" if direction=="rtl" else "left"};}}
th {{background:#F9FAFB;font-size:12px;color:#6B7280;padding:8px 14px;font-weight:600;}}
tr:nth-child(even) td {{background:#FAFAFA;}}
.footer {{text-align:center;font-size:11px;color:#D1D5DB;margin-top:32px;padding:16px 0;border-top:1px solid #F3F4F6;}}
</style>
</head>
<body>
<div class="header">
  <div><h1>🧠 {titles["title"]}</h1><p>Cross-Pollination Index · Dr. Elhabib Kherroubi · ESU-001</p></div>
  <div class="formula">CI = NK × EH</div>
</div>
<div class="card">
  <h2>{titles["ses"]} / {titles["date"]}</h2>
  <p style="font-size:15px;font-weight:700;margin-bottom:6px">{s["label"]} &nbsp;·&nbsp; {s["date"]}</p>
  <p style="font-size:22px;font-weight:800;font-family:monospace;color:{lvl['color']}">{s['cpi']}% — {lvl['label']}</p>
</div>
<div class="card">
  <h2>{titles["dim"]}</h2>
  <table>
    <thead><tr><th>Key</th><th>{titles["dim"]}</th><th>Score</th><th>Bar</th></tr></thead>
    <tbody>{dim_rows}</tbody>
  </table>
</div>
<div class="card"><h2>{titles["rec"]}</h2>{recs_html}</div>
{"" if len(all_sessions) < 2 else f'<div class="card"><h2>{titles["hist"]}</h2>{trend_svg(all_sessions)}<table style="margin-top:12px"><thead><tr><th>{titles["ses"]}</th><th>{titles["date"]}</th><th>CPI</th><th></th></tr></thead><tbody>{history_rows}</tbody></table></div>'}
<div class="footer">CPI · Dr. Elhabib Kherroubi · ESU-001 · {datetime.datetime.now().strftime("%Y-%m-%d")}</div>
</body></html>"""

# ════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════════════
if "lang"      not in st.session_state: st.session_state.lang      = "ar"
if "sessions"  not in st.session_state: st.session_state.sessions  = []
if "scores"    not in st.session_state: st.session_state.scores    = {k: 0 for k in DIM_KEYS}
if "fac_msgs"  not in st.session_state: st.session_state.fac_msgs  = []
if "fac_mode"  not in st.session_state: st.session_state.fac_mode  = "transcript"
if "api_key"   not in st.session_state: st.session_state.api_key   = ""

lang = st.session_state.lang
inject_css(lang)

# ════════════════════════════════════════════════════════════════════
#  HEADER + LANGUAGE SWITCHER
# ════════════════════════════════════════════════════════════════════
col_head, col_lang = st.columns([5, 1])

with col_head:
    st.markdown(f"""
<div class="cpi-header">
  <div>
    <h1>🧠 {t('app_title')}</h1>
    <p>{t('app_sub')}</p>
  </div>
  <div class="cpi-formula">{t('formula_label')}</div>
</div>
""", unsafe_allow_html=True)

with col_lang:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    lang_choice = st.radio(
        "🌐",
        options=["ar", "en", "fr"],
        format_func=lambda x: {"ar": "🇩🇿 العربية", "en": "🇬🇧 English", "fr": "🇫🇷 Français"}[x],
        index=["ar", "en", "fr"].index(st.session_state.lang),
        key="lang_radio",
        label_visibility="visible",
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

lang = st.session_state.lang  # refresh after possible change

# ════════════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    t("tab_assess"),
    t("tab_dashboard"),
    f"{t('tab_history')} ({len(st.session_state.sessions)})",
    t("tab_facilitator"),
])

# ════════════════════════════════════════════════════════════════════
#  TAB 1 — ASSESSMENT
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <div style="font-size:13px; color:#6B7280; margin-bottom:16px;">
    {t('assess_intro')}<br>
    <strong>{t('scale_hint')}</strong>
    </div>
    """, unsafe_allow_html=True)

    session_name = st.text_input(
        t("session_name_ph"),
        placeholder=t("session_name_ph"),
        label_visibility="collapsed",
        key="session_name_input",
    )

    st.markdown("---")

    for k in DIM_KEYS:
        d = DIMS_DATA[k]
        current = st.session_state.scores[k]
        border_color = d["color"] + "66" if current > 0 else "#E5E7EB"
        name = d[lang]["name"]
        desc = d[lang]["desc"]
        q    = d[lang]["q"]

        st.markdown(f"""
        <div style="background:white; border:1.5px solid {border_color};
                    border-radius:12px; padding:14px 16px; margin-bottom:6px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="background:{d['color']}18; color:{d['color']}; font-weight:800;
                             font-size:12px; padding:2px 10px; border-radius:6px;">{k}</span>
                <span style="font-size:16px; font-weight:700; color:{d['color']}">{name}</span>
            </div>
            <div style="font-size:11px; color:#9CA3AF; margin-bottom:3px">{desc}</div>
            <em style="font-size:12px; color:#374151">«{q}»</em>
        </div>
        """, unsafe_allow_html=True)

        score_labels = t("score_labels")
        score_val = st.select_slider(
            label=k,
            options=[1, 2, 3, 4],
            value=current if current > 0 else 1,
            format_func=lambda v, sl=score_labels: f"{v} — {sl[v]}",
            label_visibility="collapsed",
            key=f"slider_{k}",
        )
        if score_val != current:
            st.session_state.scores[k] = score_val
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    cpi_now = calc_cpi(st.session_state.scores)
    if cpi_now is not None:
        level = get_level(cpi_now)
        col_gauge, col_radar = st.columns([1, 1])
        with col_gauge:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background:#F0F7FF;
                        border:1px solid #BFDBFE; border-radius:12px;">
                <div style="font-size:12px; color:#6B7280; margin-bottom:4px">{t('cpi_computed')}</div>
                {gauge_svg(cpi_now)}
                <div style="font-size:13px; font-weight:700; color:{level['color']}; margin-top:4px">{level['label']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_radar:
            st.markdown(
                f'<div class="radar-wrap">{radar_svg(st.session_state.scores, 220)}</div>',
                unsafe_allow_html=True
            )

        if st.button(f"{t('btn_record')} — CPI: {cpi_now}%", type="primary", use_container_width=True):
            entry = {
                "id": datetime.datetime.now().timestamp(),
                "label": session_name or f"{'جلسة' if lang=='ar' else 'Session'} {len(st.session_state.sessions) + 1}",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "scores": dict(st.session_state.scores),
                "cpi": cpi_now,
                "lang": lang,
            }
            st.session_state.sessions.append(entry)
            st.session_state.scores = {k: 0 for k in DIM_KEYS}
            st.success(f"✓ CPI: {cpi_now}% — {level['label']}")
            st.rerun()
    else:
        st.info(t("complete_all"))

# ════════════════════════════════════════════════════════════════════
#  TAB 2 — DASHBOARD
# ════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.sessions:
        st.markdown(f"""
        <div style="text-align:center; color:#9CA3AF; padding:60px 20px;">
            <div style="font-size:48px; margin-bottom:12px">📊</div>
            <div style="font-size:14px">{t('no_data')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        last        = st.session_state.sessions[-1]
        dash_cpi    = last["cpi"]
        dash_scores = last["scores"]
        level       = get_level(dash_cpi)
        bdi         = calc_bdi(st.session_state.sessions)

        col_g, col_r = st.columns([1, 1])
        with col_g:
            st.markdown(f"""
            <div style="text-align:center; padding:24px; background:white;
                        border:1px solid #E5E7EB; border-radius:12px; height:100%">
                <div style="font-size:12px; color:#6B7280; margin-bottom:4px">{t('last_cpi')}</div>
                {gauge_svg(dash_cpi)}
                <div style="font-size:14px; font-weight:700; color:{level['color']}; margin-top:6px">{level['label']}</div>
                <div style="font-size:11px; color:#9CA3AF; margin-top:4px">{last['label']} · {last['date']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_r:
            st.markdown(
                f'<div class="radar-wrap" style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:16px;">'
                f'{radar_svg(dash_scores, 240)}</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f'<div class="cpi-card"><div style="font-size:14px;font-weight:700;margin-bottom:14px">{t("dim_detail")}</div>', unsafe_allow_html=True)
        for k in DIM_KEYS:
            v = dash_scores.get(k, 0)
            pct = (v / 4) * 100
            color = DIMS_DATA[k]["color"]
            name = DIMS_DATA[k][lang]["name"]
            icon = "🔴" if v <= 2 else ("🔵" if v == 3 else "🟢")
            st.markdown(f"""
            <div style="margin-bottom:14px">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px">
                    <span style="font-size:13px; font-weight:600">{name} ({k})</span>
                    <span style="font-size:13px; font-weight:700; color:{color}; font-family:monospace">{v}/4 {icon}</span>
                </div>
                <div class="prog-wrap"><div class="prog-bar" style="width:{pct}%; background:{color}"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if bdi is not None:
            bdi_color = "#10B981" if bdi >= 75 else ("#3B82F6" if bdi >= 50 else "#EF4444")
            st.markdown(f"""
            <div class="bdi-card">
                <div>
                    <div style="font-size:13px; color:#7C3AED; font-weight:600">{t('bdi_title')}</div>
                    <div style="font-size:11px; color:#9CA3AF; margin-top:2px">{t('bdi_sub')}</div>
                </div>
                <div class="bdi-val" style="color:{bdi_color}">{bdi}%</div>
            </div>
            """, unsafe_allow_html=True)

        if len(st.session_state.sessions) >= 2:
            st.markdown(f'<div class="cpi-card"><div style="font-size:14px;font-weight:700;margin-bottom:12px">{t("trend_title")}</div>', unsafe_allow_html=True)
            st.markdown(trend_svg(st.session_state.sessions), unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:11px;color:#9CA3AF;margin-top:8px">{len(st.session_state.sessions)} {t("sessions_recorded")}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        weak = [k for k in DIM_KEYS if dash_scores.get(k, 0) <= 2]
        st.markdown(f'<div class="cpi-card"><div style="font-size:14px;font-weight:700;margin-bottom:12px">{t("recs_title")}</div>', unsafe_allow_html=True)
        if not weak:
            st.markdown(f'<div style="font-size:13px;color:#10B981;font-weight:600">{t("recs_all_good")}</div>', unsafe_allow_html=True)
        else:
            for k in weak:
                name, color, rec_text = RECS[k][lang]
                st.markdown(f"""
                <div class="rec-card">
                    <div style="font-weight:700;color:{color};margin-bottom:3px">{name}</div>
                    <div style="color:#92400E">{rec_text}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  TAB 3 — HISTORY
# ════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.sessions:
        st.markdown(f"""
        <div style="text-align:center; color:#9CA3AF; padding:60px 20px;">
            <div style="font-size:48px; margin-bottom:12px">🗂️</div>
            <div>{t('no_sessions')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_h, col_del = st.columns([3, 1])
        with col_h:
            st.markdown(f'<div style="font-size:14px;font-weight:700;padding:8px 0">{len(st.session_state.sessions)} {t("sessions_recorded")}</div>', unsafe_allow_html=True)
        with col_del:
            if st.button(t("delete_all"), type="secondary"):
                st.session_state.sessions = []
                st.rerun()

        report_all_html = generate_report_html(st.session_state.sessions[-1], st.session_state.sessions, lang)
        b64_all = base64.b64encode(report_all_html.encode("utf-8")).decode()
        filename_all = f"CPI_Report_{lang}_{datetime.datetime.now().strftime('%Y%m%d')}.html"
        st.markdown(
            f'<a href="data:text/html;base64,{b64_all}" download="{filename_all}"'
            f' style="display:block;text-align:center;background:#0F172A;color:white;'
            f'padding:10px 20px;border-radius:8px;text-decoration:none;'
            f'font-weight:600;font-size:13px;margin-bottom:16px">'
            f'{t("export_all")}</a>',
            unsafe_allow_html=True
        )

        for s in reversed(st.session_state.sessions):
            lvl = get_level(s["cpi"])
            tags_html = "".join(
                f'<span class="dim-tag"><span style="color:{DIMS_DATA[k]["color"]}">{k}</span> '
                f'<span style="color:#6B7280">{s["scores"].get(k,0)}/4</span></span>'
                for k in DIM_KEYS
            )
            session_html = generate_report_html(s, st.session_state.sessions, lang)
            b64 = base64.b64encode(session_html.encode("utf-8")).decode()
            safe_label = s["label"].replace(" ", "_")[:30]
            filename = f"CPI_{lang}_{safe_label}_{s['date'][:10]}.html"
            st.markdown(f"""
            <div class="session-card">
                <div class="session-header">
                    <div>
                        <div class="session-name">{s['label']}</div>
                        <div class="session-date">{s['date']}</div>
                    </div>
                    <div class="session-cpi" style="background:{lvl['color']}18; color:{lvl['color']}">{s['cpi']}%</div>
                </div>
                <div style="margin-bottom:8px">{tags_html}</div>
                <a href="data:text/html;base64,{b64}" download="{filename}"
                   style="display:inline-block;background:#F8FAFC;border:1px solid #E5E7EB;
                          color:#374151;padding:5px 12px;border-radius:6px;text-decoration:none;
                          font-size:12px;font-weight:600">{t('export_session')}</a>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  TAB 4 — FACILITATOR
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
    <div style="background:#0F172A; color:white; border-radius:12px; padding:18px 22px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <div style="width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,#2563EB,#7C3AED);
                        display:flex;align-items:center;justify-content:center;font-size:18px">🧠</div>
            <div>
                <div style="font-weight:700;font-size:15px">{t('tab_facilitator')}</div>
                <div style="font-size:11px;color:#94A3B8">Powered by Claude AI · Anthropic</div>
            </div>
        </div>
        <div style="font-size:12px;color:#CBD5E1;line-height:1.7">{t('fac_sub')}</div>
    </div>
    """, unsafe_allow_html=True)

    api_key_input = st.text_input(
        t("api_key_label"),
        value=st.session_state.api_key,
        type="password",
        placeholder=t("api_key_ph"),
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    mode_options = list(FAC_MODES.keys())
    mode_labels  = [FAC_MODES[k][lang]["label"] for k in mode_options]

    selected_idx = st.radio(
        t("fac_mode_label"),
        options=range(len(mode_options)),
        format_func=lambda i: mode_labels[i],
        index=mode_options.index(st.session_state.fac_mode),
        horizontal=True,
        label_visibility="collapsed",
    )
    new_mode = mode_options[selected_idx]
    if new_mode != st.session_state.fac_mode:
        st.session_state.fac_mode = new_mode
        st.session_state.fac_msgs = []
        st.rerun()

    st.markdown("---")

    for msg in st.session_state.fac_msgs:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-ai"><div class="msg-ai-label">🧠 {t("tab_facilitator")}</div>{msg["content"]}</div>', unsafe_allow_html=True)

    mode_cfg = FAC_MODES[st.session_state.fac_mode]
    user_input = st.text_area(
        "",
        placeholder=mode_cfg[lang]["ph"],
        height=120,
        label_visibility="collapsed",
        key="fac_input_area",
    )

    col_send, col_clear = st.columns([3, 1])
    with col_send:
        send_clicked = st.button(t("send_btn"), type="primary", use_container_width=True)
    with col_clear:
        if st.button(t("clear_btn"), use_container_width=True):
            st.session_state.fac_msgs = []
            st.rerun()

    if send_clicked:
        if not st.session_state.api_key:
            st.error(t("error_no_key"))
        elif not user_input.strip():
            st.warning(t("error_no_input"))
        else:
            system_key = f"system_{lang}"
            system_prompt = mode_cfg[system_key]
            st.session_state.fac_msgs.append({"role": "user", "content": user_input.strip()})
            with st.spinner(t("fac_thinking")):
                reply = call_claude(
                    messages=st.session_state.fac_msgs,
                    system_prompt=system_prompt,
                    api_key=st.session_state.api_key,
                )
            st.session_state.fac_msgs.append({"role": "assistant", "content": reply})
            st.rerun()

# ════════════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; font-size:11px; color:#D1D5DB; margin-top:40px; padding:20px 0;">
    {t('footer')}
</div>
""", unsafe_allow_html=True)
