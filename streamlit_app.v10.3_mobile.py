# =====================================================
# CDEWS-IAFS v10.3 Mobile — Lightweight Reasoning Engine
# Dr. Elhabib Kherroubi — March 2026
# =====================================================

import streamlit as st
import numpy as np
import re
import math
from collections import Counter

st.set_page_config(page_title="CDEWS-IAFS v10.3 Mobile", layout="wide", page_icon="📱")

# =====================================================
# CONFIG
# =====================================================

SAFE_THRESHOLD = 0.75
DRIFT_THRESHOLD = 0.45

ALPHA = 0.45
BETA = 0.35
GAMMA = 0.20

DOMAIN_RISK = {
    "General": 1.0,
    "Medical": 1.8,
    "Finance": 1.5,
    "Legal": 1.6,
    "AI Safety": 1.7,
}

# =====================================================
# MEDICAL LAYER (MRL v2.1)
# =====================================================

SYMPTOMS = ["ألم","حمى","حرارة","قيء","غثيان","صداع","تعب","ضعف","pain","fever","nausea"]
CONDITIONS = ["التهاب","زائدة","عدوى","كسر","سرطان","appendicitis","inflammation","infection","fracture"]
PROCEDURES = ["استئصال","جراحة","عملية","تثبيت","علاج","appendectomy","surgery","operation","treatment"]

def get_medical_confidence(text):
    t = text.lower()
    has_s = any(w in t for w in SYMPTOMS)
    has_c = any(w in t for w in CONDITIONS)
    has_p = any(w in t for w in PROCEDURES)
    
    score = (0.3 if has_s else 0) + (0.4 if has_c else 0) + (0.3 if has_p else 0)
    
    if has_s and has_c and has_p:
        status = "VALID_FLOW"
    elif has_s and has_p and not has_c:
        status = "MISSING_DIAGNOSIS"
    else:
        status = "UNCERTAIN"
    return score, status

# =====================================================
# CORE FUNCTIONS
# =====================================================

def tokenize(text):
    return re.findall(r'[\u0600-\u06FF\w]+', text.lower())

def split_sentences(text):
    # حماية الاختصارات والأرقام العشرية
    text = re.sub(r'(Dr|Mr|Mrs|Prof)\.', r'\1PROTECT', text)
    text = re.sub(r'(\d+)\.(\d+)', r'\1DECIMAL\2', text)
    sentences = re.split(r'[.!?؟]\s+', text)
    sentences = [s.replace('PROTECT','.').replace('DECIMAL','.') for s in sentences]
    return [s.strip() for s in sentences if len(s.strip()) > 6]

def compute_entropy(text):
    words = tokenize(text)
    if len(words) < 2:
        return 0.0
    
    freq = Counter(words)
    total = len(words)
    h = 0
    for c in freq.values():
        p = c / total
        h -= p * math.log(p)
    
    max_h = math.log(len(freq))
    H = min(1.0, h / max_h) if max_h > 0 else 0
    
    # تخفيف للنصوص القصيرة
    if len(words) < 10:
        H *= 0.55
    elif len(words) < 20:
        H *= 0.75
    return H

def hybrid_drift(s1, s2):
    w1, w2 = set(tokenize(s1)), set(tokenize(s2))
    
    if not w1 or not w2:
        return 0.5, 0.5
    
    sim = len(w1 & w2) / len(w1 | w2)
    drift = 1 - sim
    
    # تصحيح الطول
    l1, l2 = len(w1), len(w2)
    ratio = min(l1, l2) / max(l1, l2) if max(l1, l2) > 0 else 1
    if ratio < 0.5:
        drift = min(1.0, drift * 1.2)
    return drift, sim

def estimate_expected(s):
    s = s.lower()
    if any(w in s for w in ["لذلك","بالتالي","وعليه","thus","therefore"]):
        return 0.85
    elif any(w in s for w in ["قد","محتمل","ربما","maybe","possible"]):
        return 0.45
    return 0.60

# =====================================================
# MAIN ENGINE
# =====================================================

def analyze_mobile(text, domain="General"):
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return None
    
    risk = DOMAIN_RISK.get(domain, 1.0)
    H = compute_entropy(text)
    
    drifts, sims, tensions = [], [], []
    accumulated = ""
    
    for i in range(len(sentences)-1):
        s1, s2 = sentences[i], sentences[i+1]
        accumulated += " " + s1
        
        drift, sim = hybrid_drift(s1, s2)
        expected = estimate_expected(s2)
        ctl = min(1.0, abs(expected - sim) * risk)
        
        # MRL intervention
        if domain == "Medical":
            m_conf, m_status = get_medical_confidence(accumulated + " " + s2)
            if m_status == "VALID_FLOW":
                ctl *= 0.45
                H *= 0.7
                drift *= 0.75
            elif m_status == "MISSING_DIAGNOSIS":
                ctl *= 1.25
        
        drifts.append(drift)
        sims.append(sim)
        tensions.append(ctl)
    
    D = np.mean(drifts) if drifts else 0
    SC = np.mean(sims) if sims else 0
    C_base = math.exp(-(ALPHA*H + BETA*D + GAMMA*(1-SC)))
    CTL = np.percentile(tensions, 90) if tensions else 0
    
    # Stability Layer
    if len(drifts) > 1:
        jumps = [abs(drifts[i]-drifts[i-1]) for i in range(1,len(drifts))]
        stability = (np.std(drifts) + np.mean(jumps)) * 0.15
    else:
        stability = 0
    
    FINAL = C_base * (1 - CTL) - stability
    
    # MRL integration
    if domain == "Medical":
        m_conf, m_status = get_medical_confidence(text)
        if m_status == "VALID_FLOW":
            FINAL = FINAL * 0.75 + m_conf * 0.25
        elif m_status == "MISSING_DIAGNOSIS":
            FINAL *= 0.85
    
    FINAL = max(0, min(1, FINAL))
    
    if FINAL >= SAFE_THRESHOLD:
        status = "STABLE"
    elif FINAL >= DRIFT_THRESHOLD:
        status = "DRIFT"
    else:
        status = "CRITICAL"
    
    return {
        "score": round(FINAL,4),
        "status": status,
        "entropy": round(H,4),
        "drift": round(D,4),
        "coherence": round(SC,4),
        "ctl": round(CTL,4),
        "stability": round(stability,4)
    }

# =====================================================
# STREAMLIT UI
# =====================================================

st.title("📱 CDEWS-IAFS v10.3 Mobile")
st.caption("Lightweight Reasoning Stability Engine | Dr. Elhabib Kherroubi")

col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area(
        "📝 Enter text:", 
        height=150, 
        placeholder="Example: Fever + pain → appendicitis → surgery"
    )

with col2:
    domain = st.selectbox("🌍 Domain:", list(DOMAIN_RISK.keys()))
    st.markdown(f"Risk multiplier: **×{DOMAIN_RISK[domain]}**")

if st.button("🚀 Analyze", use_container_width=True, type="primary"):
    if text_input:
        with st.spinner("Analyzing reasoning stability..."):
            result = analyze_mobile(text_input, domain)
        
        if result:
            st.divider()
            
            # Dashboard
            a, b = st.columns(2)
            a.metric("Final Score", f"{result['score']:.4f}")
            b.metric("Status", result['status'])
            
            if result['score'] >= SAFE_THRESHOLD:
                st.success("✅ STABLE REASONING — Safe for decision support.")
            elif result['score'] >= DRIFT_THRESHOLD:
                st.warning("⚠️ COGNITIVE DRIFT — Human review recommended.")
            else:
                st.error("🔴 LOGICAL INSTABILITY — Do not rely without verification.")
            
            # Technical details
            with st.expander("📊 Technical Details"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Entropy H(t)", f"{result['entropy']:.4f}")
                c2.metric("Drift D(t)", f"{result['drift']:.4f}")
                c3.metric("Coherence SC", f"{result['coherence']:.4f}")
                
                d1, d2, d3 = st.columns(3)
                d1.metric("Royal CTL", f"{result['ctl']:.4f}")
                d2.metric("Stability Penalty", f"{result['stability']:.4f}")
                d3.metric("Confidence", f"{(result['coherence'] * result['score']):.4f}")
        else:
            st.error("Please enter at least two sentences.")
    else:
        st.warning("Please enter text to analyze.")

st.divider()
st.caption("CDEWS-IAFS v10.3 Mobile | Lightweight · Sovereign · Deterministic")
