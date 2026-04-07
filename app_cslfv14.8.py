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
        """فحص استحقاق الحضور: هل الكيان متسق مع نفسه لغوياً وبنيوياً؟"""
        paradoxes = [] # وصف للتناقض وليس إدانة بالفساد
        structural_gaps = [] # فجوات في القالب الهيكلي
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

        # 4. حساب الكثافة الوجودية (KLL)
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
st.markdown("> **“أنا لا أحكم عليك.. أنا فقط أكشف لك كيف يرى المنطق وجودك.”**")

# [واجهة الإدخال للأركان الأربعة]

if st.button("⚖️ استنطاق الوجود"):
    # الصاعق الأولي (شرط الاتفاق مع محمد: الكثافة اللغوية)
    if any(len(d["text"].strip()) < 40 for d in p_data.values()):
        st.error("💥 الكيان لا يملك الكثافة الكافية ليعبر بوابة الوجود.")
        st.stop()

    engine = CSLFNeutralGateV14_8()
    kll, status, collapsed, all_issues = engine.evaluate_presence(p_data)
    
    if status == "NULL_STATE":
        st.markdown(f"<div class='status-panel null'>💥 NULL_STATE<br><small>انهيار في {collapsed}</small></div>", unsafe_allow_html=True)
    elif status == "PARADOXICAL_EXISTENCE":
        st.markdown(f"<div class='status-panel paradoxical'>🧬 PARADOXICAL_EXISTENCE<br><small>وجود مفارقي: الكيان يقر بوجوده ولكن رُصدت فيه تناقضات داخلية.</small></div>", unsafe_allow_html=True)
        for i in all_issues: st.warning(i)
    elif status == "INCOMPLETE_EXISTENCE":
        st.markdown(f"<div class='status-panel incomplete'>⚠️ INCOMPLETE_EXISTENCE<br><small>وجود غير مكتمل: الكيان يعبر البوابة ولكن بنقص في البنية.</small></div>", unsafe_allow_html=True)
        for i in all_issues: st.info(i)
    else:
        st.markdown(f"<div class='status-panel exists'>✨ EXISTS<br><small>وجود متماسك: الكيان مستوفٍ لشروط الحضور الإبستيمي.</small></div>", unsafe_allow_html=True)

    st.code(f"STATUS: {status} | ONTOLOGICAL_INDEX: {round(kll, 3)}")

