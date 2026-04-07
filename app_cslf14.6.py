import streamlit as st
import hashlib
import json
import time

# =============================================================
# 1. المحرك الأنطولوجي (Ontology Engine)
# =============================================================
class CSLFEpistemicOntologyEngineV14_6:
    def __init__(self):
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }

    def evaluate(self, pillars):
        issues = []
        fatal = []
        soft = []

        vals = {k: v["val"] for k, v in pillars.items()}

        # 1️⃣ الانهيار (العدم المطلق)
        collapsed = [p for p, v in vals.items() if v < 0.5]
        if collapsed:
            return 0.0, "NULL_STATE", collapsed, []

        # 2️⃣ فحص القالب (CIL)
        for name, data in pillars.items():
            text = data["text"].strip().lower()
            missing = [t for t in self.REQUIRED_PATTERNS[name] if t not in text]
            if missing:
                soft.append(f"⚠️ {name}: نقص بنيوي في {missing}")

        # 3️⃣ التناقضات القاتلة (Fatal Inconsistencies)
        if vals["CI"] > vals["SA"] + 0.3:
            fatal.append("⚡ تناقض سيادي: ادعاء سببية تفوق متانة البناء.")

        if vals["EG"] > 0.8 and len(pillars["EG"]["text"]) < 60:
            fatal.append("⚡ تناقض معرفي: ادعاء صلابة وتجذر بنص ضئيل جداً.")

        # 4️⃣ حساب المؤشر
        kll = min(vals.values())

        # 5️⃣ تصنيف طبقات الوجود (Existential Stratification)
        if fatal:
            if kll >= 0.85:
                status = "STRUCTURALLY_CORRUPTED" # قوي رقمياً، مزيف داخلياً
            else:
                status = "FRAGILE_EXISTENCE"      # ضعيف ومتصدع
        elif soft:
            if kll > 0.85:
                status = "EXISTS"
            else:
                status = "WEAK_EXISTENCE"
        else:
            if kll >= 0.90:
                status = "EPISTEMICALLY_STABLE"
            elif kll >= 0.75:
                status = "EXISTS"
            else:
                status = "WEAK_EXISTENCE"

        # 6️⃣ حالة الانهيار التدريجي (Override)
        if kll < 0.6:
            status = "COLLAPSING_EXISTENCE"

        return kll, status, [], fatal + soft

# =============================================================
# 2. الواجهة الأنطولوجية (The UI)
# =============================================================
st.set_page_config(page_title="CSLF v14.6 | Ontology Engine", layout="wide")

st.markdown("""
    <style>
    .status-panel { padding: 25px; border-radius: 12px; text-align: center; font-weight: bold; border: 3px solid; margin: 20px 0; font-size: 22px; }
    .stable { color: #00e5ff; border-color: #00e5ff; background: rgba(0, 229, 255, 0.05); }
    .exists { color: #00ffcc; border-color: #00ffcc; background: rgba(0, 255, 204, 0.05); }
    .weak { color: #ffcc00; border-color: #ffcc00; background: rgba(255, 204, 0, 0.05); }
    .fragile { color: #ff6600; border-color: #ff6600; background: rgba(255, 102, 0, 0.05); }
    .corrupted { color: #d946ef; border-color: #d946ef; background: rgba(217, 70, 239, 0.1); text-shadow: 0 0 5px #d946ef; }
    .collapsing { color: #ff3333; border-color: #ff3333; background: rgba(255, 51, 51, 0.05); }
    .null { color: #8b0000; border-color: #8b0000; background: rgba(139, 0, 0, 0.1); }
    .stTextArea textarea { border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("👤 سيادة المعماري")
    u_id = st.text_input("Architect ID", "ARCH_SUPREME")
    st.divider()
    st.markdown("### 🧬 طبقات الوجود:")
    st.caption("💎 EPISTEMICALLY_STABLE\n\n🟢 EXISTS\n\n🟡 WEAK_EXISTENCE\n\n🟠 FRAGILE_EXISTENCE\n\n☣️ STRUCTURALLY_CORRUPTED\n\n🔴 COLLAPSING_EXISTENCE\n\n💥 NULL_STATE")

st.title("🏛️ CSLF v14.6 — Epistemic Ontology Engine")
st.markdown("> **“ليس كل ما يلمع إبستيمياً حقيقي.. بعض الوجود صلب، وبعضه فاسد من الداخل.”**")

# مصفوفة الإدخال
p_data = {}
c1, c2 = st.columns(2)

fields = [
    ("SA", "🏗️ الأهلية البنيوية", ["مقدمة", "بنية", "نتيجة"]),
    ("CI", "🔗 النزاهة السببية", ["سبب", "آلية", "أثر"]),
    ("SV", "📖 الصلاحية الدلالية", ["تعريف", "سياق", "انضباط"]),
    ("EG", "🧪 التجذر المعرفي", ["دليل", "مصدر", "تحقق"])
]

for i, (key, label, terms) in enumerate(fields):
    col = c1 if i < 2 else c2
    with col:
        st.subheader(label)
        st.caption(f"القيود (CIL): {' | '.join(terms)}")
        val = st.slider(f"الوزن {key}", 0.0, 1.0, 0.80, key=f"v_{key}")
        text = st.text_area(f"حيثيات {key}", key=f"t_{key}", height=120)
        p_data[key] = {"val": val, "text": text}

st.divider()

if st.button("⚖️ استنطاق الوجود"):
    if any(len(d["text"].strip()) < 40 for d in p_data.values()):
        st.error("💥 رفض مبدئي: الكيان يفتقر للكثافة اللغوية الدنيا.")
        st.stop()

    engine = CSLFEpistemicOntologyEngineV14_6()
    kll, status, collapsed, all_issues = engine.evaluate(p_data)
    
    # واجهة العرض
    if status == "NULL_STATE":
        st.markdown(f"<div class='status-panel null'>💥 NULL_STATE<br><small>عدم مطلق في {collapsed}</small></div>", unsafe_allow_html=True)
    
    elif status == "COLLAPSING_EXISTENCE":
        st.markdown(f"<div class='status-panel collapsing'>🔴 COLLAPSING_EXISTENCE<br><small>الكيان يترنح وجودياً (KLL < 0.6)</small></div>", unsafe_allow_html=True)
        for i in all_issues: st.warning(i)

    elif status == "STRUCTURALLY_CORRUPTED":
        st.markdown(f"<div class='status-panel corrupted'>☣️ STRUCTURALLY_CORRUPTED<br><small>فساد بنيوي: الكيان يدعي قوة مطلقة (KLL > 0.85) لكنه يحمل تناقضاً قاتلاً</small></div>", unsafe_allow_html=True)
        for i in all_issues: st.error(i)

    elif status == "FRAGILE_EXISTENCE":
        st.markdown(f"<div class='status-panel fragile'>🟠 FRAGILE_EXISTENCE<br><small>وجود متصدع: الكيان يحمل تناقضاً</small></div>", unsafe_allow_html=True)
        for i in all_issues: st.error(i)

    elif status == "WEAK_EXISTENCE":
        st.markdown(f"<div class='status-panel weak'>🟡 WEAK_EXISTENCE<br><small>وجود ضعيف: الكيان يفتقر للاكتمال</small></div>", unsafe_allow_html=True)
        for i in all_issues: st.info(i)

    elif status == "EXISTS":
        st.markdown(f"<div class='status-panel exists'>🟢 EXISTS<br><small>وجود مقبول: الكيان متماسك</small></div>", unsafe_allow_html=True)

    elif status == "EPISTEMICALLY_STABLE":
        st.markdown(f"<div class='status-panel stable'>💎 EPISTEMICALLY_STABLE<br><small>وجود صلب: كيان سيادي</small></div>", unsafe_allow_html=True)
        st.balloons()

    trace = hashlib.sha256(json.dumps(p_data, sort_keys=True).encode()).hexdigest()
    st.code(f"STRATUM: {status}\nONTOLOGICAL_INDEX (KLL): {round(kll, 3)}\nTRACE_ID: {trace}")
