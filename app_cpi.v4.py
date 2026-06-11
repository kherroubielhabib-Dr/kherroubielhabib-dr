```python
#  ═══════════════════════════════════════════════════════════════════
#  مؤشر التلاقح المعرفي — CPI Dashboard (الإصدار v4.1 المدمج والسيادي)
#  Cross-Pollination Index · Indice de Pollinisation Croisée
#  المصمم المعرفي: الدكتور الحبيب خروبي · المعرف المرجعي: ESU-001
#  ═══════════════════════════════════════════════════════════════════

import streamlit as st
import json
import math
import datetime
import requests
import base64
import os
import tempfile
import subprocess
import pandas as pd
from io import BytesIO
from cpi_db import init_db, save_cpi_session, load_historical_scores, get_statistics, get_all_teams

# ── إعداد الصفحة ────────────────────────────────────────────────────
st.set_page_config(
    page_title="CPI Dashboard",
    page_icon=" 🧠 ",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# تفعيل قاعدة البيانات فور إقلاع خادم Streamlit
try:
    init_db()
except Exception as e:
    st.sidebar.warning(f"⚠️ وضع الحماية المحلي نشط: {str(e)}")

#  ════════════════════════════════════════════════════════════════════
#  TRANSLATIONS — قاموس الترجمة المركزي الشامل
#  ════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "app_title": {"ar": "مؤشر التلاقح المعرفي", "en": "Cross-Pollination Index", "fr": "Indice de Pollinisation Croisée"},
    "app_sub": {"ar": "CPI Dashboard · د. الحبيب خروبي · ESU-001", "en": "CPI Dashboard · Dr. Elhabib Kherroubi · ESU-001", "fr": "Tableau de bord CPI · Dr. Elhabib Kherroubi · ESU-001"},
    "formula_label": {"ar": "CI = NK × EH", "en": "CI = NK × EH", "fr": "IC = SC × HE"},
    
    "tab_assess": {"ar": " 📝  تقييم جلسة", "en": " 📝  Session Assessment", "fr": " 📝  Évaluation de séance"},
    "tab_dashboard": {"ar": " 📊  لوحة القيادة", "en": " 📊  Dashboard", "fr": " 📊  Tableau de bord"},
    "tab_history": {"ar": " 🗂️  السجل التاريخي", "en": " 🗂️  History Log", "fr": " 🗂️  Historique"},
    "tab_facilitator": {"ar": " 🧠  الميسر المعرفي", "en": " 🧠  Cognitive Facilitator", "fr": " 🧠  Facilitateur Cognitif"},
    "tab_charter": {"ar": " 📜  الميثاق", "en": " 📜  Charter", "fr": " 📜  Charte"},
    "tab_admin": {"ar": " 📈  الإحصائيات الإدارية", "en": " 📈  Admin Stats", "fr": " 📈  Stats Admin"},
    
    "charter_title": {"ar": "ميثاق التلاقح المعرفي", "en": "Cognitive Cross-Pollination Charter", "fr": "Charte de Pollinisation Croisée Cognitive"},
    "charter_version": {"ar": "الإصدار 1.1 · د. الحبيب خروبي · ESU-001 · جوان 2026", "en": "v1.1 · Dr. Elhabib Kherroubi · ESU-001 · June 2026", "fr": "v1.1 · Dr. Elhabib Kherroubi · ESU-001 · Juin 2026"},
    "charter_preamble": {"ar": "انطلاقاً من أن الابتكار الحقيقي لا ينتج عن تجميع المعارف الفردية بصورة منفصلة، بل عن التفاعل المنهجي بينها وتحويل الاختلافات المعرفية إلى طاقة إبداعية مشتركة — نعتمد هذا الميثاق عقداً معرفياً وأخلاقياً وتشغيلياً لفريقنا.", "en": "True innovation in cross-disciplinary teams does not arise from aggregating knowledge separately, but from its systematic interaction — transforming cognitive differences into shared creative energy. We adopt this Charter as a cognitive, ethical, and operational contract.", "fr": "La véritable innovation ne provient pas de l'agrégation des connaissances individuelles, mais de leur interaction systématique — transformant les différences cognitives en énergie créative partagée. Nous adoptons cette Charte comme contrat cognitif, éthique et opérationnel."},
    "charter_axiom": {"ar": "التواضع المعرفي ليس مجرد فضيلة أخلاقية، بل بنية تشغيلية لازمة لظهور الذكاء الجماعي.", "en": "Epistemic humility is not merely an ethical virtue — it is an operational structure necessary for collective intelligence to emerge.", "fr": "L'humilité épistémique n'est pas seulement une vertu éthique — c'est une structure opérationnelle nécessaire à l'émergence de l'intelligence collective."},
    "charter_sign_title": {"ar": "التوقيع على الميثاق", "en": "Sign the Charter", "fr": "Signer la Charte"},
    "charter_sign_ph": {"ar": "اسمك الكامل وتخصصك الميداني", "en": "Your full name & specialty", "fr": "Votre nom complet et spécialité"},
    "charter_sign_btn": {"ar": " ✍️  أوقّع وألتزم", "en": " ✍️  Sign & Commit", "fr": " ✍️  Signer et s'engager"},
    "charter_signed_msg": {"ar": "تم تسجيل التزامك بنجاح.", "en": "Commitment recorded successfully.", "fr": "Engagement enregistré avec succès."},
    "charter_signatories": {"ar": "الموقّعون في هذه الجلسة", "en": "Signatories in this session", "fr": "Signataires de cette séance"},
    "charter_clear": {"ar": " 🗑️  مسح التوقيعات الحالية", "en": " 🗑️  Clear signatures", "fr": " 🗑️  Effacer les signatures"},
    
    "pdf_export_session": {"ar": " 📥  تحميل تقرير PDF للجلسة", "en": " 📥  Download PDF Report", "fr": " 📥  Télécharger rapport PDF"},
    "pdf_export_all": {"ar": " 📥  تحميل تقرير PDF شامل للسجل", "en": " 📥  Download Full PDF History", "fr": " 📥  Télécharger historique PDF"},
    "pdf_generating": {"ar": " ⏳  جاري توليد ملف PDF...", "en": " ⏳  Generating PDF...", "fr": " ⏳  Génération du PDF..."},
    "pdf_error": {"ar": " ⚠️  تعذّر توليد PDF سحابياً.", "en": " ⚠️  Could not generate PDF.", "fr": " ⚠️  Impossible de générer le PDF."},
    
    "assess_intro": {"ar": "قيّم الأبعاد الأربعة بعد كل اجتماع حاسم.", "en": "Rate the four dimensions after each key meeting.", "fr": "Évaluez les quatre dimensions après chaque réunion clé."},
    "scale_hint": {"ar": "1 = ضعيف · 2 = مقبول · 3 = جيد · 4 = متقدم (اختفاء الحدود)", "en": "1 = Weak · 2 = Acceptable · 3 = Good · 4 = Advanced", "fr": "1 = Faible · 2 = Acceptable · 3 = Bien · 4 = Avancé"},
    "score_labels": {"ar": {1: "ضعيف", 2: "مقبول", 3: "جيد", 4: "متقدم"}, "en": {1: "Weak", 2: "Acceptable", 3: "Good", 4: "Advanced"}, "fr": {1: "Faible", 2: "Acceptable", 3: "Bien", 4: "Avancé"}},
    "cpi_computed": {"ar": "مؤشر CPI المحسوب", "en": "Computed CPI Score", "fr": "CPI calculé"},
    "btn_record": {"ar": " 💾  حفظ وتوثيق مخرجات الجلسة", "en": " 💾  Save & Archive Outcomes", "fr": " 💾  Enregistrer les résultats"},
    "btn_record_saving": {"ar": " ⏳  جاري الحفظ في قاعدة البيانات...", "en": " ⏳  Saving to database...", "fr": " ⏳  Sauvegarde en cours..."},
    "btn_record_success": {"ar": " ✅  تم تأمين وحفظ الحالة المعرفية بنجاح!", "en": " ✅  Session saved successfully!", "fr": " ✅  Session enregistrée !"},
    "complete_all": {"ar": "يرجى تقييم الأبعاد الأربعة لحفظ السجل.", "en": "Complete all four dimensions to save.", "fr": "Complétez les quatre dimensions pour enregistrer."},
    
    "last_cpi": {"ar": "مؤشر التلاقح الأخير", "en": "Latest recorded CPI", "fr": "Dernier CPI enregistré"},
    "dim_detail": {"ar": "تفصيل مستويات الأبعاد", "en": "Dimension breakdown", "fr": "Détail des dimensions"},
    "bdi_title": {"ar": "مؤشر اختفاء الحدود (BDI)", "en": "Boundary Disappearance Index (BDI)", "fr": "Indice de disparition des frontières (IDF)"},
    "bdi_sub": {"ar": "كلما اقترب من 100% كلما بني الذكاء الجماعي الحقيقي", "en": "Closer to 100% means genuine collective intelligence", "fr": "Proche de 100% signifie intelligence collective réelle"},
    "trend_title": {"ar": "مسار CPI التاريخي", "en": "CPI trend over time", "fr": "Évolution du CPI dans le temps"},
    "sessions_recorded": {"ar": "جلسة تلاقح مؤرشفة", "en": "sessions recorded", "fr": "séances enregistrées"},
    "recs_title": {"ar": "التوصيات والتدخلات المعرفية", "en": "Improvement recommendations", "fr": "Recommandations d'amélioration"},
    "recs_all_good": {"ar": "✓ جميع الأبعاد في مستوى رائع.", "en": "✓ All dimensions are excellent.", "fr": "✓ Toutes les dimensions sont excellentes."},
    "no_data": {"ar": "لا توجد بيانات محفوظة. ابدأ بحفظ الجلسة الأولى.", "en": "No data yet — record your first session.", "fr": "Aucune donnée — enregistrez votre première séance."},
    
    "no_sessions": {"ar": "لا توجد جلسات مسجّلة حالياً", "en": "No sessions recorded yet", "fr": "Aucune séance enregistrée"},
    "delete_all": {"ar": " 🗑️  حذف السجل المحلي", "en": " 🗑️  Delete local log", "fr": " 🗑️  Tout supprimer"},
    
    "team_name_label": {"ar": "🏢 اسم الفريق النشط", "en": "🏢 Team Name", "fr": "🏢 Nom de l'équipe"},
    "project_name_label": {"ar": "📋 اسم الحالة السريرية / المشروع", "en": "📋 Project / Clinical Case Name", "fr": "📋 Projet / Cas clinique"},
    "session_number_label": {"ar": "🔢 رقم الجلسة", "en": "🔢 Session Number", "fr": "🔢 Numéro de session"},
    
    "statistics_title": {"ar": "📊 إحصائيات المنصة المركزية", "en": "📊 Platform Statistics", "fr": "📊 Statistiques de la plateforme"},
    "stat_total_sessions": {"ar": "إجمالي الجلسات الحية", "en": "Total Sessions", "fr": "Sessions totales"},
    "stat_avg_cpi": {"ar": "متوسط CPI العام", "en": "Average CPI", "fr": "CPI moyen"},
    "stat_total_teams": {"ar": "عدد الفرق المعتمدة", "en": "Registered Teams", "fr": "Équipes enregistrées"},
    
    "fac_sub": {"ar": "وسيط معرفي ذكي محايد، يحلل لغة الفريق، يكشف الأنا وصمت الخبراء.", "en": "Neutral third party. Analyses team language and reveals cognitive biases.", "fr": "Tiers neutre. Analyse le langage et révèle les biais cognitifs."},
    "api_key_label": {"ar": " 🔑  مفتاح Anthropic (API Key)", "en": " 🔑  Anthropic API Key", "fr": " 🔑  Clé Anthropic API"},
    "api_key_ph": {"ar": "أدخل مفتاح Claude هنا...", "en": "sk-ant-...", "fr": "sk-ant-..."},
    "ai_facilitator_ready": {"ar": "🧠 الميسر الذكي جاهز (API Key Loaded)", "en": "🧠 AI Facilitator ready", "fr": "🧠 Facilitateur IA prêt"},
    "ai_facilitator_missing": {"ar": "⚠️ الميسر الذكي يحتاج لمفتاح API.", "en": "⚠️ AI Facilitator needs an API key.", "fr": "⚠️ Le facilitateur IA nécessite une clé API."},
    "fac_mode_label": {"ar": "وظيفة الميسر الذكي:", "en": "Facilitator mode:", "fr": "Mode du facilitateur :"},
    "send_btn": {"ar": " 📤  إرسال للتحليل الفوري", "en": " 📤  Send to facilitator", "fr": " 📤  Envoyer au facilitateur"},
    "clear_btn": {"ar": " 🗑️  مسح حقل المحادثة", "en": " 🗑️  Clear chat", "fr": " 🗑️  Effacer"},
    "fac_thinking": {"ar": " 🧠  الميسر الذكي يحلل الآن...", "en": " 🧠  Facilitator analysing...", "fr": " 🧠  Le facilitateur analyse..."},
    "error_no_key": {"ar": "يرجى تأمين مفتاح API أولاً.", "en": "Please enter your API key first.", "fr": "Veuillez d'abord saisir votre clé API."},
    "error_no_input": {"ar": "اكتب النص أولاً للتحليل.", "en": "Please write your message first.", "fr": "Veuillez d'abord écrire votre message."},
    
    "footer": {"ar": "CPI — منظومة التلاقح والمعرفة التوليدية · د. الحبيب خروبي · ESU-001", "en": "CPI — Cross-Pollination Index · Dr. Elhabib Kherroubi · ESU-001", "fr": "CPI — Indice de Pollinisation Croisée · Dr. Elhabib Kherroubi · ESU-001"},
}

def t(key):
    lang = st.session_state.get("lang", "ar")
    return TRANSLATIONS.get(key, {}).get(lang, TRANSLATIONS.get(key, {}).get("ar", key))

# ── الأبعاد والمحاور ──────────────────────────────────────────
DIMS_DATA = {
    "P": {
        "color": "#2563EB",
        "ar": {"name": "الممارسة", "desc": "استيعاب كل تخصص لأولويات التخصص الآخر", "q": "هل فهمنا أولويات بعضنا في القرارات؟"},
        "en": {"name": "Practice", "desc": "Grasping each other's priorities", "q": "Did we understand priorities in decisions?"},
        "fr": {"name": "Pratique", "desc": "Comprendre les priorités de l'autre", "q": "Avons-nous compris les priorités dans les décisions ?"},
    },
    "L": {
        "color": "#059669",
        "ar": {"name": "اللغة", "desc": "وجود قاموس مفاهيمي موحد يمنع الغموض", "q": "هل تحدثنا بلغة تلاقحية واضحة؟"},
        "en": {"name": "Language", "desc": "Unified vocabulary preventing ambiguity", "q": "Did we speak clearly without ambiguity?"},
        "fr": {"name": "Langage", "desc": "Vocabulaire unifié prévenant l'ambiguïté", "q": "Avons-nous parlé clairement sans ambiguïté ?"},
    },
    "G": {
        "color": "#7C3AED",
        "ar": {"name": "التوجيه", "desc": "تدفق الملاحظات من الميدان للأعلى", "q": "هل تدفقت الأفكار بحرية من الواقع؟"},
        "en": {"name": "Guidance", "desc": "Flow of observations from field upward", "q": "Did ideas flow freely from the field?"},
        "fr": {"name": "Orientation", "desc": "Flux d'observations du terrain vers le haut", "q": "Les idées ont-elles circulé librement du terrain ?"},
    },
    "EH": {
        "color": "#DC2626",
        "ar": {"name": "التواضع", "desc": "القدرة على مراجعة المواقف وتحديث القناعات", "q": "هل تم تعديل الرأي لتكامل الحل؟"},
        "en": {"name": "Humility", "desc": "Capacity to review and update convictions", "q": "Was opinions adjusted for a complete solution?"},
        "fr": {"name": "Humilité", "desc": "Capacité à revoir et mettre à jour ses convictions", "q": "Les opinions ont-elles été ajustées pour une solution complète ?"},
    },
}
DIM_KEYS = ["P", "L", "G", "EH"]

LEVELS = {
    "ar": [
        {"min": 0, "max": 20, "label": "المستوى 0: الانعزال المعرفي", "color": "#EF4444", "cls": "level-0"},
        {"min": 20, "max": 40, "label": "المستوى 1: الإدراك المعرفي", "color": "#F59E0B", "cls": "level-1"},
        {"min": 40, "max": 55, "label": "المستوى 2: التبادل الخطي", "color": "#3B82F6", "cls": "level-2"},
        {"min": 55, "max": 70, "label": "المستوى 3: التكامل المعرفي", "color": "#8B5CF6", "cls": "level-2"},
        {"min": 70, "max": 85, "label": "المستوى 4: التوليد المشترك", "color": "#10B981", "cls": "level-3"},
        {"min": 85, "max": 101, "label": "المستوى 5: الذكاء الجماعي الناشئ", "color": "#059669", "cls": "level-3"},
    ],
    "en": [
        {"min": 0, "max": 20, "label": "L0: Cognitive Isolation", "color": "#EF4444", "cls": "level-0"},
        {"min": 20, "max": 40, "label": "L1: Cognitive Awareness", "color": "#F59E0B", "cls": "level-1"},
        {"min": 40, "max": 55, "label": "L2: Information Exchange", "color": "#3B82F6", "cls": "level-2"},
        {"min": 55, "max": 70, "label": "L3: Cognitive Integration", "color": "#8B5CF6", "cls": "level-2"},
        {"min": 70, "max": 85, "label": "L4: Co-Generation Mode", "color": "#10B981", "cls": "level-3"},
        {"min": 85, "max": 101, "label": "L5: Emergent Collective Intelligence", "color": "#059669", "cls": "level-3"},
    ],
    "fr": [
        {"min": 0, "max": 20, "label": "L0: Isolation Cognitive", "color": "#EF4444", "cls": "level-0"},
        {"min": 20, "max": 40, "label": "L1: Conscience Cognitive", "color": "#F59E0B", "cls": "level-1"},
        {"min": 40, "max": 55, "label": "L2: Échange d'Information", "color": "#3B82F6", "cls": "level-2"},
        {"min": 55, "max": 70, "label": "L3: Intégration Cognitive", "color": "#8B5CF6", "cls": "level-2"},
        {"min": 70, "max": 85, "label": "L4: Co-Génération Active", "color": "#10B981", "cls": "level-3"},
        {"min": 85, "max": 101, "label": "L5: Intelligence Collective Émergente", "color": "#059669", "cls": "level-3"},
    ],
}

RECS = {
    "P": {
        "ar": ("الممارسة", "#2563EB", "تفعيل التظليل الوظيفي المتبادل."),
        "en": ("Practice", "#2563EB", "Implement mutual job shadowing."),
        "fr": ("Pratique", "#2563EB", "Mettre en place l'observation croisée."),
    },
    "L": {
        "ar": ("اللغة", "#059669", "تشغيل ورشة بناء الأنطولوجيا المشتركة."),
        "en": ("Language", "#059669", "Run a shared ontology workshop."),
        "fr": ("Langage", "#059669", "Animer un atelier d'ontologie partagée."),
    },
    "G": {
        "ar": ("التوجيه", "#7C3AED", "إلغاء البيروقراطية لتبني أفكار الميدان."),
        "en": ("Guidance", "#7C3AED", "Remove bureaucracy to adopt field ideas."),
        "fr": ("Orientation", "#7C3AED", "Supprimer la bureaucratie pour adopter les idées terrain."),
    },
    "EH": {
        "ar": ("التواضع", "#DC2626", "اعتماد التقييم الأعمى للأفكار."),
        "en": ("Humility", "#DC2626", "Adopt blind evaluation of ideas."),
        "fr": ("Humilité", "#DC2626", "Adopter l'évaluation à l'aveugle des idées."),
    },
}

FAC_MODES = {
    "transcript": {
        "ar": {"label": " 📋  تحليل محضر جلسة", "ph": "الصق نص الحوار هنا..."},
        "en": {"label": " 📋  Transcript Analysis", "ph": "Paste transcript here..."},
        "fr": {"label": " 📋  Analyse de compte rendu", "ph": "Collez le texte ici..."},
        "system_ar": "أنت ميسر معرفي (CPI). حلل النص وقدم: أداء الأبعاد، المصطلحات الغامضة، الأنا مقابل النحن، وإجراء تحسيني واحد.",
        "system_en": "You are a CPI facilitator. Analyze text and provide: dimension performance, ambiguous terms, Ego vs We, and 1 action item.",
        "system_fr": "Vous êtes un facilitateur CPI. Analysez et fournissez : perf des dimensions, termes ambigus, Ego vs Nous, et 1 action.",
    },
    "glossary": {
        "ar": {"label": " 📖  تفكيك المصطلحات", "ph": "اكتب المصطلح الغامض..."},
        "en": {"label": " 📖  Detangle Terms", "ph": "Enter ambiguous term..."},
        "fr": {"label": " 📖  Démêler les termes", "ph": "Entrez le terme ambigu..."},
        "system_ar": "أنت ميسر معرفي. قدم للمصطلح: تعريف مبسط، مثال ميداني، ولماذا يهم التخصصات الأخرى.",
        "system_en": "You are a facilitator. Provide for the term: simple def, field example, and why it matters across disciplines.",
        "system_fr": "Vous êtes un facilitateur. Fournissez : def simple, exemple terrain, et importance interdisciplinaire.",
    },
    "bias": {
        "ar": {"label": " ⚖️  رصد التحيزات", "ph": "صف كيف اتخذتم القرار..."},
        "en": {"label": " ⚖️  Detect Biases", "ph": "Describe the decision process..."},
        "fr": {"label": " ⚖️  Détecter les biais", "ph": "Décrivez le processus de décision..."},
        "system_ar": "حلل النص لكشف تحيزات (التأكيد، السلطة، الإجماع) واطرح سؤالاً نقدياً غفل عنه الفريق.",
        "system_en": "Analyze to detect biases (confirmation, authority, groupthink) and ask a critical missed question.",
        "system_fr": "Analysez pour détecter les biais (confirmation, autorité, pensée de groupe) et posez une question critique omise.",
    },
}

CHARTER_PRINCIPLES = {
    "ar": [
        {"key": "EH", "icon": " 🤝 ", "color": "#DC2626", "title": "التواضع المعرفي", "body": "مراجعة الرأي بناءً على الأدلة هو معيار النضج.", "commit": "أستقبل النقد كهدية معرفية."},
        {"key": "L", "icon": " 💬 ", "color": "#059669", "title": "اللغة المشتركة", "body": "تبسيط المصطلحات للآخرين مسؤولية الجميع.", "commit": "لا أحتكر مصطلحاتي وسأبني قاموساً مشتركاً."},
        {"key": "P", "icon": " ⚙️ ", "color": "#2563EB", "title": "الممارسة التشاركية", "body": "فهم أولويات الزملاء والقيود الواقعية.", "commit": "أفهم أولويات زملائي قبل قراراتي."},
        {"key": "G", "icon": " 🌊 ", "color": "#7C3AED", "title": "التوجيه الميداني", "body": "صوت الميدان هو البوصلة.", "commit": "أرفع صوتي بتحديات الميدان."},
        {"key": "S", "icon": " 🛡️ ", "color": "#0891B2", "title": "السلامة المعرفية", "body": "الأمان لطرح الأفكار الناقصة والاعتراف بعدم المعرفة.", "commit": "أحمي هذه البيئة الآمنة للجميع."}
    ],
    "en": [
        {"key": "EH", "icon": " 🤝 ", "color": "#DC2626", "title": "Humility", "body": "Revising opinions is cognitive maturity.", "commit": "I accept critique as a gift."},
        {"key": "L", "icon": " 💬 ", "color": "#059669", "title": "Shared Language", "body": "Simplifying terms is everyone's duty.", "commit": "I will build a shared glossary."},
        {"key": "P", "icon": " ⚙️ ", "color": "#2563EB", "title": "Practice", "body": "Understanding colleagues' constraints.", "commit": "I consider priorities before deciding."},
        {"key": "G", "icon": " 🌊 ", "color": "#7C3AED", "title": "Field Guidance", "body": "Field realities dictate priorities.", "commit": "I voice real field challenges."},
        {"key": "S", "icon": " 🛡️ ", "color": "#0891B2", "title": "Safety", "body": "Safe to share incomplete ideas.", "commit": "I protect this safe environment."}
    ],
    "fr": [
        {"key": "EH", "icon": " 🤝 ", "color": "#DC2626", "title": "Humilité", "body": "Réviser ses opinions est une maturité cognitive.", "commit": "J'accepte la critique comme un cadeau."},
        {"key": "L", "icon": " 💬 ", "color": "#059669", "title": "Langage Commun", "body": "Simplifier les termes est le devoir de tous.", "commit": "Je construirai un glossaire partagé."},
        {"key": "P", "icon": " ⚙️ ", "color": "#2563EB", "title": "Pratique", "body": "Comprendre les contraintes des collègues.", "commit": "Je considère les priorités avant de décider."},
        {"key": "G", "icon": " 🌊 ", "color": "#7C3AED", "title": "Orientation Terrain", "body": "Les réalités du terrain dictent les priorités.", "commit": "J'exprime les vrais défis du terrain."},
        {"key": "S", "icon": " 🛡️ ", "color": "#0891B2", "title": "Sécurité", "body": "En sécurité pour partager des idées incomplètes.", "commit": "Je protège cet environnement sûr."}
    ],
}

# ── مكملات الذكاء الاصطناعي ───────────────────────────────────────────
def get_api_key():
    if st.session_state.get("api_key"): return st.session_state.api_key
    try:
        if st.secrets.get("ANTHROPIC_API_KEY"): return st.secrets["ANTHROPIC_API_KEY"]
    except: pass
    return ""

def call_claude(messages, system_prompt, api_key):
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 1000, "system": system_prompt, "messages": messages}, timeout=60)
        data = r.json()
        if "content" in data: return data["content"][0]["text"]
        return f" ⚠️  API Error: {data.get('error',{}).get('message','Unknown error')}"
    except Exception as e:
        return f" ⚠️  Connection error: {str(e)}"

# ── الحسابات والرسوم (SVG) ────────────────────────────────────────────
def get_level(cpi):
    lang = st.session_state.get("lang", "ar")
    for l in LEVELS[lang]:
        if l["min"] <= float(cpi) < l["max"]: return l
    return LEVELS[lang][-1]

def calc_cpi(scores):
    vals = [v for v in scores.values() if v > 0]
    return round(sum(vals)/16 * 100) if len(vals) == 4 else None

def calc_bdi(sessions_list):
    if len(sessions_list) < 2: return None
    last = sessions_list[-1]
    vals = [float(last.get('score_eh',0)), float(last.get('score_l',0)), float(last.get('score_p',0)), float(last.get('score_g',0))]
    mean = sum(vals)/4
    variance = sum((v - mean)**2 for v in vals)/4
    return round((1 - variance/2.25)*100)

RADAR_RING_COLORS = ["#F3F4F6", "#E9EBF5", "#D4D9F0", "#BFC6EA"]

def radar_svg(scores, size=280):
    lang, pad, cx, cy = st.session_state.get("lang", "ar"), 52, size/2, size/2
    r, n, colors = (size/2)-pad, len(DIM_KEYS), [DIMS_DATA[k]["color"] for k in DIM_KEYS]
    def angle(i): return math.pi*2*i/n - math.pi/2
    def pt(i, val): return cx + (val/4)*r*math.cos(angle(i)), cy + (val/4)*r*math.sin(angle(i))
    def ring_pts(v): return " ".join(f"{cx + (v/4)*r*math.cos(angle(i)):.1f},{cy + (v/4)*r*math.sin(angle(i)):.1f}" for i in range(n))
    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">']
    for idx, v in enumerate([4,3,2,1]): svg.append(f'<polygon points="{ring_pts(v)}" fill="{RADAR_RING_COLORS[idx]}" stroke="#D1D5DB" stroke-width="0.8"/>')
    for i in range(n): svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx+r*math.cos(angle(i)):.1f}" y2="{cy+r*math.sin(angle(i)):.1f}" stroke="#C7CDE8" stroke-width="1" stroke-dasharray="4 3"/>')
    for vt in [1,2,3,4]:
        for i in range(n): svg.append(f'<circle cx="{cx+(vt/4)*r*math.cos(angle(i)):.1f}" cy="{cy+(vt/4)*r*math.sin(angle(i)):.1f}" r="2" fill="#C7CDE8"/>')
    filled_pts = " ".join(f"{pt(i, scores.get(k,0))[0]:.1f},{pt(i, scores.get(k,0))[1]:.1f}" for i, k in enumerate(DIM_KEYS))
    svg.append(f'<polygon points="{filled_pts}" fill="rgba(37,99,235,0.18)" stroke="#2563EB" stroke-width="2.5" stroke-linejoin="round"/>')
    for i, k in enumerate(DIM_KEYS):
        x, y, c = *pt(i, scores.get(k,0)), colors[i]
        svg.extend([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{c}" opacity="0.15"/>', f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{c}" stroke="white" stroke-width="2"/>', f'<text x="{x:.1f}" y="{y+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="7" font-weight="700" fill="white">{scores.get(k,0)}</text>'])
    for i, k in enumerate(DIM_KEYS):
        lx, ly, c, sn = cx+(r+32)*math.cos(angle(i)), cy+(r+32)*math.sin(angle(i)), colors[i], DIMS_DATA[k][lang]["name"]
        svg.extend([f'<rect x="{lx-28:.1f}" y="{ly-11:.1f}" width="56" height="22" rx="6" fill="{c}" opacity="0.12"/>', f'<text x="{lx:.1f}" y="{ly+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-weight="700" fill="{c}" font-family="sans-serif">{sn}</text>'])
    svg.extend([f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="#94A3B8"/>', "</svg>"])
    return "\n".join(svg)

def gauge_svg(value):
    if value is None: return ""
    color, circ = get_level(value)["color"], math.pi*58
    dash, nx, ny = (value/100)*circ, 88 + 46*math.cos(math.radians(180-(value/100)*180)), 84 - 46*math.sin(math.radians(180-(value/100)*180))
    return f'<svg width="176" height="100" viewBox="0 0 176 100" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="ggrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#EF4444"/><stop offset="40%" stop-color="#F59E0B"/><stop offset="70%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#10B981"/></linearGradient></defs><path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round"/><path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="url(#ggrad)" stroke-width="14" stroke-linecap="round" opacity="0.25"/><path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/><circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{color}" opacity="0.9"/><text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827" font-family="monospace">{int(value)}%</text></svg>'

# ── توليد الـ PDF الاحترافي ───────────────────────────────────────────
def build_pdf_html(session, all_sessions, lang):
    s, lvl, color, dir_ = session, get_level(session["cpi_score_final"]), get_level(session["cpi_score_final"])["color"], "rtl" if lang=="ar" else "ltr"
    titles = {
        "ar": {"report": "تقرير التلاقح والذكاء الجماعي", "session": "الحالة", "dims": "الأبعاد", "recs": "التوصيات", "hist": "مسار CPI", "date_lbl": "التاريخ", "ses_lbl": "الجلسة", "generated": "تم الإصدار", "weakest": "الأضعف", "bdi": "مؤشر BDI", "page": "صفحة"},
        "en": {"report": "CPI Collective Intelligence Report", "session": "Case", "dims": "Dimensions", "recs": "Recommendations", "hist": "CPI Trend", "date_lbl": "Date", "ses_lbl": "Session", "generated": "Generated", "weakest": "Weakest", "bdi": "BDI Score", "page": "Page"},
        "fr": {"report": "Rapport CPI Intelligence Collective", "session": "Cas", "dims": "Dimensions", "recs": "Recommandations", "hist": "Tendance CPI", "date_lbl": "Date", "ses_lbl": "Séance", "generated": "Généré", "weakest": "Plus faible", "bdi": "Score BDI", "page": "Page"}
    }[lang]
    
    scores_mapped = {"EH": s["score_eh"], "L": s["score_l"], "P": s["score_p"], "G": s["score_g"]}
    dim_rows_html = "".join(f'<tr><td style="padding:10px 14px;font-weight:800;color:{DIMS_DATA[k]["color"]};font-size:13px">{k}</td><td style="padding:10px 14px;font-weight:600;font-size:13px">{DIMS_DATA[k][lang]["name"]}</td><td style="padding:10px 14px;font-family:monospace;font-weight:800;font-size:16px;color:{DIMS_DATA[k]["color"]}">{int(scores_mapped.get(k,0))}/4</td><td style="padding:10px 14px;width:180px"><div style="height:10px;background:#F1F5F9;border-radius:5px;overflow:hidden"><div style="height:100%;width:{(scores_mapped.get(k,0)/4)*100}%;background:{DIMS_DATA[k]["color"]};border-radius:5px"></div></div></td></tr>' for k in DIM_KEYS)
    
    weak = [k for k in DIM_KEYS if scores_mapped.get(k,0) <= 2]
    recs_html = f'<p style="color:#10B981;font-weight:700;font-size:14px">✓ جميع الأبعاد جيدة.</p>' if not weak else "".join(f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;padding:12px 16px;margin-bottom:10px"><div style="font-weight:800;color:{RECS[k][lang][1]};font-size:13px;margin-bottom:4px"> ⚠ {RECS[k][lang][0]}</div><div style="font-size:12px;color:#92400E;">{RECS[k][lang][2]}</div></div>' for k in weak)
    
    hist_html = ""
    if len(all_sessions) >= 2:
        rows = "".join(f'<tr><td style="padding:8px 12px;font-size:12px">{hs["project_name"]} (S{hs["session_number"]})</td><td style="padding:8px 12px;color:#6B7280;font-size:11px">{hs["session_date"]}</td><td style="padding:8px 12px;font-weight:800;font-family:monospace;color:{get_level(hs["cpi_score_final"])["color"]};font-size:14px">{int(hs["cpi_score_final"])}%</td><td style="padding:8px 12px;font-size:11px;color:{get_level(hs["cpi_score_final"])["color"]}">{get_level(hs["cpi_score_final"])["label"]}</tr>' for hs in all_sessions)
        hist_html = f'<div class="card"><h2>{titles["hist"]}</h2><table><thead><tr style="background:#F8FAFC"><th style="padding:8px 12px;font-size:11px;color:#6B7280">{titles["ses_lbl"]}</th><th style="padding:8px 12px;font-size:11px;color:#6B7280">{titles["date_lbl"]}</th><th style="padding:8px 12px;font-size:11px;color:#6B7280">CPI</th><th style="padding:8px 12px;font-size:11px;color:#6B7280"></th></tr></thead><tbody>{rows}</tbody></table></div>'
    
    bdi = calc_bdi(all_sessions)
    bdi_str = f"{bdi}%" if bdi else "N/A"
    min_key = min(DIM_KEYS, key=lambda k: scores_mapped.get(k,0))
    weakest_name = DIMS_DATA[min_key][lang]["name"]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return f"""<!DOCTYPE html><html lang="{lang}" dir="{dir_}"><head><meta charset="UTF-8"><title>CPI Report — {s["project_name"]}</title><style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:sans-serif;background:#F8FAFC;color:#111827;direction:{dir_};font-size:13px;line-height:1.6;}}@page{{size:A4;margin:15mm 18mm 20mm 18mm;@bottom-center{{content:"{titles["page"]} " counter(page) " / " counter(pages);font-size:10px;color:#94A3B8;}}}}.report-header{{background:#0F172A;color:white;padding:28px 32px;border-radius:12px;margin-bottom:20px;}}.report-header h1{{font-size:20px;font-weight:800;margin-bottom:5px;}}.formula-badge{{background:#1E3A5F;border-radius:8px;padding:8px 16px;font-family:monospace;font-size:13px;color:#7DD3FC;font-weight:700;display:inline-block;margin-top:10px;}}.score-hero{{background:white;border:1.5px solid {color}44;border-radius:14px;padding:24px 28px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;}}.score-num{{font-size:52px;font-weight:800;font-family:monospace;color:{color};}}.score-label{{font-size:15px;font-weight:700;color:{color};margin-top:6px;background:{color}15;padding:5px 14px;border-radius:20px;display:inline-block;}}.stats-row{{display:flex;gap:14px;margin-bottom:20px;}}.stat-card{{flex:1;background:white;border:1px solid #E8EDF5;border-radius:10px;padding:14px;text-align:center;}}.stat-val{{font-size:22px;font-weight:800;font-family:monospace;color:#1E293B;}}.card{{background:white;border:1px solid #E8EDF5;border-radius:12px;padding:20px;margin-bottom:18px;}}table{{width:100%;border-collapse:collapse;}}td,th{{text-align:{"right" if dir_=="rtl" else "left"};}}tr:nth-child(even) td{{background:#FAFBFF;}}.axiom-box{{background:#FFFBEB;border:1px solid #FCD34D;border-radius:10px;padding:14px;margin-bottom:20px;text-align:center;font-weight:700;color:#78350F;}}</style></head><body><div class="report-header"><h1>📊 {titles["report"]}</h1><p>Dr. Elhabib Kherroubi · ESU-001</p><p style="margin-top:8px;color:#CBD5E1">{titles["session"]}: <strong style="color:white">{s["project_name"]} (S{s["session_number"]})</strong> &nbsp;·&nbsp; {titles["date_lbl"]}: <strong style="color:white">{s["session_date"]}</strong></p><div class="formula-badge">CI = NK × EH</div></div><div class="axiom-box">❝ التواضع المعرفي بنية تشغيلية لازمة للذكاء الجماعي ❞</div><div class="score-hero"><div><div class="score-num">{int(s["cpi_score_final"])}%</div><div class="score-label">{lvl["label"]}</div></div></div><div class="stats-row"><div class="stat-card"><div class="stat-val">{bdi_str}</div><div style="font-size:11px;color:#6B7280">{titles["bdi"]}</div></div><div class="stat-card"><div class="stat-val">{weakest_name}</div><div style="font-size:11px;color:#6B7280">{titles["weakest"]}</div></div><div class="stat-card"><div class="stat-val">{len(all_sessions)}</div><div style="font-size:11px;color:#6B7280">جلسات مسجلة</div></div></div><div class="card"><h2>{titles["dims"]}</h2><table><tbody>{dim_rows_html}</tbody></table></div><div class="card"><h2>{titles["recs"]}</h2>{recs_html}</div>{hist_html}</body></html>"""

def generate_pdf_bytes(session, all_sessions, lang):
    html_content = build_pdf_html(session, all_sessions, lang)
    try:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as fh:
            fh.write(html_content)
            tmp_html = fh.name
        tmp_pdf = tmp_html.replace(".html", ".pdf")
        subprocess.run(["wkhtmltopdf", "--encoding", "utf-8", tmp_html, tmp_pdf], capture_output=True, text=True, timeout=30)
        if os.path.exists(tmp_pdf):
            with open(tmp_pdf, "rb") as f:
                return f.read(), None
        return None, "PDF Error"
    except Exception as e:
        return None, str(e)

#  ════════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
#  ════════════════════════════════════════════════════════════════════
for key, default in [("lang", "ar"), ("scores", {k:0 for k in DIM_KEYS}), ("fac_msgs", []), ("fac_mode", "transcript"), ("api_key", ""), ("signatories", []), ("team_name", ""), ("project_name", ""), ("session_number", 1)]:
    if key not in st.session_state: st.session_state[key] = default

lang = st.session_state.lang

# CSS INJECTION (Simplified for space)
st.markdown(f"""<style>html,body,[class*="css"]{{direction:{"rtl" if lang=="ar" else "ltr"};font-family:sans-serif;}}</style>""", unsafe_allow_html=True)

# FETCH DB DATA
history_db = load_historical_scores(st.session_state.team_name if st.session_state.team_name else None)

#  ════════════════════════════════════════════════════════════════════
#  HEADER + TABS
#  ════════════════════════════════════════════════════════════════════
col_head, col_lang = st.columns([5,1])
with col_head:
    st.markdown(f'<div style="background:#0F172A;color:white;padding:15px;border-radius:10px;"><h2>🧠 {t("app_title")}</h2><p>{t("app_sub")} | <b>{t("formula_label")}</b></p></div>', unsafe_allow_html=True)
with col_lang:
    lang_choice = st.radio("🌐", ["ar","en","fr"], index=["ar","en","fr"].index(st.session_state.lang), horizontal=True, label_visibility="collapsed")
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([t("tab_assess"), t("tab_dashboard"), f"{t('tab_history')} ({len(history_db)})", t("tab_facilitator"), t("tab_charter"), t("tab_admin")])

# ── Tab 1 — Assessment ──
with tab1:
    c1, c2, c3 = st.columns(3)
    with c1: st.session_state.team_name = st.text_input(t("team_name_label"), st.session_state.team_name)
    with c2: st.session_state.project_name = st.text_input(t("project_name_label"), st.session_state.project_name)
    with c3: st.session_state.session_number = st.number_input(t("session_number_label"), min_value=1, value=st.session_state.session_number)
    
    st.markdown("---")
    for k in DIM_KEYS:
        st.markdown(f"**{DIMS_DATA[k][lang]['name']}**: {DIMS_DATA[k][lang]['desc']}")
        st.session_state.scores[k] = st.select_slider(k, options=[1,2,3,4], value=st.session_state.scores[k] if st.session_state.scores[k]>0 else 1, label_visibility="collapsed")
    
    cpi_now = calc_cpi(st.session_state.scores)
    if cpi_now:
        cg, cr = st.columns(2)
        with cg: st.markdown(gauge_svg(cpi_now), unsafe_allow_html=True)
        with cr: st.markdown(radar_svg(st.session_state.scores, 280), unsafe_allow_html=True)
        
        if st.button(t("btn_record"), type="primary"):
            payload = {
                "team_name": st.session_state.team_name or "فريق", "project_name": st.session_state.project_name or "مشروع",
                "session_number": st.session_state.session_number, "session_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "score_eh": st.session_state.scores["EH"], "score_l": st.session_state.scores["L"], "score_p": st.session_state.scores["P"], "score_g": st.session_state.scores["G"],
                "cpi_score_final": cpi_now, "maturity_level": get_level(cpi_now)["label"]
            }
            save_cpi_session(payload, st.session_state.signatories)
            st.session_state.session_number += 1
            st.session_state.scores = {k:0 for k in DIM_KEYS}
            st.success(t("btn_record_success"))
            st.rerun()

# ── Tab 2 — Dashboard ──
with tab2:
    if not history_db: st.info(t("no_data"))
    else:
        last = history_db[-1]
        cg, cr = st.columns(2)
        with cg: st.markdown(gauge_svg(last["cpi_score_final"]), unsafe_allow_html=True)
        with cr: st.markdown(radar_svg({"EH":last["score_eh"], "L":last["score_l"], "P":last["score_p"], "G":last["score_g"]}, 280), unsafe_allow_html=True)

# ── Tab 3 — History & PDF ──
with tab3:
    if not history_db: st.info(t("no_data"))
    else:
        if st.button(t("pdf_export_all"), type="primary"):
            pdf, err = generate_pdf_bytes(history_db[-1], history_db, lang)
            if pdf: st.download_button("⬇️ PDF", data=pdf, file_name="CPI_Full.pdf", mime="application/pdf")
        
        df = pd.DataFrame({"S": [r["session_number"] for r in history_db], "CPI": [r["cpi_score_final"] for r in history_db]})
        st.line_chart(df.set_index("S"))

# ── Tab 4 — AI Facilitator ──
with tab4:
    api_key = get_api_key()
    if api_key: st.success(t("ai_facilitator_ready"))
    else: st.session_state.api_key = st.text_input("API Key", type="password")
    
    st.session_state.fac_mode = st.radio("Mode", list(FAC_MODES.keys()), horizontal=True)
    user_input = st.text_area("Input")
    if st.button(t("send_btn")) and api_key and user_input:
        st.session_state.fac_msgs.append({"role": "user", "content": user_input})
        reply = call_claude(st.session_state.fac_msgs, FAC_MODES[st.session_state.fac_mode][f"system_{lang}"], api_key)
        st.session_state.fac_msgs.append({"role": "assistant", "content": reply})
        st.rerun()
    for m in st.session_state.fac_msgs: st.write(f"**{m['role']}**: {m['content']}")

# ── Tab 5 — Charter ──
with tab5:
    st.write(t("charter_preamble"))
    name = st.text_input(t("charter_sign_ph"))
    if st.button(t("charter_sign_btn")) and name:
        st.session_state.signatories.append({"name": name, "time": datetime.datetime.now().strftime("%H:%M")})
        st.rerun()
    for s in st.session_state.signatories: st.write(f"✅ {s['name']} ({s['time']})")

# ── Tab 6 — Admin Stats ──
with tab6:
    stats = get_statistics()
    c1, c2, c3 = st.columns(3)
    c1.metric(t("stat_total_sessions"), stats.get("total_sessions", 0))
    c2.metric(t("stat_avg_cpi"), f"{stats.get('average_cpi', 0)}%")
    c3.metric(t("stat_total_teams"), stats.get("total_teams", 0))


```
