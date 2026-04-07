import streamlit as st
import hashlib
import json
import time

# =============================================================
# 1. المحرك الأنطولوجي (The Ontological Engine)
# =============================================================
class CSLFOntologicalEngineV14_4:
    def __init__(self):
        # القيود البنيوية (CIL) - شروط التجسد الوجودي
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }

    def evaluate_existence(self, pillars):
        """فحص استحقاق الوجود: هل هذا الكيان متماسك أم عدمي؟"""
        issues = []
        vals = {k: v["val"] for k, v in pillars.items()}
        
        # 1. اختبار الانهيار (Ontological Collapse)
        # أي ركن تحت 0.5 يعني أن الكيان يفتقر لأدنى مقومات الوجود
        collapsed = [p for p, v in vals.items() if v < 0.5]
        if collapsed:
            return 0.0, "NULL_STATE", collapsed, []

        # 2. اختبار القالب الهيكلي (CIL) - الوجود يتطلب "صورة" واضحة
        for name, data in pillars.items():
            text = data["text"].strip().lower()
            missing = [term for term in self.REQUIRED_PATTERNS[name] if term not in text]
            if missing:
                issues.append(f"⚠️ {name}: نقص في العناصر الهيكلية {missing}")

        # 3. اختبار الاتساق (Internal Consistency)
        # الوجود الهش هو الذي يحمل تناقضاً داخلياً (السببية تسبق البناء مثلاً)
        if vals["CI"] > vals["SA"] + 0.3:
            issues.append("⚡ تناقض بنيوي: ادعاء سببية تفوق متانة البناء.")
        
        if vals["EG"] > 0.8 and len(pillars["EG"]["text"]) < 60:
            issues.append("⚡ هشاشة معرفية: ادعاء تجذر صلب بكلمات معدودة.")

        kll = min(vals.values()) # مؤشر وصفي فقط لعمق الوجود

        # تحديد الحالة الوجودية (The Existential Status)
        if issues:
            status = "FRAGILE_EXISTENCE" # وجود هش/متناقض
        else:
            status = "EXISTS" # وجود متماسك
            
        return kll, status, [], issues

# =============================================================
# 2. واجهة الاعتراف بالوجود (Sovereign Existence UI)
# =============================================================
st.set_page_config(page_title="CSLF v14.4 | The Ontological Gate", layout="wide")

# تصميم يعكس الرصانة والحياد
st.markdown("""
    <style>
    .status-box { padding: 20px; border-radius: 10px; border: 2px solid; margin: 15px 0; text-align: center; font-size: 24px; font-weight: bold; }
    .exists { color: #00ffcc; border-color: #00ffcc; background-color: rgba(0, 255, 204, 0.05); }
    .fragile { color: #ffcc00; border-color: #ffcc00; background-color: rgba(255, 204, 0, 0.05); }
    .null { color: #ff4b4b; border-color: #ff4b4b; background-color: rgba(255, 75, 75, 0.05); }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("👤 سيادة المعماري")
    u_id = st.text_input("Architect ID", "ARCH_PRO")
    st.divider()
    if "edi" not in st.session_state: st.session_state.edi = 0.0
    st.metric("EDI (مؤشر الانحراف التراكمي)", round(st.session_state.edi, 2))
    st.info("فلسفة v14.4: نحن لا نحكم على الحق، نحن نعترف بالحق في الوجود.")

st.title("🏛️ CSLF v14.4 — The Ontological Gate")
st.markdown("> **“أنا لا أقرر من هو على حق… أنا أقرر فقط من يملك الحق في أن يُسمع.”**")

# مصفوفة الأركان الأربعة
p_data = {}
col1, col2 = st.columns(2)

fields = [
    ("SA", "🏗️ الأهلية البنيوية", ["مقدمة", "بنية", "نتيجة"]),
    ("CI", "🔗 النزاهة السببية", ["سبب", "آلية", "أثر"]),
    ("SV", "📖 الصلاحية الدلالية", ["تعريف", "سياق", "انضباط"]),
    ("EG", "🧪 التجذر المعرفي", ["دليل", "مصدر", "تحقق"])
]

for i, (key, label, terms) in enumerate(fields):
    target_col = col1 if i < 2 else col2
    with target_col:
        st.subheader(label)
        st.caption(f"الكلمات الإلزامية للوجود: {' | '.join(terms)}")
        val = st.slider(f"تقدير المعماري لـ {key}", 0.0, 1.0, 0.8, key=f"v_{key}")
        text = st.text_area(f"حيثيات {key}", key=f"t_{key}", height=100)
        p_data[key] = {"val": val, "text": text}

st.divider()

if st.button("⚖️ استنطاق الوجود الإبستيمي"):
    # 1. الصاعق الوجودي الأولي (منع العدم الرقمي)
    if any(len(d["text"].strip()) < 40 for d in p_data.values()):
        st.error("❌ رفض: لا يمكن للكيان أن يوجد من كلمات معدودة. (الحد الأدنى 40 حرفاً للركن)")
        st.stop()

    engine = CSLFOntologicalEngineV14_4()
    kll, status, collapsed, issues = engine.evaluate_existence(p_data)
    
    # 2. عرض الحكم الأنطولوجي
    if status == "NULL_STATE":
        st.markdown(f"<div class='status-box null'>💥 NULL_STATE<br><small>انهيار في {collapsed}: الكيان لا يملك مقومات الوجود.</small></div>", unsafe_allow_html=True)
        st.session_state.edi += 1.0
    elif status == "FRAGILE_EXISTENCE":
        st.markdown(f"<div class='status-box fragile'>⚠️ FRAGILE_EXISTENCE<br><small>الكيان موجود ولكن يعاني من تصدعات بنيوية.</small></div>", unsafe_allow_html=True)
        for i in issues: st.warning(i)
        st.session_state.edi += 0.2
    else:
        st.markdown(f"<div class='status-box exists'>✨ EXISTS<br><small>الكيان مستوفٍ لشروط التماسك الوجودي.</small></div>", unsafe_allow_html=True)
        st.balloons()

    # الختم الجنائي (Traceability)
    trace = hashlib.sha256(json.dumps(p_data, sort_keys=True).encode()).hexdigest()
    st.code(f"ONTOLOGICAL_INDEX (KLL): {round(kll, 3)}\nEXISTENCE_VERIFIED: TRUE\nTRACE_ID: {trace}")

st.markdown("---")
st.caption("CSLF v14.4 | The Final Ontological Constitution | No Quality, Just Existence")

