import streamlit as st
import hashlib
import json
import math
import time

# =============================================================
# 1. CSLF v15 — Sovereign Hybrid Engine
# =============================================================

class CSLFConsciousGateV15:

    def __init__(self):
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }

        self.NEGATION_MARKERS = ["لا", "ليس", "غير", "بدون", "يفتقر", "عدم", "لا يوجد", "خالي من"]
        self.CONFIRMATION_MARKERS = ["تم", "يوجد", "توجد", "توفير", "تضمين"]

        # وزن الشرعية
        self.W = 1.0

    # =============================================================
    # 2. Smart Negation
    # =============================================================
    def _smart_negation_check(self, text, required_terms):
        text_lower = text.lower()
        negated = []

        for term in required_terms:
            if term in text_lower:
                idx = text_lower.find(term)
                context = text_lower[max(0, idx-30):idx]

                has_neg = any(n in context for n in self.NEGATION_MARKERS)
                has_conf = any(c in context for c in self.CONFIRMATION_MARKERS)

                if has_neg and not has_conf:
                    negated.append(term)

        return negated

    # =============================================================
    # 3. KLL — Hybrid Multiplicative Law
    # =============================================================
    def compute_kll(self, vals, negations):
        product = 1.0

        for v in vals.values():
            product *= max(v, 0.0001)  # منع الصفر المطلق

        kll = product ** self.W

        # عقوبة النفي (Multiplicative damping)
        if negations:
            kll *= 0.6

        return round(kll, 4)

    # =============================================================
    # 4. Stability Model (Lyapunov-inspired)
    # =============================================================
    def compute_stability(self, vals):
        mean = sum(vals.values()) / 4
        variance = sum((v - mean) ** 2 for v in vals.values()) / 4

        H = round(variance, 4)  # hazard
        K = round(mean, 4)      # coherence

        return K, H

    # =============================================================
    # 5. Evaluation Core
    # =============================================================
    def evaluate_presence(self, pillars):

        paradoxes, gaps, negations, val_paradoxes = [], [], [], []
        vals = {k: v["val"] for k, v in pillars.items()}

        # =============================================================
        # Collapse Condition
        # =============================================================
        collapsed = [p for p, v in vals.items() if v < 0.3]
        if collapsed:
            return self._finalize(0.0, "NULL_STATE", collapsed, [], [], [], vals)

        # =============================================================
        # Structural + Semantic Checks
        # =============================================================
        for name, data in pillars.items():
            txt = data["text"].strip()
            val = data["val"]

            # نقص
            missing = [t for t in self.REQUIRED_PATTERNS[name] if t not in txt]
            if missing:
                gaps.append(f"{name}: نقص {missing}")

            # نفي
            negated_terms = self._smart_negation_check(txt, self.REQUIRED_PATTERNS[name])
            if negated_terms:
                negations.append(f"{name}: نفي {negated_terms}")

            # تناقض القيمة
            if val > 0.8 and len(txt) < 60:
                val_paradoxes.append(f"{name}: ادعاء قوي مع نص ضعيف")

        # =============================================================
        # Stability
        # =============================================================
        K, H = self.compute_stability(vals)

        if H > 0.08:
            paradoxes.append("Instability Hazard مرتفع")

        # =============================================================
        # KLL الحقيقي
        # =============================================================
        kll = self.compute_kll(vals, negations)

        # =============================================================
        # Status Logic
        # =============================================================
        if negations:
            status = "NEGATED_EXISTENCE"
        elif kll < 0.2:
            status = "NULL_STATE"
        elif paradoxes or val_paradoxes:
            status = "PARADOXICAL_EXISTENCE"
        elif gaps:
            status = "INCOMPLETE_EXISTENCE"
        else:
            status = "EXISTS"

        return self._finalize(kll, status, collapsed, paradoxes + gaps, negations, val_paradoxes, vals, K, H)

    # =============================================================
    # 6. Forensic Seal (CAV)
    # =============================================================
    def _finalize(self, kll, status, collapsed, issues, negations, val_paradoxes, vals, K=0, H=0):

        timestamp = time.time()

        payload = {
            "KLL": kll,
            "STATUS": status,
            "VALUES": vals,
            "K": K,
            "H": H,
            "TIME": timestamp
        }

        raw = json.dumps(payload, sort_keys=True)
        trace = hashlib.sha256(raw.encode()).hexdigest()

        payload["TRACE_ID"] = trace

        return kll, status, collapsed, issues, negations, val_paradoxes, payload


# =============================================================
# 7. Streamlit UI
# =============================================================

st.set_page_config(page_title="CSLF v15 — Sovereign Gate", layout="wide")

st.title("🏛️ CSLF v15 — Sovereign Epistemic Gate")
st.markdown("**هل يستحق هذا الاستدلال أن يوجد؟**")

engine = CSLFConsciousGateV15()

p_data = {}
cols = st.columns(2)

fields = [
    ("SA", "🏗️ البناء"),
    ("CI", "🔗 السببية"),
    ("SV", "📖 الدلالة"),
    ("EG", "🧪 الأدلة")
]

for i, (key, label) in enumerate(fields):
    with cols[i % 2]:
        v = st.slider(f"{label} — {key}", 0.0, 1.0, 0.8, key=f"v_{key}")
        t = st.text_area(f"نص {key}", height=120, key=f"t_{key}")

        p_data[key] = {"val": v, "text": t}

# =============================================================
# Run
# =============================================================
if st.button("⚖️ تقييم الوجود السيادي", use_container_width=True):

    if any(len(d["text"].strip()) < 40 for d in p_data.values()):
        st.error("❌ النص غير كافٍ للعبور")
    else:
        kll, status, collapsed, issues, negs, val_par, cav = engine.evaluate_presence(p_data)

        st.success(f"الحالة: {status}")
        st.metric("KLL", kll)

        if issues:
            for i in issues:
                st.warning(i)

        if negs:
            for n in negs:
                st.error(n)

        if val_par:
            for v in val_par:
                st.warning(v)

        st.subheader("🔐 CAV — الأثر المعرفي المختوم")
        st.code(json.dumps(cav, indent=2), language="json")

