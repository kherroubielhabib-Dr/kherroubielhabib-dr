# ═══════════════════════════════════════════════════════════════════
# مؤشر التلاقح المعرفي - CPI Dashboard v7.3.1
# Cross-Pollination Index · Indice de Pollinisation Croisée
# د. الحبيب خروبي · ESU-001
# الإصدار: v7.3.1 - الترجمة الكاملة المثالية
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import math
import datetime
import requests
import cpi_db

# ════════════════════════════════════════════════════════════════════
# 1. إعداد الصفحة
# ════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CPI Dashboard v7.3.1",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
# 2. تهيئة SESSION STATE
# ════════════════════════════════════════════════════════════════════

if "lang" not in st.session_state:
    st.session_state.lang = "ar"

if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "scores" not in st.session_state:
    st.session_state.scores = {"P": 2, "L": 2, "G": 2, "EH": 2}

if "fac_msgs" not in st.session_state:
    st.session_state.fac_msgs = []

if "fac_mode" not in st.session_state:
    st.session_state.fac_mode = "transcript"

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "signatories" not in st.session_state:
    st.session_state.signatories = []

if "session_num_counter" not in st.session_state:
    st.session_state.session_num_counter = 1

if "pmp_participants" not in st.session_state:
    st.session_state.pmp_participants = []

if "pmp_next_uid" not in st.session_state:
    st.session_state.pmp_next_uid = 1

if "pmp_stats" not in st.session_state:
    st.session_state.pmp_stats = None

# تحميل البيانات من قاعدة البيانات
if "data_loaded" not in st.session_state:
    try:
        cpi_db.init_db()
        db_sessions = cpi_db.load_historical_scores(limit=500)
        formatted_sessions = []
        for row in db_sessions:
            formatted_sessions.append({
                "id": row.get("id"),
                "label": row.get("project_name", "جلسة"),
                "team": row.get("team_name", "فريق"),
                "date": row.get("session_date", str(datetime.date.today())),
                "cpi": float(row.get("cpi_score_final", 0)),
                "alignment_index": row.get("alignment_index"),
                "scores": {
                    "EH": float(row.get("score_eh", 2)),
                    "L": float(row.get("score_l", 2)),
                    "P": float(row.get("score_p", 2)),
                    "G": float(row.get("score_g", 2))
                },
                "session_number": row.get("session_number", 0)
            })
        st.session_state.sessions = formatted_sessions
        if formatted_sessions:
            st.session_state.session_num_counter = len(formatted_sessions) + 1
    except Exception:
        st.session_state.sessions = []
    st.session_state.data_loaded = True

# ════════════════════════════════════════════════════════════════════
# 3. قاموس الترجمة المركزي الكامل
# ════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    # التطبيق
    "app_title": {"ar": "مؤشر التلاقح المعرفي", "en": "Cross-Pollination Index", "fr": "Indice de Pollinisation Croisée"},
    "app_sub": {"ar": "CPI Dashboard v7.3.1 · د. الحبيب خروبي · ESU-001", "en": "CPI Dashboard v7.3.1 · Dr. Elhabib Kherroubi · ESU-001", "fr": "Tableau de bord CPI v7.3.1 · Dr. Elhabib Kherroubi · ESU-001"},
    "formula_label": {"ar": "CI = NK × EH", "en": "CI = NK × EH", "fr": "IC = SC × HE"},
    
    # التبويبات
    "tab_assess": {"ar": "📝 تقييم جلسة", "en": "📝 Session Assessment", "fr": "📝 Évaluation de session"},
    "tab_dashboard": {"ar": "📊 لوحة القيادة", "en": "📊 Dashboard", "fr": "📊 Tableau de bord"},
    "tab_history": {"ar": "🗂️ السجل", "en": "🗂️ History", "fr": "🗂️ Historique"},
    "tab_facilitator": {"ar": "🧠 الميسر المعرفي", "en": "🧠 Cognitive Facilitator", "fr": "🧠 Facilitateur Cognitif"},
    "tab_charter": {"ar": "📜 الميثاق", "en": "📜 Charter", "fr": "📜 Charte"},
    "tab_admin": {"ar": "📊 الإدارة", "en": "📊 Admin", "fr": "📊 Administration"},
    
    # حقول الإدخال
    "team_name": {"ar": "اسم الفريق", "en": "Team Name", "fr": "Nom de l'équipe"},
    "project_name": {"ar": "اسم المشروع/الجلسة", "en": "Project / Session Name", "fr": "Projet / Nom de la session"},
    "session_num": {"ar": "رقم الجلسة", "en": "Session #", "fr": "N° de session"},
    "session_date": {"ar": "التاريخ", "en": "Date", "fr": "Date"},
    "mode_label": {"ar": "نمط القياس:", "en": "Measurement Mode:", "fr": "Mode de mesure :"},
    
    # أنماط القياس
    "mode_solo": {"ar": "👤 تقييم فردي سريع", "en": "👤 Quick Individual", "fr": "👤 Évaluation individuelle"},
    "mode_pmp": {"ar": "👥 القياس التشاركي (PMP)", "en": "👥 Participatory Measurement (PMP)", "fr": "👥 Mesure participative (PMP)"},
    
    # الأزرار
    "btn_record": {"ar": "✅ تسجيل الجلسة", "en": "✅ Record Session", "fr": "✅ Enregistrer"},
    "save_success": {"ar": "✅ تم حفظ الجلسة بنجاح!", "en": "✅ Session saved successfully!", "fr": "✅ Session enregistrée avec succès!"},
    "delete_all": {"ar": "🗑️ حذف الكل", "en": "🗑️ Delete all", "fr": "🗑️ Tout supprimer"},
    "pmp_remove_participant": {"ar": "🗑️ حذف", "en": "🗑️ Remove", "fr": "🗑️ Supprimer"},
    
    # PMP
    "pmp_collective_cpi": {"ar": "CPI الجماعي", "en": "Collective CPI", "fr": "CPI Collectif"},
    "pmp_cai_title": {"ar": "مؤشر الانسجام الإدراكي (CAI)", "en": "Cognitive Alignment Index (CAI)", "fr": "Indice d'alignement cognitif (CAI)"},
    "pmp_add_participant": {"ar": "➕ إضافة مشارك", "en": "➕ Add Participant", "fr": "➕ Ajouter un participant"},
    "pmp_compute": {"ar": "🧮 حساب النتائج الجماعية", "en": "🧮 Compute Collective Results", "fr": "🧮 Calculer les résultats collectifs"},
    "pmp_save_btn": {"ar": "💾 حفظ جلسة PMP", "en": "💾 Save PMP Session", "fr": "💾 Enregistrer la séance PMP"},
    "pmp_intro": {"ar": "كل عضو يُدخل تقييمه الخاص بشكل منفصل (تقييم أعمى). يحسب النظام CPI الجماعي ومؤشر الانسجام الإدراكي (CAI) آلياً.", "en": "Each member enters their own assessment separately (blind assessment). The system automatically computes the Collective CPI and Cognitive Alignment Index (CAI).", "fr": "Chaque membre saisit sa propre évaluation séparément (évaluation à l'aveugle). Le système calcule automatiquement le CPI collectif et l'indice d'alignement cognitif (CAI)."},
    "pmp_participant": {"ar": "المشارك", "en": "Participant", "fr": "Participant"},
    "pmp_name": {"ar": "الاسم", "en": "Name", "fr": "Nom"},
    "pmp_specialization": {"ar": "التخصص", "en": "Specialization", "fr": "Spécialisation"},
    "pmp_role": {"ar": "الدور", "en": "Role", "fr": "Rôle"},
    "pmp_results_title": {"ar": "نتائج القياس التشاركي", "en": "Participatory Measurement Results", "fr": "Résultats de la mesure participative"},
    "pmp_gap_map_title": {"ar": "خريطة الفجوات الإدراكية حسب البُعد", "en": "Cognitive Gap Map by Dimension", "fr": "Carte des écarts cognitifs par dimension"},
    "pmp_individual_table": {"ar": "تقييمات الأفراد", "en": "Individual Assessments", "fr": "Évaluations individuelles"},
    "pmp_discussion_title": {"ar": "سؤال للنقاش الجماعي", "en": "Discussion Prompt", "fr": "Question pour la discussion"},
    "pmp_capped_note": {"ar": "⚠ المستوى محدود بسبب الانسجام الإدراكي المنخفض (CAI). لا يمكن بلوغ مستوى أعلى دون تقارب رؤى الفريق.", "en": "⚠ Level capped due to low Cognitive Alignment (CAI). A higher level requires closer team perception.", "fr": "⚠ Niveau limité en raison d'un faible alignement cognitif (CAI). Un niveau supérieur nécessite une perception d'équipe plus proche."},
    
    # رسائل
    "no_data": {"ar": "لا توجد بيانات مسجلة بعد.", "en": "No data recorded yet.", "fr": "Aucune donnée enregistrée."},
    "no_sessions": {"ar": "لا توجد جلسات مسجّلة بعد", "en": "No sessions recorded yet", "fr": "Aucune séance enregistrée"},
    "complete_all": {"ar": "أكمل تقييم الأبعاد الأربعة لحساب CPI", "en": "Complete all four dimensions to compute CPI", "fr": "Complétez les quatre dimensions pour calculer le CPI"},
    "cpi_computed": {"ar": "CPI المحسوب", "en": "Computed CPI", "fr": "CPI calculé"},
    "last_cpi": {"ar": "آخر CPI مسجّل", "en": "Latest recorded CPI", "fr": "Dernier CPI enregistré"},
    "dim_detail": {"ar": "تفصيل الأبعاد", "en": "Dimension breakdown", "fr": "Détail des dimensions"},
    "trend_title": {"ar": "مسار CPI عبر الزمن", "en": "CPI trend over time", "fr": "Évolution du CPI dans le temps"},
    "sessions_recorded": {"ar": "جلسة مسجّلة", "en": "sessions recorded", "fr": "séances enregistrées"},
    "recs_title": {"ar": "توصيات التحسين", "en": "Improvement recommendations", "fr": "Recommandations d'amélioration"},
    "recs_all_good": {"ar": "✓ جميع الأبعاد في مستوى جيد. استمر في المسار الحالي.", "en": "✓ All dimensions are at a good level. Keep up the current path.", "fr": "✓ Toutes les dimensions sont à un bon niveau. Continuez sur cette lancée."},
    "assess_intro": {"ar": "قيّم الأبعاد الأربعة بعد كل Sprint أو اجتماع حاسم.", "en": "Rate the four dimensions after each Sprint or key meeting.", "fr": "Évaluez les quatre dimensions après chaque Sprint ou réunion clé."},
    "scale_hint": {"ar": "1 = ضعيف · 2 = مقبول · 3 = جيد · 4 = متقدم (اختفاء الحدود)", "en": "1 = Weak · 2 = Acceptable · 3 = Good · 4 = Advanced (boundary disappearance)", "fr": "1 = Faible · 2 = Acceptable · 3 = Bien · 4 = Avancé (disparition des frontières)"},
    "bdi_title": {"ar": "مؤشر اختفاء الحدود (BDI)", "en": "Boundary Disappearance Index (BDI)", "fr": "Indice de disparition des frontières (IDF)"},
    "bdi_sub": {"ar": "كلما اقترب من 100% كلما اقترب الفريق من العقل الجماعي", "en": "The closer to 100%, the closer the team is to genuine collective intelligence", "fr": "Plus proche de 100%, plus l'équipe approche l'intelligence collective"},
    
    # تبويب الإدارة (المضاف حديثاً)
    "stats_title": {"ar": "إحصائيات المنصة", "en": "Platform Statistics", "fr": "Statistiques de la plateforme"},
    "total_sessions": {"ar": "إجمالي الجلسات", "en": "Total Sessions", "fr": "Total des sessions"},
    "avg_cpi": {"ar": "متوسط CPI", "en": "Average CPI", "fr": "CPI Moyen"},
    "total_teams": {"ar": "إجمالي الفرق", "en": "Total Teams", "fr": "Total des équipes"},
    "teams_list_title": {"ar": "الفرق المسجّلة", "en": "Registered Teams", "fr": "Équipes enregistrées"},
    "export_btn": {"ar": "📥 تصدير CSV", "en": "📥 Export CSV", "fr": "📥 Exporter CSV"},
    "download_csv": {"ar": "📥 تحميل CSV", "en": "📥 Download CSV", "fr": "📥 Télécharger CSV"},
    
    # الميثاق
    "charter_title": {"ar": "ميثاق التلاقح المعرفي", "en": "Cognitive Cross-Pollination Charter", "fr": "Charte de Pollinisation Croisée Cognitive"},
    "charter_preamble": {"ar": "انطلاقاً من أن الابتكار الحقيقي لا ينتج عن تجميع المعارف الفردية بصورة منفصلة، بل عن التفاعل المنهجي بينها وتحويل الاختلافات المعرفية إلى طاقة إبداعية مشتركة --- نعتمد هذا الميثاق عقداً معرفياً وأخلاقياً وتشغيلياً لفريقنا.", "en": "True innovation in cross-disciplinary teams does not arise from aggregating knowledge separately, but from its systematic interaction --- transforming cognitive differences into shared creative energy.", "fr": "La véritable innovation ne provient pas de l'agrégation des connaissances individuelles, mais de leur interaction systématique --- transformant les différences cognitives en énergie créative partagée."},
    "charter_axiom": {"ar": "التواضع المعرفي ليس مجرد فضيلة أخلاقية، بل بنية تشغيلية لازمة لظهور الذكاء الجماعي.", "en": "Epistemic humility is not merely an ethical virtue --- it is an operational structure necessary for collective intelligence to emerge.", "fr": "L'humilité épistémique n'est pas seulement une vertu éthique --- c'est une structure opérationnelle nécessaire à l'émergence de l'intelligence collective."},
    "fac_sub": {"ar": "طرف ثالث محايد. يحلل لغة الفريق ويكشف التحيزات المعرفية.", "en": "A neutral third party. Analyses team language and reveals cognitive biases.", "fr": "Un tiers neutre. Analyse le langage de l'équipe et révèle les biais cognitifs."},
    
    "footer": {"ar": "CPI --- مؤشر التلاقح المعرفي · د. الحبيب خروبي · ESU-001", "en": "CPI --- Cross-Pollination Index · Dr. Elhabib Kherroubi · ESU-001", "fr": "CPI --- Indice de Pollinisation Croisée · Dr. Elhabib Kherroubi · ESU-001"},
}

def t(key, default=""):
    lang = st.session_state.get("lang", "ar")
    entry = TRANSLATIONS.get(key, {})
    result = entry.get(lang, entry.get("ar", default if default else key))
    return result

# ════════════════════════════════════════════════════════════════════
# 4. البيانات الأساسية
# ════════════════════════════════════════════════════════════════════

DIM_KEYS = ["P", "L", "G", "EH"]

DIMS_DATA = {
    "P": {"color": "#2563EB", "ar": {"name": "الممارسة", "desc": "مدى استيعاب كل تخصص لأولويات التخصص الآخر", "q": "هل فهمنا أولويات بعضنا في القرارات؟"},
          "en": {"name": "Practice", "desc": "How much each discipline grasps the other's priorities", "q": "Did we understand each other's priorities in decisions?"},
          "fr": {"name": "Pratique", "desc": "Dans quelle mesure chaque discipline comprend les priorités de l'autre", "q": "Avons-nous compris les priorités de chacun dans les décisions ?"}},
    "L": {"color": "#059669", "ar": {"name": "اللغة المشتركة", "desc": "وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال", "q": "هل تحدثنا بلغة مشتركة دون سوء فهم؟"},
          "en": {"name": "Shared Language", "desc": "A unified conceptual vocabulary enabling effective communication", "q": "Did we speak a common language without misunderstanding?"},
          "fr": {"name": "Langage commun", "desc": "Un vocabulaire conceptuel unifié permettant une communication efficace", "q": "Avons-nous parlé un langage commun sans malentendus ?"}},
    "G": {"color": "#7C3AED", "ar": {"name": "التوجيه", "desc": "اتجاه تدفق الأفكار داخل النظام", "q": "هل تدفقت الأفكار من الجميع (وليس فقط من القائد)؟"},
          "en": {"name": "Guidance", "desc": "Direction of idea flow within the system", "q": "Did ideas flow from everyone (not just the leader)?"},
          "fr": {"name": "Orientation", "desc": "Direction du flux d'idées au sein du système", "q": "Les idées ont-elles circulé de tous (pas seulement du leader) ?"}},
    "EH": {"color": "#DC2626", "ar": {"name": "التواضع المعرفي", "desc": "قدرة الأفراد على قبول التصحيح والتعلم من الآخرين", "q": "هل استمعنا لبعضنا بتواضع وغيرنا مواقفنا؟"},
           "en": {"name": "Epistemic Humility", "desc": "Individuals' capacity to accept correction and learn from others", "q": "Did we listen humbly and change our positions?"},
           "fr": {"name": "Humilité épistémique", "desc": "Capacité des individus à accepter la correction et apprendre des autres", "q": "Avons-nous écouté humblement et changé nos positions ?"}},
}

LEVELS = {
    "ar": [{"min": 0, "max": 25, "cls": "level-0", "title": "الصومعة المعرفية", "color": "#DC2626"},
           {"min": 25, "max": 45, "cls": "level-1", "title": "العبقري المنعزل", "color": "#EA580C"},
           {"min": 45, "max": 60, "cls": "level-2", "title": "تعاون شكلي", "color": "#D97706"},
           {"min": 60, "max": 75, "cls": "level-3", "title": "تلاقح ناشئ", "color": "#2563EB"},
           {"min": 75, "max": 90, "cls": "level-4", "title": "ذكاء جماعي واعٍ", "color": "#059669"},
           {"min": 90, "max": 101, "cls": "level-5", "title": "اختفاء الحدود", "color": "#7C3AED"}],
    "en": [{"min": 0, "max": 25, "cls": "level-0", "title": "Knowledge Silo", "color": "#DC2626"},
           {"min": 25, "max": 45, "cls": "level-1", "title": "Isolated Genius", "color": "#EA580C"},
           {"min": 45, "max": 60, "cls": "level-2", "title": "Formal Cooperation", "color": "#D97706"},
           {"min": 60, "max": 75, "cls": "level-3", "title": "Emerging Cross-Pollination", "color": "#2563EB"},
           {"min": 75, "max": 90, "cls": "level-4", "title": "Aware Collective Intelligence", "color": "#059669"},
           {"min": 90, "max": 101, "cls": "level-5", "title": "Boundary Disappearance", "color": "#7C3AED"}],
    "fr": [{"min": 0, "max": 25, "cls": "level-0", "title": "Silo cognitif", "color": "#DC2626"},
           {"min": 25, "max": 45, "cls": "level-1", "title": "Génie isolé", "color": "#EA580C"},
           {"min": 45, "max": 60, "cls": "level-2", "title": "Coopération formelle", "color": "#D97706"},
           {"min": 60, "max": 75, "cls": "level-3", "title": "Pollinisation émergente", "color": "#2563EB"},
           {"min": 75, "max": 90, "cls": "level-4", "title": "Intelligence collective consciente", "color": "#059669"},
           {"min": 90, "max": 101, "cls": "level-5", "title": "Disparition des frontières", "color": "#7C3AED"}],
}

CAI_GATES = {"level-0": 0, "level-1": 0, "level-2": 50, "level-3": 65, "level-4": 80, "level-5": 85}
LEVEL_ORDER = ["level-0", "level-1", "level-2", "level-3", "level-4", "level-5"]

PMP_ROLES = {
    "ar": ["ميسر معرفي", "خبير سريري", "مهندس أنظمة", "مطور برمجيات", "محلل بيانات", "منسق"],
    "en": ["Cognitive Facilitator", "Clinical Expert", "Systems Engineer", "Software Developer", "Data Analyst", "Coordinator"],
    "fr": ["Facilitateur Cognitif", "Expert Clinique", "Ingénieur Systèmes", "Développeur", "Analyste de Données", "Coordinateur"],
}

RECS = {
    "P": {"ar": ("الممارسة", "#2563EB", "جلسات تظليل وظيفي أسبوعية"), "en": ("Practice", "#2563EB", "Weekly job shadowing sessions"), "fr": ("Pratique", "#2563EB", "Séances d'observation hebdomadaires")},
    "L": {"ar": ("اللغة المشتركة", "#059669", "ورشة قاموس مشترك"), "en": ("Shared Language", "#059669", "Shared glossary workshop"), "fr": ("Langage commun", "#059669", "Atelier glossaire commun")},
    "G": {"ar": ("التوجيه", "#7C3AED", "إلغاء الموافقات الهرمية"), "en": ("Guidance", "#7C3AED", "Remove hierarchical approvals"), "fr": ("Orientation", "#7C3AED", "Supprimer les approbations hiérarchiques")},
    "EH": {"ar": ("التواضع المعرفي", "#DC2626", "جلسات مراجعة عمياء"), "en": ("Epistemic Humility", "#DC2626", "Blind review sessions"), "fr": ("Humilité épistémique", "#DC2626", "Séances de révision à l'aveugle")},
}

# ════════════════════════════════════════════════════════════════════
# 5. دوال المساعدة
# ════════════════════════════════════════════════════════════════════

def get_level(cpi):
    lang = st.session_state.get("lang", "ar")
    for l in LEVELS[lang]:
        if l["min"] <= cpi < l["max"]:
            return l
    return LEVELS[lang][-1]

def get_level_v7(cpi, cai=None):
    raw = get_level(cpi)
    if cai is None:
        return raw, False
    raw_cls = raw["cls"]
    if raw_cls not in LEVEL_ORDER:
        return raw, False
    raw_idx = LEVEL_ORDER.index(raw_cls)
    eff_idx = 0
    for i in range(raw_idx, -1, -1):
        if cai >= CAI_GATES[LEVEL_ORDER[i]]:
            eff_idx = i
            break
    if eff_idx == raw_idx:
        return raw, False
    lang = st.session_state.get("lang", "ar")
    eff_cls = LEVEL_ORDER[eff_idx]
    for l in LEVELS[lang]:
        if l["cls"] == eff_cls:
            return l, True
    return raw, False

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
    raw = (1 - variance / 2.25) * 100
    return round(max(0, min(100, raw)))

def radar_svg(scores, size=300):
    lang = st.session_state.get("lang", "ar")
    pad = 55
    cx = cy = size / 2
    r = (size / 2) - pad
    n = len(DIM_KEYS)
    colors = [DIMS_DATA[k]["color"] for k in DIM_KEYS]
    
    def angle(i):
        return math.pi * 2 * i / n - math.pi / 2
    
    def pt(i, val):
        a = angle(i)
        d = (val / 4) * r
        return cx + d * math.cos(a), cy + d * math.sin(a)
    
    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">']
    
    for v in [4, 3, 2, 1]:
        pts = []
        for i in range(n):
            a = angle(i)
            d = (v / 4) * r
            pts.append(f"{cx + d*math.cos(a):.1f},{cy + d*math.sin(a):.1f}")
        fill = "#F8FAFC" if v % 2 == 0 else "#F1F5F9"
        svg.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#E2E8F0" stroke-width="0.8"/>')
    
    for i in range(n):
        a = angle(i)
        x2 = cx + r * math.cos(a)
        y2 = cy + r * math.sin(a)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="4 3"/>')
    
    pts = []
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        pts.append(f"{x:.1f},{y:.1f}")
    svg.append(f'<polygon points="{" ".join(pts)}" fill="rgba(37,99,235,0.15)" stroke="#2563EB" stroke-width="2.5" stroke-linejoin="round"/>')
    
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 0)
        x, y = pt(i, v)
        c = colors[i]
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{c}" opacity="0.2"/>')
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{c}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{x:.1f}" y="{y+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="8" font-weight="700" fill="white">{v}</text>')
    
    label_dist = r + 35
    for i, k in enumerate(DIM_KEYS):
        a = angle(i)
        lx = cx + label_dist * math.cos(a)
        ly = cy + label_dist * math.sin(a)
        c = colors[i]
        name_short = DIMS_DATA[k][lang]["name"]
        svg.append(f'<rect x="{lx-30:.1f}" y="{ly-12:.1f}" width="60" height="24" rx="6" fill="{c}" opacity="0.12"/>')
        svg.append(f'<text x="{lx:.1f}" y="{ly+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="10" font-weight="700" fill="{c}">{name_short}</text>')
    
    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="#94A3B8"/>')
    svg.append("</svg>")
    return "\n".join(svg)

def gauge_svg(value):
    if value is None:
        return ""
    level = get_level(value)
    color = level["color"]
    circ = math.pi * 58
    dash = (value / 100) * circ
    nx = 88 + 46 * math.cos(math.radians(180 - (value/100)*180))
    ny = 84 - 46 * math.sin(math.radians(180 - (value/100)*180))
    return f'''
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
        <circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{color}" opacity="0.9"/>
        <text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827" font-family="monospace">{value}%</text>
    </svg>'''

def trend_svg(sessions, w=350, h=90):
    if len(sessions) < 2:
        return ""
    vals = [s["cpi"] for s in sessions if s.get("cpi")]
    if len(vals) < 2:
        return ""
    pad = 16
    min_v = max(0, min(vals) - 10)
    max_v = min(100, max(vals) + 10)
    def x(i):
        return pad + (i / (len(vals) - 1)) * (w - pad * 2)
    def y(v):
        if max_v == min_v:
            return h / 2
        return h - pad - ((v - min_v) / (max_v - min_v)) * (h - pad * 2)
    area_pts = f"{x(0):.1f},{h} "
    area_pts += " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    area_pts += f" {x(len(vals)-1):.1f},{h}"
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

def metric_gauge_svg(value, color):
    if value is None:
        return ""
    circ = math.pi * 58
    dash = (max(0, min(100, value)) / 100) * circ
    nx = 88 + 46 * math.cos(math.radians(180 - (value/100)*180))
    ny = 84 - 46 * math.sin(math.radians(180 - (value/100)*180))
    return f'''
    <svg width="176" height="100" viewBox="0 0 176 100" xmlns="http://www.w3.org/2000/svg">
        <path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round"/>
        <path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/>
        <circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{color}" opacity="0.9"/>
        <text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827" font-family="monospace">{value}%</text>
    </svg>'''

def get_api_key():
    try:
        secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if secret_key:
            return secret_key, True
    except Exception:
        pass
    return st.session_state.get("api_key", ""), False

def call_claude(messages, system_prompt, api_key):
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
            json={"model": "claude-3-sonnet-20240229", "max_tokens": 1000, "system": system_prompt, "messages": messages},
            timeout=60
        )
        data = r.json()
        if "content" in data:
            return data["content"][0]["text"]
        return f"⚠️ API Error: {data.get('error', {}).get('message', 'Unknown')}"
    except Exception as e:
        return f"⚠️ Connection error: {str(e)}"

def inject_css(lang):
    direction = "rtl" if lang == "ar" else "ltr"
    st.markdown(f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'IBM Plex Sans Arabic', 'IBM Plex Sans', 'Segoe UI', sans-serif !important; direction: {direction}; background: #F8FAFC; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .cpi-header {{ background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white; padding: 20px 28px; border-radius: 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
    .cpi-header h1 {{ font-size: 20px; font-weight: 800; margin: 0; }}
    .cpi-header p {{ font-size: 11px; color: #94A3B8; margin: 5px 0 0; }}
    .cpi-formula {{ background: #1E3A5F; border-radius: 10px; padding: 8px 18px; font-size: 13px; color: #7DD3FC; font-weight: 700; font-family: monospace; }}
    .cpi-card {{ background: white; border: 1px solid #E8EDF5; border-radius: 14px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
    .gauge-wrap {{ background: linear-gradient(135deg, #F0F7FF, #EBF4FF); border: 1px solid #BFDBFE; border-radius: 14px; padding: 20px; text-align: center; }}
    .radar-wrap {{ display: flex; justify-content: center; padding: 12px; background: white; border: 1px solid #E8EDF5; border-radius: 14px; }}
    .level-0 {{ background: #FEF2F2; color: #DC2626; border: 1.5px solid #FECACA; }}
    .level-1 {{ background: #FFF7ED; color: #EA580C; border: 1.5px solid #FED7AA; }}
    .level-2 {{ background: #FFFBEB; color: #D97706; border: 1.5px solid #FDE68A; }}
    .level-3 {{ background: #EFF6FF; color: #2563EB; border: 1.5px solid #BFDBFE; }}
    .level-4 {{ background: #F0FDF4; color: #059669; border: 1.5px solid #A7F3D0; }}
    .level-5 {{ background: #F5F3FF; color: #7C3AED; border: 1.5px solid #DDD6FE; }}
    .stButton>button {{ border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s ease !important; }}
    .stButton>button:hover {{ transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: #F8FAFC; border-radius: 12px; padding: 4px; border: 1px solid #E8EDF5; }}
    .stTabs [data-baseweb="tab"] {{ border-radius: 8px !important; font-weight: 600 !important; font-size: 13px !important; padding: 8px 14px !important; }}
    .stTabs [aria-selected="true"] {{ background: white !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important; }}
    .msg-user {{ background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white; border-radius: 12px 12px 4px 12px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; max-width: 88%; margin-left: auto; }}
    .msg-ai {{ background: white; color: #111827; border: 1px solid #E8EDF5; border-radius: 4px 12px 12px 12px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; max-width: 88%; }}
    .msg-ai-label {{ font-size: 10px; color: #7C3AED; font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 4px; }}
    </style>
    ''', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# 6. واجهة المستخدم الرئيسية
# ════════════════════════════════════════════════════════════════════

lang = st.session_state.lang
inject_css(lang)

col_head, col_lang = st.columns([5, 1])
with col_head:
    st.markdown(f'''
    <div class="cpi-header">
        <div>
            <h1>🧠 {t('app_title')}</h1>
            <p>{t('app_sub')}</p>
        </div>
        <div class="cpi-formula">{t('formula_label')}</div>
    </div>
    ''', unsafe_allow_html=True)

with col_lang:
    lang_choice = st.radio("🌐", ["ar", "en", "fr"],
        format_func=lambda x: {"ar": "🇩🇿 العربية", "en": "🇬🇧 English", "fr": "🇫🇷 Français"}[x],
        index=["ar", "en", "fr"].index(st.session_state.lang),
        key="lang_radio", label_visibility="visible")
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

# ════════════════════════════════════════════════════════════════════
# 7. التبويبات
# ════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("tab_assess"), t("tab_dashboard"),
    f"{t('tab_history')} ({len(st.session_state.sessions)})",
    t("tab_facilitator"), t("tab_charter"), t("tab_admin")
])

# ════════════════════════════════════════════════════════════════════
# 8. TAB 1: تقييم جلسة (مختصر لتوفير المساحة - نفس الكود السابق)
# ════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown(f'<div style="font-size:13px; color:#6B7280; margin-bottom:16px;">{t("assess_intro")}<br><strong>{t("scale_hint")}</strong></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        team_name = st.text_input(t("team_name"), value="فريق الابتكار", key="team_name_input")
    with col2:
        project_name = st.text_input(t("project_name"), value="Sprint 1", key="project_name_input")
    
    col3, col4 = st.columns(2)
    with col3:
        session_num = st.number_input(t("session_num"), min_value=1, value=st.session_state.session_num_counter, key="session_num_input")
    with col4:
        session_date = st.date_input(t("session_date"), value=datetime.date.today(), key="session_date_input")
    
    st.markdown("---")
    
    mode_choice = st.radio(t("mode_label"), [t("mode_solo"), t("mode_pmp")], horizontal=True, key="assess_mode")
    st.markdown("---")
    
    # Solo Mode (مختصر)
    if mode_choice == t("mode_solo"):
        for k in DIM_KEYS:
            d = DIMS_DATA[k]
            current = st.session_state.scores.get(k, 2)
            name = d[lang]["name"]
            desc = d[lang]["desc"]
            q = d[lang]["q"]
            st.markdown(f'''
            <div style="background:#FAFBFF; border:1.5px solid #E8EDF5; border-radius:14px; padding:16px; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    <span style="background:{d['color']}18; color:{d['color']}; font-weight:800; font-size:12px; padding:3px 12px; border-radius:20px;">{k}</span>
                    <span style="font-size:16px; font-weight:800; color:{d['color']}">{name}</span>
                    <span style="margin-right:auto; font-size:18px; font-weight:800; font-family:monospace; color:{d['color']}">{current}/4</span>
                </div>
                <div style="font-size:12px; color:#94A3B8; margin-bottom:5px;">{desc}</div>
                <div style="font-size:13px; color:#475569; font-style:italic; background:rgba(255,255,255,0.7); border-radius:8px; padding:6px 12px; border-right:3px solid {d['color']};">«{q}»</div>
            </div>
            ''', unsafe_allow_html=True)
            new_val = st.select_slider(k, options=[1,2,3,4], value=current if current>0 else 2,
                format_func=lambda v: f"{v} --- {['ضعيف','مقبول','جيد','متقدم'][v-1]}" if lang=="ar" else f"{v}",
                label_visibility="collapsed", key=f"slider_{k}")
            if new_val != current:
                st.session_state.scores[k] = new_val
                st.rerun()
        
        cpi_now = calc_cpi(st.session_state.scores)
        if cpi_now:
            level = get_level(cpi_now)
            col_g, col_r = st.columns(2)
            with col_g:
                st.markdown(f'<div class="gauge-wrap"><div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px;">{t("cpi_computed")}</div>{gauge_svg(cpi_now)}<div style="font-size:14px;font-weight:800;color:{level["color"]};margin-top:8px;background:{level["color"]}15;padding:6px 16px;border-radius:20px;display:inline-block">{level["title"]}</div></div>', unsafe_allow_html=True)
            with col_r:
                st.markdown(f'<div class="radar-wrap">{radar_svg(st.session_state.scores)}</div>', unsafe_allow_html=True)
            
            if st.button(f"{t('btn_record')} --- CPI: {cpi_now}%", type="primary", use_container_width=True):
                try:
                    cpi_db.init_db()
                    cpi_db.save_cpi_session({
                        "team_name": team_name, "project_name": project_name,
                        "session_number": int(session_num), "session_date": str(session_date),
                        "score_eh": float(st.session_state.scores.get("EH",2)),
                        "score_l": float(st.session_state.scores.get("L",2)),
                        "score_p": float(st.session_state.scores.get("P",2)),
                        "score_g": float(st.session_state.scores.get("G",2)),
                        "cpi_score_final": float(cpi_now), "alignment_index": 100.0,
                        "std_deviation": 0.0, "participant_count": 1,
                        "maturity_level": level["title"], "lang": lang,
                    })
                    db_sessions = cpi_db.load_historical_scores(limit=500)
                    new_sessions = []
                    for row in db_sessions:
                        new_sessions.append({
                            "id": row.get("id"), "label": row.get("project_name", "جلسة"),
                            "team": row.get("team_name", "فريق"), "date": row.get("session_date", ""),
                            "cpi": float(row.get("cpi_score_final", 0)),
                            "alignment_index": row.get("alignment_index"),
                            "scores": {"EH": float(row.get("score_eh",2)), "L": float(row.get("score_l",2)),
                                      "P": float(row.get("score_p",2)), "G": float(row.get("score_g",2))},
                            "session_number": row.get("session_number", 0)
                        })
                    st.session_state.sessions = new_sessions
                    st.session_state.session_num_counter = int(session_num) + 1
                    st.session_state.scores = {k: 2 for k in DIM_KEYS}
                    st.success(t("save_success"))
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
        else:
            st.info(t("complete_all"))
    
    # PMP Mode (مختصر)
    else:
        st.markdown(f'<div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:12px; padding:14px; margin-bottom:18px; font-size:13px; color:#4C1D95;">👥 {t("pmp_intro")}</div>', unsafe_allow_html=True)
        
        if not st.session_state.pmp_participants:
            st.session_state.pmp_participants = [{"uid": 1, "name": "", "specialization": "", "role": PMP_ROLES[lang][0], "scores": {"P": 2, "L": 2, "G": 2, "EH": 2}}]
            st.session_state.pmp_next_uid = 2
        
        for idx, p in enumerate(st.session_state.pmp_participants):
            uid = p["uid"]
            with st.expander(f"👤 {t('pmp_participant')} {idx+1}: {p['name'] or 'جديد'} - {p['role']}", expanded=(idx == len(st.session_state.pmp_participants)-1)):
                c1, c2, c3 = st.columns([2,2,1.5])
                with c1:
                    p["name"] = st.text_input(t("pmp_name"), value=p["name"], key=f"pmp_name_{uid}")
                with c2:
                    p["specialization"] = st.text_input(t("pmp_specialization"), value=p["specialization"], key=f"pmp_spec_{uid}")
                with c3:
                    p["role"] = st.selectbox(t("pmp_role"), PMP_ROLES[lang], index=PMP_ROLES[lang].index(p["role"]) if p["role"] in PMP_ROLES[lang] else 0, key=f"pmp_role_{uid}")
                
                st.markdown("**التقييم:**")
                cols = st.columns(4)
                for i, k in enumerate(DIM_KEYS):
                    with cols[i]:
                        p["scores"][k] = st.number_input(f"{k}", min_value=1, max_value=4, value=p["scores"][k], step=1, key=f"pmp_score_{uid}_{k}")
            
            if len(st.session_state.pmp_participants) > 1:
                if st.button(t("pmp_remove_participant"), key=f"remove_{uid}"):
                    st.session_state.pmp_participants = [x for x in st.session_state.pmp_participants if x["uid"] != uid]
                    st.session_state.pmp_stats = None
                    st.rerun()
        
        col_add, col_comp = st.columns([1,2])
        with col_add:
            if st.button(t("pmp_add_participant"), use_container_width=True):
                st.session_state.pmp_participants.append({"uid": st.session_state.pmp_next_uid, "name": "", "specialization": "", "role": PMP_ROLES[lang][0], "scores": {"P": 2, "L": 2, "G": 2, "EH": 2}})
                st.session_state.pmp_next_uid += 1
                st.rerun()
        with col_comp:
            if st.button(t("pmp_compute"), type="primary", use_container_width=True):
                named = [p for p in st.session_state.pmp_participants if p["name"].strip()]
                if not named:
                    st.warning("أضف اسم مشارك واحد على الأقل")
                else:
                    scores_list = [p["scores"] for p in named]
                    st.session_state.pmp_stats = cpi_db.calculate_collective_stats(scores_list)
                    st.session_state.pmp_named = named
        
        if st.session_state.pmp_stats:
            stats = st.session_state.pmp_stats
            collective_cpi = stats["collective_cpi"]
            cai = stats["alignment_index"]
            std_dev = stats["std_deviation"]
            individual_cpis = stats["individual_cpis"]
            gap_by_dim = stats["gap_by_dimension"]
            named = st.session_state.get("pmp_named", [])
            
            level, capped = get_level_v7(collective_cpi, cai)
            cai_info = cpi_db.cai_interpretation(cai, lang)
            
            team_avg = {}
            for k in DIM_KEYS:
                vals = [p["scores"].get(k, 2) for p in named]
                team_avg[k] = sum(vals) / len(vals) if vals else 2
            
            st.markdown("---")
            st.markdown(f"### 📊 {t('pmp_results_title')}")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(f'<div class="gauge-wrap">{gauge_svg(int(round(collective_cpi)))}<div style="margin-top:8px;font-weight:800;color:{level["color"]}">{level["title"]}</div></div>', unsafe_allow_html=True)
            with col_c2:
                st.markdown(f'<div class="gauge-wrap">{metric_gauge_svg(int(round(cai)), cai_info["color"])}<div style="margin-top:8px;font-weight:800;color:{cai_info["color"]}">{cai_info["title"]}</div><div style="font-size:11px;color:#94A3B8">{cai_info["desc"]}</div></div>', unsafe_allow_html=True)
            
            if capped:
                st.warning(t("pmp_capped_note"))
            
            st.markdown(f"### 🗺️ {t('pmp_gap_map_title')}")
            for k in DIM_KEYS:
                gap = gap_by_dim.get(k, 0)
                pct = min(100, (gap / 1.5) * 100)
                gcol = "#10B981" if gap < 0.4 else ("#F59E0B" if gap < 0.9 else "#DC2626")
                st.markdown(f'''
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                        <span style="font-weight:700; color:{DIMS_DATA[k]['color']}">{DIMS_DATA[k][lang]['name']} ({k})</span>
                        <span style="font-family:monospace; font-weight:800; color:{gcol}">σ = {gap}</span>
                    </div>
                    <div style="height:8px; background:#F1F5F9; border-radius:100px; overflow:hidden;">
                        <div style="height:100%; width:{pct}%; background:{gcol}; border-radius:100px;"></div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown(f"### 👥 {t('pmp_individual_table')}")
            for p, icpi in zip(named, individual_cpis):
                ilvl = get_level(icpi)
                st.markdown(f'''
                <div style="display:flex; justify-content:space-between; align-items:center; background:#FAFBFF; border:1px solid #E8EDF5; border-radius:10px; padding:10px 16px; margin-bottom:8px;">
                    <div><span style="font-weight:700">{p['name']}</span> <span style="font-size:11px; color:#94A3B8"> · {p['specialization']} · {p['role']}</span></div>
                    <span style="font-weight:800; font-family:monospace; font-size:18px; color:{ilvl['color']}">{icpi}%</span>
                </div>
                ''', unsafe_allow_html=True)
            
            prompt = cpi_db.discussion_prompt(cai, lang)
            st.markdown(f'''
            <div style="background:#FFF7ED; border:1.5px solid #FCD34D; border-radius:12px; padding:16px; margin-top:12px; text-align:center;">
                <div style="font-size:11px; font-weight:700; color:#92400E; margin-bottom:8px;">💬 {t('pmp_discussion_title')}</div>
                <div style="font-size:14px; font-weight:700; color:#78350F;">❝ {prompt} ❞</div>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button(t("pmp_save_btn"), type="primary", use_container_width=True):
                try:
                    participants_payload = []
                    for p, icpi in zip(named, individual_cpis):
                        participants_payload.append({
                            "name": p["name"], "specialization": p["specialization"], "role": p["role"],
                            "scores": p["scores"], "individual_cpi": icpi
                        })
                    cpi_db.init_db()
                    cpi_db.save_cpi_session({
                        "team_name": team_name, "project_name": project_name,
                        "session_number": int(session_num), "session_date": str(session_date),
                        "score_eh": float(team_avg["EH"]), "score_l": float(team_avg["L"]),
                        "score_p": float(team_avg["P"]), "score_g": float(team_avg["G"]),
                        "cpi_score_final": float(collective_cpi), "alignment_index": float(cai),
                        "std_deviation": float(std_dev), "participant_count": len(named),
                        "maturity_level": level["title"], "lang": lang,
                    }, participants=participants_payload)
                    
                    db_sessions = cpi_db.load_historical_scores(limit=500)
                    new_sessions = []
                    for row in db_sessions:
                        new_sessions.append({
                            "id": row.get("id"), "label": row.get("project_name", "جلسة"),
                            "team": row.get("team_name", "فريق"), "date": row.get("session_date", ""),
                            "cpi": float(row.get("cpi_score_final", 0)),
                            "alignment_index": row.get("alignment_index"),
                            "scores": {"EH": float(row.get("score_eh",2)), "L": float(row.get("score_l",2)),
                                      "P": float(row.get("score_p",2)), "G": float(row.get("score_g",2))},
                            "session_number": row.get("session_number", 0)
                        })
                    st.session_state.sessions = new_sessions
                    st.session_state.pmp_participants = [{"uid": 1, "name": "", "specialization": "", "role": PMP_ROLES[lang][0], "scores": {"P": 2, "L": 2, "G": 2, "EH": 2}}]
                    st.session_state.pmp_next_uid = 2
                    st.session_state.pmp_stats = None
                    st.session_state.session_num_counter = int(session_num) + 1
                    st.success(t("save_success"))
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")

# ════════════════════════════════════════════════════════════════════
# 9. TAB 2: لوحة القيادة
# ════════════════════════════════════════════════════════════════════

with tab2:
    if not st.session_state.sessions:
        st.info(t("no_data"))
    else:
        last = st.session_state.sessions[-1]
        level = get_level(last["cpi"])
        bdi = calc_bdi(st.session_state.sessions)
        
        col_g, col_r = st.columns(2)
        with col_g:
            st.markdown(f'<div class="gauge-wrap"><div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px;">{t("last_cpi")}</div>{gauge_svg(last["cpi"])}<div style="font-size:14px;font-weight:800;color:{level["color"]};margin-top:8px;">{level["title"]}</div><div style="font-size:11px;color:#94A3B8;margin-top:8px;">{last["label"]} · {last["date"]}</div></div>', unsafe_allow_html=True)
        with col_r:
            st.markdown(f'<div class="radar-wrap">{radar_svg(last["scores"])}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"### 📊 {t('dim_detail')}")
        for k in DIM_KEYS:
            v = last["scores"].get(k, 0)
            color = DIMS_DATA[k]["color"]
            name = DIMS_DATA[k][lang]["name"]
            pct = (v / 4) * 100
            st.markdown(f'''
            <div style="margin-bottom:12px; padding:12px; background:#FAFBFF; border-radius:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div><span style="background:{color}18; color:{color}; font-weight:800; padding:2px 10px; border-radius:20px; font-size:11px;">{k}</span> <span style="font-weight:700; margin-left:8px;">{name}</span></div>
                    <span style="font-weight:800; font-family:monospace; color:{color}">{v}/4</span>
                </div>
                <div style="height:8px; background:#F1F5F9; border-radius:100px; overflow:hidden;">
                    <div style="height:100%; width:{pct}%; background:{color}; border-radius:100px;"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        if bdi:
            bdi_color = "#10B981" if bdi >= 75 else ("#3B82F6" if bdi >= 50 else "#EF4444")
            st.markdown(f'<div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:14px; padding:16px; display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;"><div><div style="font-weight:600;">{t("bdi_title")}</div><div style="font-size:11px; color:#9CA3AF;">{t("bdi_sub")}</div></div><div style="font-size:34px; font-weight:800; font-family:monospace; color:{bdi_color}">{bdi}%</div></div>', unsafe_allow_html=True)
        
        if len(st.session_state.sessions) >= 2:
            st.markdown(f'<div class="cpi-card"><div style="font-weight:700; margin-bottom:12px;">{t("trend_title")}</div>{trend_svg(st.session_state.sessions)}<div style="font-size:11px; color:#9CA3AF; margin-top:8px;">{len(st.session_state.sessions)} {t("sessions_recorded")}</div></div>', unsafe_allow_html=True)
        
        weak = [k for k in DIM_KEYS if last["scores"].get(k, 0) <= 2]
        st.markdown(f'<div class="cpi-card"><div style="font-weight:700; margin-bottom:12px;">{t("recs_title")}</div>', unsafe_allow_html=True)
        if not weak:
            st.markdown(f'<div style="color:#10B981; font-weight:600;">{t("recs_all_good")}</div>', unsafe_allow_html=True)
        else:
            for k in weak:
                name, color, rec_text = RECS[k][lang]
                st.markdown(f'<div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:10px; padding:10px; margin-bottom:8px;"><div style="font-weight:700; color:{color};">⚠ {name}</div><div style="color:#92400E; font-size:13px;">{rec_text}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# 10. TAB 3: السجل
# ════════════════════════════════════════════════════════════════════

with tab3:
    if not st.session_state.sessions:
        st.info(t("no_sessions"))
    else:
        col_h, col_d = st.columns([3,1])
        with col_h:
            st.markdown(f"### 📋 {len(st.session_state.sessions)} {t('sessions_recorded')}")
        with col_d:
            if st.button(t("delete_all"), type="secondary"):
                st.session_state.sessions = []
                st.rerun()
        
        for s in reversed(st.session_state.sessions):
            lvl = get_level(s["cpi"])
            with st.expander(f"📌 {s['label']} --- {s['date']} (CPI: {s['cpi']}%)"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**الفريق:** {s['team']}")
                    st.markdown(f"**المستوى:** {lvl['title']}")
                    st.markdown(f"**CAI:** {s.get('alignment_index', 'غير محدد')}%")
                with col_b:
                    st.markdown(f"**CPI:** {s['cpi']}%")
                st.markdown("**تفصيل الأبعاد:**")
                cols = st.columns(4)
                for i, k in enumerate(DIM_KEYS):
                    with cols[i]:
                        st.markdown(f"**{k}**<br>{s['scores'].get(k, 0)}/4", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# 11. TAB 4: الميسر المعرفي
# ════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown(f'<div style="background:linear-gradient(135deg,#0F172A,#1E293B); color:white; border-radius:16px; padding:20px; margin-bottom:16px;"><div style="display:flex; align-items:center; gap:12px;"><div style="font-size:28px;">🧠</div><div><div style="font-weight:800; font-size:18px;">{t("tab_facilitator")}</div><div style="font-size:11px; color:#94A3B8;">Powered by Claude AI</div></div></div><div style="font-size:13px; color:#CBD5E1; background:rgba(255,255,255,0.05); border-radius:10px; padding:10px; margin-top:12px;">{t("fac_sub")}</div></div>', unsafe_allow_html=True)
    
    api_key, from_secrets = get_api_key()
    if not from_secrets:
        api_key_input = st.text_input("Anthropic API Key", value=st.session_state.api_key, type="password")
        if api_key_input:
            st.session_state.api_key = api_key_input
    
    user_input = st.text_area("المدخلات:", placeholder="الصق محضر الاجتماع أو اكتب سؤالك هنا...", height=150)
    if st.button("📤 إرسال للميسر", type="primary"):
        if not st.session_state.api_key:
            st.error("أدخل مفتاح Anthropic API أولاً")
        elif not user_input.strip():
            st.warning("اكتب رسالتك أولاً")
        else:
            with st.spinner("🧠 الميسر يحلل..."):
                system_prompt = f"أنت ميسر معرفي محايد متخصص في نظرية CPI (مؤشر التلاقح المعرفي) لـ د. الحبيب خروبي. الصيغة: CI = NK × EH. قم بتحليل النص وتقديم تقييم ورؤى وتوصيات. الرد بـ {lang}."
                reply = call_claude([{"role": "user", "content": user_input}], system_prompt, st.session_state.api_key)
                st.markdown(f'<div class="msg-ai"><div class="msg-ai-label">🧠 {t("tab_facilitator")}</div>{reply}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# 12. TAB 5: الميثاق
# ════════════════════════════════════════════════════════════════════

with tab5:
    st.markdown(f'<div style="background:linear-gradient(135deg,#0F172A,#1E293B); color:white; border-radius:16px; padding:24px; margin-bottom:20px;"><div style="display:flex; align-items:center; gap:12px;"><div style="font-size:28px;">📜</div><div><div style="font-size:18px; font-weight:800;">{t("charter_title")}</div><div style="font-size:11px; color:#94A3B8;">الإصدار 1.1 · د. الحبيب خروبي · ESU-001 · جوان 2026</div></div></div><div style="font-size:13px; color:#CBD5E1; background:rgba(255,255,255,0.05); border-radius:10px; padding:12px; margin-top:12px;">{t("charter_preamble")}</div></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div style="background:#FFF7ED; border:1.5px solid #FCD34D; border-radius:14px; padding:18px; margin-bottom:22px; text-align:center;"><div style="font-size:11px; font-weight:700; color:#92400E; margin-bottom:8px;">المبدأ المحوري</div><div style="font-size:15px; font-weight:700; color:#78350F;">❝ {t("charter_axiom")} ❞</div><div style="font-size:12px; font-family:monospace; color:#B45309; margin-top:10px;">CI = NK × EH</div></div>', unsafe_allow_html=True)
    
    signer = st.text_input("اسمك الكامل", placeholder="ادخل اسمك...")
    if st.button("✍️ أوقّع", type="primary"):
        if signer.strip():
            st.session_state.signatories.append({"name": signer.strip(), "time": datetime.datetime.now().strftime("%H:%M")})
            st.success("التزامك مُسجَّل --- يمكنك الانتقال إلى تقييم الجلسة.")
            st.rerun()
    
    if st.session_state.signatories:
        st.markdown(f"**الموقّعون في هذه الجلسة ({len(st.session_state.signatories)}):**")
        for sig in st.session_state.signatories:
            st.markdown(f"✅ {sig['name']} ({sig['time']})")

# ════════════════════════════════════════════════════════════════════
# 13. TAB 6: الإدارة (المُصلح بالكامل)
# ════════════════════════════════════════════════════════════════════

with tab6:
    try:
        stats = cpi_db.get_statistics()
        teams = cpi_db.get_all_teams()
    except Exception as e:
        stats = {"total_sessions": 0, "avg_cpi": 0, "total_teams": 0}
        teams = []
    
    st.markdown(f"### 📊 {t('stats_title')}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric(t("total_sessions"), stats.get("total_sessions", 0))
    c2.metric(t("avg_cpi"), f"{stats.get('avg_cpi', 0)}%")
    c3.metric(t("total_teams"), stats.get("total_teams", 0))
    
    if teams:
        st.markdown(f"### 🏢 {t('teams_list_title')}")
        for team in teams:
            st.markdown(f"- {team}")
    
    st.markdown("---")
    
    if st.button(t("export_btn"), type="secondary"):
        csv_data = cpi_db.export_all_csv()
        if csv_data:
            st.download_button(
                t("download_csv"), 
                data=csv_data, 
                file_name=f"CPI_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv", 
                mime="text/csv"
            )

# ════════════════════════════════════════════════════════════════════
# 14. Footer
# ════════════════════════════════════════════════════════════════════

st.markdown(f'''
<div style="text-align:center; margin-top:48px; padding:20px; background:linear-gradient(135deg,#0F172A,#1E293B); border-radius:16px;">
    <div style="font-size:13px; font-weight:700; color:#E2E8F0;">🧠 {t("footer")}</div>
    <div style="font-size:11px; color:#64748B; font-family:monospace;">CPI Framework v7.3.1 · CI = NK × EH · {datetime.datetime.now().year}</div>
</div>
''', unsafe_allow_html=True)
