# ═══════════════════════════════════════════════════════════════════
# مؤشر التلاقح المعرفي — CPI Dashboard v7.3.4
# Cross-Pollination Index · Indice de Pollinisation Croisée
# د. الحبيب خروبي · ESU-001
# الإصلاحات: mode_choice ثابت، PMP sliders، CAI None%، footer،
#            ترجمة البُعد P، محدد اللغة أفقي، placeholder بدل value،
#            نموذج Claude محدّث، حذف DB حقيقي
# ═══════════════════════════════════════════════════════════════════
import streamlit as st
import math
import datetime
import requests
import cpi_db

st.set_page_config(
    page_title="CPI Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════
if "lang"                not in st.session_state: st.session_state.lang                = "ar"
if "sessions"            not in st.session_state: st.session_state.sessions            = []
if "scores"              not in st.session_state: st.session_state.scores              = {"P":1,"L":1,"G":1,"EH":1}
if "fac_msgs"            not in st.session_state: st.session_state.fac_msgs            = []
if "api_key"             not in st.session_state: st.session_state.api_key             = ""
if "signatories"         not in st.session_state: st.session_state.signatories         = []
if "session_num_counter" not in st.session_state: st.session_state.session_num_counter = 1
if "pmp_participants"    not in st.session_state: st.session_state.pmp_participants    = []
if "pmp_next_uid"        not in st.session_state: st.session_state.pmp_next_uid        = 1
if "pmp_stats"           not in st.session_state: st.session_state.pmp_stats           = None

# ── تحميل DB عند أول إقلاع ──────────────────────────────────────────
if "data_loaded" not in st.session_state:
    try:
        cpi_db.init_db()
        rows = cpi_db.load_historical_scores(limit=500)
        st.session_state.sessions = [{
            "id":              r.get("id"),
            "label":           r.get("project_name","جلسة"),
            "team":            r.get("team_name","فريق"),
            "date":            str(r.get("session_date","")),
            "cpi":             float(r.get("cpi_score_final",0)),
            "alignment_index": r.get("alignment_index"),
            "session_number":  r.get("session_number",1),
            "maturity_level":  r.get("maturity_level",""),
            "lang":            r.get("lang","ar"),
            "scores": {
                "P":  float(r.get("score_p",1)),
                "L":  float(r.get("score_l",1)),
                "G":  float(r.get("score_g",1)),
                "EH": float(r.get("score_eh",1)),
            },
        } for r in rows]
        if st.session_state.sessions:
            st.session_state.session_num_counter = len(st.session_state.sessions) + 1
    except Exception:
        st.session_state.sessions = []
    st.session_state.data_loaded = True

# ════════════════════════════════════════════════════════════════════
# دالة إعادة تحميل من DB
# ════════════════════════════════════════════════════════════════════
def _reload_from_db():
    try:
        cpi_db.init_db()
        rows = cpi_db.load_historical_scores(limit=500)
        st.session_state.sessions = [{
            "id":              r.get("id"),
            "label":           r.get("project_name","جلسة"),
            "team":            r.get("team_name","فريق"),
            "date":            str(r.get("session_date","")),
            "cpi":             float(r.get("cpi_score_final",0)),
            "alignment_index": r.get("alignment_index"),
            "session_number":  r.get("session_number",1),
            "maturity_level":  r.get("maturity_level",""),
            "lang":            r.get("lang","ar"),
            "scores": {
                "P":  float(r.get("score_p",1)),
                "L":  float(r.get("score_l",1)),
                "G":  float(r.get("score_g",1)),
                "EH": float(r.get("score_eh",1)),
            },
        } for r in rows]
    except Exception:
        pass

# ════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ════════════════════════════════════════════════════════════════════
TR = {
"app_title":      {"ar":"مؤشر التلاقح المعرفي",       "en":"Cross-Pollination Index",           "fr":"Indice de Pollinisation Croisée"},
"app_sub":        {"ar":"CPI Dashboard · د. الحبيب خروبي · ESU-001","en":"CPI Dashboard · Dr. Elhabib Kherroubi · ESU-001","fr":"Tableau de bord CPI · Dr. Elhabib Kherroubi · ESU-001"},
"formula":        {"ar":"CI = NK × EH",                "en":"CI = NK × EH",                      "fr":"IC = SC × HE"},
"tab_assess":     {"ar":"📝 تقييم جلسة",               "en":"📝 Session Assessment",             "fr":"📝 Évaluation de session"},
"tab_dash":       {"ar":"📊 لوحة القيادة",             "en":"📊 Dashboard",                      "fr":"📊 Tableau de bord"},
"tab_hist":       {"ar":"🗂️ السجل",                   "en":"🗂️ History",                       "fr":"🗂️ Historique"},
"tab_fac":        {"ar":"🧠 الميسر المعرفي",           "en":"🧠 Cognitive Facilitator",          "fr":"🧠 Facilitateur Cognitif"},
"tab_charter":    {"ar":"📜 الميثاق",                  "en":"📜 Charter",                        "fr":"📜 Charte"},
"tab_admin":      {"ar":"📊 الإدارة",                  "en":"📊 Admin",                          "fr":"📊 Administration"},
"team_lbl":       {"ar":"اسم الفريق",                  "en":"Team Name",                         "fr":"Nom de l'équipe"},
"team_ph":        {"ar":"مثال: فريق الابتكار",         "en":"e.g. Innovation Team",              "fr":"ex. Équipe Innovation"},
"proj_lbl":       {"ar":"اسم المشروع / الجلسة",        "en":"Project / Session Name",            "fr":"Projet / Nom de la session"},
"proj_ph":        {"ar":"مثال: Sprint 3",              "en":"e.g. Sprint 3",                     "fr":"ex. Sprint 3"},
"sess_num":       {"ar":"رقم الجلسة",                  "en":"Session #",                         "fr":"N° de session"},
"sess_date":      {"ar":"التاريخ",                     "en":"Date",                              "fr":"Date"},
"mode_lbl":       {"ar":"نمط القياس:",                 "en":"Measurement Mode:",                 "fr":"Mode de mesure :"},
"mode_solo":      {"ar":"👤 تقييم فردي سريع",          "en":"👤 Quick Individual",               "fr":"👤 Évaluation individuelle"},
"mode_pmp":       {"ar":"👥 القياس التشاركي (PMP)",    "en":"👥 Participatory (PMP)",            "fr":"👥 Mesure participative (PMP)"},
"btn_record":     {"ar":"✅ تسجيل الجلسة",             "en":"✅ Record Session",                 "fr":"✅ Enregistrer la séance"},
"save_ok":        {"ar":"✅ تم الحفظ بنجاح!",          "en":"✅ Saved successfully!",             "fr":"✅ Enregistré avec succès!"},
"complete_all":   {"ar":"أكمل تقييم الأبعاد الأربعة", "en":"Complete all four dimensions",      "fr":"Complétez les quatre dimensions"},
"cpi_computed":   {"ar":"CPI المحسوب",                 "en":"Computed CPI",                      "fr":"CPI calculé"},
"last_cpi":       {"ar":"آخر CPI مسجّل",               "en":"Latest recorded CPI",               "fr":"Dernier CPI enregistré"},
"dim_detail":     {"ar":"تفصيل الأبعاد",               "en":"Dimension Breakdown",               "fr":"Détail des dimensions"},
"trend_title":    {"ar":"مسار CPI عبر الزمن",          "en":"CPI Trend Over Time",               "fr":"Évolution du CPI"},
"sessions_count": {"ar":"جلسة مسجّلة",                 "en":"sessions recorded",                 "fr":"séances enregistrées"},
"recs_title":     {"ar":"توصيات التحسين",               "en":"Improvement Recommendations",       "fr":"Recommandations d'amélioration"},
"recs_good":      {"ar":"✓ جميع الأبعاد في مستوى جيد.","en":"✓ All dimensions at a good level.", "fr":"✓ Toutes les dimensions sont bonnes."},
"bdi_title":      {"ar":"مؤشر اختفاء الحدود (BDI)",    "en":"Boundary Disappearance Index (BDI)","fr":"Indice de disparition des frontières"},
"bdi_sub":        {"ar":"كلما اقترب من 100% اقترب الفريق من العقل الجماعي","en":"Closer to 100% = closer to genuine collective intelligence","fr":"Plus proche de 100% = plus proche de l'intelligence collective"},
"no_data":        {"ar":"لا توجد بيانات مسجّلة بعد.",  "en":"No data recorded yet.",             "fr":"Aucune donnée enregistrée."},
"no_sessions":    {"ar":"لا توجد جلسات مسجّلة بعد",    "en":"No sessions recorded yet",          "fr":"Aucune séance enregistrée"},
"delete_all":     {"ar":"🗑️ حذف الكل",                "en":"🗑️ Delete all",                    "fr":"🗑️ Tout supprimer"},
"assess_intro":   {"ar":"قيّم الأبعاد الأربعة بعد كل Sprint أو اجتماع حاسم.","en":"Rate the four dimensions after each Sprint or key meeting.","fr":"Évaluez les quatre dimensions après chaque Sprint ou réunion clé."},
"scale_hint":     {"ar":"1=ضعيف · 2=مقبول · 3=جيد · 4=متقدم (اختفاء الحدود)","en":"1=Weak · 2=Acceptable · 3=Good · 4=Advanced (boundary disappearance)","fr":"1=Faible · 2=Acceptable · 3=Bien · 4=Avancé (disparition des frontières)"},
"pmp_intro":      {"ar":"كل عضو يُدخل تقييمه بشكل منفصل (أعمى). يحسب النظام CPI الجماعي وCAI آلياً.","en":"Each member enters their assessment separately (blind). The system computes Collective CPI and CAI automatically.","fr":"Chaque membre saisit son évaluation séparément (à l'aveugle). Le système calcule automatiquement le CPI collectif et le CAI."},
"pmp_remove":     {"ar":"🗑️ حذف",                     "en":"🗑️ Remove",                        "fr":"🗑️ Supprimer"},
"pmp_add":        {"ar":"➕ إضافة مشارك",              "en":"➕ Add Participant",                "fr":"➕ Ajouter un participant"},
"pmp_compute":    {"ar":"🧮 حساب النتائج الجماعية",    "en":"🧮 Compute Collective Results",     "fr":"🧮 Calculer les résultats"},
"pmp_save":       {"ar":"💾 حفظ جلسة PMP",             "en":"💾 Save PMP Session",               "fr":"💾 Enregistrer la séance PMP"},
"pmp_collective": {"ar":"CPI الجماعي",                 "en":"Collective CPI",                    "fr":"CPI Collectif"},
"pmp_cai":        {"ar":"مؤشر الانسجام الإدراكي (CAI)","en":"Cognitive Alignment Index (CAI)",  "fr":"Indice d'alignement cognitif (CAI)"},
"pmp_gap":        {"ar":"خريطة الفجوات الإدراكية",     "en":"Cognitive Gap Map",                 "fr":"Carte des écarts cognitifs"},
"pmp_individuals":{"ar":"تقييمات الأفراد",             "en":"Individual Assessments",            "fr":"Évaluations individuelles"},
"pmp_discuss":    {"ar":"سؤال للنقاش الجماعي",         "en":"Discussion Prompt",                 "fr":"Question pour la discussion"},
"pmp_capped":     {"ar":"⚠ المستوى محدود بسبب انخفاض CAI.","en":"⚠ Level capped due to low CAI.","fr":"⚠ Niveau limité en raison d'un faible CAI."},
"pmp_warn":       {"ar":"أضف اسم مشارك واحد على الأقل","en":"Add at least one participant name", "fr":"Ajoutez au moins un nom de participant"},
"pmp_name":       {"ar":"الاسم",                       "en":"Name",                              "fr":"Nom"},
"pmp_spec":       {"ar":"التخصص",                      "en":"Specialization",                    "fr":"Spécialisation"},
"pmp_role":       {"ar":"الدور",                       "en":"Role",                              "fr":"Rôle"},
"pmp_results":    {"ar":"نتائج القياس التشاركي",       "en":"Participatory Measurement Results", "fr":"Résultats de la mesure participative"},
"hist_team":      {"ar":"الفريق:",                     "en":"Team:",                             "fr":"Équipe :"},
"hist_level":     {"ar":"المستوى:",                    "en":"Level:",                            "fr":"Niveau :"},
"hist_cai":       {"ar":"مؤشر الانسجام:",              "en":"Alignment:",                        "fr":"Alignement :"},
"not_defined":    {"ar":"غير محدد",                    "en":"N/A",                               "fr":"N/D"},
"fac_sub":        {"ar":"طرف ثالث محايد. يحلل لغة الفريق ويكشف التحيزات المعرفية.","en":"A neutral third party. Analyses team language and reveals cognitive biases.","fr":"Un tiers neutre. Analyse le langage de l'équipe et révèle les biais cognitifs."},
"fac_key":        {"ar":"مفتاح Anthropic API",         "en":"Anthropic API Key",                 "fr":"Clé API Anthropic"},
"fac_ph":         {"ar":"الصق محضر الاجتماع أو اكتب سؤالك هنا...","en":"Paste meeting minutes or type your question here...","fr":"Collez le compte rendu ou tapez votre question ici..."},
"fac_send":       {"ar":"📤 إرسال للميسر",             "en":"📤 Send to Facilitator",            "fr":"📤 Envoyer au facilitateur"},
"fac_clear":      {"ar":"🗑️ مسح المحادثة",            "en":"🗑️ Clear Chat",                    "fr":"🗑️ Effacer la conversation"},
"fac_thinking":   {"ar":"🧠 الميسر يحلل...",           "en":"🧠 Facilitator analysing...",       "fr":"🧠 Le facilitateur analyse..."},
"fac_err_key":    {"ar":"أدخل مفتاح Anthropic API أولاً","en":"Enter Anthropic API key first",  "fr":"Entrez d'abord la clé API Anthropic"},
"fac_err_msg":    {"ar":"اكتب رسالتك أولاً",           "en":"Type your message first",           "fr":"Tapez d'abord votre message"},
"charter_title":  {"ar":"ميثاق التلاقح المعرفي",       "en":"Cognitive Cross-Pollination Charter","fr":"Charte de Pollinisation Croisée Cognitive"},
"charter_ver":    {"ar":"الإصدار 1.1 · د. الحبيب خروبي · ESU-001 · جوان 2026","en":"v1.1 · Dr. Elhabib Kherroubi · ESU-001 · June 2026","fr":"v1.1 · Dr. Elhabib Kherroubi · ESU-001 · Juin 2026"},
"charter_body":   {"ar":"انطلاقاً من أن الابتكار الحقيقي لا ينتج عن تجميع المعارف الفردية بصورة منفصلة، بل عن التفاعل المنهجي بينها وتحويل الاختلافات المعرفية إلى طاقة إبداعية مشتركة — نعتمد هذا الميثاق عقداً معرفياً وأخلاقياً وتشغيلياً لفريقنا.","en":"True innovation does not arise from aggregating knowledge separately, but from its systematic interaction — transforming cognitive differences into shared creative energy. We adopt this Charter as our cognitive, ethical, and operational contract.","fr":"La véritable innovation ne provient pas de l'agrégation des connaissances individuelles, mais de leur interaction systématique — transformant les différences cognitives en énergie créative partagée. Nous adoptons cette Charte comme contrat cognitif, éthique et opérationnel."},
"charter_axiom":  {"ar":"التواضع المعرفي ليس مجرد فضيلة أخلاقية، بل بنية تشغيلية لازمة لظهور الذكاء الجماعي.","en":"Epistemic humility is not merely an ethical virtue — it is an operational structure necessary for collective intelligence to emerge.","fr":"L'humilité épistémique n'est pas seulement une vertu éthique — c'est une structure opérationnelle nécessaire à l'émergence de l'intelligence collective."},
"core_axiom":     {"ar":"المبدأ المحوري",              "en":"Core Axiom",                        "fr":"Axiome central"},
"charter_name_lbl":{"ar":"اسمك الكامل",               "en":"Full Name",                         "fr":"Nom complet"},
"charter_name_ph":{"ar":"أدخل اسمك...",                "en":"Enter your name...",                "fr":"Entrez votre nom..."},
"charter_sign":   {"ar":"✍️ أوقّع",                   "en":"✍️ Sign",                           "fr":"✍️ Signer"},
"charter_ok":     {"ar":"التزامك مُسجَّل — يمكنك الانتقال إلى تقييم الجلسة.","en":"Commitment recorded — proceed to session assessment.","fr":"Engagement enregistré — passez à l'évaluation de session."},
"charter_signers":{"ar":"الموقّعون في هذه الجلسة",    "en":"Signatories in this session",       "fr":"Signataires de cette session"},
"stats_title":    {"ar":"إحصائيات المنصة",             "en":"Platform Statistics",               "fr":"Statistiques de la plateforme"},
"total_sessions": {"ar":"إجمالي الجلسات",              "en":"Total Sessions",                    "fr":"Total des sessions"},
"avg_cpi":        {"ar":"متوسط CPI",                   "en":"Average CPI",                       "fr":"CPI Moyen"},
"total_teams":    {"ar":"إجمالي الفرق",                "en":"Total Teams",                       "fr":"Total des équipes"},
"teams_list":     {"ar":"الفرق المسجّلة",              "en":"Registered Teams",                  "fr":"Équipes enregistrées"},
"export_csv":     {"ar":"📥 تصدير CSV",                "en":"📥 Export CSV",                     "fr":"📥 Exporter CSV"},
"dl_csv":         {"ar":"📥 تحميل CSV",                "en":"📥 Download CSV",                   "fr":"📥 Télécharger CSV"},
"footer_text":    {"ar":"CPI — مؤشر التلاقح المعرفي · د. الحبيب خروبي · ESU-001","en":"CPI — Cross-Pollination Index · Dr. Elhabib Kherroubi · ESU-001","fr":"CPI — Indice de Pollinisation Croisée · Dr. Elhabib Kherroubi · ESU-001"},
}

def t(key):
    lang = st.session_state.get("lang","ar")
    return TR.get(key,{}).get(lang, TR.get(key,{}).get("ar", key))

# ════════════════════════════════════════════════════════════════════
# DATA
# ════════════════════════════════════════════════════════════════════
DIM_KEYS = ["P","L","G","EH"]

DIMS = {
"P":  {"color":"#2563EB",
       "ar":{"name":"الممارسة",        "desc":"مدى استيعاب كل تخصص لأولويات التخصص الآخر",         "q":"هل فهمنا أولويات بعضنا في القرارات؟"},
       "en":{"name":"Practice",         "desc":"How much each discipline grasps the other's priorities","q":"Did we understand each other's priorities in decisions?"},
       "fr":{"name":"Pratique",         "desc":"Dans quelle mesure chaque discipline comprend les priorités de l'autre","q":"Avons-nous compris les priorités de chacun dans les décisions ?"}},
"L":  {"color":"#059669",
       "ar":{"name":"اللغة المشتركة",  "desc":"وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال",      "q":"هل تحدثنا بلغة مشتركة دون سوء فهم؟"},
       "en":{"name":"Shared Language",  "desc":"A unified conceptual vocabulary enabling effective communication","q":"Did we speak a common language without misunderstanding?"},
       "fr":{"name":"Langage commun",   "desc":"Un vocabulaire conceptuel unifié permettant une communication efficace","q":"Avons-nous parlé un langage commun sans malentendus ?"}},
"G":  {"color":"#7C3AED",
       "ar":{"name":"التوجيه",          "desc":"اتجاه تدفق الأفكار داخل النظام",                    "q":"هل تدفقت الأفكار من الجميع (وليس فقط من القائد)؟"},
       "en":{"name":"Guidance",          "desc":"Direction of idea flow within the system",             "q":"Did ideas flow from everyone (not just the leader)?"},
       "fr":{"name":"Orientation",       "desc":"Direction du flux d'idées au sein du système",         "q":"Les idées ont-elles circulé de tous (pas seulement du leader) ?"}},
"EH": {"color":"#DC2626",
       "ar":{"name":"التواضع المعرفي", "desc":"قدرة الأفراد على قبول التصحيح والتعلم من الآخرين",  "q":"هل استمعنا لبعضنا بتواضع وغيرنا مواقفنا؟"},
       "en":{"name":"Epistemic Humility","desc":"Individuals' capacity to accept correction and learn from others","q":"Did we listen humbly and change our positions?"},
       "fr":{"name":"Humilité épistémique","desc":"Capacité des individus à accepter la correction et apprendre des autres","q":"Avons-nous écouté humblement et changé nos positions ?"}},
}

SL = {
"ar":{1:"ضعيف",2:"مقبول",3:"جيد",4:"متقدم"},
"en":{1:"Weak", 2:"Acceptable",3:"Good",4:"Advanced"},
"fr":{1:"Faible",2:"Acceptable",3:"Bien",4:"Avancé"},
}

LEVELS = {
"ar":[
{"min":0,  "max":25,  "cls":"level-0","title":"الصومعة المعرفية",  "color":"#DC2626","desc":"كل تخصص يعمل في عزلة تامة. الأولوية: كسر الصومعة وبناء أول جسر."},
{"min":25, "max":45,  "cls":"level-1","title":"العبقري المنعزل",   "color":"#EA580C","desc":"التخصصات تعمل بالتوازي دون تفاعل حقيقي. يلزم إعادة هيكلة ثقافة الفريق."},
{"min":45, "max":60,  "cls":"level-2","title":"تعاون شكلي",        "color":"#D97706","desc":"هناك تواصل لكنه تنفيذي لا توليدي. الأفكار لا تتقاطع بعمق."},
{"min":60, "max":75,  "cls":"level-3","title":"تلاقح ناشئ",        "color":"#2563EB","desc":"بدأ التلاقح المعرفي الحقيقي. الأفكار تتقاطع وتولد معرفة جديدة."},
{"min":75, "max":90,  "cls":"level-4","title":"ذكاء جماعي واعٍ",  "color":"#059669","desc":"التلاقح يحدث بانتظام. الفريق يعمل كوحدة متكاملة."},
{"min":90, "max":101, "cls":"level-5","title":"اختفاء الحدود",     "color":"#7C3AED","desc":"المعرفة خاصية ناشئة للنظام. العقل الجماعي الحقيقي تحقق."},
],
"en":[
{"min":0,  "max":25,  "cls":"level-0","title":"Knowledge Silo",               "color":"#DC2626","desc":"Each discipline operates in complete isolation. Priority: break the silo."},
{"min":25, "max":45,  "cls":"level-1","title":"Isolated Genius",              "color":"#EA580C","desc":"Disciplines work in parallel without real interaction. Cultural overhaul needed."},
{"min":45, "max":60,  "cls":"level-2","title":"Formal Cooperation",           "color":"#D97706","desc":"Communication exists but serves execution. Ideas rarely cross-pollinate deeply."},
{"min":60, "max":75,  "cls":"level-3","title":"Emerging Cross-Pollination",   "color":"#2563EB","desc":"Real cross-pollination has begun. Ideas intersect and generate new knowledge."},
{"min":75, "max":90,  "cls":"level-4","title":"Aware Collective Intelligence","color":"#059669","desc":"Cross-pollination occurs regularly. Team works as an integrated unit."},
{"min":90, "max":101, "cls":"level-5","title":"Boundary Disappearance",       "color":"#7C3AED","desc":"Knowledge is an emergent property of the system. True collective mind achieved."},
],
"fr":[
{"min":0,  "max":25,  "cls":"level-0","title":"Silo cognitif",                    "color":"#DC2626","desc":"Chaque discipline fonctionne en isolation totale. Priorité : briser le silo."},
{"min":25, "max":45,  "cls":"level-1","title":"Génie isolé",                      "color":"#EA580C","desc":"Les disciplines travaillent en parallèle sans interaction réelle."},
{"min":45, "max":60,  "cls":"level-2","title":"Coopération formelle",             "color":"#D97706","desc":"La communication existe mais reste exécutive. Les idées ne se croisent pas profondément."},
{"min":60, "max":75,  "cls":"level-3","title":"Pollinisation émergente",          "color":"#2563EB","desc":"La vraie pollinisation a commencé. Les idées génèrent de nouvelles connaissances."},
{"min":75, "max":90,  "cls":"level-4","title":"Intelligence collective consciente","color":"#059669","desc":"La pollinisation se produit régulièrement. L'équipe fonctionne comme une unité intégrée."},
{"min":90, "max":101, "cls":"level-5","title":"Disparition des frontières",       "color":"#7C3AED","desc":"La connaissance est une propriété émergente du système. Véritable intelligence collective."},
],
}

RECS = {
"P":  {"ar":("الممارسة",          "#2563EB","جلسات تظليل وظيفي أسبوعية — يظلل كل تخصص الآخر."),
       "en":("Practice",           "#2563EB","Weekly job shadowing sessions — each discipline shadows the other."),
       "fr":("Pratique",           "#2563EB","Séances d'observation hebdomadaires — chaque discipline observe l'autre.")},
"L":  {"ar":("اللغة المشتركة",    "#059669","ورشة قاموس مشترك — يوم واحد + تحديثات أسبوعية."),
       "en":("Shared Language",    "#059669","Shared glossary workshop — one day + weekly updates."),
       "fr":("Langage commun",     "#059669","Atelier glossaire commun — une journée + mises à jour hebdomadaires.")},
"G":  {"ar":("التوجيه",            "#7C3AED","إلغاء الموافقات الهرمية على الاقتراحات الصغيرة."),
       "en":("Guidance",           "#7C3AED","Remove hierarchical approval requirements for small proposals."),
       "fr":("Orientation",        "#7C3AED","Supprimer les approbations hiérarchiques pour les petites propositions.")},
"EH": {"ar":("التواضع المعرفي",   "#DC2626","جلسات مراجعة عمياء — تقييم الأفكار دون معرفة صاحبها."),
       "en":("Epistemic Humility", "#DC2626","Blind review sessions — evaluate ideas without knowing their author."),
       "fr":("Humilité épistémique","#DC2626","Séances de révision à l'aveugle — évaluer les idées sans connaître leur auteur.")},
}

PMP_ROLES = {
"ar":["ميسر معرفي","خبير","مهندس","مطور","محلل","منسق","عضو"],
"en":["Cognitive Facilitator","Expert","Engineer","Developer","Analyst","Coordinator","Member"],
"fr":["Facilitateur Cognitif","Expert","Ingénieur","Développeur","Analyste","Coordinateur","Membre"],
}

CAI_GATES   = {"level-0":0,"level-1":0,"level-2":50,"level-3":65,"level-4":80,"level-5":85}
LEVEL_ORDER = ["level-0","level-1","level-2","level-3","level-4","level-5"]

# ════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════
def get_level(cpi):
    lang = st.session_state.get("lang","ar")
    for l in LEVELS[lang]:
        if l["min"] <= cpi < l["max"]: return l
    return LEVELS[lang][-1]

def get_level_v7(cpi, cai=None):
    raw = get_level(cpi)
    if cai is None: return raw, False
    raw_idx = LEVEL_ORDER.index(raw["cls"]) if raw["cls"] in LEVEL_ORDER else 0
    eff_idx = 0
    for i in range(raw_idx, -1, -1):
        if cai >= CAI_GATES[LEVEL_ORDER[i]]:
            eff_idx = i; break
    if eff_idx == raw_idx: return raw, False
    lang = st.session_state.get("lang","ar")
    for l in LEVELS[lang]:
        if l["cls"] == LEVEL_ORDER[eff_idx]: return l, True
    return raw, False

def calc_cpi(scores):
    vals = [v for v in scores.values() if v > 0]
    if len(vals) < 4: return None
    return round(sum(vals) / 16 * 100)

def calc_bdi(sessions):
    if len(sessions) < 2: return None
    last = sessions[-1]["scores"]
    vals = [last[k] for k in DIM_KEYS]
    mean = sum(vals)/4
    var  = sum((v-mean)**2 for v in vals)/4
    return round(max(0, min(100, (1-var/2.25)*100)))

def get_api_key():
    try:
        k = st.secrets.get("ANTHROPIC_API_KEY","")
        if k: return k, True
    except Exception: pass
    return st.session_state.get("api_key",""), False

def call_claude(messages, system_prompt, api_key):
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"},
            json={"model":"claude-sonnet-4-6","max_tokens":1200,"system":system_prompt,"messages":messages},
            timeout=60,
        )
        data = r.json()
        if "content" in data: return data["content"][0]["text"]
        return "API Error: " + str(data.get("error",{}).get("message","Unknown"))
    except Exception as e:
        return f"Connection error: {e}"

# ════════════════════════════════════════════════════════════════════
# SVG
# ════════════════════════════════════════════════════════════════════
def radar_svg(scores, size=300):
    lang = st.session_state.get("lang","ar")
    pad=55; cx=cy=size/2; r=(size/2)-pad; n=len(DIM_KEYS)
    colors=[DIMS[k]["color"] for k in DIM_KEYS]
    def angle(i): return math.pi*2*i/n - math.pi/2
    def pt(i,val):
        a=angle(i); d=(val/4)*r
        return cx+d*math.cos(a), cy+d*math.sin(a)
    svg=[f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">']
    for v in [4,3,2,1]:
        pts=[]; fill="#F8FAFC" if v%2==0 else "#F1F5F9"
        for i in range(n):
            a=angle(i); d=(v/4)*r
            pts.append(f"{cx+d*math.cos(a):.1f},{cy+d*math.sin(a):.1f}")
        svg.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#E2E8F0" stroke-width="0.8"/>')
    for i in range(n):
        a=angle(i); x2=cx+r*math.cos(a); y2=cy+r*math.sin(a)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="4 3"/>')
    fp=[]
    for i,k in enumerate(DIM_KEYS):
        v=scores.get(k,0); x,y=pt(i,v); fp.append(f"{x:.1f},{y:.1f}")
    svg.append(f'<polygon points="{" ".join(fp)}" fill="rgba(37,99,235,0.15)" stroke="#2563EB" stroke-width="2.5" stroke-linejoin="round"/>')
    for i,k in enumerate(DIM_KEYS):
        v=scores.get(k,0); x,y=pt(i,v); c=colors[i]
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{c}" opacity="0.2"/>')
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{c}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{x:.1f}" y="{y+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="8" font-weight="700" fill="white">{v}</text>')
    for i,k in enumerate(DIM_KEYS):
        a=angle(i); lx=cx+(r+36)*math.cos(a); ly=cy+(r+36)*math.sin(a); c=colors[i]
        name=DIMS[k][lang]["name"]
        svg.append(f'<rect x="{lx-34:.1f}" y="{ly-12:.1f}" width="68" height="24" rx="6" fill="{c}" opacity="0.12"/>')
        svg.append(f'<text x="{lx:.1f}" y="{ly+1:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="10" font-weight="700" fill="{c}">{name}</text>')
    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="#94A3B8"/>')
    svg.append("</svg>")
    return "\n".join(svg)

def gauge_svg(value):
    if value is None: return ""
    level=get_level(value); color=level["color"]
    circ=math.pi*58; dash=(value/100)*circ
    nx=88+46*math.cos(math.radians(180-(value/100)*180))
    ny=84-46*math.sin(math.radians(180-(value/100)*180))
    return (f'<svg width="176" height="100" viewBox="0 0 176 100" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="gg" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" stop-color="#EF4444"/><stop offset="40%" stop-color="#F59E0B"/>'
            f'<stop offset="70%" stop-color="#3B82F6"/><stop offset="100%" stop-color="#10B981"/>'
            f'</linearGradient></defs>'
            f'<path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="url(#gg)" stroke-width="14" stroke-linecap="round" opacity="0.25"/>'
            f'<path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/>'
            f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{color}" opacity="0.9"/>'
            f'<text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827" font-family="monospace">{value}%</text>'
            f'</svg>')

def metric_gauge_svg(value, color):
    if value is None: return ""
    circ=math.pi*58; dash=(max(0,min(100,value))/100)*circ
    nx=88+46*math.cos(math.radians(180-(value/100)*180))
    ny=84-46*math.sin(math.radians(180-(value/100)*180))
    return (f'<svg width="176" height="100" viewBox="0 0 176 100" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M 18 84 A 70 70 0 0 1 158 84" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/>'
            f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{color}" opacity="0.9"/>'
            f'<text x="88" y="80" text-anchor="middle" font-size="26" font-weight="800" fill="#111827" font-family="monospace">{value}%</text>'
            f'</svg>')

def trend_svg(sessions, w=340, h=90):
    if len(sessions)<2: return ""
    vals=[s["cpi"] for s in sessions if s.get("cpi")]
    if len(vals)<2: return ""
    pad=16; min_v=max(0,min(vals)-10); max_v=min(100,max(vals)+10)
    def x(i): return pad+(i/(len(vals)-1))*(w-pad*2)
    def y(v): return h/2 if max_v==min_v else h-pad-((v-min_v)/(max_v-min_v))*(h-pad*2)
    area=f"{x(0):.1f},{h} "+" ".join(f"{x(i):.1f},{y(v):.1f}" for i,v in enumerate(vals))+f" {x(len(vals)-1):.1f},{h}"
    svg=[f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;overflow:visible">']
    svg.append('<defs><linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2563EB" stop-opacity="0.2"/><stop offset="100%" stop-color="#2563EB" stop-opacity="0.02"/></linearGradient></defs>')
    for vr in [40,65,85]:
        yr=y(vr)
        if pad<=yr<=h-pad:
            svg.append(f'<line x1="{pad}" y1="{yr:.1f}" x2="{w-pad}" y2="{yr:.1f}" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="4 3"/>')
            svg.append(f'<text x="{w-pad+4}" y="{yr+4:.1f}" font-size="9" fill="#94A3B8" font-family="monospace">{vr}%</text>')
    svg.append(f'<polygon points="{area}" fill="url(#tg)"/>')
    svg.append(f'<polyline points="{" ".join(f"{x(i):.1f},{y(v):.1f}" for i,v in enumerate(vals))}" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    for i,v in enumerate(vals):
        c=get_level(v)["color"]; xi=x(i); yi=y(v)
        svg.append(f'<circle cx="{xi:.1f}" cy="{yi:.1f}" r="5" fill="{c}" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{xi:.1f}" y="{yi-10:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="{c}" font-family="monospace">{v}%</text>')
    svg.append("</svg>")
    return "\n".join(svg)

# ════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════
def inject_css(lang):
    d="rtl" if lang=="ar" else "ltr"
    side="right" if lang=="ar" else "left"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'IBM Plex Sans Arabic','IBM Plex Sans','Segoe UI',sans-serif!important;direction:{d};background:#F8FAFC;}}
#MainMenu,footer,header{{visibility:hidden;}}
.cpi-header{{background:linear-gradient(135deg,#0F172A,#1E293B);color:white;padding:18px 22px;border-radius:16px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 20px rgba(15,23,42,0.3);}}
.cpi-header h1{{font-size:17px;font-weight:800;margin:0;line-height:1.3;}}
.cpi-header p{{font-size:11px;color:#94A3B8;margin:4px 0 0;}}
.cpi-formula{{background:linear-gradient(135deg,#1E3A5F,#1E3056);border-radius:10px;padding:8px 14px;font-size:13px;color:#7DD3FC;font-weight:700;font-family:monospace;white-space:nowrap;flex-shrink:0;border:1px solid rgba(125,211,252,0.2);}}
div[data-testid="stRadio"]>div[role="radiogroup"]{{display:flex!important;flex-direction:row!important;gap:6px!important;flex-wrap:nowrap!important;}}
div[data-testid="stRadio"]>div[role="radiogroup"] label{{flex:1!important;border:1.5px solid #E2E8F0!important;border-radius:10px!important;padding:8px 4px!important;text-align:center!important;cursor:pointer!important;font-size:12px!important;font-weight:600!important;background:white!important;transition:all 0.2s!important;}}
div[data-testid="stRadio"]>div[role="radiogroup"] label:has(input:checked){{background:linear-gradient(135deg,#EFF6FF,#E0ECFF)!important;border-color:#2563EB!important;color:#1D4ED8!important;box-shadow:0 2px 8px rgba(37,99,235,0.2)!important;}}
div[data-testid="stRadio"]>div[role="radiogroup"] input[type="radio"]{{display:none!important;}}
.gauge-wrap{{background:linear-gradient(135deg,#F0F7FF,#EBF4FF);border:1px solid #BFDBFE;border-radius:14px;padding:18px 14px;text-align:center;box-shadow:0 2px 10px rgba(37,99,235,0.08);}}
.radar-wrap{{display:flex;justify-content:center;padding:12px;background:white;border:1px solid #E8EDF5;border-radius:14px;}}
.bdi-card{{background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1px solid #DDD6FE;border-radius:14px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}}
.prog-wrap{{height:8px;background:#F1F5F9;border-radius:100px;overflow:hidden;margin-top:6px;}}
.prog-bar{{height:100%;border-radius:100px;transition:width 0.5s ease;}}
.level-0{{background:#FEF2F2;color:#DC2626;border:1.5px solid #FECACA;border-radius:20px;padding:3px 12px;display:inline-block;font-size:12px;font-weight:700;}}
.level-1{{background:#FFF7ED;color:#EA580C;border:1.5px solid #FED7AA;border-radius:20px;padding:3px 12px;display:inline-block;font-size:12px;font-weight:700;}}
.level-2{{background:#FFFBEB;color:#D97706;border:1.5px solid #FDE68A;border-radius:20px;padding:3px 12px;display:inline-block;font-size:12px;font-weight:700;}}
.level-3{{background:#EFF6FF;color:#2563EB;border:1.5px solid #BFDBFE;border-radius:20px;padding:3px 12px;display:inline-block;font-size:12px;font-weight:700;}}
.level-4{{background:#F0FDF4;color:#059669;border:1.5px solid #A7F3D0;border-radius:20px;padding:3px 12px;display:inline-block;font-size:12px;font-weight:700;}}
.level-5{{background:#F5F3FF;color:#7C3AED;border:1.5px solid #DDD6FE;border-radius:20px;padding:3px 12px;display:inline-block;font-size:12px;font-weight:700;}}
div[data-testid="stSlider"]>div>div>div{{direction:ltr!important;}}
div[data-testid="stSlider"]{{padding:0 4px!important;}}
.stButton>button{{border-radius:10px!important;font-weight:600!important;transition:all 0.2s!important;}}
.stButton>button:hover{{transform:translateY(-1px)!important;box-shadow:0 4px 12px rgba(0,0,0,0.15)!important;}}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{border-radius:10px!important;border:1.5px solid #E2E8F0!important;font-family:inherit!important;}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{border-color:#2563EB!important;box-shadow:0 0 0 3px rgba(37,99,235,0.1)!important;}}
.stTabs [data-baseweb="tab-list"]{{gap:4px;background:#F8FAFC;border-radius:12px;padding:4px;border:1px solid #E8EDF5;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px!important;font-weight:600!important;font-size:12px!important;padding:8px 12px!important;}}
.stTabs [aria-selected="true"]{{background:white!important;box-shadow:0 1px 4px rgba(0,0,0,0.1)!important;}}
.msg-user{{background:linear-gradient(135deg,#2563EB,#1D4ED8);color:white;border-radius:12px 12px 4px 12px;padding:12px 16px;font-size:13px;margin-bottom:10px;max-width:90%;margin-{side}:auto;box-shadow:0 2px 10px rgba(37,99,235,0.25);line-height:1.6;}}
.msg-ai{{background:white;color:#111827;border:1px solid #E8EDF5;border-radius:4px 12px 12px 12px;padding:12px 16px;font-size:13px;margin-bottom:10px;max-width:90%;box-shadow:0 2px 8px rgba(0,0,0,0.06);line-height:1.7;}}
.msg-lbl{{font-size:10px;color:#7C3AED;font-weight:700;margin-bottom:6px;}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# HEADER + LANGUAGE
# ════════════════════════════════════════════════════════════════════
lang = st.session_state.lang
inject_css(lang)

col_h, col_l = st.columns([4,1])
with col_h:
    st.markdown(f"""
<div class="cpi-header">
  <div><h1>🧠 {t('app_title')}</h1><p>{t('app_sub')}</p></div>
  <div class="cpi-formula">{t('formula')}</div>
</div>""", unsafe_allow_html=True)
with col_l:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    lc = st.radio("🌐",options=["ar","en","fr"],
        format_func=lambda x:{"ar":"🇩🇿 العربية","en":"🇬🇧 English","fr":"🇫🇷 Français"}[x],
        index=["ar","en","fr"].index(st.session_state.lang),
        key="lang_radio", label_visibility="visible", horizontal=True)
    if lc != st.session_state.lang:
        st.session_state.lang = lc; st.rerun()

lang = st.session_state.lang

# ════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    t("tab_assess"), t("tab_dash"),
    f"{t('tab_hist')} ({len(st.session_state.sessions)})",
    t("tab_fac"), t("tab_charter"), t("tab_admin"),
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — تقييم جلسة
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div style="font-size:13px;color:#6B7280;margin-bottom:14px">{t("assess_intro")}<br><strong>{t("scale_hint")}</strong></div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1: team_name  = st.text_input(t("team_lbl"), placeholder=t("team_ph"), key="inp_team")
    with c2: proj_name  = st.text_input(t("proj_lbl"), placeholder=t("proj_ph"),  key="inp_proj")
    c3,c4 = st.columns(2)
    with c3: sess_num   = st.number_input(t("sess_num"),  min_value=1, value=st.session_state.session_num_counter, key="inp_num")
    with c4: sess_date  = st.date_input(t("sess_date"), value=datetime.date.today(), key="inp_date")

    st.markdown("---")

    # ── اختيار النمط — مفاتيح ثابتة (إصلاح #1) ──────────────────────
    mode = st.radio(t("mode_lbl"), options=["solo","pmp"],
        format_func=lambda v: t("mode_solo") if v=="solo" else t("mode_pmp"),
        horizontal=True, key="assess_mode")
    st.markdown("---")

    # ══════════════════════ SOLO ══════════════════════
    if mode == "solo":
        sl = SL[lang]
        for k in DIM_KEYS:
            d = DIMS[k]; cur = st.session_state.scores.get(k,1)
            c = d["color"]
            name=d[lang]["name"]; desc=d[lang]["desc"]; q=d[lang]["q"]
            st.markdown(f"""
<div style="background:{c}08;border:1.5px solid {c}40;border-radius:14px;padding:14px 18px;margin-bottom:6px;box-shadow:0 2px 8px rgba(0,0,0,0.04)">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
    <span style="background:{c}18;color:{c};font-weight:800;font-size:11px;padding:3px 10px;border-radius:20px">{k}</span>
    <span style="font-size:15px;font-weight:800;color:{c}">{name}</span>
    <span style="margin-{"right" if lang=="ar" else "left"}:auto;font-size:18px;font-weight:800;font-family:monospace;color:{c}">{cur}/4</span>
  </div>
  <div style="font-size:12px;color:#94A3B8;margin-bottom:5px">{desc}</div>
  <div style="font-size:13px;color:#475569;font-style:italic;background:rgba(255,255,255,0.8);border-radius:8px;padding:6px 12px;border-right:3px solid {c}">«{q}»</div>
</div>""", unsafe_allow_html=True)
            nv = st.select_slider(k, options=[1,2,3,4], value=cur,
                format_func=lambda v,s=sl: f"{v} — {s[v]}",
                label_visibility="collapsed", key=f"sl_{k}")
            if nv != cur:
                st.session_state.scores[k]=nv; st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

        cpi_now = calc_cpi(st.session_state.scores)
        if cpi_now is not None:
            level = get_level(cpi_now)
            cg,cr = st.columns(2)
            with cg:
                st.markdown(f"""
<div class="gauge-wrap">
  <div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px">{t('cpi_computed')}</div>
  {gauge_svg(cpi_now)}
  <div style="margin-top:8px"><span class="{level['cls']}">{level['title']}</span></div>
  <div style="font-size:11px;color:#94A3B8;margin-top:8px">{level['desc']}</div>
</div>""", unsafe_allow_html=True)
            with cr:
                st.markdown(f'<div class="radar-wrap">{radar_svg(st.session_state.scores)}</div>', unsafe_allow_html=True)

            if st.button(f"{t('btn_record')} — CPI: {cpi_now}%", type="primary", use_container_width=True):
                tn = st.session_state.get("inp_team","") or "Default"
                pn = st.session_state.get("inp_proj","") or "Session"
                try:
                    cpi_db.init_db()
                    cpi_db.save_cpi_session({
                        "team_name":tn,"project_name":pn,
                        "session_number":int(sess_num),"session_date":str(sess_date),
                        "score_p":float(st.session_state.scores["P"]),
                        "score_l":float(st.session_state.scores["L"]),
                        "score_g":float(st.session_state.scores["G"]),
                        "score_eh":float(st.session_state.scores["EH"]),
                        "cpi_score_final":float(cpi_now),
                        "alignment_index":100.0,"std_deviation":0.0,
                        "participant_count":1,"maturity_level":level["title"],"lang":lang,
                    })
                    _reload_from_db()
                    st.session_state.session_num_counter = int(sess_num)+1
                    st.session_state.scores = {k:1 for k in DIM_KEYS}
                    st.success(t("save_ok")); st.rerun()
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.info(t("complete_all"))

    # ══════════════════════ PMP ══════════════════════
    else:
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#F5F3FF,#EFF6FF);border:1.5px solid #DDD6FE;border-radius:12px;padding:14px 18px;margin-bottom:16px;font-size:13px;color:#4C1D95;line-height:1.7">
  👥 {t('pmp_intro')}
</div>""", unsafe_allow_html=True)

        if not st.session_state.pmp_participants:
            st.session_state.pmp_participants=[{"uid":1,"name":"","specialization":"","role":PMP_ROLES[lang][0],"scores":{"P":2,"L":2,"G":2,"EH":2}}]
            st.session_state.pmp_next_uid=2

        sl=SL[lang]
        for idx,p in enumerate(st.session_state.pmp_participants):
            uid=p["uid"]; disp=p["name"].strip() or f"{t('pmp_participant' if 'pmp_participant' in TR else 'pmp_name')} {idx+1}"
            with st.expander(f"👤 {p['name'] or 'Participant '+str(idx+1)} — {p['role']}", expanded=(idx==len(st.session_state.pmp_participants)-1)):
                ca,cb,cc=st.columns([2,2,1.5])
                with ca: p["name"]           = st.text_input(t("pmp_name"), value=p["name"], key=f"pn_{uid}")
                with cb: p["specialization"] = st.text_input(t("pmp_spec"), value=p["specialization"], key=f"ps_{uid}")
                with cc:
                    roles=PMP_ROLES[lang]; cur_r=p["role"] if p["role"] in roles else roles[0]
                    p["role"]=st.selectbox(t("pmp_role"), roles, index=roles.index(cur_r), key=f"pr_{uid}")
                for k in DIM_KEYS:
                    d=DIMS[k]
                    st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin-top:10px;margin-bottom:2px">
  <span style="background:{d['color']}18;color:{d['color']};font-weight:800;font-size:11px;padding:2px 10px;border-radius:20px">{k}</span>
  <span style="font-size:13px;font-weight:700;color:{d['color']}">{d[lang]['name']}</span>
</div>""", unsafe_allow_html=True)
                    p["scores"][k]=st.select_slider(
                        f"pmp_{uid}_{k}", options=[1,2,3,4], value=p["scores"].get(k,2),
                        format_func=lambda v,s=sl: f"{v} — {s[v]}",
                        label_visibility="collapsed", key=f"psc_{uid}_{k}")
                if len(st.session_state.pmp_participants)>1:
                    if st.button(t("pmp_remove"), key=f"rm_{uid}"):
                        st.session_state.pmp_participants=[x for x in st.session_state.pmp_participants if x["uid"]!=uid]
                        st.session_state.pmp_stats=None; st.rerun()

        ca2,cb2=st.columns([1,2])
        with ca2:
            if st.button(t("pmp_add"), use_container_width=True):
                st.session_state.pmp_participants.append({"uid":st.session_state.pmp_next_uid,"name":"","specialization":"","role":PMP_ROLES[lang][0],"scores":{"P":2,"L":2,"G":2,"EH":2}})
                st.session_state.pmp_next_uid+=1; st.rerun()
        with cb2:
            if st.button(t("pmp_compute"), type="primary", use_container_width=True):
                named=[p for p in st.session_state.pmp_participants if p["name"].strip()]
                if not named: st.warning(t("pmp_warn"))
                else:
                    st.session_state.pmp_stats=cpi_db.calculate_collective_stats([p["scores"] for p in named])
                    st.session_state.pmp_named=named

        if st.session_state.pmp_stats:
            stats=st.session_state.pmp_stats
            coll=stats["collective_cpi"]; cai=stats["alignment_index"]
            std=stats["std_deviation"]; icpis=stats["individual_cpis"]
            gaps=stats["gap_by_dimension"]; named=st.session_state.get("pmp_named",[])
            level,capped=get_level_v7(coll,cai)
            cai_info=cpi_db.cai_interpretation(cai,lang)
            team_avg={k:sum(p["scores"].get(k,2) for p in named)/len(named) for k in DIM_KEYS}

            st.markdown("---")
            st.markdown(f'<div style="font-size:15px;font-weight:800;color:#1E293B;margin-bottom:14px">📊 {t("pmp_results")}</div>', unsafe_allow_html=True)

            cg2,cr2=st.columns(2)
            with cg2:
                st.markdown(f"""
<div class="gauge-wrap">
  <div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px">{t('pmp_collective')}</div>
  {gauge_svg(int(round(coll)))}
  <div style="margin-top:8px"><span class="{level['cls']}">{level['title']}</span></div>
</div>""", unsafe_allow_html=True)
            with cr2:
                st.markdown(f"""
<div class="gauge-wrap">
  <div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px">{t('pmp_cai')}</div>
  {metric_gauge_svg(int(round(cai)), cai_info['color'])}
  <div style="margin-top:8px;font-size:13px;font-weight:800;color:{cai_info['color']};background:{cai_info['color']}15;padding:5px 14px;border-radius:20px;display:inline-block">{cai_info['title']}</div>
  <div style="font-size:11px;color:#94A3B8;margin-top:6px">{cai_info['desc']}</div>
</div>""", unsafe_allow_html=True)

            if capped: st.warning(t("pmp_capped"))

            st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1E293B;margin:16px 0 10px">🗺️ {t("pmp_gap")}</div>', unsafe_allow_html=True)
            for k in DIM_KEYS:
                gap=gaps.get(k,0); pct=min(100,(gap/1.5)*100)
                gc="#10B981" if gap<0.4 else ("#F59E0B" if gap<0.9 else "#DC2626")
                st.markdown(f"""
<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="font-size:13px;font-weight:700;color:{DIMS[k]['color']}">{DIMS[k][lang]['name']} ({k})</span>
    <span style="font-size:13px;font-weight:800;font-family:monospace;color:{gc}">σ = {gap}</span>
  </div>
  <div class="prog-wrap"><div class="prog-bar" style="width:{pct}%;background:{gc}"></div></div>
</div>""", unsafe_allow_html=True)

            st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1E293B;margin:16px 0 10px">👥 {t("pmp_individuals")} ({len(named)})</div>', unsafe_allow_html=True)
            for p,ic in zip(named,icpis):
                ilvl=get_level(ic)
                st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;background:#FAFBFF;border:1px solid #E8EDF5;border-radius:10px;padding:10px 16px;margin-bottom:8px">
  <div>
    <span style="font-weight:700;font-size:13px;color:#1E293B">{p['name']}</span>
    <span style="font-size:11px;color:#94A3B8;margin-{"right" if lang=="ar" else "left"}:8px">{p['specialization']} · {p['role']}</span>
  </div>
  <span style="font-weight:800;font-family:monospace;font-size:18px;color:{ilvl['color']}">{ic}%</span>
</div>""", unsafe_allow_html=True)

            prompt=cpi_db.discussion_prompt(cai,lang)
            st.markdown(f"""
<div style="background:#FFF7ED;border:1.5px solid #FCD34D;border-radius:12px;padding:16px;margin-top:8px;text-align:center">
  <div style="font-size:11px;font-weight:700;color:#92400E;margin-bottom:8px">💬 {t('pmp_discuss')}</div>
  <div style="font-size:14px;font-weight:700;color:#78350F;line-height:1.7">❝ {prompt} ❞</div>
</div>""", unsafe_allow_html=True)

            if st.button(t("pmp_save"), type="primary", use_container_width=True):
                tn=st.session_state.get("inp_team","") or "Default"
                pn=st.session_state.get("inp_proj","") or "Session"
                pp=[{"name":p["name"],"specialization":p["specialization"],"role":p["role"],"scores":p["scores"],"individual_cpi":ic} for p,ic in zip(named,icpis)]
                try:
                    cpi_db.init_db()
                    cpi_db.save_cpi_session({
                        "team_name":tn,"project_name":pn,
                        "session_number":int(sess_num),"session_date":str(sess_date),
                        "score_p":float(team_avg["P"]),"score_l":float(team_avg["L"]),
                        "score_g":float(team_avg["G"]),"score_eh":float(team_avg["EH"]),
                        "cpi_score_final":float(coll),"alignment_index":float(cai),
                        "std_deviation":float(std),"participant_count":len(named),
                        "maturity_level":level["title"],"lang":lang,
                    }, participants=pp)
                    _reload_from_db()
                    st.session_state.pmp_participants=[{"uid":1,"name":"","specialization":"","role":PMP_ROLES[lang][0],"scores":{"P":2,"L":2,"G":2,"EH":2}}]
                    st.session_state.pmp_next_uid=2; st.session_state.pmp_stats=None
                    st.session_state.session_num_counter=int(sess_num)+1
                    st.success(t("save_ok")); st.rerun()
                except Exception as e:
                    st.error(f"⚠️ {e}")

# ════════════════════════════════════════════════════════════════════
# TAB 2 — لوحة القيادة
# ════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.sessions:
        st.markdown(f'<div style="text-align:center;color:#9CA3AF;padding:60px 20px"><div style="font-size:48px;margin-bottom:12px">📊</div><div>{t("no_data")}</div></div>', unsafe_allow_html=True)
    else:
        last=st.session_state.sessions[-1]; level=get_level(last["cpi"]); bdi=calc_bdi(st.session_state.sessions)
        cg,cr=st.columns(2)
        with cg:
            st.markdown(f"""
<div class="gauge-wrap">
  <div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px">{t('last_cpi')}</div>
  {gauge_svg(last['cpi'])}
  <div style="margin-top:8px"><span class="{level['cls']}">{level['title']}</span></div>
  <div style="font-size:11px;color:#94A3B8;margin-top:6px">{last['label']} · {last['date']}</div>
  <div style="font-size:12px;color:{level['color']};margin-top:8px;line-height:1.5">{level['desc']}</div>
</div>""", unsafe_allow_html=True)
        with cr:
            st.markdown(f'<div class="radar-wrap">{radar_svg(last["scores"])}</div>', unsafe_allow_html=True)

        cai_val=last.get("alignment_index")
        if cai_val is not None:
            cai_info=cpi_db.cai_interpretation(cai_val,lang)
            st.markdown(f"""
<div class="gauge-wrap" style="margin-top:14px">
  <div style="font-size:11px;font-weight:600;color:#64748B;margin-bottom:6px">{t('pmp_cai')}</div>
  {metric_gauge_svg(int(round(cai_val)), cai_info['color'])}
  <div style="margin-top:8px;font-size:13px;font-weight:800;color:{cai_info['color']};background:{cai_info['color']}15;padding:5px 14px;border-radius:20px;display:inline-block">{cai_info['title']}</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1E293B;margin:18px 0 10px">{t("dim_detail")}</div>', unsafe_allow_html=True)
        cols=st.columns(4)
        for i,k in enumerate(DIM_KEYS):
            with cols[i]:
                v=last["scores"].get(k,0); c=DIMS[k]["color"]; name=DIMS[k][lang]["name"]
                pct=(v/4)*100
                st.markdown(f"""
<div style="background:{c}08;border:1.5px solid {c}30;border-radius:12px;padding:14px;text-align:center">
  <div style="font-size:11px;font-weight:700;color:{c};margin-bottom:6px">{name}</div>
  <div style="font-size:26px;font-weight:800;font-family:monospace;color:{c}">{v}/4</div>
  <div class="prog-wrap" style="margin-top:8px"><div class="prog-bar" style="width:{pct}%;background:{c}"></div></div>
</div>""", unsafe_allow_html=True)

        if bdi is not None:
            bc="#10B981" if bdi>=75 else ("#3B82F6" if bdi>=50 else "#EF4444")
            st.markdown(f"""
<div class="bdi-card" style="margin-top:14px">
  <div>
    <div style="font-size:13px;font-weight:700;color:#4C1D95">{t('bdi_title')}</div>
    <div style="font-size:11px;color:#7C3AED;margin-top:3px">{t('bdi_sub')}</div>
  </div>
  <div style="font-size:34px;font-weight:800;font-family:monospace;color:{bc}">{bdi}%</div>
</div>""", unsafe_allow_html=True)

        if len(st.session_state.sessions)>=2:
            st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1E293B;margin:18px 0 10px">{t("trend_title")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:white;border:1px solid #E8EDF5;border-radius:14px;padding:16px">{trend_svg(st.session_state.sessions)}<div style="font-size:11px;color:#9CA3AF;margin-top:8px">{len(st.session_state.sessions)} {t("sessions_count")}</div></div>', unsafe_allow_html=True)

        weak=[k for k in DIM_KEYS if last["scores"].get(k,0)<=2]
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1E293B;margin:18px 0 10px">{t("recs_title")}</div>', unsafe_allow_html=True)
        if not weak:
            st.success(t("recs_good"))
        else:
            for k in weak:
                name,color,rec=RECS[k][lang]
                st.markdown(f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:10px;padding:12px 16px;margin-bottom:10px"><div style="font-weight:700;color:{color};margin-bottom:4px">⚠ {name}</div><div style="font-size:13px;color:#92400E">{rec}</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — السجل
# ════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.sessions:
        st.markdown(f'<div style="text-align:center;color:#9CA3AF;padding:60px 20px"><div style="font-size:48px;margin-bottom:12px">🗂️</div><div>{t("no_sessions")}</div></div>', unsafe_allow_html=True)
    else:
        ch,cd=st.columns([3,1])
        with ch: st.markdown(f'<span style="font-size:13px;color:#64748B">{len(st.session_state.sessions)} {t("sessions_count")}</span>', unsafe_allow_html=True)
        with cd:
            if st.button(t("delete_all"), type="secondary", use_container_width=True):
                try:
                    for s in st.session_state.sessions:
                        if s.get("id"): cpi_db.delete_session(s["id"])
                except Exception: pass
                st.session_state.sessions=[]; st.rerun()

        for s in reversed(st.session_state.sessions):
            lvl=get_level(s["cpi"])
            # إصلاح #3 — CAI آمن
            cai_raw=s.get("alignment_index")
            cai_str=f"{cai_raw:.1f}%" if cai_raw is not None else t("not_defined")
            with st.expander(f"📌 {s['label']} — {s['date']} · CPI: {s['cpi']}%"):
                ca,cb=st.columns(2)
                with ca:
                    st.markdown(f"**{t('hist_team')}** {s.get('team',t('not_defined'))}")
                    st.markdown(f"**{t('hist_level')}** {lvl['title']}")
                    st.markdown(f"**{t('hist_cai')}** {cai_str}")
                with cb:
                    for k in DIM_KEYS:
                        c=DIMS[k]["color"]; name=DIMS[k][lang]["name"]; v=s["scores"].get(k,0)
                        st.markdown(f'<span style="background:{c}18;color:{c};font-weight:700;font-size:11px;padding:2px 10px;border-radius:20px;display:inline-block;margin:2px">{name}: {v}/4</span>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 4 — الميسر المعرفي
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0F172A,#1E293B);color:white;border-radius:16px;padding:20px;margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="font-size:28px">🧠</div>
    <div>
      <div style="font-weight:800;font-size:17px">{t('tab_fac')}</div>
      <div style="font-size:11px;color:#94A3B8">Powered by Claude AI · claude-sonnet-4-6</div>
    </div>
  </div>
  <div style="font-size:13px;color:#CBD5E1;background:rgba(255,255,255,0.05);border-radius:10px;padding:10px;margin-top:12px">{t('fac_sub')}</div>
</div>""", unsafe_allow_html=True)

    api_key,from_secrets=get_api_key()
    if not from_secrets:
        api_in=st.text_input(t("fac_key"), value=st.session_state.api_key, type="password", placeholder="sk-ant-...")
        if api_in != st.session_state.api_key: st.session_state.api_key=api_in
        api_key=st.session_state.api_key
    else:
        st.success("🔑 API Key loaded from secrets.")

    for msg in st.session_state.fac_msgs:
        if msg["role"]=="user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-ai"><div class="msg-lbl">🧠 {t("tab_fac")}</div>{msg["content"]}</div>', unsafe_allow_html=True)

    user_in=st.text_area("input", placeholder=t("fac_ph"), height=120, label_visibility="collapsed", key="fac_input")
    cs,cc=st.columns([3,1])
    with cs:
        if st.button(t("fac_send"), type="primary", use_container_width=True):
            if not api_key: st.error(t("fac_err_key"))
            elif not user_in.strip(): st.warning(t("fac_err_msg"))
            else:
                st.session_state.fac_msgs.append({"role":"user","content":user_in})
                sys_p={"ar":"أنت ميسر معرفي محايد متخصص في نظرية CPI (مؤشر التلاقح المعرفي) لـ د. الحبيب خروبي. الصيغة: CI = NK × EH. الأبعاد الأربعة: الممارسة (P)، اللغة المشتركة (L)، التوجيه (G)، التواضع المعرفي (EH). حلل النص وقدم تقييماً ورؤى وتوصيات. الرد بالعربية.",
                        "en":"You are a neutral cognitive facilitator specialising in CPI theory (Cross-Pollination Index) by Dr. Elhabib Kherroubi. Formula: CI = NK × EH. Four dimensions: Practice (P), Shared Language (L), Guidance (G), Epistemic Humility (EH). Analyse the input and provide assessment, insights and recommendations. Reply in English.",
                        "fr":"Vous êtes un facilitateur cognitif neutre spécialisé dans la théorie CPI du Dr. Elhabib Kherroubi. Formule : IC = SC × HE. Quatre dimensions : Pratique, Langage commun, Orientation, Humilité épistémique. Analysez et fournissez des recommandations. Répondre en français."}[lang]
                with st.spinner(t("fac_thinking")):
                    msgs=[{"role":m["role"],"content":m["content"]} for m in st.session_state.fac_msgs]
                    reply=call_claude(msgs, sys_p, api_key)
                st.session_state.fac_msgs.append({"role":"assistant","content":reply}); st.rerun()
    with cc:
        if st.button(t("fac_clear"), use_container_width=True):
            st.session_state.fac_msgs=[]; st.rerun()

# ════════════════════════════════════════════════════════════════════
# TAB 5 — الميثاق
# ════════════════════════════════════════════════════════════════════
with tab5:
    d="rtl" if lang=="ar" else "ltr"
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0F172A,#1E293B);color:white;border-radius:16px;padding:24px;margin-bottom:20px;direction:{d}">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="font-size:28px">📜</div>
    <div>
      <div style="font-size:18px;font-weight:800">{t('charter_title')}</div>
      <div style="font-size:11px;color:#94A3B8">{t('charter_ver')}</div>
    </div>
  </div>
  <div style="font-size:13px;color:#CBD5E1;background:rgba(255,255,255,0.05);border-radius:10px;padding:12px;margin-top:12px;line-height:1.8">{t('charter_body')}</div>
</div>
<div style="background:linear-gradient(135deg,#FFF7ED,#FFFBEB);border:1.5px solid #FCD34D;border-radius:14px;padding:18px;margin-bottom:22px;text-align:center">
  <div style="font-size:11px;font-weight:700;color:#92400E;margin-bottom:8px;letter-spacing:1px">{t('core_axiom')}</div>
  <div style="font-size:15px;font-weight:700;color:#78350F;line-height:1.7">❝ {t('charter_axiom')} ❞</div>
  <div style="font-size:12px;font-family:monospace;color:#B45309;margin-top:10px">CI = NK × EH</div>
</div>""", unsafe_allow_html=True)

    signer=st.text_input(t("charter_name_lbl"), placeholder=t("charter_name_ph"), key="charter_signer")
    if st.button(t("charter_sign"), type="primary"):
        if signer.strip():
            st.session_state.signatories.append({"name":signer.strip(),"time":datetime.datetime.now().strftime("%H:%M")})
            st.success(t("charter_ok")); st.rerun()
    if st.session_state.signatories:
        st.markdown(f"**{t('charter_signers')} ({len(st.session_state.signatories)}):**")
        for sig in st.session_state.signatories:
            st.markdown(f"✅ {sig['name']} — {sig['time']}")

# ════════════════════════════════════════════════════════════════════
# TAB 6 — الإدارة
# ════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(f'<div style="font-size:18px;font-weight:800;color:#1E293B;margin-bottom:16px">📊 {t("stats_title")}</div>', unsafe_allow_html=True)
    try:
        stats=cpi_db.get_statistics(); teams=cpi_db.get_all_teams()
    except Exception as e:
        stats={"total_sessions":0,"avg_cpi":0,"total_teams":0}; teams=[]
        st.warning(f"⚠️ DB: {e}")

    avg_val=stats.get("avg_cpi") or 0
    if avg_val is None: avg_val=0

    ca,cb,cc=st.columns(3)
    for col,lbl,val in [(ca,t("total_sessions"),stats.get("total_sessions",0)),(cb,t("avg_cpi"),f"{avg_val}%"),(cc,t("total_teams"),stats.get("total_teams",0))]:
        with col:
            st.markdown(f'<div style="background:white;border:1px solid #E8EDF5;border-radius:12px;padding:16px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.04)"><div style="font-size:22px;font-weight:800;color:#1E293B">{val}</div><div style="font-size:11px;color:#6B7280;margin-top:4px">{lbl}</div></div>', unsafe_allow_html=True)

    if teams:
        st.markdown(f"---\n### 🏢 {t('teams_list')}")
        for team in teams:
            st.markdown(f"— {team}")

    st.markdown("---")
    if st.button(t("export_csv"), type="secondary", use_container_width=True):
        try:
            csv_data=cpi_db.export_all_csv()
            if csv_data:
                st.download_button(t("dl_csv"), data=csv_data,
                    file_name=f"CPI_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")
        except Exception as e:
            st.error(f"⚠️ {e}")

# ════════════════════════════════════════════════════════════════════
# FOOTER — نص ثابت غير قابل للترجمة التلقائية (إصلاح #6)
# ════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;margin-top:48px;padding:20px;background:linear-gradient(135deg,#0F172A,#1E293B);border-radius:16px">
  <div style="font-size:13px;font-weight:700;color:#E2E8F0">🧠 {t('footer_text')}</div>
  <div style="font-size:11px;color:#64748B;font-family:monospace;margin-top:4px">
    CPI Framework v7.3.4 · CI = NK × EH · {datetime.datetime.now().year}
  </div>
</div>
""", unsafe_allow_html=True)
