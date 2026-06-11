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
    "tab_charter": {
        "ar": "📜 الميثاق",
        "en": "📜 Charter",
        "fr": "📜 Charte",
    },
    # ── Charter ────────────────────────────────────────────────────
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
        "ar": "انطلاقاً من أن الابتكار الحقيقي لا ينتج عن تجميع المعارف الفردية بصورة منفصلة، بل عن التفاعل المنهجي بينها وتحويل الاختلافات المعرفية إلى طاقة إبداعية مشتركة — نعتمد هذا الميثاق عقداً معرفياً وأخلاقياً وتشغيلياً لفريقنا.",
        "en": "True innovation in cross-disciplinary teams does not arise from aggregating knowledge separately, but from its systematic interaction — transforming cognitive differences into shared creative energy. We adopt this Charter as a cognitive, ethical, and operational contract.",
        "fr": "La véritable innovation ne provient pas de l'agrégation des connaissances individuelles, mais de leur interaction systématique — transformant les différences cognitives en énergie créative partagée. Nous adoptons cette Charte comme contrat cognitif, éthique et opérationnel.",
    },
    "charter_axiom": {
        "ar": "التواضع المعرفي ليس مجرد فضيلة أخلاقية، بل بنية تشغيلية لازمة لظهور الذكاء الجماعي.",
        "en": "Epistemic humility is not merely an ethical virtue — it is an operational structure necessary for collective intelligence to emerge.",
        "fr": "L'humilité épistémique n'est pas seulement une vertu éthique — c'est une structure opérationnelle nécessaire à l'émergence de l'intelligence collective.",
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
        "ar": "التزامك مُسجَّل — يمكنك الانتقال إلى تقييم الجلسة.",
        "en": "Commitment recorded — proceed to the session assessment.",
        "fr": "Engagement enregistré — passez à l'évaluation de séance.",
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
    direction  = "rtl" if lang == "ar" else "ltr"
    text_align = "right" if lang == "ar" else "left"
    ml = "left"  if lang == "ar" else "right"
    mr = "right" if lang == "ar" else "left"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
/* ── Reset & Base ── */
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans Arabic', 'IBM Plex Sans', 'Segoe UI', sans-serif !important;
    direction: {direction};
    background: #F8FAFC;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
/* ── Radio group (language selector) ── */
div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    gap: 8px !important;
    flex-wrap: nowrap !important;
}}
div[role="radiogroup"] label {{
    flex: 1 !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 10px 6px !important;
    text-align: center !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    background: white !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}}
div[role="radiogroup"] label:has(input:checked) {{
    background: linear-gradient(135deg, #EFF6FF, #E0ECFF) !important;
    border-color: #2563EB !important;
    color: #1D4ED8 !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.2) !important;
}}
div[role="radiogroup"] input[type="radio"] {{ display: none !important; }}
/* ── Header ── */
.cpi-header {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: white;
    padding: 20px 28px 16px;
    border-radius: 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px rgba(15,23,42,0.3);
    border: 1px solid rgba(255,255,255,0.05);
}}
.cpi-header h1 {{ font-size: 20px; font-weight: 800; margin: 0; letter-spacing: -0.3px; }}
.cpi-header p  {{ font-size: 11px; color: #94A3B8; margin: 5px 0 0; }}
.cpi-formula {{
    background: linear-gradient(135deg, #1E3A5F, #1E3056);
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 13px;
    color: #7DD3FC;
    font-weight: 700;
    font-family: monospace;
    letter-spacing: 1.5px;
    border: 1px solid rgba(125,211,252,0.2);
    white-space: nowrap;
}}
/* ── Cards ── */
.cpi-card {{
    background: white;
    border: 1px solid #E8EDF5;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}}
.cpi-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
/* ── Dimension cards ── */
.dim-card {{
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 14px;
    border: 1.5px solid #E8EDF5;
    background: linear-gradient(135deg, #FAFBFF, #F8FAFC);
    transition: all 0.2s ease;
}}
.dim-card:hover {{
    border-color: #BFDBFE;
    box-shadow: 0 2px 12px rgba(37,99,235,0.08);
    transform: translateY(-1px);
}}
.dim-title {{ font-size: 17px; font-weight: 700; }}
.dim-desc  {{ font-size: 12px; color: #94A3B8; margin: 3px 0 8px; line-height: 1.5; }}
.dim-q     {{ font-size: 13px; color: #374151; font-style: italic; margin-bottom: 10px; }}
/* ── Level badges ── */
.level-0 {{ background: linear-gradient(135deg,#FEF2F2,#FFF5F5); color:#DC2626; border:1.5px solid #FECACA; }}
.level-1 {{ background: linear-gradient(135deg,#FFFBEB,#FFFDF0); color:#D97706; border:1.5px solid #FDE68A; }}
.level-2 {{ background: linear-gradient(135deg,#EFF6FF,#F0F7FF); color:#2563EB; border:1.5px solid #BFDBFE; }}
.level-3 {{ background: linear-gradient(135deg,#F0FDF4,#F0FFF5); color:#059669; border:1.5px solid #A7F3D0; }}
/* ── Sliders ── */
div[data-testid="stSlider"] > div > div > div {{ direction: ltr !important; }}
div[data-testid="stSlider"] > label {{ direction: {direction} !important; }}
div[data-testid="stSlider"] {{ padding: 0 4px !important; }}
/* ── Gauge container ── */
.gauge-wrap {{
    background: linear-gradient(135deg, #F0F7FF, #EBF4FF);
    border: 1px solid #BFDBFE;
    border-radius: 14px;
    padding: 22px 16px 16px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(37,99,235,0.08);
}}
/* ── Radar container ── */
.radar-wrap {{
    display: flex;
    justify-content: center;
    padding: 12px 0;
    background: white;
    border: 1px solid #E8EDF5;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
/* ── Progress bars ── */
.prog-wrap {{
    height: 8px;
    background: #F1F5F9;
    border-radius: 100px;
    overflow: hidden;
    margin-top: 5px;
}}
.prog-bar {{
    height: 100%;
    border-radius: 100px;
    transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}}
/* ── BDI card ── */
.bdi-card {{
    background: linear-gradient(135deg, #F5F3FF, #EDE9FE);
    border: 1px solid #DDD6FE;
    border-radius: 14px;
    padding: 18px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(124,58,237,0.08);
}}
.bdi-val {{
    font-size: 34px;
    font-weight: 800;
    font-family: monospace;
    letter-spacing: -1px;
}}
/* ── Recommendation cards ── */
.rec-card {{
    background: linear-gradient(135deg, #FFFBEB, #FFF8E1);
    border: 1px solid #FCD34D;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 13px;
    box-shadow: 0 1px 4px rgba(251,191,36,0.12);
}}
/* ── Session history cards ── */
.session-card {{
    background: white;
    border: 1px solid #E8EDF5;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    transition: all 0.2s;
}}
.session-card:hover {{
    border-color: #BFDBFE;
    box-shadow: 0 4px 14px rgba(37,99,235,0.1);
    transform: translateY(-1px);
}}
.session-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }}
.session-name   {{ font-weight:700; font-size:15px; color:#1E293B; }}
.session-date   {{ font-size:11px; color:#94A3B8; margin-top:3px; }}
.session-cpi    {{
    font-size: 22px;
    font-weight: 800;
    font-family: monospace;
    padding: 5px 14px;
    border-radius: 10px;
    letter-spacing: -0.5px;
}}
.dim-tag {{
    display: inline-block;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    margin-{ml}: 6px;
    margin-bottom: 5px;
}}
/* ── Chat messages (facilitator) ── */
.msg-user {{
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: white;
    border-radius: {"12px 12px 4px 12px" if direction=="rtl" else "12px 12px 12px 4px"};
    padding: 12px 16px;
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 12px;
    max-width: 88%;
    margin-{"right" if direction=="rtl" else "left"}: auto;
    box-shadow: 0 2px 10px rgba(37,99,235,0.25);
}}
.msg-ai {{
    background: white;
    color: #111827;
    border: 1px solid #E8EDF5;
    border-radius: {"12px 12px 12px 4px" if direction=="rtl" else "4px 12px 12px 12px"};
    padding: 12px 16px;
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 12px;
    max-width: 88%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.msg-ai-label {{
    font-size: 10px;
    color: #7C3AED;
    font-weight: 700;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
}}
/* ── Streamlit overrides ── */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    border-radius: 10px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-family: inherit !important;
    transition: border-color 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: #F8FAFC;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #E8EDF5;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
}}
.stTabs [aria-selected="true"] {{
    background: white !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}}
div[data-testid="stAlert"] {{
    border-radius: 10px !important;
}}
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
# اختصارات التسميات للرادار — قصيرة وواضحة على الموبايل
RADAR_LABELS = {
    "P":  {"ar": "الممارسة", "en": "Practice",    "fr": "Pratique"},
    "L":  {"ar": "اللغة",    "en": "Language",    "fr": "Langage"},
    "G":  {"ar": "التوجيه",  "en": "Guidance",    "fr": "Orientation"},
    "EH": {"ar": "التواضع",  "en": "Humility",    "fr": "Humilité"},
}
# ألوان متدرجة لكل مستوى في الرادار
RADAR_RING_COLORS = ["#F3F4F6", "#E9EBF5", "#D4D9F0", "#BFC6EA"]
def radar_svg(scores, size=280):
    """رادار محسّن: canvas أكبر، تدرج لوني للحلقات، تسميات مختصرة واضحة."""
    lang = st.session_state.get("lang", "ar")
    # مساحة داخلية لتجنب اقتطاع التسميات
    pad   = 52
    cx    = cy = size / 2
    r     = (size / 2) - pad
    n     = len(DIM_KEYS)
    colors = [DIMS_DATA[k]["color"] for k in DIM_KEYS]
    def angle(i):  return math.pi * 2 * i / n - math.pi / 2
    def pt(i, val):
        a = angle(i); d = (val / 4) * r
        return cx + d * math.cos(a), cy + d * math.sin(a)
    def ring_pts(v):
        pts = []
        for i in range(n):
            a = angle(i); d = (v / 4) * r
            pts.append(f"{cx + d*math.cos(a):.1f},{cy + d*math.sin(a):.1f}")
        return " ".join(pts)
    svg = [
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">'
    ]
    # ── حلقات خلفية متدرجة اللون ──
    for idx, v in enumerate([4, 3, 2, 1]):
        fill = RADAR_RING_COLORS[idx]
        svg.append(f'<polygon points="{ring_pts(v)}" fill="{fill}" stroke="#D1D5DB" stroke-width="0.8"/>')
    # ── خطوط المحاور ──
    for i in range(n):
        a  = angle(i)
        x2 = cx + r * math.cos(a)
        y2 = cy + r * math.sin(a)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="#C7CDE8" stroke-width="1" stroke-dasharray="4 3"/>')
    # ── نقاط التدريج على المحاور ──
    for v_tick in [1, 2, 3, 4]:
        for i in range(n):
            a  = angle(i)
            tx = cx + (v_tick / 4) * r * math.cos(a)
            ty = cy + (v_tick / 4) * r * math.sin(a)
            svg.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2" fill="#C7CDE8"/>')
    # ── المضلع المملوء ──
    filled_pts = []
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        filled_pts.append(f"{x:.1f},{y:.1f}")
    svg.append(
        f'<polygon points="{" ".join(filled_pts)}" '
        f'fill="rgba(37,99,235,0.18)" stroke="#2563EB" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
    )
    # ── نقاط ملونة على رأس كل محور ──
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        c = colors[i]
        # ظل خفيف
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{c}" opacity="0.15"/>')
        # النقطة الأساسية
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{c}" stroke="white" stroke-width="2"/>')
        # القيمة داخل النقطة
        svg.append(
            f'<text x="{x:.1f}" y="{y+1:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-size="7" font-weight="700" fill="white">{v}</text>'
        )
    # ── التسميات الخارجية — مختصرة ومضمونة ──
    label_offset = r + 32
    for i, k in enumerate(DIM_KEYS):
        a  = angle(i)
        lx = cx + label_offset * math.cos(a)
        ly = cy + label_offset * math.sin(a)
        c  = colors[i]
        short_name = RADAR_LABELS[k][lang]
        key_label  = k
        # خلفية صغيرة للتسمية
        svg.append(
            f'<rect x="{lx-28:.1f}" y="{ly-11:.1f}" width="56" height="22" '
            f'rx="6" fill="{c}" opacity="0.12"/>'
        )
        # النص الرئيسي
        svg.append(
            f'<text x="{lx:.1f}" y="{ly+1:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-size="11" font-weight="700" fill="{c}" '
            f'font-family="IBM Plex Sans Arabic, IBM Plex Sans, sans-serif">'
            f'{short_name}</text>'
        )
    # ── نقطة المركز ──
    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="#94A3B8"/>')
    svg.append("</svg>")
    return "\n".join(svg)
def trend_svg(sessions, w=320, h=90):
    if len(sessions) < 2:
        return ""
    vals = [s["cpi"] for s in sessions if s.get("cpi")]
    if len(vals) < 2:
        return ""
    pad   = 16
    min_v = max(0,   min(vals) - 10)
    max_v = min(100, max(vals) + 10)
    def x(i): return pad + (i / (len(vals) - 1)) * (w - pad * 2)
    def y(v):
        if max_v == min_v: return h / 2
        return h - pad - ((v - min_v) / (max_v - min_v)) * (h - pad * 2)
    # خط الحد لمنطقة التعبئة
    area_pts = f"{x(0):.1f},{h} "
    area_pts += " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    area_pts += f" {x(len(vals)-1):.1f},{h}"
    svg = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg" style="width:100%;overflow:visible">'
    ]
    # تعريف التدرج
    svg.append("""
    <defs>
      <linearGradient id="tgrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%"   stop-color="#2563EB" stop-opacity="0.2"/>
        <stop offset="100%" stop-color="#2563EB" stop-opacity="0.02"/>
      </linearGradient>
    </defs>""")
    # خطوط مرجعية
    for v_ref in [40, 65, 85]:
        yr = y(v_ref)
        if pad <= yr <= h - pad:
            svg.append(f'<line x1="{pad}" y1="{yr:.1f}" x2="{w-pad}" y2="{yr:.1f}" '
                       f'stroke="#E2E8F0" stroke-width="1" stroke-dasharray="4 3"/>')
            svg.append(f'<text x="{w-pad+4}" y="{yr+4:.1f}" font-size="9" fill="#94A3B8" font-family="monospace">{v_ref}%</text>')
    # منطقة التعبئة
    svg.append(f'<polygon points="{area_pts}" fill="url(#tgrad)"/>')
    # الخط
    line_pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    svg.append(f'<polyline points="{line_pts}" fill="none" stroke="#2563EB" '
               f'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    # النقاط والقيم
    for i, v in enumerate(vals):
        c = get_level(v)["color"]
        xi, yi = x(i), y(v)
        svg.append(f'<circle cx="{xi:.1f}" cy="{yi:.1f}" r="5" fill="{c}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{xi:.1f}" y="{yi-10:.1f}" text-anchor="middle" '
                   f'font-size="9" font-weight="700" fill="{c}" font-family="monospace">{v}%</text>')
    svg.append("</svg>")
    return "\n".join(svg)
def gauge_svg(value):
    if value is None:
        return ""
    level  = get_level(value)
    color  = level["color"]
    circ   = math.pi * 58
    dash   = (value / 100) * circ
    # حساب نقطة نهاية القوس للمؤشر
    angle_deg = 180 - (value / 100) * 180
    angle_rad = math.radians(angle_deg)
    needle_x  = 88 + 46 * math.cos(math.radians(180 - (value/100)*180))
    needle_y  = 84 - 46 * math.sin(math.radians(180 - (value/100)*180))
    return f"""
<svg width="176" height="100" viewBox="0 0 176 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ggrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#EF4444"/>
      <stop offset="40%"  stop-color="#F59E0B"/>
      <stop offset="70%"  stop-color="#3B82F6"/>
      <stop offset="100%" stop-color="#10B981"/>
    </linearGradient>
  </defs>
  <!-- Track -->
  <path d="M 18 84 A 70 70 0 0 1 158 84"
        fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round"/>
  <!-- Colored arc -->
  <path d="M 18 84 A 70 70 0 0 1 158 84"
        fill="none" stroke="url(#ggrad)" stroke-width="14"
        stroke-linecap="round" opacity="0.25"/>
  <!-- Active arc -->
  <path d="M 18 84 A 70 70 0 0 1 158 84"
        fill="none" stroke="{color}" stroke-width="14"
        stroke-linecap="round"
        stroke-dasharray="{dash:.1f} {circ:.1f}"/>
  <!-- Needle dot -->
  <circle cx="{needle_x:.1f}" cy="{needle_y:.1f}" r="5" fill="{color}" opacity="0.9"/>
  <!-- Value -->
  <text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827"
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
if "signatories" not in st.session_state: st.session_state.signatories = []
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t("tab_assess"),
    t("tab_dashboard"),
    f"{t('tab_history')} ({len(st.session_state.sessions)})",
    t("tab_facilitator"),
    t("tab_charter"),
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
        border_color = d["color"] + "44" if current > 0 else "#E8EDF5"
        bg_color     = d["color"] + "08" if current > 0 else "#FAFBFF"
        name = d[lang]["name"]
        desc = d[lang]["desc"]
        q    = d[lang]["q"]
        st.markdown(f"""
        <div style="background:{bg_color}; border:1.5px solid {border_color};
                    border-radius:14px; padding:16px 20px; margin-bottom:6px;
                    transition:all 0.2s; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                <div style="background:{d['color']}18; color:{d['color']}; font-weight:800;
                             font-size:12px; padding:3px 12px; border-radius:20px;
                             border:1px solid {d['color']}30; letter-spacing:0.5px">{k}</div>
                <span style="font-size:16px; font-weight:800; color:{d['color']}">{name}</span>
                {"<span style='margin-right:auto;font-size:20px;font-weight:800;font-family:monospace;color:" + d['color'] + "'>" + str(current) + "/4</span>" if current > 0 else ""}
            </div>
            <div style="font-size:12px; color:#94A3B8; margin-bottom:5px; line-height:1.5">{desc}</div>
            <div style="font-size:13px; color:#475569; font-style:italic;
                        background:rgba(255,255,255,0.7); border-radius:8px;
                        padding:6px 12px; border-right:3px solid {d['color']}">«{q}»</div>
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
            <div class="gauge-wrap">
                <div style="font-size:11px;font-weight:600;color:#64748B;letter-spacing:0.5px;margin-bottom:6px;text-transform:uppercase">{t('cpi_computed')}</div>
                {gauge_svg(cpi_now)}
                <div style="font-size:14px;font-weight:800;color:{level['color']};margin-top:8px;
                            background:{level['color']}15;padding:6px 16px;border-radius:20px;display:inline-block">
                    {level['label']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_radar:
            st.markdown(
                f'<div class="radar-wrap">{radar_svg(st.session_state.scores, 280)}</div>',
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
            <div class="gauge-wrap" style="height:100%">
                <div style="font-size:11px;font-weight:600;color:#64748B;letter-spacing:0.5px;margin-bottom:6px;text-transform:uppercase">{t('last_cpi')}</div>
                {gauge_svg(dash_cpi)}
                <div style="font-size:14px;font-weight:800;color:{level['color']};margin-top:8px;
                            background:{level['color']}15;padding:6px 16px;border-radius:20px;display:inline-block">
                    {level['label']}
                </div>
                <div style="font-size:11px;color:#94A3B8;margin-top:8px">{last['label']} · {last['date']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_r:
            st.markdown(
                f'<div class="radar-wrap">{radar_svg(dash_scores, 280)}</div>',
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="cpi-card"><div style="font-size:14px;font-weight:800;color:#1E293B;margin-bottom:16px">{t("dim_detail")}</div>', unsafe_allow_html=True)
        for k in DIM_KEYS:
            v     = dash_scores.get(k, 0)
            pct   = (v / 4) * 100
            color = DIMS_DATA[k]["color"]
            name  = DIMS_DATA[k][lang]["name"]
            icons = {1:"🔴", 2:"🟡", 3:"🔵", 4:"🟢"}
            icon  = icons.get(v, "⚪")
            action = RECS[k][lang][2] if v <= 2 else ("" )
            st.markdown(f"""
            <div style="margin-bottom:16px; padding:14px 16px; background:#FAFBFF;
                        border-radius:10px; border:1px solid #E8EDF5">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
                    <div style="display:flex;align-items:center;gap:8px">
                        <span style="background:{color}18;color:{color};font-weight:800;
                                     font-size:11px;padding:2px 10px;border-radius:20px">{k}</span>
                        <span style="font-size:14px;font-weight:700;color:#1E293B">{name}</span>
                    </div>
                    <span style="font-size:16px;font-weight:800;font-family:monospace;color:{color}">{v}/4 {icon}</span>
                </div>
                <div class="prog-wrap">
                    <div class="prog-bar" style="width:{pct}%;background:linear-gradient(90deg,{color}88,{color})"></div>
                </div>
                {"<div style='font-size:11px;color:#94A3B8;margin-top:6px;font-style:italic'>→ " + action + "</div>" if action else ""}
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
                f'<span class="dim-tag">'
                f'<span style="color:{DIMS_DATA[k]["color"]};font-weight:700">{k}</span> '
                f'<span style="color:#64748B">{s["scores"].get(k,0)}/4</span></span>'
                for k in DIM_KEYS
            )
            # Progress mini bars
            bars_html = ""
            for k in DIM_KEYS:
                v   = s["scores"].get(k, 0)
                pct = (v / 4) * 100
                c   = DIMS_DATA[k]["color"]
                bars_html += f'<div style="flex:1"><div style="font-size:9px;color:#94A3B8;margin-bottom:2px;font-weight:600">{k}</div><div class="prog-wrap"><div class="prog-bar" style="width:{pct}%;background:{c}"></div></div></div>'
            session_html = generate_report_html(s, st.session_state.sessions, lang)
            b64      = base64.b64encode(session_html.encode("utf-8")).decode()
            safe_lbl = s["label"].replace(" ", "_")[:30]
            filename = f"CPI_{lang}_{safe_lbl}_{s['date'][:10]}.html"
            st.markdown(f"""
            <div class="session-card">
                <div class="session-header">
                    <div>
                        <div class="session-name">{s['label']}</div>
                        <div class="session-date">📅 {s['date']}</div>
                    </div>
                    <div class="session-cpi {lvl['cls']}">{s['cpi']}%</div>
                </div>
                <div style="display:flex;gap:8px;margin-bottom:12px">{bars_html}</div>
                <div style="margin-bottom:10px">{tags_html}</div>
                <a href="data:text/html;base64,{b64}" download="{filename}"
                   style="display:inline-flex;align-items:center;gap:6px;
                          background:linear-gradient(135deg,#F8FAFC,#F1F5F9);
                          border:1px solid #E2E8F0;color:#374151;
                          padding:6px 14px;border-radius:8px;text-decoration:none;
                          font-size:12px;font-weight:600;transition:all 0.2s">
                    📄 {t('export_session')}
                </a>
            </div>
            """, unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════
#  TAB 4 — FACILITATOR
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0F172A,#1E293B); color:white;
                border-radius:16px; padding:20px 24px; margin-bottom:16px;
                box-shadow:0 4px 16px rgba(15,23,42,0.2)">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
            <div style="width:40px;height:40px;border-radius:10px;
                        background:linear-gradient(135deg,#2563EB,#7C3AED);
                        display:flex;align-items:center;justify-content:center;font-size:20px">🧠</div>
            <div>
                <div style="font-weight:800;font-size:16px">{t('tab_facilitator')}</div>
                <div style="font-size:11px;color:#94A3B8">Powered by Claude AI · Anthropic</div>
            </div>
        </div>
        <div style="font-size:13px;color:#CBD5E1;line-height:1.7;
                    background:rgba(255,255,255,0.05);border-radius:10px;padding:10px 14px">
            {t('fac_sub')}
        </div>
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
#  TAB 5 — CHARTER
# ════════════════════════════════════════════════════════════════════
CHARTER_PRINCIPLES = {
    "ar": [
        {
            "key": "EH", "icon": "🤝", "color": "#DC2626",
            "title": "التواضع المعرفي",
            "body": "نلتزم باعتبار القدرة على مراجعة الرأي وتحديث القناعات بناءً على الأدلة الجديدة معياراً للنضج المعرفي. لا توجد معرفة مكتملة داخل مجال منفرد.",
            "commit": "أتعهد بأن أستقبل النقد بوصفه هبة معرفية، لا تهديداً شخصياً.",
        },
        {
            "key": "L",  "icon": "💬", "color": "#059669",
            "title": "اللغة المشتركة",
            "body": "نلتزم ببناء جسر لغوي بين تخصصاتنا. كل مصطلح متخصص نستخدمه هو مسؤوليتنا أن نبسّطه للآخرين. اللغة بنية تحتية للتكامل، لا أداة للإقصاء.",
            "commit": "أتعهد بألا أحتكر مصطلحات تخصصي، وأن أبني قاموساً مشتركاً مع زملائي.",
        },
        {
            "key": "P",  "icon": "⚙️", "color": "#2563EB",
            "title": "الممارسة التشاركية",
            "body": "لا نكتفي بتقديم مخرجات تخصصنا، بل نسعى لفهم أولويات الزملاء والقيود الواقعية للتطبيق. كل قرار يأخذ في الاعتبار منطق التخصصات الأخرى.",
            "commit": "أتعهد بأن أفهم أولويات زملائي قبل اتخاذ أي قرار يؤثر على عملهم.",
        },
        {
            "key": "G",  "icon": "🌊", "color": "#7C3AED",
            "title": "التوجيه الميداني",
            "body": "نؤمن أن أفضل الأفكار تأتي من قلب الممارسة الميدانية. الأجندة تُشكَّل من الأسفل، لا تُملى من الأعلى. صوت الميدان هو البوصلة.",
            "commit": "أتعهد بأن أرفع صوتي بالتحديات الحقيقية التي أواجهها في الميدان.",
        },
        {
            "key": "S",  "icon": "🛡️", "color": "#0891B2",
            "title": "السلامة المعرفية",
            "body": "نضمن بيئة يشعر فيها كل عضو بالأمان لطرح الأفكار غير المكتملة، والاعتراف بعدم المعرفة، وتغيير الرأي. النقد يستهدف الأفكار لا الأشخاص.",
            "commit": "أتعهد بأن أحمي هذه البيئة الآمنة لكل من يشاركني هذه الجلسة.",
        },
    ],
    "en": [
        {
            "key": "EH", "icon": "🤝", "color": "#DC2626",
            "title": "Epistemic Humility",
            "body": "We commit to treating the ability to revise opinions and update convictions based on new evidence as a mark of cognitive maturity. No knowledge is complete within a single discipline.",
            "commit": "I commit to receiving critique as a cognitive gift, not a personal threat.",
        },
        {
            "key": "L",  "icon": "💬", "color": "#059669",
            "title": "Shared Language",
            "body": "We commit to building a linguistic bridge between our disciplines. Every specialized term we use is our responsibility to simplify for others. Language is infrastructure for integration, not a tool for exclusion.",
            "commit": "I commit to not monopolizing my discipline's terminology and to building a shared glossary with my colleagues.",
        },
        {
            "key": "P",  "icon": "⚙️", "color": "#2563EB",
            "title": "Participatory Practice",
            "body": "We do not limit ourselves to delivering outputs from our own discipline. We seek to understand our colleagues' priorities and the practical constraints of implementation. Every decision considers the logic of other disciplines.",
            "commit": "I commit to understanding my colleagues' priorities before making any decision that affects their work.",
        },
        {
            "key": "G",  "icon": "🌊", "color": "#7C3AED",
            "title": "Field-Driven Guidance",
            "body": "We believe the best ideas emerge from the heart of field practice. The agenda is shaped from the bottom up, not dictated from above. The field's voice is the compass.",
            "commit": "I commit to raising my voice about the real challenges I face in the field.",
        },
        {
            "key": "S",  "icon": "🛡️", "color": "#0891B2",
            "title": "Cognitive Safety",
            "body": "We guarantee an environment where every member feels safe to share incomplete ideas, admit lack of knowledge, and change their mind. Critique targets ideas, not people.",
            "commit": "I commit to protecting this safe environment for everyone sharing this session with me.",
        },
    ],
    "fr": [
        {
            "key": "EH", "icon": "🤝", "color": "#DC2626",
            "title": "Humilité épistémique",
            "body": "Nous nous engageons à considérer la capacité à réviser ses opinions comme une marque de maturité cognitive. Aucune connaissance n'est complète dans une seule discipline.",
            "commit": "Je m'engage à recevoir la critique comme un cadeau cognitif, non comme une menace personnelle.",
        },
        {
            "key": "L",  "icon": "💬", "color": "#059669",
            "title": "Langage commun",
            "body": "Nous nous engageons à construire un pont linguistique entre nos disciplines. Chaque terme spécialisé doit être simplifié pour les autres. Le langage est une infrastructure d'intégration.",
            "commit": "Je m'engage à ne pas monopoliser la terminologie de ma discipline et à construire un glossaire partagé.",
        },
        {
            "key": "P",  "icon": "⚙️", "color": "#2563EB",
            "title": "Pratique participative",
            "body": "Nous cherchons à comprendre les priorités de nos collègues et les contraintes pratiques. Chaque décision prend en compte la logique des autres disciplines.",
            "commit": "Je m'engage à comprendre les priorités de mes collègues avant toute décision les concernant.",
        },
        {
            "key": "G",  "icon": "🌊", "color": "#7C3AED",
            "title": "Orientation terrain",
            "body": "Les meilleures idées émergent du cœur de la pratique terrain. L'agenda se construit de bas en haut. La voix du terrain est la boussole.",
            "commit": "Je m'engage à exprimer les vrais défis que je rencontre sur le terrain.",
        },
        {
            "key": "S",  "icon": "🛡️", "color": "#0891B2",
            "title": "Sécurité cognitive",
            "body": "Nous garantissons un environnement où chacun se sent libre de partager des idées incomplètes, d'admettre son ignorance et de changer d'avis. La critique vise les idées, pas les personnes.",
            "commit": "Je m'engage à protéger cet environnement sûr pour tous les participants.",
        },
    ],
}
with tab5:
    lang = st.session_state.lang
    principles = CHARTER_PRINCIPLES[lang]
    dir_style  = "rtl" if lang == "ar" else "ltr"
    # ── Header ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0F172A,#1E293B);color:white;
                border-radius:16px;padding:24px 28px;margin-bottom:20px;
                box-shadow:0 4px 20px rgba(15,23,42,0.25)">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <div style="font-size:28px">📜</div>
            <div>
                <div style="font-size:18px;font-weight:800">{t('charter_title')}</div>
                <div style="font-size:11px;color:#94A3B8;margin-top:3px">{t('charter_version')}</div>
            </div>
        </div>
        <div style="font-size:13px;color:#CBD5E1;line-height:1.8;
                    background:rgba(255,255,255,0.05);border-radius:10px;padding:12px 16px">
            {t('charter_preamble')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ── Axiom ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFF7ED,#FFFBEB);
                border:1.5px solid #FCD34D;border-radius:14px;
                padding:18px 22px;margin-bottom:22px;text-align:center">
        <div style="font-size:11px;font-weight:700;color:#92400E;
                    letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">
            {'المبدأ المحوري' if lang=='ar' else ('Core Axiom' if lang=='en' else 'Axiome central')}
        </div>
        <div style="font-size:15px;font-weight:700;color:#78350F;line-height:1.7">
            ❝ {t('charter_axiom')} ❞
        </div>
        <div style="font-size:12px;font-family:monospace;color:#B45309;
                    margin-top:10px;font-weight:600">CI = NK × EH</div>
    </div>
    """, unsafe_allow_html=True)
    # ── Five Principles ──
    title_5 = {'ar':'المبادئ الخمسة','en':'The Five Principles','fr':'Les Cinq Principes'}[lang]
    st.markdown(f'<div style="font-size:13px;font-weight:800;color:#1E293B;'
                f'letter-spacing:0.5px;text-transform:uppercase;margin-bottom:14px">'
                f'{title_5}</div>', unsafe_allow_html=True)
    for p in principles:
        c = p["color"]
        st.markdown(f"""
        <div style="border:1.5px solid {c}22;background:linear-gradient(135deg,{c}08,white);
                    border-radius:14px;padding:18px 22px;margin-bottom:14px;
                    border-right:4px solid {c}" >
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
                <div style="background:{c}18;border-radius:8px;
                            width:36px;height:36px;display:flex;align-items:center;
                            justify-content:center;font-size:18px">{p['icon']}</div>
                <div>
                    <span style="background:{c}18;color:{c};font-weight:800;
                                 font-size:11px;padding:2px 10px;border-radius:20px">{p['key']}</span>
                    <span style="font-size:15px;font-weight:800;color:{c};
                                 margin-{"right" if lang=="ar" else "left"}:8px">{p['title']}</span>
                </div>
            </div>
            <div style="font-size:13px;color:#374151;line-height:1.75;margin-bottom:10px">
                {p['body']}
            </div>
            <div style="background:{c}10;border-radius:8px;padding:8px 14px;
                        font-size:12px;color:{c};font-style:italic;font-weight:600;
                        border-right:3px solid {c}">
                {'«' if lang=='ar' else '"'} {p['commit']} {'»' if lang=='ar' else '"'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    # ── Signature area ──
    sign_title = t('charter_sign_title')
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#F0F7FF,#EBF4FF);
                border:1.5px solid #BFDBFE;border-radius:14px;
                padding:20px 24px;margin-bottom:16px">
        <div style="font-size:15px;font-weight:800;color:#1E3A5F;margin-bottom:6px">
            ✍️ {sign_title}
        </div>
        <div style="font-size:13px;color:#64748B;line-height:1.6">
            {'أدخل اسمك للتعبير عن التزامك بمبادئ الميثاق في هذه الجلسة.' if lang=="ar"
             else ('Enter your name to express your commitment to the Charter principles in this session.' if lang=="en"
             else 'Saisissez votre nom pour exprimer votre engagement envers les principes de cette Charte.')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_inp, col_btn = st.columns([3, 1])
    with col_inp:
        signer_name = st.text_input(
            t("charter_sign_ph"),
            placeholder=t("charter_sign_ph"),
            label_visibility="collapsed",
            key="signer_input",
        )
    with col_btn:
        if st.button(t("charter_sign_btn"), type="primary", use_container_width=True):
            name = signer_name.strip()
            if name:
                now_str = datetime.datetime.now().strftime("%H:%M")
                entry   = {"name": name, "time": now_str, "lang": lang}
                if not any(s["name"].lower() == name.lower()
                           for s in st.session_state.signatories):
                    st.session_state.signatories.append(entry)
                st.success(t("charter_signed_msg"))
                st.rerun()
            else:
                st.warning({"ar":"أدخل اسمك أولاً","en":"Please enter your name first","fr":"Veuillez saisir votre nom"}[lang])
    # ── Signatories list ──
    if st.session_state.signatories:
        st.markdown(f"""
        <div style="margin-top:8px">
            <div style="font-size:12px;font-weight:700;color:#64748B;
                        letter-spacing:0.5px;text-transform:uppercase;margin-bottom:10px">
                {t('charter_signatories')} ({len(st.session_state.signatories)})
            </div>
        </div>
        """, unsafe_allow_html=True)
        sig_html = ""
        for sig in st.session_state.signatories:
            sig_html += f"""
            <div style="display:inline-flex;align-items:center;gap:8px;
                        background:white;border:1px solid #E8EDF5;border-radius:10px;
                        padding:8px 14px;margin:4px;box-shadow:0 1px 4px rgba(0,0,0,0.05)">
                <div style="width:28px;height:28px;border-radius:50%;
                            background:linear-gradient(135deg,#2563EB,#7C3AED);
                            display:flex;align-items:center;justify-content:center;
                            font-size:12px;font-weight:700;color:white">
                    {sig['name'][0].upper()}
                </div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:#1E293B">{sig['name']}</div>
                    <div style="font-size:10px;color:#94A3B8">{sig['time']}</div>
                </div>
                <div style="font-size:14px">✅</div>
            </div>"""
        st.markdown(f'<div style="display:flex;flex-wrap:wrap">{sig_html}</div>',
                    unsafe_allow_html=True)
        col_c, col_g = st.columns([1, 2])
        with col_c:
            if st.button(t("charter_clear"), type="secondary", use_container_width=True):
                st.session_state.signatories = []
                st.rerun()
# ════════════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center; margin-top:48px; padding:24px 16px;
            background:linear-gradient(135deg,#0F172A,#1E293B);
            border-radius:16px; box-shadow:0 4px 16px rgba(15,23,42,0.15)">
    <div style="font-size:13px; font-weight:700; color:#E2E8F0; margin-bottom:6px">
        🧠 {t('footer')}
    </div>
    <div style="font-size:11px; color:#475569; font-family:monospace; letter-spacing:0.5px">
        CI = NK × EH · v2.0 · {datetime.datetime.now().strftime("%Y")}
    </div>
</div>
""", unsafe_allow_html=True)
