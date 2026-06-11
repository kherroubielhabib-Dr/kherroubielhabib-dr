# ═══════════════════════════════════════════════════════════════════
#  مؤشر التلاقح المعرفي — CPI Dashboard
#  Cross-Pollination Index
#  د. الحبيب خروبي · ESU-001
#  Streamlit app — app.py
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import json
import math
import datetime
import requests

# ── إعداد الصفحة ────────────────────────────────────────────────────
st.set_page_config(
    page_title="مؤشر التلاقح المعرفي — CPI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS مخصص ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans Arabic', 'Segoe UI', sans-serif !important;
    direction: rtl;
}

/* إخفاء عناصر Streamlit الافتراضية */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Header */
.cpi-header {
    background: #0F172A;
    color: white;
    padding: 18px 28px 14px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1E3A5F;
}
.cpi-header h1 { font-size: 22px; font-weight: 700; margin: 0; }
.cpi-header p  { font-size: 12px; color: #94A3B8; margin: 4px 0 0; }
.cpi-formula {
    background: #1E3A5F;
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 13px;
    color: #7DD3FC;
    font-weight: 600;
    font-family: monospace;
    letter-spacing: 1px;
}

/* Cards */
.cpi-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* بطاقة البُعد */
.dim-card {
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 14px;
    border: 1.5px solid #E5E7EB;
    background: #FAFAFA;
}
.dim-title { font-size: 17px; font-weight: 700; }
.dim-desc  { font-size: 12px; color: #9CA3AF; margin: 3px 0 8px; }
.dim-q     { font-size: 13px; color: #374151; font-style: italic; margin-bottom: 10px; }

/* CPI Badge */
.cpi-badge {
    border-radius: 10px;
    padding: 16px 24px;
    text-align: center;
    font-family: monospace;
}
.cpi-value  { font-size: 42px; font-weight: 800; }
.cpi-label  { font-size: 13px; font-weight: 600; margin-top: 4px; }

/* Level colors */
.level-0 { background:#FEF2F2; color:#EF4444; border:1.5px solid #FECACA; }
.level-1 { background:#FFFBEB; color:#F59E0B; border:1.5px solid #FDE68A; }
.level-2 { background:#EFF6FF; color:#3B82F6; border:1.5px solid #BFDBFE; }
.level-3 { background:#F0FDF4; color:#10B981; border:1.5px solid #A7F3D0; }

/* Score buttons */
.score-row { display: flex; gap: 8px; margin-top: 6px; }
.score-btn {
    width: 46px; height: 46px;
    border-radius: 8px;
    font-size: 16px; font-weight: 700;
    border: 1.5px solid #D1D5DB;
    background: white; color: #374151;
    cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center;
}
.score-btn.active { color: white; border: 2px solid; }

/* توصيات */
.rec-card {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
}
.rec-title { font-weight: 700; margin-bottom: 3px; }
.rec-body  { color: #92400E; }

/* تاريخ الجلسات */
.session-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.session-header { display:flex; justify-content:space-between; margin-bottom:8px; }
.session-name   { font-weight:700; font-size:14px; }
.session-date   { font-size:11px; color:#9CA3AF; }
.session-cpi    { font-size:20px; font-weight:800; font-family:monospace; padding:4px 12px; border-radius:8px; }
.dim-tag {
    display:inline-block;
    background:#F9FAFB;
    border-radius:6px;
    padding:3px 10px;
    font-size:11px;
    font-weight:600;
    margin-left:6px;
    margin-bottom:4px;
}

/* الميسر */
.msg-user {
    background: #2563EB; color: white;
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px; font-size: 13px;
    line-height: 1.7; white-space: pre-wrap;
    margin-bottom: 10px; max-width: 88%;
    margin-right: auto;
}
.msg-ai {
    background: white; color: #111827;
    border: 1px solid #E5E7EB;
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px; font-size: 13px;
    line-height: 1.7; white-space: pre-wrap;
    margin-bottom: 10px; max-width: 88%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.msg-ai-label { font-size:10px; color:#7C3AED; font-weight:700; margin-bottom:5px; }

/* Radar SVG container */
.radar-wrap { display:flex; justify-content:center; padding:10px 0; }

/* Progress bar */
.prog-wrap { height:8px; background:#F3F4F6; border-radius:4px; overflow:hidden; margin-top:4px; }
.prog-bar  { height:100%; border-radius:4px; transition: width 0.5s ease; }

/* BDI card */
.bdi-card {
    background:#F5F3FF; border:1px solid #DDD6FE;
    border-radius:12px; padding:16px 20px;
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom:16px;
}
.bdi-val { font-size:32px; font-weight:800; font-family:monospace; }
</style>
""", unsafe_allow_html=True)

# ── البيانات الثابتة ─────────────────────────────────────────────────
DIMS = [
    {"key": "P",  "ar": "الممارسة",        "color": "#2563EB",
     "desc": "مدى استيعاب كل تخصص لأولويات التخصص الآخر",
     "q":    "هل فهمنا أولويات بعضنا البعض في القرارات؟"},
    {"key": "L",  "ar": "اللغة المشتركة",  "color": "#059669",
     "desc": "وجود قاموس مفاهيمي موحد يسمح بالتواصل الفعال",
     "q":    "هل تحدثنا بلغة مشتركة دون سوء فهم؟"},
    {"key": "G",  "ar": "التوجيه",          "color": "#7C3AED",
     "desc": "اتجاه تدفق الأفكار داخل النظام",
     "q":    "هل تدفقت الأفكار من الجميع (وليس فقط من القائد)؟"},
    {"key": "EH", "ar": "التواضع المعرفي", "color": "#DC2626",
     "desc": "قدرة الأفراد على قبول التصحيح والتعلم من الآخرين",
     "q":    "هل استمعنا لبعضنا بتواضع وغيرنا مواقفنا؟"},
]

LEVELS = [
    {"min": 0,  "max": 40,  "label": "نموذج العبقري المنعزل",             "color": "#EF4444", "cls": "level-0"},
    {"min": 40, "max": 65,  "label": "تعاون شكلي",                         "color": "#F59E0B", "cls": "level-1"},
    {"min": 65, "max": 85,  "label": "ذكاء جماعي واعٍ جزئياً",            "color": "#3B82F6", "cls": "level-2"},
    {"min": 85, "max": 101, "label": "ذكاء جماعي حقيقي — اختفاء الحدود", "color": "#10B981", "cls": "level-3"},
]

FAC_MODES = {
    "transcript": {
        "label": "📋 تحليل محضر اجتماع",
        "ph": "الصق هنا نص محضر الاجتماع أو ملخص ما دار فيه...",
        "system": """أنت ميسر معرفي محايد متخصص في نظرية CPI (مؤشر التلاقح المعرفي) وضعه د. الحبيب خروبي.
نظريتك: CI = NK × EH — الذكاء الجماعي = المعرفة الشبكية × التواضع المعرفي.
الأبعاد: P (الممارسة)، L (اللغة المشتركة)، G (التوجيه)، EH (التواضع المعرفي).

مهمتك — تحليل المحضر وإرجاع:
1. مؤشر تقديري لكل بُعد من 1 إلى 4 مع تبرير موجز
2. المصطلحات التخصصية التي تحتاج تفسيراً بين التخصصات
3. أبرز لحظة تواضع معرفي وأبرز لحظة أنا مرتفعة
4. توصية واحدة عملية للجلسة القادمة

الرد بالعربية، مركّز، بدون مقدمات.""",
    },
    "glossary": {
        "label": "📖 فك الاشتباك المعرفي",
        "ph": "اكتب مصطلحاً تقنياً تريد تبسيطه لبقية الفريق...",
        "system": """أنت ميسر معرفي متخصص في بناء القاموس المشترك بين التخصصات ضمن إطار CPI.

مهمتك — شرح المصطلح بثلاث طبقات:
1. تعريف بسيط (جملة واحدة، بدون مصطلحات تقنية)
2. مثال من الواقع يفهمه غير المتخصص
3. لماذا هذا المصطلح مهم للفريق متعدد التخصصات؟

الرد بالعربية، موجز ومباشر.""",
    },
    "ego": {
        "label": "🔍 رصد الأنا",
        "ph": "الصق مقتطفات من حوار الفريق أو رسائل المجموعة...",
        "system": """أنت ميسر معرفي محايد تحلل لغة الفريق وفق بُعد التواضع المعرفي (EH) في إطار CPI.

مهمتك:
1. نسبة تقديرية لغة "أنا" مقابل "نحن" (%)
2. أمثلة محددة على لغة الأنا الفردية
3. أمثلة على لغة الجماعة (إن وجدت)
4. تقييم EH من 1 إلى 4 مع تبرير
5. جملة واحدة تُرسَل للفريق كتغذية راجعة محايدة

الرد بالعربية، محايد، بدون أحكام شخصية.""",
    },
    "bias": {
        "label": "⚖️ كشف التحيزات",
        "ph": "صف ما جرى في الاجتماع أو القرار الذي اتُّخذ...",
        "system": """أنت ميسر معرفي محايد متخصص في كشف التحيزات المعرفية داخل الفرق وفق إطار CPI.

التحيزات التي ترصدها:
- تحيز التأكيد: البحث عن أدلة تؤيد رأياً مسبقاً
- تحيز السلطة: تبني أفكار ذوي المناصب دون نقد
- الثقة المفرطة: المبالغة في تقدير دقة التوقعات
- تحيز الإجماع: تجنب الخلاف لأسباب اجتماعية

مهمتك:
1. التحيزات المرصودة مع شواهد
2. السؤال الذي كان يجب طرحه ولم يُطرح
3. توصية واحدة لتفادي التحيز المرة القادمة

الرد بالعربية، تحليلي ومباشر.""",
    },
}

RECS = {
    "P":  ("الممارسة",        "#2563EB", "جلسات «تظليل وظيفي» أسبوعية — يظلل كل تخصص الآخر."),
    "L":  ("اللغة المشتركة",  "#059669", "ورشة «قاموس مشترك» — يوم واحد + تحديثات أسبوعية."),
    "G":  ("التوجيه",          "#7C3AED", "إلغاء الموافقات الهرمية على الاقتراحات الصغيرة."),
    "EH": ("التواضع المعرفي", "#DC2626", "جلسات «مراجعة عمياء» — تقييم الأفكار دون معرفة صاحبها."),
}

# ── دوال مساعدة ──────────────────────────────────────────────────────
def get_level(cpi):
    for l in LEVELS:
        if l["min"] <= cpi < l["max"]:
            return l
    return LEVELS[-1]

def calc_cpi(scores):
    vals = [v for v in scores.values() if v > 0]
    if len(vals) < 4:
        return None
    return round(sum(vals) / 16 * 100)

def calc_bdi(sessions):
    if len(sessions) < 2:
        return None
    last = sessions[-1]["scores"]
    vals = [last[d["key"]] for d in DIMS]
    mean = sum(vals) / 4
    variance = sum((v - mean) ** 2 for v in vals) / 4
    return round((1 - variance / 2.25) * 100)

def radar_svg(scores, size=220):
    """رسم Radar Chart بـ SVG خالص"""
    cx = cy = size / 2
    r = size * 0.36
    n = len(DIMS)
    colors = [d["color"] for d in DIMS]

    def angle(i):
        return math.pi * 2 * i / n - math.pi / 2

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

    # حلقات الخلفية
    for v in [1, 2, 3, 4]:
        svg.append(f'<polygon points="{ring_points(v)}" fill="none" stroke="#E5E7EB" stroke-width="1"/>')

    # محاور
    for i in range(n):
        a = angle(i)
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        svg.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#E5E7EB" stroke-width="1"/>')

    # المضلع المملوء
    filled_pts = []
    for i, d in enumerate(DIMS):
        v = scores.get(d["key"], 0)
        x, y = pt(i, v)
        filled_pts.append(f"{x:.1f},{y:.1f}")
    svg.append(f'<polygon points="{" ".join(filled_pts)}" fill="rgba(37,99,235,0.15)" stroke="#2563EB" stroke-width="2" stroke-linejoin="round"/>')

    # نقاط
    for i, d in enumerate(DIMS):
        v = scores.get(d["key"], 0)
        x, y = pt(i, v)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{d["color"]}"/>')

    # تسميات
    for i, d in enumerate(DIMS):
        a = angle(i)
        lx = cx + (r + 26) * math.cos(a)
        ly = cy + (r + 26) * math.sin(a)
        svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" '
                   f'font-size="10" font-weight="600" fill="#374151" '
                   f'font-family="IBM Plex Sans Arabic, sans-serif">{d["ar"]}</text>')

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
        font-family="IBM Plex Sans Arabic, monospace">{value}%</text>
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
            return f"⚠️ خطأ من API: {data['error']['message']}"
        else:
            return "⚠️ استجابة غير متوقعة من الخادم."
    except Exception as e:
        return f"⚠️ خطأ في الاتصال: {str(e)}"

# ── Session State ─────────────────────────────────────────────────────
if "sessions"   not in st.session_state: st.session_state.sessions   = []
if "scores"     not in st.session_state: st.session_state.scores     = {d["key"]: 0 for d in DIMS}
if "fac_msgs"   not in st.session_state: st.session_state.fac_msgs   = []
if "fac_mode"   not in st.session_state: st.session_state.fac_mode   = "transcript"
if "api_key"    not in st.session_state: st.session_state.api_key    = ""

# ── Header ───────────────────────────────────────────────────────────
st.markdown("""
<div class="cpi-header">
  <div>
    <h1>🧠 مؤشر التلاقح المعرفي</h1>
    <p>Cross-Pollination Index — CPI Dashboard · د. الحبيب خروبي · ESU-001</p>
  </div>
  <div class="cpi-formula">CI = NK × EH</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 تقييم جلسة",
    "📊 لوحة القيادة",
    f"🗂️ السجل ({len(st.session_state.sessions)})",
    "🧠 الميسر المعرفي",
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — تقييم جلسة
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div style="font-size:13px; color:#6B7280; margin-bottom:16px;">
    قيّم الأبعاد الأربعة بعد كل Sprint أو اجتماع حاسم.<br>
    <strong>1 = ضعيف · 2 = مقبول · 3 = جيد · 4 = متقدم (اختفاء الحدود)</strong>
    </div>
    """, unsafe_allow_html=True)

    session_name = st.text_input(
        "اسم الجلسة (اختياري)",
        placeholder="مثال: اجتماع التخطيط - يوليو 2026",
        label_visibility="collapsed",
        key="session_name_input"
    )

    st.markdown("---")

    # أزرار التقييم لكل بُعد
    for d in DIMS:
        col_info, col_btns = st.columns([3, 2])
        with col_info:
            st.markdown(f"""
            <div style="padding:4px 0">
                <span style="display:inline-block; background:{d['color']}18; color:{d['color']};
                      font-weight:800; font-size:12px; padding:2px 8px; border-radius:6px; margin-bottom:4px">{d['key']}</span>
                <span style="font-size:16px; font-weight:700; margin-right:8px; color:{d['color']}">{d['ar']}</span><br>
                <span style="font-size:11px; color:#9CA3AF">{d['desc']}</span><br>
                <em style="font-size:12px; color:#374151">«{d['q']}»</em>
            </div>
            """, unsafe_allow_html=True)
        with col_btns:
            current = st.session_state.scores[d["key"]]
            labels = ["1\nضعيف", "2\nمقبول", "3\nجيد", "4\nمتقدم"]
            bcols = st.columns(4)
            for vi, (bc, lbl) in enumerate(zip(bcols, labels), 1):
                with bc:
                    is_active = current == vi
                    btn_style = f"background:{d['color']}; border:2px solid {d['color']};" if is_active else ""
                    if st.button(
                        str(vi),
                        key=f"btn_{d['key']}_{vi}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                    ):
                        st.session_state.scores[d["key"]] = vi
                        st.rerun()

        st.markdown("---")

    # CPI المحسوب
    cpi_now = calc_cpi(st.session_state.scores)

    if cpi_now is not None:
        level = get_level(cpi_now)
        col_gauge, col_radar = st.columns([1, 1])
        with col_gauge:
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background:#F0F7FF;
                        border:1px solid #BFDBFE; border-radius:12px;">
                <div style="font-size:12px; color:#6B7280; margin-bottom:4px">CPI المحسوب</div>
                {gauge_svg(cpi_now)}
                <div style="font-size:13px; font-weight:700; color:{level['color']}; margin-top:4px">{level['label']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_radar:
            st.markdown(
                f'<div class="radar-wrap">{radar_svg(st.session_state.scores, 220)}</div>',
                unsafe_allow_html=True
            )

        if st.button(f"✅ تسجيل الجلسة — CPI: {cpi_now}%", type="primary", use_container_width=True):
            entry = {
                "id": datetime.datetime.now().timestamp(),
                "label": session_name or f"جلسة {len(st.session_state.sessions) + 1}",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "scores": dict(st.session_state.scores),
                "cpi": cpi_now,
            }
            st.session_state.sessions.append(entry)
            st.session_state.scores = {d["key"]: 0 for d in DIMS}
            st.success(f"✓ تم تسجيل الجلسة — CPI: {cpi_now}% | {level['label']}")
            st.rerun()
    else:
        st.info("أكمل تقييم الأبعاد الأربعة لحساب CPI")


# ════════════════════════════════════════════════════════════════════
# TAB 2 — لوحة القيادة
# ════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.sessions:
        st.markdown("""
        <div style="text-align:center; color:#9CA3AF; padding:60px 20px;">
            <div style="font-size:48px; margin-bottom:12px">📊</div>
            <div style="font-size:16px; font-weight:600; margin-bottom:6px">لا توجد بيانات بعد</div>
            <div style="font-size:13px">سجّل أول جلسة من تبويب «تقييم جلسة»</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        last = st.session_state.sessions[-1]
        dash_cpi    = last["cpi"]
        dash_scores = last["scores"]
        level       = get_level(dash_cpi)
        bdi         = calc_bdi(st.session_state.sessions)

        # Gauge + Radar
        col_g, col_r = st.columns([1, 1])
        with col_g:
            st.markdown(f"""
            <div style="text-align:center; padding:24px; background:white;
                        border:1px solid #E5E7EB; border-radius:12px; height:100%">
                <div style="font-size:12px; color:#6B7280; margin-bottom:4px">آخر CPI مسجّل</div>
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

        # تفصيل الأبعاد
        st.markdown('<div class="cpi-card"><div style="font-size:14px;font-weight:700;margin-bottom:14px">تفصيل الأبعاد — آخر جلسة</div>', unsafe_allow_html=True)
        for d in DIMS:
            v = dash_scores.get(d["key"], 0)
            pct = (v / 4) * 100
            icon = "🔴" if v <= 2 else ("🔵" if v == 3 else "🟢")
            st.markdown(f"""
            <div style="margin-bottom:14px">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px">
                    <span style="font-size:13px; font-weight:600">{d['ar']} ({d['key']})</span>
                    <span style="font-size:13px; font-weight:700; color:{d['color']}; font-family:monospace">{v}/4 {icon}</span>
                </div>
                <div class="prog-wrap">
                    <div class="prog-bar" style="width:{pct}%; background:{d['color']}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # BDI
        if bdi is not None:
            bdi_color = "#10B981" if bdi >= 75 else ("#3B82F6" if bdi >= 50 else "#EF4444")
            st.markdown(f"""
            <div class="bdi-card">
                <div>
                    <div style="font-size:13px; color:#7C3AED; font-weight:600">مؤشر اختفاء الحدود (BDI)</div>
                    <div style="font-size:11px; color:#9CA3AF; margin-top:2px">كلما اقترب من 100% كلما اقترب الفريق من العقل الجماعي الحقيقي</div>
                </div>
                <div class="bdi-val" style="color:{bdi_color}">{bdi}%</div>
            </div>
            """, unsafe_allow_html=True)

        # مسار CPI
        if len(st.session_state.sessions) >= 2:
            st.markdown('<div class="cpi-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:14px;font-weight:700;margin-bottom:12px">مسار CPI عبر الزمن</div>', unsafe_allow_html=True)
            st.markdown(trend_svg(st.session_state.sessions), unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:11px;color:#9CA3AF;margin-top:8px">{len(st.session_state.sessions)} جلسة مسجّلة</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # توصيات
        weak = [d for d in DIMS if dash_scores.get(d["key"], 0) <= 2]
        st.markdown('<div class="cpi-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px;font-weight:700;margin-bottom:12px">توصيات التحسين</div>', unsafe_allow_html=True)
        if not weak:
            st.markdown('<div style="font-size:13px;color:#10B981;font-weight:600">✓ جميع الأبعاد في مستوى جيد. استمر في المسار الحالي.</div>', unsafe_allow_html=True)
        else:
            for d in weak:
                key = d["key"]
                name, color, rec_text = RECS[key]
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title" style="color:{color}">{name} — يحتاج تعزيز</div>
                    <div class="rec-body">{rec_text}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 3 — السجل
# ════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.sessions:
        st.markdown("""
        <div style="text-align:center; color:#9CA3AF; padding:60px 20px;">
            <div style="font-size:48px; margin-bottom:12px">🗂️</div>
            <div>لا توجد جلسات مسجّلة بعد</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_h, col_del = st.columns([3, 1])
        with col_h:
            st.markdown(f'<div style="font-size:14px;font-weight:700;padding:8px 0">{len(st.session_state.sessions)} جلسة مسجّلة</div>', unsafe_allow_html=True)
        with col_del:
            if st.button("🗑️ حذف الكل", type="secondary"):
                st.session_state.sessions = []
                st.rerun()

        for s in reversed(st.session_state.sessions):
            lvl = get_level(s["cpi"])
            tags_html = "".join(
                f'<span class="dim-tag"><span style="color:{d["color"]}">{d["key"]}</span> '
                f'<span style="color:#6B7280">{s["scores"].get(d["key"],0)}/4</span></span>'
                for d in DIMS
            )
            st.markdown(f"""
            <div class="session-card">
                <div class="session-header">
                    <div>
                        <div class="session-name">{s['label']}</div>
                        <div class="session-date">{s['date']}</div>
                    </div>
                    <div class="session-cpi" style="background:{lvl['color']}18; color:{lvl['color']}">{s['cpi']}%</div>
                </div>
                <div>{tags_html}</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 4 — الميسر المعرفي
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div style="background:#0F172A; color:white; border-radius:12px; padding:18px 22px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <div style="width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,#2563EB,#7C3AED);
                        display:flex;align-items:center;justify-content:center;font-size:18px">🧠</div>
            <div>
                <div style="font-weight:700;font-size:15px">الميسر المعرفي</div>
                <div style="font-size:11px;color:#94A3B8">Cognitive Facilitator — مدعوم بـ Claude AI</div>
            </div>
        </div>
        <div style="font-size:12px;color:#CBD5E1;line-height:1.7">
        طرف ثالث محايد لا يملك أنا ولا مصلحة. يحلل لغة الفريق، يفك الاشتباك المعرفي، ويقول الحقيقة لأنه لا يملك ثمناً يخسره.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # مفتاح API
    api_key_input = st.text_input(
        "🔑 مفتاح Anthropic API",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
        help="المفتاح لا يُخزَّن خارج الجلسة الحالية"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    # اختيار الوظيفة
    mode_options = list(FAC_MODES.keys())
    mode_labels  = [FAC_MODES[k]["label"] for k in mode_options]
    selected_idx = st.radio(
        "وظيفة الميسر:",
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

    # عرض المحادثة
    for msg in st.session_state.fac_msgs:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-ai"><div class="msg-ai-label">🧠 الميسر المعرفي</div>{msg["content"]}</div>', unsafe_allow_html=True)

    # إدخال المستخدم
    mode_cfg = FAC_MODES[st.session_state.fac_mode]
    user_input = st.text_area(
        "إدخال:",
        placeholder=mode_cfg["ph"],
        height=120,
        label_visibility="collapsed",
        key="fac_input_area"
    )

    col_send, col_clear = st.columns([3, 1])
    with col_send:
        send_clicked = st.button("📤 إرسال للميسر", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ مسح", use_container_width=True):
            st.session_state.fac_msgs = []
            st.rerun()

    if send_clicked:
        if not st.session_state.api_key:
            st.error("أدخل مفتاح Anthropic API أولاً.")
        elif not user_input.strip():
            st.warning("اكتب رسالتك أولاً.")
        else:
            st.session_state.fac_msgs.append({"role": "user", "content": user_input.strip()})
            with st.spinner("🧠 الميسر يحلل..."):
                reply = call_claude(
                    messages=st.session_state.fac_msgs,
                    system_prompt=mode_cfg["system"],
                    api_key=st.session_state.api_key,
                )
            st.session_state.fac_msgs.append({"role": "assistant", "content": reply})
            st.rerun()

# ── Footer ───────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; font-size:11px; color:#D1D5DB; margin-top:40px; padding:20px 0;">
    CPI — مؤشر التلاقح المعرفي · د. الحبيب خروبي · ESU-001
</div>
""", unsafe_allow_html=True)
