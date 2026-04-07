import streamlit as st
import hashlib
import json
import time
import math

# =============================================================
# 1. المحرك السيادي النهائي (The Final Sovereign Engine)
# =============================================================
class CSLFSovereignEngineV14_2:
    def __init__(self, k_min):
        self.K_MIN = k_min
        # قوالب الاستدلال الإجباري (Constraint Injection Layer - CIL)
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }

    def validate_testimony(self, pillars):
        """التحقق متعدد الطبقات: الكثافة، الاتساق، والقيود الهيكلية"""
        issues = []
        
        for name, data in pillars.items():
            text = data["text"].strip().lower()
            val = data["val"]
            
            # 1. اختبار CIL: الالتزام بهيكل الاستدلال
            missing_terms = [term for term in self.REQUIRED_PATTERNS[name] if term not in text]
            if missing_terms:
                issues.append(f"🚫 {name}: غياب العناصر الهيكلية الإلزامية {missing_terms}.")

            # 2. اختبار الكثافة المفاهيمية (Conceptual Density)
            unique_words = len(set(text.split()))
            if val > 0.8 and unique_words < 20:
                issues.append(f"⚠️ {name}: ادعاء جدارة عالية مع فقر مفاهيمي (الكلمات الفريدة: {unique_words}).")

        # 3. اختبار الاتساق المتقاطع (Cross-Pillar Consistency)
        if pillars["CI"]["val"] > pillars["SA"]["val"] + 0.2:
            issues.append("⚡ تناقض سيادي: النزاهة السببية (CI) لا يمكن أن تتجاوز متانة البناء (SA).")
        
        if pillars["EG"]["val"] > 0.8 and pillars["SV"]["val"] < 0.6:
            issues.append("⚡ خلل إبستيمي: ادعاء تجذر صلب (EG) مع عدم انضباط دلالي (SV).")

        return issues

    def execute_judgment(self, pillars, issues):
        """تحديد رتبة الوجود بناءً على قوانين CSLF الصارمة"""
        vals = {k: v["val"] for k, v in pillars.items()}
        
        # قانون الانهيار الصفري (Zero-Collapse Law)
        collapsed = [p for p, v in vals.items() if v < 0.5]
        if collapsed:
            return 0.0, "NULL_STATE", collapsed

        # حساب القيمة الإبستيمية الصغرى (KLL)
        kll = min(vals.values())
        
        if kll < self.K_MIN:
            status = "REJECTED"
        elif issues:
            status = "CONDITIONALLY_ADMISSIBLE"
        else:
            status = "ADMISSIBLE"
            
        return kll, status, []

# =============================================================
# 2. واجهة "المكبس المنطقي" (The Sovereign UI)
# =============================================================
st.set_page_config(page_title="CSLF v14.2 | The Monolith", layout="wide")

# CSS احترافي لتعزيز الهيبة السيادية
st.markdown("""
    <style>
    .stTextArea textarea { border: 2px dashed #334155 !important; background-color: #020617 !important; color: #00ffcc !important; }
    .status-panel { padding: 25px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 20px; border: 2px solid; margin: 20px 0; }
    .constraint-tag { background: #1e293b; color: #94a3b8; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("👤 سيادة المعماري")
    u_id = st.text_input("Architect ID", "ARCH_PRO")
    domain = st.selectbox("النطاق السيادي", ["LEGAL (0.90)", "MEDICAL (0.75)", "STRATEGIC (0.80)"])
    k_threshold = float(domain.split("(")[1].split(")")[0])
    
    if "edi" not in st.session_state: st.session_state.edi = 0.0
    st.metric("EDI (مؤشر الانحراف)", round(st.session_state.edi, 2))
    st.caption(f"معامل الاحتكاك الحالي: {int(math.pow(3, int(st.session_state.edi)))}x")

st.title("🏛️ CSLF v14.2 — The Sovereign Monolith")
st.markdown("> **“حيث ينتهي ضجيج البيانات، ويبدأ صمت الحقيقة الموثقة.”**")

# مصفوفة الأركان الأربعة
p_data = {}
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏗️ الأهلية البنيوية (SA)")
    st.markdown("<span class='constraint-tag'>مقدمة</span> <span class='constraint-tag'>بنية</span> <span class='constraint-tag'>نتيجة</span>", unsafe_allow_html=True)
    v1 = st.slider("قيمة SA", 0.0, 1.0, 0.8, key="s1")
    t1 = st.text_area("حيثيات SA", key="t1", placeholder="اكتب تبرير البناء هنا...")
    p_data["SA"] = {"val": v1, "text": t1}

    st.subheader("🔗 النزاهة السببية (CI)")
    st.markdown("<span class='constraint-tag'>سبب</span> <span class='constraint-tag'>آلية</span> <span class='constraint-tag'>أثر</span>", unsafe_allow_html=True)
    v2 = st.slider("قيمة CI", 0.0, 1.0, 0.8, key="s2")
    t2 = st.text_area("حيثيات CI", key="t2", placeholder="اكتب تبرير السببية هنا...")
    p_data["CI"] = {"val": v2, "text": t2}

with col2:
    st.subheader("📖 الصلاحية الدلالية (SV)")
    st.markdown("<span class='constraint-tag'>تعريف</span> <span class='constraint-tag'>سياق</span> <span class='constraint-tag'>انضباط</span>", unsafe_allow_html=True)
    v3 = st.slider("قيمة SV", 0.0, 1.0, 0.8, key="s3")
    t3 = st.text_area("حيثيات SV", key="t3", placeholder="اكتب تبرير الدلالة هنا...")
    p_data["SV"] = {"val": v3, "text": t3}

    st.subheader("🧪 التجذر المعرفي (EG)")
    st.markdown("<span class='constraint-tag'>دليل</span> <span class='constraint-tag'>مصدر</span> <span class='constraint-tag'>تحقق</span>", unsafe_allow_html=True)
    v4 = st.slider("قيمة EG", 0.0, 1.0, 0.8, key="s4")
    t4 = st.text_area("حيثيات EG", key="t4", placeholder="اكتب تبرير المرجعية هنا...")
    p_data["EG"] = {"val": v4, "text": t4}

st.divider()
decl = st.checkbox("✅ أشهد بمسؤوليتي الإبستيمية أن هذه الحيثيات نهائية ومغلقة سيادياً.")

if st.button("🏛️ استنطاق الوجود السيادي"):
    # --- الصاعق الأول: منع الفراغ الإبستيمي ---
    insufficient = [n for n, d in p_data.items() if len(d["text"].strip()) < 40]
    if insufficient:
        st.error(f"❌ انهيار إبستيمي: الحيثيات في {', '.join(insufficient)} فارغة أو ضئيلة جداً.")
        st.session_state.edi += 0.2
        st.stop()

    engine = CSLFSovereignEngineV14_2(k_threshold)
    issues = engine.validate_testimony(p_data)
    
    # --- الصاعق الثاني: الالتزام الصارم بـ CIL ---
    critical_v = [i for i in issues if "غياب العناصر الهيكلية" in i]
    if critical_v:
        st.error("🚫 رفض هيكلي: الشهادة لا تلتزم بقالب الاستدلال المفروض (CIL).")
        for i in critical_v: st.warning(i)
        st.session_state.edi += 1.0
        st.stop()

    # --- تنفيذ الحكم النهائي ---
    kll, status, collapsed = engine.execute_judgment(p_data, issues)
    trace_hash = hashlib.sha256(json.dumps(p_data, sort_keys=True).encode()).hexdigest()

    # عرض النتائج
    if status == "NULL_STATE":
        st.markdown(f"<div class='status-panel' style='color:red; border-color:red;'>💥 NULL STATE: انهيار في {collapsed}</div>", unsafe_allow_html=True)
        st.session_state.edi += 2.0
    elif status == "REJECTED":
        st.markdown(f"<div class='status-panel' style='color:#ff4b4b; border-color:#ff4b4b;'>❌ REJECTED: $KLL$ ({kll:.3f}) دون العتبة</div>", unsafe_allow_html=True)
        st.session_state.edi += 1.0
    elif status == "CONDITIONALLY_ADMISSIBLE":
        st.markdown(f"<div class='status-panel' style='color:orange; border-color:orange;'>⚠️ CONDITIONALLY ADMISSIBLE</div>", unsafe_allow_html=True)
        for i in issues: st.warning(i)
        st.session_state.edi += 0.5
    else:
        st.markdown(f"<div class='status-panel' style='color:#00ffcc; border-color:#00ffcc;'>✨ ADMISSIBLE: وجود إبستيمي كامل ✨</div>", unsafe_allow_html=True)

    # الختم الجنائي النهائي
    cav_data = {"u_id": u_id, "kll": kll, "status": status, "closure": True, "trace": trace_hash, "ts": time.time()}
    st.subheader("🔒 الختم الإبستيمي المغلق (Final CAV)")
    st.code(f"CAV_SIGNATURE: {hashlib.sha256(str(cav_data).encode()).hexdigest()}\nTRACE_FINGERPRINT: {trace_hash}\nEPISTEMIC_CLOSURE: TRUE\nCIL_STATUS: VERIFIED")

st.markdown("---")
st.caption("CSLF v14.2 | Sovereign Monolith | The End of Reasoning Simulation")
