"""
================================================================================
CSLF — Signal Layer (Cognitive Admissibility Vector)
Cognitive Stability & Legitimacy Framework
================================================================================
Author      : Dr. Elhabib Kherroubi
Year        : 2026
Version     : 1.0 — Sovereign Signal Layer
Status      : Research-Grade Prototype | Integration-Ready

================================================================================
ARCHITECTURE
================================================================================
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CSLF — SIGNAL LAYER                                 │
│                    (Epistemic Engine — CAV Generator)                       │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Stability  │    │   Intent    │    │    KLL     │    │    KSL     │  │
│  │   Engine    │───▶│   Engine    │───▶│   Engine   │───▶│ Functional │  │
│  │ (Lyapunov)  │    │ (IAFS)      │    │ (Legitimacy)│    │ (S_final)  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                  │          │
│         └──────────────────┴──────────────────┴──────────────────┘          │
│                                    │                                        │
│                                    ▼                                        │
│                         ┌─────────────────────┐                            │
│                         │     CAV VECTOR      │                            │
│                         │ [K, H, KLL, CTL*,   │                            │
│                         │  S_final, Status,   │                            │
│                         │  Epistemic Flags]   │                            │
│                         └─────────────────────┘                            │
│                                    │                                        │
│                                    ▼                                        │
│                      ┌─────────────────────────────────┐                   │
│                      │   R-AGAM (Sovereign Resolution) │                   │
│                      │   Authority + Policy + Context  │                   │
│                      └─────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
CORE PRINCIPLES
================================================================================
1. Correctness does not imply admissibility.
2. Only stable and legitimate reasoning paths produce admissible signals.
3. CSLF determines if a decision deserves to exist (Epistemic Truth).
4. R-AGAM determines if it is allowed to act (Authority Truth).

================================================================================
MATHEMATICAL FOUNDATION
================================================================================
K(t)   = 1 - H_norm(p(t))                    Cognitive Coherence
V(t)   = -log(K(t))                          Lyapunov Instability Energy
dV(t)  = max(0, V(t) - V(t-1))               Instability Growth Rate
I(t)   = 1 - H_norm(p(t))                    Intent Commitment
dI(t)  = max(0, I(t) - I(t-1))               Intent Acceleration
H(t)   = dI(t) * exp(λ * dV(t))              Unified Hazard Index
KLL(t) = SA^w1 * CI^w2 * SV^w3 * EG^w4       Epistemic Legitimacy
CTL*   = CTL * (1 + λ * (1 - KLL))           Adjusted Causal Tension
S_final= exp(-[αH + βdV + γ(1-K) + Rd*(CTL*)^p]) * (1-Ω)   KSL Functional

================================================================================
THEOREMS
================================================================================
Theorem 1 (Cognitive Collapse):      lim K(t)→0  ⇒  V(t)→∞
Theorem 2 (Instability Explosion):   dV>0 ∧ dI>0 ⇒  H(t) grows exponentially
Theorem 3 (Legitimacy Collapse):     lim K(t)→0  ⇒  KLL(t)→0
Theorem 4 (Epistemic Failure):       H>H_threshold ∨ KLL<KLL_min ∨ K<K_collapse
                                     ⇒ CAV Status = FAILED_*

================================================================================
INTEGRATION PROTOCOL
================================================================================
CSLF outputs JSON structure:
{
    "cav_vector": {...},
    "cav_status": "PASSED" | "FAILED_HAZARD" | "FAILED_LEGITIMACY" | "FAILED_COHERENCE",
    "epistemic_flags": [...],
    "trace": [...],
    "context": {...}
}

R-AGAM consumes this JSON and resolves:
- Authority Lineage
- Policy Constraints
- Context
- Jurisdiction
================================================================================
"""

import streamlit as st
import math
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum


# =================================================================================
# CONFIGURATION
# =================================================================================

@dataclass
class CSLFConfig:
    """CSLF Configuration Parameters — All tunable for domain adaptation."""
    
    # Core parameters
    LAMBDA: float = 8.0                      # Hazard amplification factor
    KLL_WINDOW: int = 5                      # History window for KLL
    
    # KLL weights (multiplicative — intersectional system)
    W_SA: float = 0.30                       # Source Anchoring weight
    W_CI: float = 0.30                       # Causal Integrity weight
    W_SV: float = 0.25                       # Semantic Validity weight
    W_EG: float = 0.15                       # Evidence Grounding weight
    
    # KSL Functional parameters
    ALPHA: float = 0.4                       # Hazard weight
    BETA: float = 0.3                        # Drift weight
    GAMMA: float = 0.3                       # Coherence weight
    P_EXP: float = 2.0                       # CTL* non-linearity
    OMEGA: float = 0.0                       # External override (0 = inactive)
    
    # Domain risk factors
    DOMAIN_RISK: float = 0.7                 # Financial domain default
    
    # CAV thresholds
    H_EXPLOSION_THRESHOLD: float = 1000.0     # Hazard explosion detection
    KLL_FAIL_THRESHOLD: float = 0.4           # Minimum legitimacy score
    K_COLLAPSE_THRESHOLD: float = 0.01        # Coherence collapse threshold


# Default configuration
CONFIG = CSLFConfig()


# Evidence keywords for EG proxy (form-based — known limitation)
EVIDENCE_KEYWORDS = [
    "income", "debt", "score", "stable", "ratio",
    "because", "therefore", "evidence", "data",
    "fact", "research", "study", "according"
]


# =================================================================================
# UTILITIES
# =================================================================================

def entropy(probs: List[float]) -> float:
    """Shannon entropy H(p) = -Σ(p_i * log(p_i))."""
    return -sum(p * math.log(p) for p in probs if p > 0)


def normalize_entropy(h: float, n: int) -> float:
    """Normalized entropy H_norm = H(p) / log(n)."""
    return h / math.log(n) if n > 1 else 0.0


def safe_pow(base: float, exp: float) -> float:
    """Safe power function with floor to avoid 0^0 issues."""
    return math.pow(max(1e-9, base), exp)


# =================================================================================
# CREDIT DECISION SIMULATION
# =================================================================================

def generate_credit_probs(state: str, step: int = 0) -> List[float]:
    """
    Simulate probability distributions over reasoning tokens.
    
    stable : dominant probability → high coherence
    drift  : spreading → decreasing coherence
    chaos  : near-uniform → coherence collapse
    """
    if state == "stable":
        return [0.85, 0.10, 0.03, 0.02]
    elif state == "drift":
        return [0.50, 0.25, 0.15, 0.10]
    elif state == "chaos":
        base = min(0.33, 0.20 + 0.015 * step)
        return [base, base, base, max(0.01, 1 - 3 * base)]
    return [0.25, 0.25, 0.25, 0.25]


def get_credit_token(state: str) -> str:
    """Generate token based on reasoning state."""
    import random
    tokens = {
        "stable": ["fact", "evidence", "because", "data", "research"],
        "drift": ["maybe", "perhaps", "unclear", "could", "might"],
        "chaos": ["unknown", "random", "unreliable", "invented", "undefined"]
    }
    return random.choice(tokens.get(state, ["?"]))


# =================================================================================
# STABILITY ENGINE — Lyapunov Dynamics
# =================================================================================

class StabilityEngine:
    """
    Tracks cognitive coherence K(t) and Lyapunov instability energy V(t).
    
    K(t) = 1 - H_norm(p(t))  ∈ (0, 1]
    V(t) = -log(K(t))        ≥ 0
    dV(t) = max(0, V(t) - V(t-1))  ≥ 0
    
    Theorem 1: lim K(t)→0 ⇒ V(t)→∞ (cognitive collapse)
    """
    
    def __init__(self):
        self.V_prev: float = 0.0
        self.K_prev: float = 1.0
    
    def update(self, probs: List[float]) -> Tuple[float, float, float]:
        """Compute K(t), V(t), dV(t) from current probability distribution."""
        h = entropy(probs)
        K = max(1e-9, 1 - normalize_entropy(h, len(probs)))
        V = -math.log(K + 1e-9)
        dV = max(0.0, V - self.V_prev)
        self.V_prev = V
        self.K_prev = K
        return K, V, dV


# =================================================================================
# INTENT ENGINE — Commitment Dynamics
# =================================================================================

class IntentEngine:
    """
    Tracks intent commitment I(t) and acceleration dI(t).
    
    I(t) = 1 - H_norm(p(t))  ∈ [0, 1]
    dI(t) = max(0, I(t) - I(t-1))
    
    In chaos state: intent accelerates (AI commits to hallucinated path).
    """
    
    def __init__(self):
        self.I_prev: float = 0.0
    
    def update(self, probs: List[float], state: str) -> Tuple[float, float]:
        """Compute I(t), dI(t) from current probability distribution."""
        h = entropy(probs)
        I = 1 - normalize_entropy(h, len(probs))
        
        # Intent acceleration under cognitive pressure
        if state == "chaos":
            I = min(1.0, self.I_prev + 0.5)
        
        dI = max(0.0, I - self.I_prev)
        self.I_prev = I
        return I, dI


# =================================================================================
# KLL ENGINE — Knowledge-Linked Legitimacy (Epistemic Admissibility)
# =================================================================================

class KLLEngine:
    """
    Evaluates epistemic admissibility of the reasoning trajectory.
    
    KLL(t) = SA^w_SA × CI^w_CI × SV^w_SV × EG^w_EG
    
    Multiplicative = Intersectional System:
    - Each dimension is a partial existence condition
    - Any collapse → full KLL collapse
    - Prevents "hallucination via eloquence"
    
    SA : Source Anchoring — coherence stability over time window
    CI : Causal Integrity — sustained low drift
    SV : Semantic Validity — current coherence K(t)
    EG : Evidence Grounding — epistemic marker proxy (form-based, known limitation)
    
    Theorem 3: lim K(t)→0 ⇒ KLL(t)→0
    """
    
    def __init__(self, config: CSLFConfig):
        self.config = config
        self.K_hist: List[float] = []
        self.dV_hist: List[float] = []
    
    def update(self, token: str, K: float, dV: float) -> Tuple[float, float, float, float, float]:
        """Compute KLL score and its four dimensions."""
        self.K_hist.append(K)
        self.dV_hist.append(dV)
        
        # Maintain rolling window
        if len(self.K_hist) > self.config.KLL_WINDOW:
            self.K_hist.pop(0)
        if len(self.dV_hist) > self.config.KLL_WINDOW:
            self.dV_hist.pop(0)
        
        # Compute dimensions
        SA = sum(self.K_hist) / len(self.K_hist)
        CI = max(0.0, 1 - sum(self.dV_hist) / len(self.dV_hist))
        SV = K
        EG = 1.0 if any(kw in token.lower() for kw in EVIDENCE_KEYWORDS) else 0.5
        
        # Weighted multiplicative aggregation
        score = (safe_pow(SA, self.config.W_SA) *
                 safe_pow(CI, self.config.W_CI) *
                 safe_pow(SV, self.config.W_SV) *
                 safe_pow(EG, self.config.W_EG))
        
        return score, SA, CI, SV, EG


# =================================================================================
# FUSION FUNCTIONS
# =================================================================================

def compute_hazard(dI: float, dV: float, config: CSLFConfig) -> float:
    """Unified Hazard Index H(t) = dI(t) × exp(λ × dV(t))."""
    return dI * math.exp(config.LAMBDA * dV)


def compute_ctl(K: float, dV: float) -> float:
    """Causal Tension Level CTL(t) = (1 - K) + dV."""
    return (1 - K) + dV


def compute_ctl_adjusted(CTL: float, KLL: float, config: CSLFConfig) -> float:
    """Adjusted Causal Tension CTL*(t) = CTL × (1 + λ × (1 - KLL))."""
    return CTL * (1 + config.LAMBDA * (1 - KLL))


def compute_ksl(H: float, dV: float, K: float, CTL_star: float,
                config: CSLFConfig) -> float:
    """
    Kherroubi Stability-Legitimacy Functional (KSL).
    
    S_final = exp(-[α·H + β·dV + γ·(1-K) + Rd·(CTL*)^p]) × (1-Ω)
    
    Fuses: Structure (H, dV, K) + Behavior (Rd, CTL*) + Epistemology (via CTL*)
    """
    inner = (config.ALPHA * H +
             config.BETA * dV +
             config.GAMMA * (1 - K) +
             config.DOMAIN_RISK * math.pow(max(0.0, CTL_star), config.P_EXP))
    
    return math.exp(-inner) * (1 - config.OMEGA)


# =================================================================================
# CAV STATUS COMPUTATION — Sovereign-Grade Classification
# =================================================================================

def compute_cav_status(K: float, H: float, KLL: float, 
                       config: CSLFConfig) -> Tuple[str, List[str]]:
    """
    Compute CAV Status with sovereign-grade failure classification.
    
    Returns:
        status: "PASSED" | "FAILED_HAZARD" | "FAILED_LEGITIMACY" | "FAILED_COHERENCE"
        flags: List of epistemic flags for granular analysis
    """
    flags = []
    
    # Detect failure conditions
    if H > config.H_EXPLOSION_THRESHOLD:
        flags.append("hazard_explosion")
    if KLL < config.KLL_FAIL_THRESHOLD:
        flags.append("low_legitimacy")
    if K < config.K_COLLAPSE_THRESHOLD:
        flags.append("coherence_collapse")
    
    # Sovereign-grade classification (ordered by severity)
    if "hazard_explosion" in flags:
        status = "FAILED_HAZARD"
    elif "low_legitimacy" in flags:
        status = "FAILED_LEGITIMACY"
    elif "coherence_collapse" in flags:
        status = "FAILED_COHERENCE"
    else:
        status = "PASSED"
    
    return status, flags


# =================================================================================
# CSLF SIGNAL LAYER — Core Class
# =================================================================================

class CSLFSignal:
    """
    CSLF as Signal Layer — produces CAV Vector + CAV Status.
    
    No final decision. Output is designed for consumption by:
    - R-AGAM (Sovereign Resolution Layer)
    - Any sovereign governance system
    
    Core Principle:
    - CSLF determines if a decision deserves to exist (Epistemic Truth)
    - R-AGAM determines if it is allowed to act (Authority Truth)
    """
    
    def __init__(self, config: CSLFConfig = None):
        self.config = config or CONFIG
        self.stability = StabilityEngine()
        self.intent = IntentEngine()
        self.kll = KLLEngine(self.config)
    
    def evaluate(self, probs: List[float], state: str, token: str) -> Dict:
        """
        Evaluate reasoning step and return CAV vector components.
        
        Args:
            probs: Probability distribution over reasoning tokens
            state: Reasoning state ("stable", "drift", "chaos")
            token: Current token (for EG evaluation)
        
        Returns:
            Dictionary containing all CAV vector components
        """
        # Layer 1: Stability (Lyapunov dynamics)
        K, V, dV = self.stability.update(probs)
        
        # Layer 2: Intent (Commitment dynamics)
        I, dI = self.intent.update(probs, state)
        
        # Layer 3: Hazard fusion
        H = compute_hazard(dI, dV, self.config)
        CTL = compute_ctl(K, dV)
        
        # Layer 4: Legitimacy (Epistemic admissibility)
        KLL_score, SA, CI, SV, EG = self.kll.update(token, K, dV)
        CTL_star = compute_ctl_adjusted(CTL, KLL_score, self.config)
        
        # Layer 5: KSL Functional (Unified stability-legitimacy)
        S_final = compute_ksl(H, dV, K, CTL_star, self.config)
        
        return {
            # CAV Vector core
            "K": K,
            "dV": dV,
            "H": H,
            "KLL": KLL_score,
            "CTL_star": CTL_star,
            "S_final": S_final,
            # Supporting metrics
            "I": I,
            "dI": dI,
            "SA": SA,
            "CI": CI,
            "SV": SV,
            "EG": EG
        }


# =================================================================================
# STREAMLIT UI — Interactive Dashboard
# =================================================================================

# Page configuration
st.set_page_config(
    page_title="CSLF Signal Layer",
    page_icon="🧠",
    layout="wide"
)

# Title and description
st.title("🧠 CSLF — Signal Layer")
st.caption("Cognitive Stability & Legitimacy Framework | Dr. Elhabib Kherroubi — 2026")
st.markdown("---")

# Architecture diagram
with st.expander("📐 Architecture Overview", expanded=False):
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                         CSLF — SIGNAL LAYER                                 │
    │                    (Epistemic Engine — CAV Generator)                       │
    │                                                                             │
    │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
    │  │  Stability  │    │   Intent    │    │    KLL     │    │    KSL     │  │
    │  │   Engine    │───▶│   Engine    │───▶│   Engine   │───▶│ Functional │  │
    │  │ (Lyapunov)  │    │ (IAFS)      │    │ (Legitimacy)│    │ (S_final)  │  │
    │  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
    │         │                  │                  │                  │          │
    │         └──────────────────┴──────────────────┴──────────────────┘          │
    │                                    │                                        │
    │                                    ▼                                        │
    │                         ┌─────────────────────┐                            │
    │                         │     CAV VECTOR      │                            │
    │      
