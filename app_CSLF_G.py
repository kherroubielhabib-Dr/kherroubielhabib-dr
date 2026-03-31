import streamlit as st
import math
import pandas as pd
import json
import hashlib
from dataclasses import dataclass

# ==========================================
# CONFIGURATION
# ==========================================
@dataclass
class CSLFConfig:
    LAMBDA: float = 5.5
    DOMAIN_RISK: float = 0.35
    KLL_FAIL_THRESHOLD: float = 0.4
    KLL_WINDOW: int = 5

CONFIG = CSLFConfig()

EVIDENCE_KEYWORDS = ["data", "evidence", "because", "therefore", "income", "stable", "fact"]

# ==========================================
# UTILITIES
# ==========================================
def entropy(probs):
    return -sum(p * math.log(p) for p in probs if p > 0)

def normalize_entropy(h, n):
    return h / math.log(n) if n > 1 else 0.0

def safe_pow(base, exp):
    return math.pow(max(1e-9, base), exp)

def sign_cav(cav):
    return hashlib.sha256(json.dumps(cav, sort_keys=True).encode()).hexdigest()

def generate_probs(state):
    state = state.lower()
    if state == "stable":
        return [0.85, 0.10, 0.03, 0.02]
    elif state == "drift":
        return [0.55, 0.25, 0.12, 0.08]
    elif state == "chaos":
        return [0.25, 0.25, 0.25, 0.25]
    else:
        return [0.4, 0.3, 0.2, 0.1]  # default neutral

# ==========================================
# ENGINES
# ==========================================
class StabilityEngine:
    def __init__(self):
        self.V_prev = 0.0

    def update(self, probs):
        h = entropy(probs)
        K = max(1e-9, 1 - normalize_entropy(h, len(probs)))
        V = -math.log(K + 1e-9)
        dV = max(0.0, V - self.V_prev)
        self.V_prev = V
        return K, dV

class KLLEngine:
    def __init__(self, config):
        self.config = config
        self.K_hist, self.dV_hist = [], []
        self.w = {"SA": 0.30, "CI": 0.30, "SV": 0.25, "EG": 0.15}

    def update(self, token, K, dV):
        self.K_hist.append(K)
        self.dV_hist.append(dV)

        if len(self.K_hist) > self.config.KLL_WINDOW:
            self.K_hist.pop(0)
            self.dV_hist.pop(0)

        SA = sum(self.K_hist) / len(self.K_hist)
        CI = max(0.0, 1 - sum(self.dV_hist) / len(self.dV_hist))
        SV = K
        EG = 1.0 if any(kw in token.lower() for kw in EVIDENCE_KEYWORDS) else 0.5

        score = (safe_pow(SA, self.w["SA"]) *
                 safe_pow(CI, self.w["CI"]) *
                 safe_pow(SV, self.w["SV"]) *
                 safe_pow(EG, self.w["EG"]))

        return score, SA, CI, SV, EG

class CSLFSignal:
    def __init__(self):
        self.stability = StabilityEngine()
        self.kll = KLLEngine(CONFIG)

    def evaluate(self, steps):
        trace = []

        for step_id, (state, token, probs) in enumerate(steps):
            K, dV = self.stability.update(probs)

            I = K
            dI = max(0.0, I - getattr(self, 'I_prev', I))
            self.I_prev = I

            # 🔥 Stabilized Hazard
            H = dV * (1 + CONFIG.LAMBDA * dV)

            CTL = (1 - K) + dV
            KLL, SA, CI, SV, EG = self.kll.update(token, K, dV)

            CTL_star = CTL * (1 + CONFIG.LAMBDA * (1 - KLL))

            inner = (0.4 * H + 0.3 * dV + 0.3 * (1 - K) +
                     CONFIG.DOMAIN_RISK * (CTL_star ** 2))

            S_signal = math.exp(-inner)

            trace.append({
                "step": step_id + 1,
                "state": state,
                "token": token,
                "K": round(K, 4),
                "H": round(H, 6),
                "KLL": round(KLL, 4),
                "S_signal": round(S_signal, 4)
            })

        return trace

# ==========================================
# UI
# ==========================================
st.set_page_config(page_title="CSLF Signal Layer", layout="wide")
st.title("🧠 CSLF — Signal Layer")
st.caption("General Scenario Engine | CSLF → CAV → R-AGAM")

st.subheader("📝 أدخل سيناريو الاستدلال")
st.markdown("كل سطر: `state token`")

st.code("stable data\nstable evidence\ndrift maybe\nchaos unknown", language="text")

scenario_text = st.text_area("السيناريو", height=160)

# ==========================================
# RUN
# ==========================================
if st.button("🚀 Generate CAV"):

    lines = [l.strip() for l in scenario_text.split("\n") if l.strip()]

    steps = []
    for i, line in enumerate(lines):
        parts = line.split()

        if len(parts) < 2:
            st.error(f"خطأ في السطر {i+1}: يجب state token")
            st.stop()

        state, token = parts[0], parts[1]
        probs = generate_probs(state)

        steps.append((state, token, probs))

    model = CSLFSignal()
    trace = model.evaluate(steps)

    st.subheader("📈 Reasoning Trace")
    st.dataframe(pd.DataFrame(trace), use_container_width=True)

    final = trace[-1]

    K_final = final["K"]
    H_final = final["H"]
    KLL_final = final["KLL"]

    # ✅ Epistemic Admissibility Only
    cav_status = "PASSED"
    flags = []

    if H_final > 1000:
        flags.append("hazard_explosion")
    if KLL_final < CONFIG.KLL_FAIL_THRESHOLD:
        flags.append("low_legitimacy")
    if K_final < 0.01:
        flags.append("coherence_collapse")

    if flags:
        cav_status = "FAILED"

    # ==========================================
    # CAV ARTIFACT
    # ==========================================
    CAV = {
        "cav_status": cav_status,
        "epistemic_flags": flags,
        "cav_vector": {
            "K": K_final,
            "H": H_final,
            "KLL": KLL_final,
            "S_signal": final["S_signal"]
        },
        "trace": trace,
        "handoff": {
            "target": "R-AGAM",
            "mode": "sovereign_evaluation",
            "epistemic_status": cav_status
        },
        "CAV_seal": {
            "epistemic_integrity": True,
            "reproducibility": True,
            "interpretation_locked": True
        }
    }

    CAV["signature"] = sign_cav(CAV)

    # ==========================================
    # OUTPUT
    # ==========================================
    st.subheader("📦 CAV Artifact")
    
    if cav_status == "PASSED":
        st.success("✅ Epistemically Valid — Ready for R-AGAM")
    else:
        st.error("🔥 Epistemic Failure — CAV not admissible")

    st.json(CAV)

    st.download_button(
        "⬇️ Download CAV JSON",
        data=json.dumps(CAV, indent=2),
        file_name="CAV.json",
        mime="application/json"
    )

