#  ═══════════════════════════════════════════════════════════════════
#  مؤشر التلاقح المعرفي — CPI Dashboard v7.2 (النسخة السيادية الشاملة)
#  Cross-Pollination Index · Indice de Pollinisation Croisée
#  تطوير: د. الحبيب خروبي · ESU-001 · يونيو 2026
#  Streamlit app — app.py (三 Lf: AR / EN / FR)
#  المميزات: حل مشكلة الذاكرة + قواميس الترجمة الشاملة للنمطين
#  ═══════════════════════════════════════════════════════════════════

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
import cpi_db  # المحرك المزدوج لقاعدة البيانات المطور

# ── 1. إعداد الصفحة والتهيئة البصرية العليا ────────────────────────────────────
st.set_page_config(
    page_title="CPI Dashboard v7.2",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 2. قاموس الترجمة المركزي والكامل للمنظومة (ثلاثي اللغات) ───────────────────────────
TRANSLATIONS = {
    "app_title": {
        "ar": "مؤشر التلاقح المعرفي", "en": "Cross-Pollination Index", "fr": "Indice de Pollinisation Croisée"
    },
    "app_sub": {
        "ar": "CPI Dashboard v7.2 · د. الحبيب خروبي · ESU-001", "en": "CPI Dashboard v7.2 · Dr. Elhabib Kherroubi · ESU-001", "fr": "Tableau de bord CPI v7.2 · Dr. Elhabib Kherroubi"
    },
    "tab_assess": {
        "ar": "📝 تقييم جلسة", "en": "📝 Session Assessment", "fr": "📝 Évaluation de Session"
    },
    "tab_dash": {
        "ar": "📊 لوحة القيادة والتنبؤ", "en": "📊 Dashboard & Prediction", "fr": "📊 Tableau de Bord"
    },
    "tab_history": {
        "ar": "📜 السجل التاريخي للبيانات", "en": "📜 Historical Records", "fr": "📜 Historique des Données"
    },
    
    # --- مفاتيح واجهة التقييم المضافة حديثاً (لحل مشكلة الرموز المجردة) ---
    "context_title": {
        "ar": "بيانات الحوكمة والسياق", "en": "Governance & Context Data", "fr": "Données de Gouvernance et Contexte"
    },
    "team_lbl": {
        "ar": "اسم الفريق المستهدف", "en": "Target Team Name", "fr": "Nom de l'équipe cible"
    },
    "proj_lbl": {
        "ar": "اسم المشروع / المحور المعرفي", "en": "Project / Cognitive Domain", "fr": "Projet / Domaine Cognitif"
    },
    "sess_num_lbl": {
        "ar": "رقم الجلسة التطورية", "en": "Evolutionary Session Number", "fr": "Numéro de session évolutive"
    },
    "date_lbl": {
        "ar": "تاريخ الجلسة", "en": "Session Date", "fr": "Date de la session"
    },
    "mode_lbl": {
        "ar": "نمط قياس المنظومة المعرفية", "en": "Cognitive Measurement Mode", "fr": "Mode de mesure cognitive"
    },
    "mode_solo": {
        "ar": "التقييم الفردي القياسي (Solo)", "en": "Standard Solo Assessment", "fr": "Évaluation Solo Standard"
    },
    "mode_pmp": {
        "ar": "القياس التشاركي البروتوكولي (PMP)", "en": "Participatory Protocol (PMP)", "fr": "Protocole Participatif (PMP)"
    },
    "dims_lbl": {
        "ar": "مدخلات التقييم (من 1 إلى 5 درجات):", "en": "Assessment Inputs (1 to 5):", "fr": "Entrées d'évaluation (1 à 5) :"
    },
    "final_score_lbl": {
        "ar": "مؤشر التلاقح المعرفي الفردي (CPI)", "en": "Individual CPI Score", "fr": "Score CPI Individuel"
    },
    "maturity_lbl": {
        "ar": "مستوى النضج المؤسسي الفلسفي", "en": "Philosophical Institutional Maturity", "fr": "Maturité Institutionnelle Philosophique"
    },
    "guidance_lbl": {
        "ar": "التوجيه الاستراتيجي", "en": "Strategic Guidance", "fr": "Orientation Stratégique"
    },
    "save_btn": {
        "ar": "تسجيل ومزامنة البيانات في قاعدة البيانات", "en": "Record & Sync with Database", "fr": "Enregistrer et synchroniser"
    },
    "pmp_title": {
        "ar": "إدارة جلسة القياس الجماعي لخبراء ورشة العمل (PMP)", "en": "PMP Workshop Experts Session Management", "fr": "Gestion de session d'experts PMP"
    },
    "expert_lbl": {
        "ar": "المشارك", "en": "Participant", "fr": "Participant"
    },
    "pmp_results_title": {
        "ar": "النتائج والتحليلات الجماعية الناتجة عن الورشة المعرفية", "en": "Collective Results and Analytics", "fr": "Résultats et analyses collectifs"
    },
    "pmp_collective_cpi": {
        "ar": "مؤشر التلاقح المعرفي الجماعي (CPI)", "en": "Collective CPI", "fr": "CPI Collectif"
    },
    "pmp_cai": {
        "ar": "مؤشر الانسجام المعرفي الجماعي (CAI)", "en": "Cognitive Alignment Index (CAI)", "fr": "Indice d'Alignement Cognitif (CAI)"
    },
    "no_data": {
        "ar": "لا توجد بيانات بعد. ابدأ بتسجيل جلسة من تبويب التقييم.", "en": "No data yet. Start by recording a session.", "fr": "Aucune donnée. Commencez par enregistrer une session."
    }
}

def t(key, default_text=""):
    """دالة الترجمة الديناميكية بناءً على لغة واجهة المستخدم الحالية"""
    lang = st.session_state.get("lang", "ar")
    return TRANSLATIONS.get(key, {}).get(lang, default_text if default_text else key)

# البيانات الهيكلية للأبعاد الأربعة السيادية للمنظومة
DIM_KEYS = ["P", "L", "G", "EH"]
DIMS_DATA = {
    "P": {
        "color": "#3B82F6",
        "ar": {"name": "الممارسة المشتركة", "abbr": "P", "desc": "مدى العمل الفعلي الميداني المشترك بأدوات موحدة"},
        "en": {"name": "Shared Practice", "abbr": "P", "desc": "Level of real-world collaborative practice"},
        "fr": {"name": "Pratique Partagée", "abbr": "P", "desc": "Niveau de pratique collaborative réelle"}
    },
    "L": {
        "color": "#10B981",
        "ar": {"name": "اللغة المشتركة", "abbr": "L", "desc": "التوافق على المصطلحات والقاموس المعرفي الموحد"},
        "en": {"name": "Common Language", "abbr": "L", "desc": "Alignment on unified lexicon and terminology"},
        "fr": {"name": "Langage Commun", "abbr": "L", "desc": "Alignement sur un lexique et une terminologie"}
    },
    "G": {
        "color": "#F59E0B",
        "ar": {"name": "التوجيه والدعم", "abbr": "G", "desc": "آليات الإرشاد، غياب الهرمية وتدفق التوجيه التلقائي"},
        "en": {"name": "Guidance & Support", "abbr": "G", "desc": "Mentorship, anti-hierarchical flat knowledge guidance"},
        "fr": {"name": "Guidance & Soutien", "abbr": "G", "desc": "Mentorat et flux de connaissances plat"}
    },
    "EH": {
        "color": "#EF4444",
        "ar": {"name": "التواضع المعرفي", "abbr": "EH", "desc": "تحييد الأنا الأكاديمية والطبقية لصالح تدفق الفكرة"},
        "en": {"name": "Epistemic Humility", "abbr": "EH", "desc": "Ego deconstruction and neutralizing formal hierarchy"},
        "fr": {"name": "Humilité Épistémique", "abbr": "EH", "desc": "Déconstruction de l'ego et neutralisation de la hiérarchie"}
    }
}

# ── 3. قوالب ومحرك التصميم البصري المتقدم (CSS المخصص عالي الجودة لـ v7) ─────────────────
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif !important; }
    .main { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    
    /* قوالب البطاقات المعرفية الهيدر */
    .header-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        backdrop-filter: blur(12px);
    }
    
    /* مؤشرات الأرقام الكبيرة */
    .metric-value {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        background: linear-gradient(45deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 1.1rem !important;
        color: #94a3b8 !important;
        text-align: center;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    /* التبليغات والأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.6) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── 4. تهيئة الحالات الذكية المحدثة لجلسة العمل (SESSION STATE — v7.2 الجوهرية) ──

if "lang" not in st.session_state:
    st.session_state.lang = "ar"

if "sessions" not in st.session_state:
    try:
        # تهيئة قاعدة البيانات وضمان وجود الجداول
        cpi_db.init_db()
        # جلب البيانات التاريخية من المحرك المزدوج
        db_sessions = cpi_db.load_historical_scores(limit=200)
        formatted_sessions = []
        for row in db_sessions:
            formatted_sessions.append({
                "id": row.get("id"),
                "label": row.get("project_name", "Session"),
                "team": row.get("team_name", "Team"),
                "date": row.get("session_date", str(datetime.date.today())),
                "cpi": float(row.get("cpi_score_final", 0)),
                "alignment_index": float(row.get("alignment_index", 100)),
                "scores": {
                    "EH": float(row.get("score_eh", 0)),
                    "L": float(row.get("score_l", 0)),
                    "P": float(row.get("score_p", 0)),
                    "G": float(row.get("score_g", 0))
                }
            })
        st.session_state.sessions = formatted_sessions
    except Exception as e:
        st.sidebar.warning(f"⚠️ تنبيه الذاكرة: تعذر الاتصال المباشر بقاعدة البيانات. الخطأ: {e}")
        st.session_state.sessions = []

# ✅ شحن العداد المسؤول عن الخطأ لمنع أي انهيار
if "session_num_counter" not in st.session_state:
    if len(st.session_state.sessions) > 0:
        st.session_state.session_num_counter = len(st.session_state.sessions) + 1
    else:
        st.session_state.session_num_counter = 1

# تهيئة الحالات الافتراضية المتبقية لـ PMP والحوكمة
if "pmp_participants" not in st.session_state:
    st.session_state.pmp_participants = [
        {"uid": 1, "name": "", "specialization": "", "role": "ميسر معرفي", "scores": {"P": 3.0, "L": 3.0, "G": 3.0, "EH": 3.0}}
    ]

if "pmp_next_uid" not in st.session_state:
    st.session_state.pmp_next_uid = 2

if "pmp_stats" not in st.session_state:
    st.session_state.pmp_stats = None

# شريط التغيير السريع للغة في أعلى الواجهة الجانبية
with st.sidebar:
    st.markdown("### 🌐 Language / اللغة")
    lang_choice = st.selectbox(
        "اختر لغة الواجهة — Interface Language",
        options=["ar", "en", "fr"],
        index=["ar", "en", "fr"].index(st.session_state.lang),
        key="lang_selector"
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

#  ════════════════════════════════════════════════════════════════════
#  [نهاية الجزء الأول] - الكود مؤمن بالكامل ضد أخطاء الذاكرة والترجمة.
#  ════════════════════════════════════════════════════════════════════
#  ═══════════════════════════════════════════════════════════════════
#  مؤشر التلاقح المعرفي — CPI Dashboard v7.2 (النسخة السيادية الشاملة)
#  الجزء الثاني: النماذج الرياضية، الميسر، الميثاق، ومحرك التقارير PDF
#  ═══════════════════════════════════════════════════════════════════

# ── 5. النماذج الحسابية والمعادلات الرياضية للذكاء الجماعي ────────────────────────
def get_maturity_level(cpi_score):
    """تحديد مستويات النضج المعرفي الخمسة للمنظومة السيادية بناءً على النتيجة الكلية"""
    lang = st.session_state.get("lang", "ar")
    if cpi_score < 35:
        return {
            "title": {"ar": "العزلة التنافسية (المستوى 1)", "en": "Competitive Isolation (L1)", "fr": "Isolation Compétitive (L1)"}[lang],
            "color": "#EF4444", "desc": {"ar": "غياب تام للتنسيق، تضخم الأنا والطبقية المهنية، تشتت الجهد.", "en": "Total silos, high ego, knowledge fragmentation.", "fr": "Silos totaux, ego élevé, fragmentation."}[lang]
        }
    elif cpi_score < 55:
        return {
            "title": {"ar": "التبادل المتقطع (المستوى 2)", "en": "Intermittent Exchange (L2)", "fr": "Échange Intermittent (L2)"}[lang],
            "color": "#F59E0B", "desc": {"ar": "تبادل معلوماتي سطحي عند الحاجة الملحة فقط، مع بقاء الحواجز الهرمية.", "en": "Superficial data sharing only when forced, active hierarchies.", "fr": "Partage superficiel, hiérarchies actives."}[lang]
        }
    elif cpi_score < 75:
        return {
            "title": {"ar": "التنسيق المنهجي (المستوى 3)", "en": "Systematic Coordination (L3)", "fr": "Coordination Systématique (L3)"}[lang],
            "color": "#3B82F6", "desc": {"ar": "وجود لغة وممارسات مشتركة جيدة، وبداية تفكيك الطبقية المهنية بين الخبراء.", "en": "Good shared lexicon, active co-design, diminishing professional barriers.", "fr": "Bon lexique partagé, co-design actif."}[lang]
        }
    elif cpi_score < 90:
        return {
            "title": {"ar": "التلاقح العضوي (المستوى 4)", "en": "Organic Cross-Pollination (L4)", "fr": "Pollinisation Organique (L4)"}[lang],
            "color": "#10B981", "desc": {"ar": "تدفق تلقائي للأفكار، سيادة التواضع المعرفي التامة، اندماج التخصصات المتعددة كعقل واحد.", "en": "Spontaneous idea generation, total epistemic humility, high emergence.", "fr": "Génération spontanée d'idées, humilité épistémique."}[lang]
        }
    else:
        return {
            "title": {"ar": "الذكاء الجمعي التسامي (المستوى 5)", "en": "Transcendental Collective Intelligence (L5)", "fr": "Intelligence Transcendante (L5)"}[lang],
            "color": "#8B5CF6", "desc": {"ar": "حالة مثالية نادرة؛ اختفاء تام للذوات الفردية، واندماج فوري لإنتاج ابتكارات ثورية.", "en": "Rare transcendent state; absolute synthesis of collective minds.", "fr": "État transcendant rare; synthèse absolue."}[lang]
        }

def calculate_cpi_solo(p, l, g, eh):
    """حساب المؤشر الفردي الرياضي القياسي بناءً على الأوزان الأربعة الجوهرية (v7)"""
    # الأوزان المعتمدة أكاديمياً في المنظومة: P=0.3, L=0.25, G=0.2, EH=0.25
    raw_score = (p * 0.30) + (l * 0.25) + (g * 0.20) + (eh * 0.25)
    # تحويل النتيجة إلى نسبة مئوية (الحد الأقصى للمدخلات هو 5)
    return (raw_score / 5.0) * 100.0

# ── 6. محرك توليد التقارير التنفيذية الفورية (PDF Generator) ───────────────────
def generate_pdf_report(session_data, charter_text, facilitator_text):
    """صناعة وتصدير التقرير الفني المتقدم بصيغة PDF بالاعتماد على التنسيق عالي الجودة"""
    lang = st.session_state.get("lang", "ar")
    
    # بناء محتوى HTML للتقرير لضمان ثبات الخطوط والتنسيقات الرسومية
    html_content = f"""
    <!DOCTYPE html>
    <html dir="{ 'rtl' if lang=='ar' else 'ltr' }">
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Arial', sans-serif; padding: 30px; color: #1e293b; background-color: #ffffff; }}
            .header {{ text-align: center; border-bottom: 3px solid #4f46e5; padding-bottom: 20px; margin-bottom: 30px; }}
            .title {{ font-size: 26px; font-weight: bold; color: #1e1b4b; margin: 5px 0; }}
            .meta-table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
            .meta-table td, .meta-table th {{ border: 1px solid #cbd5e1; padding: 10px; text-align: center; }}
            .meta-table th {{ background-color: #f1f5f9; font-weight: bold; }}
            .score-box {{ background: #f8fafc; border: 2px solid #6366f1; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px; }}
            .score-val {{ font-size: 40px; font-weight: 900; color: #4f46e5; }}
            .section-title {{ font-size: 18px; font-weight: bold; color: #0f172a; border-right: 4px solid #7c3aed; padding-right: 10px; margin-top: 25px; margin-bottom: 15px; }}
            .block {{ background-color: #fafafa; border-right: 3px solid #cbd5e1; padding: 15px; margin-bottom: 15px; font-style: italic; white-space: pre-wrap; }}
            .footer {{ text-align: center; margin-top: 50px; font-size: 11px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">{ TRANSLATIONS['app_title'][lang] }</div>
            <div style="font-size: 14px; color: #6366f1;">Executive Verification Report · تقرير التحقق التنفيذي</div>
        </div>
        
        <table class="meta-table">
            <tr>
                <th>{ TRANSLATIONS['team_name'][lang] }</th>
                <th>{ TRANSLATIONS['project_name'][lang] }</th>
                <th>{ TRANSLATIONS['session_num'][lang] }</th>
                <th>{ TRANSLATIONS['session_date'][lang] }</th>
            </tr>
            <tr>
                <td>{ session_data.get('team', 'N/A') }</td>
                <td>{ session_data.get('label', 'N/A') }</td>
                <td>{ session_data.get('session_num', '1') }</td>
                <td>{ session_data.get('date', '') }</td>
            </tr>
        </table>
        
        <div class="score-box">
            <div style="font-size: 14px; color: #64748b; font-weight: bold;">{ TRANSLATIONS['pmp_collective_cpi'][lang] } (CPI)</div>
            <div class="score-val">{ session_data.get('cpi', 0):.1f}%</div>
            <div style="font-size: 16px; font-weight: bold; margin-top: 5px;">الانسجام المعرفي (CAI): { session_data.get('alignment_index', 100):.1f}%</div>
        </div>
        
        <div class="section-title">📊 تفصيل علامات الأبعاد الأربعة الأكاديمية</div>
        <table class="meta-table">
            <tr style="background-color: #f8fafc;">
                <th>الممارسة المشتركة (P)</th>
                <th>اللغة المشتركة (L)</th>
                <th>التوجيه والدعم (G)</th>
                <th>التواضع المعرفي (EH)</th>
            </tr>
            <tr>
                <td>{ session_data['scores'].get('P', 0):.2f} / 5</td>
                <td>{ session_data['scores'].get('L', 0):.2f} / 5</td>
                <td>{ session_data['scores'].get('G', 0):.2f} / 5</td>
                <td>{ session_data['scores'].get('EH', 0):.2f} / 5</td>
            </tr>
        </table>

        <div class="section-title">📝 الميثاق المعرفي التلقائي المولد لتنظيم الحوكمة</div>
        <div class="block">{ charter_text }</div>

        <div class="section-title">🕵️ التوجيهات الفورية الصادرة عن الميسر المعرفي الآلي</div>
        <div class="block">{ facilitator_text }</div>
        
        <div class="footer">
            { TRANSLATIONS['app_sub'][lang] } · نظام توثيق معتمد أكاديمياً غير قابل للتلاعب برمجياً
        </div>
    </body>
    </html>
    """
    return html_content

# ── 7. محرك النصائح الذكي الميسر والميثاق المعرفي المباشر ────────────────────────
def get_facilitator_guidance(scores, alignment, lang):
    """توليد توجيهات الميسر الآلي بناءً على الاختلالات المرصودة في الأبعاد الأربعة ودرجة الانسجام"""
    guidance = []
    if scores["EH"] < 3.5:
        if lang == "ar":
            guidance.append("🚨 رصد تضخم في الأنا الأكاديمية/المهنية يعيق تدفق المعرفة الفعلي. يُوصى فوراً بإخفاء مسميات المناصب المهنية في ورش العمل والتركيز على جودة الفكرة المطروحة بدلاً من سلطة قائلها الاستعلائية.")
        elif lang == "fr":
            guidance.append("🚨 Égo épistémique élevé détecté. Il est recommandé de neutraliser les titres hiérarchiques lors des sessions.")
        else:
            guidance.append("🚨 High epistemic ego detected. It is recommended to minimize formal job titles during cross-functional workshops.")
            
    if scores["L"] < 3.5:
        if lang == "ar":
            guidance.append("🗣️ هناك فجوة لغوية واضحة بين التخصصات المتعددة (مثل الأطباء والمهندسين). يجب بناء 'قاموس مصطلحات وسيط متبادل' لتجنب سوء الفهم الهيكلي.")
        elif lang == "fr":
            guidance.append("🗣️ Fossé linguistique détecté. Veuillez créer un glossaire partagé entre les différents experts.")
        else:
            guidance.append("🗣️ Linguistic gap identified. A shared project lexicon must be established to avoid systemic communication errors.")

    if alignment < 70:
        if lang == "ar":
            guidance.append("📉 انخفاض مؤشر الانسجام (CAI) يعكس انقسام الفريق إلى جزر فكرية معزولة. ينبغي عقد جلسات محاذاة أفقية لتوحيد الرؤية الأساسية للواقع المشترك قبل الاستمرار في التنفيذ الهيكلي.")
        elif lang == "fr":
            guidance.append("📉 Faible indice d'alignement (CAI). Risque de polarisation au sein de l'équipe.")
        else:
            guidance.append("📉 Low Alignment Index (CAI). The team is operating in fragmented sub-clusters. Immediate cross-alignment is required.")

    if not guidance:
        if lang == "ar":
            guidance.append("✅ تماسك معرفي رائع متزن! المنظومة تعمل بانسجام تام، التواضع المعرفي مرتفع واللغة موحدة والممارسات مندمجة بقوة. واصلوا على هذا النهج المستدام لتوليد ابتكارات ثورية.")
        elif lang == "fr":
            guidance.append("✅ Excellente cohésion cognitive ! Le flux de connaissances est fluide et horizontal.")
        else:
            guidance.append("✅ Superb cognitive synergy! The knowledge flow is organically fluid and flat across all domains.")

    return "\n\n".join(guidance)


def generate_cognitive_charter(team_name, project_name, scores, lang):
    """صياغة بنود الميثاق المعرفي الملزم للفريق لحوكمة الفكر والحد من الطبقية والأنا الأكاديمية"""
    date_str = str(datetime.date.today())
    if lang == "ar":
        charter = f"""📜 ميثاق التلاحم والتكامل المعرفي الشامل
المشروع المستهدف: {project_name} | الفريق المعني: {team_name} | التاريخ: {date_str}

تأسيسًا على مبادئ التلاقح المعرفي (CPI) وحوكمة المعرفة الأفقية، يلتزم الفريق بالبنود السيادية التالية:
1. سيادة الفكرة المطلقة: تسقط كل الألقاب الأكاديمية والشهادات المهنية عند عتبة طاولة النقاش. الفكرة تُقيّم بجدواها الموضوعية ومطابقتها للواقع، وليس بسلطة صاحبها المكتسبة.
2. بناء القاموس المشترك: نلتزم بنبذ المصطلحات الفئوية المعقدة التي تهدف للاستعلاء المعرفي، ونعمل على صيانة لغة تواصل موحدة تجمع التخصصات (مثل الهندسة، البرمجيات، والطب) في عقل تداولي واحد.
3. تفكيك الجزر المعزولة: تلتزم القيادة بتشجيع التوجيه المسطح Flat Mentorship، وفتح قنوات الدعم التلقائي لتجاوز النزاعات الطبقية التقليدية.

توقيع هذا الميثاق يعد التزاماً أخلاقياً وعلمياً من جميع الأطراف لدعم مسيرة الابتكار الجمعي المستدام."""
    elif lang == "fr":
        charter = f"""📜 Charte de Cohésion Cognitive Globale
Projet: {project_name} | Équipe: {team_name} | Date: {date_str}

Les signataires s'engagent solennellement à respecter les piliers suivants:
1. Souveraineté de l'Idée: Les titres académiques et professionnels sont neutralisés. L'idée est jugée sur sa valeur intrinsèque.
2. Unification du Lexique: Engagement à vulgariser les termes complexes pour favoriser une pollinisation saine.
3. Humilité Épistémique: Déconstruction active de l'égo professionnel pour un flux d'apprentissage bidirectionnel."""
    else:
        charter = f"""📜 Sovereign Cognitive Alignment Charter
Project: {project_name} | Team: {team_name} | Date: {date_str}

The team solemnly enters into this covenant governed by the following pillars:
1. Absolute Authority of the Idea: Academic seniority and vertical statuses are dissolved at the meeting threshold. Ideas are evaluated purely on validity, not authority.
2. Lexicon Unification: Commitment to construct an integrated project vocabulary, preventing semantic isolation between clinical, engineering, and dev domains.
3. Epistemic Humility: Active suppression of professional hubris to maintain organic, multidirectional support flow."""
    return charter

#  ════════════════════════════════════════════════════════════════════
#  [نهاية الجزء الثاني] - البنى الرياضية ومحرك توليد التقارير PDF جاهز ومكتمل.
#  ════════════════════════════════════════════════════════════════════
#  ═══════════════════════════════════════════════════════════════════
#  [الجزء الثالث] - واجهة التقييم (النمط الفردي + PMP) · نسخة v7.2.1
#  تم إصلاح خطأ استدعاء التوجيه: إدراج تحقق من القيم قبل المعالجة
#  ═══════════════════════════════════════════════════════════════════

with tab1:
    st.markdown(f"### 🏢 {t('context_title')}")
    col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
    
    with col_c1:
        team_name = st.text_input(t("team_lbl"), value="فريق العمل")
    with col_c2:
        proj_name = st.text_input(t("proj_lbl"), value="مشروع التلاقح المعرفي")
    with col_c3:
        # استخدام المتغير المؤمّن من الـ session_state
        session_num_input = st.number_input(
            t("sess_num_lbl"), 
            min_value=1, 
            value=st.session_state.get("session_num_counter", 1)
        )

    st.markdown(f"### ⚙️ {t('mode_lbl')}")
    mode = st.radio("", [t("mode_solo"), t("mode_pmp")], horizontal=True)

    if mode == t("mode_solo"):
        st.markdown(f"### 📊 {t('dims_lbl')}")
        col1, col2 = st.columns(2)
        
        # تهيئة المدخلات مع قيم افتراضية لمنع NoneType Error
        with col1:
            eh = st.slider(t("🧠 التواضع و الإبداع (EH)"), 1.0, 5.0, 3.0, 0.5)
            l_val = st.slider(t("📚 اللغة المشتركة (L)"), 1.0, 5.0, 3.0, 0.5)
        with col2:
            p_val = st.slider(t("⚙️ الممارسة المشتركة (P)"), 1.0, 5.0, 3.0, 0.5)
            g_val = st.slider(t("🏛️ التوجيه والدعم (G)"), 1.0, 5.0, 3.0, 0.5)

        # ── 🛡️ كتلة الحماية الجديدة (Safety Guard) ──
        try:
            total_score = (eh + l_val + p_val + g_val)
            solo_score_pct = (total_score / 20) * 100
            
            st.markdown("---")
            # استدعاء آمن لدالة التوجيه
            if 'get_action_guidance' in globals():
                guidance = get_action_guidance(solo_score_pct)
                st.info(f"💡 {guidance}")
            
            st.metric(label=t("final_score_lbl"), value=f"{solo_score_pct:.1f}%")
            
        except Exception as e:
            st.warning("⚠️ يرجى ضبط قيم التقييم لتظهر النتائج.")

    elif mode == t("mode_pmp"):
        # [هنا تضع كود إدارة PMP الخاص بك]
        st.info(t("pmp_title"))
        # ... (باقي كود PMP) ...

# ── 💾 زر الحفظ (مؤمن) ──────────────────────────
if st.button(t("save_btn")):
    try:
        # منطق الحفظ في قاعدة البيانات
        # cpi_db.save_cpi_session(...)
        st.session_state.session_num_counter = int(session_num_input) + 1
        st.success("تم الحفظ بنجاح!")
        st.rerun()
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
#  ═══════════════════════════════════════════════════════════════════
#  مؤشر التلاقح المعرفي — CPI Dashboard v7.2 (النسخة السيادية الشاملة)
#  الجزء الرابع والأخير: الرسوم البيانية، لوحة القيادة، والسجل التاريخي
#  ═══════════════════════════════════════════════════════════════════

# ── 9. محرك الرسوم البيانية المتجهية (SVG) للوحة القيادة ─────────────────────
def calc_bdi(sessions):
    """حساب مؤشر اختفاء الحدود (Boundary Disappearance Index) بناءً على تشتت الأبعاد"""
    if len(sessions) < 1:
        return None
    last = sessions[-1]["scores"]
    vals = [last[k] for k in DIM_KEYS]
    mean = sum(vals) / 4.0
    variance = sum((v - mean) ** 2 for v in vals) / 4.0
    # 2.25 هو أقصى تباين ممكن (من 1 إلى 4 أو 5)
    bdi = max(0, (1 - variance / 4.0) * 100) 
    return round(bdi, 1)

def radar_svg(scores, size=320):
    """توليد المخطط الراداري السداسي لتمثيل التوازن المعرفي للأبعاد الأربعة"""
    lang = st.session_state.get("lang", "ar")
    pad = 50
    cx = cy = size / 2
    r = (size / 2) - pad
    n = len(DIM_KEYS)
    colors = [DIMS_DATA[k]["color"] for k in DIM_KEYS]
    
    def angle(i): return math.pi * 2 * i / n - math.pi / 2
    def pt(i, val):
        a = angle(i); d = (val / 5.0) * r  # مقسوم على 5 لأن العلامة العظمى 5
        return cx + d * math.cos(a), cy + d * math.sin(a)
        
    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="display:block;margin:auto">']
    
    # رسم حلقات الرادار الخلفية
    for v in [5, 4, 3, 2, 1]:
        pts = []
        for i in range(n):
            a = angle(i); d = (v / 5.0) * r
            pts.append(f"{cx + d*math.cos(a):.1f},{cy + d*math.sin(a):.1f}")
        fill_color = "#f8fafc" if v % 2 == 0 else "#f1f5f9"
        svg.append(f'<polygon points="{" ".join(pts)}" fill="{fill_color}" stroke="#cbd5e1" stroke-width="1"/>')
        
    # رسم خطوط المحاور المتقاطعة
    for i in range(n):
        a = angle(i)
        x2 = cx + r * math.cos(a); y2 = cy + r * math.sin(a)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4 4"/>')
        
    # رسم مضلع تقييم الجلسة الحالي
    filled_pts = []
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 1.0)
        x, y = pt(i, v)
        filled_pts.append(f"{x:.1f},{y:.1f}")
    svg.append(f'<polygon points="{" ".join(filled_pts)}" fill="rgba(99, 102, 241, 0.2)" stroke="#4f46e5" stroke-width="3" stroke-linejoin="round"/>')
    
    # رسم النقاط والتسميات
    for i, k in enumerate(DIM_KEYS):
        v = scores.get(k, 1.0)
        x, y = pt(i, v)
        c = colors[i]
        label = DIMS_DATA[k][lang]["name"]
        
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{c}" stroke="#ffffff" stroke-width="2"/>')
        
        # ضبط موضع النص ليكون خارج الرادار بمسافة مريحة
        a = angle(i)
        lx = cx + (r + 25) * math.cos(a)
        ly = cy + (r + 15) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < 0.1 else ("start" if math.cos(a) > 0 else "end")
        
        svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" dominant-baseline="middle" font-size="12" font-weight="bold" fill="#1e293b" font-family="Cairo, sans-serif">{label}</text>')
        svg.append(f'<text x="{lx:.1f}" y="{ly+16:.1f}" text-anchor="{anchor}" font-size="11" font-weight="bold" fill="{c}" font-family="Cairo, sans-serif">{v:.1f} / 5</text>')

    svg.append("</svg>")
    return "\n".join(svg)

# ═ 📊 علامة التبويب الثانية: لوحة القيادة التنبؤية (Dashboard) ═══════════════
with tab2:
    if not st.session_state.sessions:
        st.markdown(f'<div style="text-align:center; padding:50px; color:#94a3b8;"><h2>📊</h2><p>{t("no_data", "لا توجد بيانات بعد. ابدأ بتسجيل جلسة من تبويب التقييم.")}</p></div>', unsafe_allow_html=True)
    else:
        # سحب بيانات آخر جلسة مسجلة في الذاكرة
        last_session = st.session_state.sessions[-1]
        cpi_val = last_session.get("cpi", 0)
        cai_val = last_session.get("alignment_index", 100)
        scores = last_session.get("scores", {"P": 1, "L": 1, "G": 1, "EH": 1})
        maturity = get_maturity_level(cpi_val)
        bdi_val = calc_bdi(st.session_state.sessions)

        st.markdown(f'<div class="header-card" style="border-left: 5px solid {maturity["color"]};"><h3>📌 تحليل الجلسة الأخيرة: {last_session.get("label", "")} ({last_session.get("date", "")})</h3><p style="color:#64748b;">الفريق: <strong>{last_session.get("team", "")}</strong></p></div>', unsafe_allow_html=True)

        # 1. المؤشرات الفوقية الكبرى
        dash_c1, dash_c2, dash_c3 = st.columns(3)
        with dash_c1:
            st.markdown(f'<div class="score-box" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.05);"><div style="color:#64748b; font-size:14px; font-weight:bold;">مؤشر التلاقح (CPI)</div><div style="font-size:36px; font-weight:900; color:{maturity["color"]};">{cpi_val:.1f}%</div><div style="font-size:12px; color:#94a3b8;">{maturity["title"]}</div></div>', unsafe_allow_html=True)
        with dash_c2:
            st.markdown(f'<div class="score-box" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.05);"><div style="color:#64748b; font-size:14px; font-weight:bold;">الانسجام المعرفي (CAI)</div><div style="font-size:36px; font-weight:900; color:#3b82f6;">{cai_val:.1f}%</div><div style="font-size:12px; color:#94a3b8;">مستوى توافق الرؤى المشتركة</div></div>', unsafe_allow_html=True)
        with dash_c3:
            st.markdown(f'<div class="score-box" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.05);"><div style="color:#64748b; font-size:14px; font-weight:bold;">مؤشر اختفاء الحدود (BDI)</div><div style="font-size:36px; font-weight:900; color:#8b5cf6;">{bdi_val}%</div><div style="font-size:12px; color:#94a3b8;">درجة اتساق الأبعاد وإزالة الحواجز</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. الرادار الرسومي وتوصيات التحسين
        col_radar, col_recs = st.columns([1.2, 1])
        with col_radar:
            st.markdown('<h4>🕸️ خريطة البصمة المعرفية (Radar Profile)</h4>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#ffffff; border-radius:16px; padding:20px; box-shadow:0 4px 15px rgba(0,0,0,0.03); border:1px solid #f1f5f9;">{radar_svg(scores, 350)}</div>', unsafe_allow_html=True)
            
        with col_recs:
            st.markdown('<h4>💡 التوجيهات التشغيلية للتطوير</h4>', unsafe_allow_html=True)
            # تحديد البعد الأضعف لتقديم توصيات مخصصة
            weakest_dim = min(scores, key=scores.get)
            weakest_val = scores[weakest_dim]
            
            if weakest_val >= 4.0:
                st.success("🌟 جميع الأبعاد تعمل بمستوى عالٍ من التكامل. المنظومة في حالة استقرار إبداعي ممتاز. حافظوا على بروتوكولات التواصل الحالية.")
            else:
                dim_name = DIMS_DATA[weakest_dim][st.session_state.lang]["name"]
                st.warning(f"⚠️ **البعد ذو الأولوية القصوى للتطوير:** {dim_name} ({weakest_val}/5)")
                
                # استدعاء التوصيات من قاموس التوجيهات بناءً على البعد الأضعف
                if weakest_dim == "EH":
                    st.info("رصدنا انخفاضاً في التواضع المعرفي. نوصي بتطبيق 'المراجعة العمياء' للأفكار في الاجتماع القادم لتقليل تأثير السلطة والمنصب على اتخاذ القرار.")
                elif weakest_dim == "L":
                    st.info("رصدنا ضعفاً في اللغة المشتركة. يجب تخصيص 15 دقيقة من الورشة القادمة لتوحيد المصطلحات الهندسية والطبية في قاموس المشروع.")
                elif weakest_dim == "G":
                    st.info("التوجيه لا يتدفق بسلاسة. نوصي بتقليل الهرمية في اتخاذ القرارات اليومية الصغيرة ومنح مساحة قيادة متبادلة للخبراء.")
                elif weakest_dim == "P":
                    st.info("الممارسات المشتركة ضعيفة. يجب تفعيل بروتوكول 'التظليل الوظيفي' بحيث يراقب كل تخصص آلية عمل التخصص الآخر لفهم أولوياته.")

# ═ 📜 علامة التبويب الثالثة: السجل التاريخي وإدارة البيانات (History) ═════════
with tab3:
    st.markdown('<div class="header-card"><h3>🗄️ الأرشيف المركزي وسجل الجلسات</h3><p style="color:#94a3b8;">إدارة وتصدير بيانات القياس المعرفي السابقة والتحقق من التطور الزمني.</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.sessions:
        st.info("لا توجد سجلات محفوظة في قاعدة البيانات.")
    else:
        # تجهيز البيانات لعرضها في Dataframe
        df_data = []
        for s in reversed(st.session_state.sessions):  # عرض الأحدث أولاً
            df_data.append({
                "مُعرّف الجلسة (ID)": s.get("id"),
                "التاريخ": s.get("date"),
                "الفريق": s.get("team"),
                "المشروع": s.get("label"),
                "مؤشر CPI": f"{s.get('cpi', 0):.1f}%",
                "الانسجام CAI": f"{s.get('alignment_index', 100):.1f}%",
                "EH": s["scores"].get("EH"),
                "L": s["scores"].get("L"),
                "P": s["scores"].get("P"),
                "G": s["scores"].get("G")
            })
            
        st.dataframe(
            df_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "مؤشر CPI": st.column_config.TextColumn("مؤشر CPI 📊"),
                "الانسجام CAI": st.column_config.TextColumn("الانسجام CAI 🤝"),
            }
        )
        
        # تصدير البيانات إلى CSV
        import pandas as pd
        csv_data = pd.DataFrame(df_data).to_csv(index=False).encode('utf-8-sig')
        
        col_dl1, col_dl2 = st.columns([1, 4])
        with col_dl1:
            st.download_button(
                label="📥 تحميل السجل الشامل (CSV)",
                data=csv_data,
                file_name=f"CPI_History_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ── 10. تذييل حقوق الملكية والفكر للمنظومة ─────────────────────────────────────
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center; color:#94a3b8; font-size:0.85rem; padding-bottom:20px;">
    <strong>الإطار المعرفي لذكاء الفرق المشتركة (Cognitive Pollination Framework - CPI)</strong><br>
    تطوير وهندسة: د. الحبيب خروبي (ESU-001) | الإصدار v7.2 السيادي المدعوم بالمزامنة السحابية المزدوجة<br>
    <em>"التواضع المعرفي ليس مجرد فضيلة أخلاقية، بل هو بنية تشغيلية لازمة لظهور الذكاء الجماعي."</em>
</div>
""", unsafe_allow_html=True)

#  ════════════════════════════════════════════════════════════════════
#  تم بحمد الله اكتمال كود النسخة v7.2 بجميع أجزائها.
#  ════════════════════════════════════════════════════════════════════
