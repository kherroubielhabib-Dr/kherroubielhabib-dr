import streamlit as st
import hashlib
import time
import math

# =============================================================
# INITIALIZATION (FIX CRITICAL)
# =============================================================

st.set_page_config(page_title="CSLF v13.2 Sovereign Core", layout="wide")

# FIX: تهيئة session_state بشكل صحيح
if "edi_store" not in st.session_state:
    st.session_state["edi_store"] = {}

# =============================================================
# CORE ENGINE
# =============================================================

class CSLF_v13_2_Engine:
    def __init__(self):
        self.K_MIN = 0.7
        self.H_MAX = 0.4

    def compute_metrics(self, trace):
        scores = [s['confidence'] for s in trace]
        kll = min(scores) if scores else 0
        hazard = 1 - (sum(scores) / len(scores)) if scores else 1
        return kll, hazard

    def check_integrity(self, trace):
        gaps = []
        valid_relations = ["CAUSES", "SUPPORTS", "JUSTIFIES", "DERIVED_FROM"]

        for i in range(len(trace) - 1):
            a, b = trace[i], trace[i+1]

            if b.get("predecessor_id") != a.get("id"):
                gaps.append(f"Structural_Gap_{i+1}")

            if b.get("relation").upper() not in valid_relations:
                gaps.append(f"Semantic_Violation_{i+1}")

        return gaps

    def get_friction(self, user_id):
        edi = st.session_state["edi_store"].get(user_id, 0)
        return math.pow(3, int(edi))


# =============================================================
# UI
# =============================================================

st.title("🏛️ CSLF v13.2: Epistemic Operating System")
st.markdown("نظام إبستيمي مغلق — يحدد فقط ما إذا كان القرار يستحق الوجود")
st.markdown("---")

engine = CSLF_v13_2_Engine()

# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:
    st.header("👤 الهوية الإبستيمية")

    user_id = st.text_input("User ID", value="ARCHITECT_01")

    current_edi = st.session_state["edi_store"].get(user_id, 0)
    st.metric("EDI (Deviation Index)", round(current_edi, 2))

    friction = engine.get_friction(user_id)
    st.warning(f"Friction: {int(friction)}x")


# =============================================================
# MAIN INPUT
# =============================================================

st.header("⚡ محاكاة المسار الاستدلالي")

col1, col2 = st.columns([2, 1])

with col1:
    num_steps = st.number_input("عدد الخطوات", min_value=1, max_value=5, value=3)

    trace = []

    for i in range(num_steps):
        with st.expander(f"Step {i+1}", expanded=True):
            c1, c2, c3 = st.columns([3, 2, 2])

            with c1:
                content = st.text_input(f"Content {i+1}", key=f"c_{i}")

            with c2:
                conf = st.slider(f"Confidence", 0.0, 1.0, 0.5, key=f"s_{i}")

            with c3:
                rel = st.selectbox(
                    "Relation",
                    ["CAUSES", "SUPPORTS", "JUSTIFIES", "DERIVED_FROM", "NONE"],
                    key=f"r_{i}"
                )

            trace.append({
                "id": i + 1,
                "content": content,
                "confidence": conf,
                "relation": rel,
                "predecessor_id": i if i > 0 else None
            })


with col2:
    st.subheader("⚙️ التحكم")

    intent = st.selectbox(
        "Intent",
        ["NORMAL", "EMERGENCY_PROTECTION", "SPECULATION", "STRATEGIC_DIVERGENCE"]
    )

    override = st.checkbox("Sovereign Override")

    if st.button("تشغيل المحرك 🚀"):

        # =============================================================
        # META LAW
        # =============================================================
        if any(s['confidence'] > 1.0 for s in trace):
            st.error("❌ VETO: Meta-Law Violation")
            st.stop()

        # =============================================================
        # COMPUTE
        # =============================================================
        kll, hazard = engine.compute_metrics(trace)
        gaps = engine.check_integrity(trace)

        admissible = kll >= engine.K_MIN and hazard <= engine.H_MAX

        # =============================================================
        # OUTPUT
        # =============================================================
        st.markdown("## 📊 النتائج")

        if admissible:
            status = "ADMISSIBLE"
            st.success("✅ CAV PRODUCED — القرار مؤهل للوجود")

        elif override:
            status = "OVERRIDDEN"
            st.warning("⚠️ تم التجاوز السيادي")

            st.session_state["edi_store"][user_id] = current_edi + 1 + (len(gaps) * 0.5)

        else:
            status = "REJECTED"
            st.error("❌ المسار مرفوض")

            st.session_state["edi_store"][user_id] = current_edi + (len(gaps) * 0.5)

        # =============================================================
        # METRICS
        # =============================================================
        m1, m2 = st.columns(2)
        m1.metric("KLL", round(kll, 3))
        m2.metric("Hazard", round(hazard, 3))

        if gaps:
            st.write("🔍 Gaps:", gaps)

        # =============================================================
        # FORENSIC SEAL
        # =============================================================
        st.markdown("---")
        st.subheader("🔒 Forensic Seal")

        payload = f"{user_id}|{kll}|{status}|{time.time()}"
        seal = hashlib.sha256(payload.encode()).hexdigest()

        st.code(f"Signature: {seal}\nStatus: {status}")


# =============================================================
# FOOTER
# =============================================================

st.markdown("---")
st.caption("CSLF v13.2 | Epistemic Closure Engine | 2026")
