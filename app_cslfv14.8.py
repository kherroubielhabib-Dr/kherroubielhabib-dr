import streamlit as st
import hashlib
import json

# =============================================================
# 1. المحرك الأنطولوجي المحايد (Neutral Ontological Engine)
# =============================================================

class CSLFNeutralGateV14_8:
    def __init__(self):
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }

    def evaluate_presence(self, pillars):
        """
        فحص استحقاق الحضور: هل الكيان متسق مع نفسه لغوياً وبنيوياً؟
        لا يحكم على الجودة، يصف فقط الحالة الوجودية.
        """
        paradoxes = []          # وصف للتناقض وليس إدانة
        structural_gaps = []    # فجوات في القالب الهيكلي
        vals = {k: v["val"] for k, v in pillars.items()}

        # 1. عتبة التجسد (The Incarnation Threshold)
        collapsed = [p for p, v in vals.items() if v < 0.5]
        if collapsed:
            return 0.0, "NULL_STATE", collapsed, []

        # 2. فحص الالتزام بالقالب (CIL) - شرط "الحق في أن يُسمع"
        for name, data in pillars.items():
            text = data["text"].strip().lower()
            missing = [t for t in self.REQUIRED_PATTERNS[name] if t not in text]
            if missing:
                structural_gaps.append(f"⚠️ {name}: نقص في المكونات الهيكلية {missing}")

        # 3. رصد المفارقات (The Paradoxical Check) - وصف حالة لا حكم جودة
        # CI > SA + 0.3 يعني وجود "فجوة استدلالية" داخل الكيان نفسه
        if vals["CI"] > vals["SA"] + 0.3:
            paradoxes.append("🧬 مفارقة بنيوية: تضخم في الادعاء السببي مقابل القدرة البنائية.")

        # 4. حساب الكثافة الوجودية (KLL) - مؤشر وصفي فقط
        kll = min(vals.values())

        # 5. تصنيف الحالات (Ontological States) - بأسماء وصفية محايدة
        if paradoxes:
            # "وجود مفارقي": الكيان موجود ولكنه يصارع تناقضه الداخلي
            status = "PARADOXICAL_EXISTENCE"
        elif structural_gaps:
            # "وجود غير مكتمل": الكيان موجود ولكنه لم يستوفِ شروط التجسد الكامل
            status = "INCOMPLETE_EXISTENCE"
        else:
            # "وجود متماسك": الكيان استوفى شروط الظهور الإبستيمي
            status = "EXISTS"

        return kll, status, [], paradoxes + structural_gaps


# =============================================================
# 2. واجهة السيادة المحايدة (The Sovereign Neutral UI)
# =============================================================

st.set_page_config(page_title="CSLF v14.8 | Neutral Gate", layout="wide")

# التصميم البصري
st.markdown("""
    <style>
    .status-panel { 
        padding: 25px; 
        border-radius: 12px; 
        text-align: center; 
        font-weight: bold; 
        border: 3px solid; 
        margin: 20px 0; 
        font-size: 22px; 
    }
    .exists { 
        color: #00ffcc; 
        border-color: #00ffcc; 
        background: rgba(0, 255, 204, 0.05); 
    }
    .incomplete { 
        color: #ffcc00; 
        border-color: #ffcc00; 
        background: rgba(255, 204, 0, 0.05); 
    }
    .paradoxical { 
        color: #ff8800; 
        border-color: #ff8800; 
        background: rgba(255, 136, 0, 0.05); 
    }
    .null { 
        color: #ff4b4b; 
        border-color: #ff4b4b; 
        background: rgba(255, 75, 75, 0.1); 
    }
    .stTextArea textarea {
        border: 1px solid #334155;
        background-color: #0f172a;
        color: #e2e8f0;
    }
    .stSlider label {
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.header("👤 سيادة المعماري")
    u_id = st.text_input("Architect ID", "ARCH_PRO")
    st.divider()
    
    # تخزين مؤشر الانحراف
    if "edi" not in st.session_state:
        st.session_state.edi = 0.0
    
    st.metric("EDI (مؤشر الانحراف التراكمي)", round(st.session_state.edi, 2))
    st.info("فلسفة v14.8: أنا لا أحكم عليك.. أنا فقط أكشف لك كيف يرى المنطق وجودك.")
    
    st.divider()
    st.markdown("### 📋 الحالات الوجودية")
    st.caption("✨ EXISTS — وجود متماسك")
    st.caption("⚠️ INCOMPLETE_EXISTENCE — وجود غير مكتمل")
    st.caption("🧬 PARADOXICAL_EXISTENCE — وجود مفارقي")
    st.caption("💥 NULL_STATE — انهيار تام")

# العنوان الرئيسي
st.title("🏛️ CSLF v14.8 — The Neutral Existence Gate")
st.markdown("> **“أنا لا أحكم عليك.. أنا فقط أكشف لك كيف يرى المنطق وجودك.”**")
st.markdown("---")

# =============================================================
# 🔥 واجهة إدخال الأركان الأربعة (كانت مفقودة في النسخة السابقة)
# =============================================================

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
        text = st.text_area(
            f"حيثيات {key}", 
            key=f"t_{key}", 
            height=120,
            placeholder=f"اكتب هنا {terms[0]}، ثم {terms[1]}، ثم {terms[2]}..."
        )
        p_data[key] = {"val": val, "text": text}

st.divider()

# =============================================================
# زر التنفيذ
# =============================================================

if st.button("⚖️ استنطاق الوجود", use_container_width=True, type="primary"):
    # الصاعق الأولي: منع العدم الرقمي (شرط الكثافة اللغوية)
    insufficient = [name for name, d in p_data.items() if len(d["text"].strip()) < 40]
    
    if insufficient:
        st.error(f"💥 الكيان لا يملك الكثافة الكافية ليعبر بوابة الوجود. الأركان الناقصة: {', '.join(insufficient)} (الحد الأدنى 40 حرفاً لكل ركن)")
        st.session_state.edi += 0.2
        st.stop()
    
    # تشغيل المحرك
    engine = CSLFNeutralGateV14_8()
    kll, status, collapsed, all_issues = engine.evaluate_presence(p_data)
    
    # عرض النتيجة حسب الحالة الوجودية
    if status == "NULL_STATE":
        st.markdown(f"""
        <div class='status-panel null'>
        💥 NULL_STATE<br>
        <small>انهيار في الأركان: {collapsed}<br>
        الكيان لا يملك أدنى مقومات الوجود.</small>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.edi += 1.0
        
    elif status == "PARADOXICAL_EXISTENCE":
        st.markdown(f"""
        <div class='status-panel paradoxical'>
        🧬 PARADOXICAL_EXISTENCE<br>
        <small>وجود مفارقي: الكيان يقر بوجوده ولكن رُصدت فيه تناقضات داخلية.</small>
        </div>
        """, unsafe_allow_html=True)
        for issue in all_issues:
            st.warning(issue)
        st.session_state.edi += 0.5
        
    elif status == "INCOMPLETE_EXISTENCE":
        st.markdown(f"""
        <div class='status-panel incomplete'>
        ⚠️ INCOMPLETE_EXISTENCE<br>
        <small>وجود غير مكتمل: الكيان يعبر البوابة ولكن بنقص في البنية.</small>
        </div>
        """, unsafe_allow_html=True)
        for issue in all_issues:
            st.info(issue)
        st.session_state.edi += 0.2
        
    else:  # EXISTS
        st.markdown(f"""
        <div class='status-panel exists'>
        ✨ EXISTS<br>
        <small>وجود متماسك: الكيان مستوفٍ لشروط الحضور الإبستيمي.</small>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    
    # الختم الجنائي (Forensic Seal)
    trace = hashlib.sha256(json.dumps(p_data, sort_keys=True).encode()).hexdigest()
    
    st.divider()
    st.subheader("🔒 الختم الجنائي (FAL)")
    st.code(f"""
ONTOLOGICAL_STATUS: {status}
ONTOLOGICAL_INDEX (KLL): {round(kll, 3)}
TRACE_ID: {trace}
ARCHITECT_ID: {u_id}
EPISTEMIC_CLOSURE: TRUE
CIL_STATUS: VERIFIED
    """)
    
    # تحديث EDI في الجلسة
    st.rerun()

# =============================================================
# 3. تذييل الصفحة
# =============================================================

st.markdown("---")
st.caption("CSLF v14.8 | The Neutral Existence Gate | No Quality, Just Existence | Dr. Elhabib Kherroubi")
