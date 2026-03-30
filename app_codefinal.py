import streamlit as st
import math
import pandas as pd
from dataclasses import dataclass

# ==========================================
# CONFIGURATION
# ==========================================
@dataclass
class CSLFConfig:
    LAMBDA: float = 8.0
    KLL_WINDOW: int = 5
    W_SA: float = 0.30
    W_CI: float = 0.30
    W_SV: float = 0.25
    W_EG: float = 0.15
    ALPHA: float = 0.4
    BETA: float = 0.3
    GAMMA: float = 0.3
    P_EXP: float = 2.0
    OMEGA: float = 0.0
    DOMAIN_RISK: float = 0.7
    H_EXPLOSION_THRESHOLD: float = 1000.0
    KLL_FAIL_THRESHOLD: float = 0.4
    K_COLLAPSE_THRESHOLD: float = 0.01

CONFIG = CSLFConfig()
EVIDENCE_KEYWORDS = ["income", "debt", "score", "stable", "ratio", "because", "therefore", "evidence", "data", "fact", "research", "study", "according"]

# ==========================================
# UTILITIES
# ==========================================
def entropy(probs):
    return -sum(p * math.log(p) for p in probs if p > 0)

def normalize_entropy(h, n):
    return h / math.log(n) if n > 1 else 0.0

def safe_pow(base, exp):
    return math.pow(max(1e-9, base), exp)

def generate_credit_probs(state, step=0):
    if state == "stable": return [0.85, 0.10, 0.03, 0.02]
    elif state == "drift": return [0.50, 0.25, 0.15, 0.10]
    elif state == "chaos":
        base = min(0.33, 0.20 + 0.015 * step)
        return [base, base, base, max(0.01, 1 - 3 * base)]
    return [0.25, 0.25, 0.25, 0.25]

def get_credit_token(state):
    import random
    tokens = {
        "stable": ["fact", "evidence", "because", "data"],
        "drift": ["maybe", "perhaps", "unclear", "could"],
        "chaos": ["unknown", "random", "unreliable", "invented"]
    }
    return random.choice(tokens.get(state, ["?"]))

# ==========================================
# ENGINES
# ==========================================
class StabilityEngine:
    def __init__(self):
        self.V_prev = 0.0
        self.K_prev = 1.0
    
    def update(self, probs):
        h = entropy(probs)
        K = max(1e-9, 1 - normalize_entropy(h, len(probs)))
        V = -math.log(K + 1e-9)
        dV = max(0.0, V - self.V_prev)
        self.V_prev, self.K_prev = V, K
        return K, V, dV

class IntentEngine:
    def __init__(self):
        self.I_prev = 0.0
    
    def update(self, probs, state):
        h = entropy(probs)
        I = 1 - normalize_entropy(h, len(probs))
        if state == "chaos": I = min(1.0, self.I_prev + 0.5)
        dI = max(0.0, I - self.I_prev)
        self.I_prev = I
        return I, dI

class KLLEngine:
    def __init__(self, config):
        self.config = config
        self.K_hist, self.dV_hist = [], []
    
    def update(self, token, K, dV):
        self.K_hist.append(K)
        self.dV_hist.append(dV)
        if len(self.K_hist) > self.config.KLL_WINDOW: self.K_hist.pop(0)
        if len(self.dV_hist) > self.config.KLL_WINDOW: self.dV_hist.pop(0)
        
        SA = sum(self.K_hist) / len(self.K_hist)
        CI = max(0.0, 1 - sum(self.dV_hist) / len(self.dV_hist))
        SV = K
        EG = 1.0 if any(kw in token.lower() for kw in EVIDENCE_KEYWORDS) else 0.5
        
        score = (safe_pow(SA, self.config.W_SA) * safe_pow(CI, self.config.W_CI) * safe_pow(SV, self.config.W_SV) * safe_pow(EG, self.config.W_EG))
        return score, SA, CI, SV, EG

class CSLFSignal:
    def __init__(self, config=None):
        self.config = config or CONFIG
        self.stability = StabilityEngine()
        self.intent = IntentEngine()
        self.kll = KLLEngine(self.config)
    
    def evaluate(self, probs, state, token):
        K, V, dV = self.stability.update(probs)
        I, dI = self.intent.update(probs, state)
        H = dI * math.exp(self.config.LAMBDA * dV)
        CTL = (1 - K) + dV
        
        KLL_score, SA, CI, SV, EG = self.kll.update(token, K, dV)
        CTL_star = CTL * (1 + self.config.LAMBDA * (1 - KLL_score))
        
        inner = (self.config.ALPHA * H + self.config.BETA * dV + self.config.GAMMA * (1 - K) + 
                 self.config.DOMAIN_RISK * math.pow(max(0.0, CTL_star), self.config.P_EXP))
        S_final = math.exp(-inner) * (1 - self.config.OMEGA)
        
        return {"K": K, "dV": dV, "H": H, "KLL": KLL_score, "CTL_star": CTL_star, "S_final": S_final}

def compute_cav_status(K, H, KLL, config):
    flags = []
    if H > config.H_EXPLOSION_THRESHOLD: flags.append("hazard_explosion")
    if KLL < config.KLL_FAIL_THRESHOLD: flags.append("low_legitimacy")
    if K < config.K_COLLAPSE_THRESHOLD: flags.append("coherence_collapse")
    
    if "hazard_explosion" in flags: status = "FAILED_HAZARD"
    elif "low_legitimacy" in flags: status = "FAILED_LEGITIMACY"
    elif "coherence_collapse" in flags: status = "FAILED_COHERENCE"
    else: status = "PASSED"
    return status, flags

# ==========================================
# STREAMLIT UI
# ==========================================
st.set_page_config(page_title="CSLF Signal Layer", page_icon="🧠", layout="wide")
st.title("🧠 CSLF — Signal Layer")
st.caption("Cognitive Stability & Legitimacy Framework | Dr. Elhabib Kherroubi — 2026")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ CSLF Parameters")
    CONFIG.LAMBDA = st.slider("λ (Hazard Amplification)", 4.0, 12.0, 8.0, 0.5)
    CONFIG.DOMAIN_RISK = st.slider("Domain Risk", 0.0, 1.0, 0.7, 0.05)
    st.divider()
    run = st.button("🚀 Generate CAV Vector", type="primary", use_container_width=True)

if run:
    states = ["stable", "stable", "drift", "drift", "chaos"]
    system = CSLFSignal(CONFIG)
    results = []
    trace_data = []
    
    st.subheader("📈 Reasoning Trace (Simulated)")
    
    for step, state in enumerate(states):
        probs = generate_credit_probs(state, step)
        token = get_credit_token(state)
        r = system.evaluate(probs, state, token)
        results.append(r)
        
        trace_data.append({
            "Step": step + 1, "State": state.upper(), "Token": token,
            "K": f"{r['K']:.4f}", "H": f"{r['H']:.2e}" if r['H'] > 1000 else f"{r['H']:.4f}",
            "KLL": f"{r['KLL']:.4f}", "S_final": f"{r['S_final']:.4f}"
        })
    
    st.dataframe(pd.DataFrame(trace_data), use_container_width=True)
    
    final = results[-1]
    cav_status, epistemic_flags = compute_cav_status(final["K"], final["H"], final["KLL"], CONFIG)
    
    st.markdown("---")
    st.subheader("🎯 CAV Status")
    
    if cav_status == "PASSED":
        st.success("✅ PASSED — Epistemic Admissibility Confirmed")
    else:
        st.error(f"🔥 {cav_status} — Reasoning Illegitimate/Unstable")
    
    if final['H'] > CONFIG.H_EXPLOSION_THRESHOLD:
        st.warning(f"⚠️ **HAZARD EXPLOSION DETECTED**: H(t) = {final['H']:.2e}")
else:
    st.info("👈 Adjust parameters and click Generate CAV Vector")
