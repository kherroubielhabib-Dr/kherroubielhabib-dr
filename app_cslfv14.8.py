import streamlit as st
import hashlib
import json

# 1. المحرك الأنطولوجي المحايد
class CSLFNeutralGateV14_8:
    def __init__(self):
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }

    def evaluate_presence(self, pillars):
        paradoxes = []
        structural_gaps = []
        vals = {k: v["val"] for k, v in pillars.items()}

        collapsed = [p for p, v in vals.items() if v < 0.5]
        if collapsed: return 0.0, "NULL_STATE", collapsed, []

        for name, data in pillars.items():
            text = data["text"].strip().lower()
            missing = [t for t in self.REQUIRED_PATTERNS[name] if t not in text]
            if missing: structural_gaps.append(f"⚠️ {name}: نقص هيكلي {missing}")

        if vals["CI"] > vals["SA"] + 0.3:
            paradoxes.append("🧬 مفارقة بنيوية: تضخم في الادعاء السببي مقابل القدرة البنائية.")

        kll = min(vals.values())
        if paradoxes: status = "PARADOXICAL_EXISTENCE"
        elif structural_gaps: status = "INCOMPLETE_EXISTENCE"
        else: status = "EXISTS"

        return kll, status, [], paradoxes + structural_gaps

# 2. واجهة العرض والتنسيق
st.set_page_config(page_title="CSLF v14.8 | Neutral Gate", layout="wide")

st.markdown("""
    <style>
    .status-panel { padding: 25px; border-radius: 12px; text-align: center; font-weight: bold; border: 3px solid; margin: 20px 0; font-size: 22px; }
    .exists { color: #00ffcc; border-color: #00ffcc; background: rgba(0, 255, 204, 0.05); }
    .incomplete { color: #ffcc00; border-color: #ffcc00; background: rgba(255, 204, 0, 0.05); }
    .paradoxical { color: #ff8800; border-color: #ff8800; background: rgba(255, 136, 0, 0.05); }
    .null { color: #ff4b4b; border-color: #ff4b4b; background: rgba(255, 75, 75, 0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("🏛️ CSLF v14.8 — The Neutral Existence Gate")
st.info("فلسفة v14.8: أنا لا أحكم عليك.. أنا فقط أكشف لك كيف يرى المنطق وجودك.")

# تعريف p_data كقاموس فارغ في البداية لضمان وصول الزر إليه
p_data = {}

c1, c2 = st.columns(2)
fields = [
    ("SA", "🏗️ الأهلية البنيوية", ["مقدمة", "بنية", "نتيجة"]),
    ("CI", "🔗 النزاهة السببية", ["سبب", "آلية", "أثر"]),
    ("SV", "📖 الصلاحية الدلالية", ["تعريف", "سياق", "انضباط"]),
    ("EG", "🧪 التجذر المعرفي", ["دليل", "مصدر", "تحقق"])
]

# بناء واجهة المدخلات
for i, (key, label, terms) in enumerate(fields):
    col = c1 if i < 2 else c2
    with col:
        st.subheader(label)
        val = st.slider(f"الوزن {key}", 0.0, 1.0, 0.8, key=f"v_{key}")
        text = st.text_area(f"حيثيات {key}", key=f"t_{key}", height=120, placeholder=f"يجب أن يتضمن: {terms}")
        p_data[key] = {"val": val, "text": text}

st.divider()

# منطقة الزر والتنفيذ
if st.button("⚖️ استنطاق الوجود", type="primary", use_container_width=True):
    # فحص الكثافة اللغوية أولاً
    error_found = False
    for key, data in p_data.items():
        if len(data["text"].strip()) < 40:
            st.error(f"💥 الركن {key} يفتقر للكثافة اللغوية (أقل من 40 حرفاً).")
            error_found = True
    
    if not error_found:
        # تشغيل المحرك
        engine = CSLFNeutralGateV14_8()
        kll, status, collapsed, all_issues = engine.evaluate_presence(p_data)
        
        # عرض النتائج بناءً على الحالة
        if status == "NULL_STATE":
            st.markdown(f"<div class='status-panel null'>💥 NULL_STATE: انهيار في {collapsed}</div>", unsafe_allow_html=True)
        elif status == "PARADOXICAL_EXISTENCE":
            st.markdown(f"<div class='status-panel paradoxical'>🧬 PARADOXICAL_EXISTENCE: وجود مفارقي</div>", unsafe_allow_html=True)
            for i in all_issues: st.warning(i)
        elif status == "INCOMPLETE_EXISTENCE":
            st.markdown(f"<div class='status-panel incomplete'>⚠️ INCOMPLETE_EXISTENCE: وجود غير مكتمل</div>", unsafe_allow_html=True)
            for i in all_issues: st.info(i)
        else:
            st.markdown(f"<div class='status-panel exists'>✨ EXISTS: وجود متماسك</div>", unsafe_allow_html=True)
            st.balloons()

        # الختم الجنائي (FAL)
        trace = hashlib.sha256(json.dumps(p_data, sort_keys=True).encode()).hexdigest()
        st.code(f"STATUS: {status} | KLL: {round(kll, 3)}\nTRACE_ID: {trace}")
