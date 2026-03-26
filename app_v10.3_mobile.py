# =====================================================
# CDEWS-IAFS v10.3 Mobile — FIXED EDITION
# Stable · Lightweight · Causal-Aware · MRL Enhanced
# Dr. Elhabib Kherroubi — 2026
# =====================================================

import numpy as np
import re
import math
from collections import Counter

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

SYMPTOMS = ["ألم", "حمى", "حرارة", "قيء", "غثيان", "صداع", "pain", "fever"]
CONDITIONS = ["التهاب", "زائدة", "عدوى", "كسر", "appendicitis", "infection"]
PROCEDURES = ["استئصال", "جراحة", "عملية", "تثبيت", "appendectomy", "surgery"]

def get_medical_confidence(text):
    text = text.lower()
    
    has_s = any(w in text for w in SYMPTOMS)
    has_c = any(w in text for w in CONDITIONS)
    has_p = any(w in text for w in PROCEDURES)
    
    score = (0.3 if has_s else 0) + (0.4 if has_c else 0) + (0.3 if has_p else 0)
    
    if has_s and has_c and has_p:
        status = "VALID_FLOW"
    elif has_s and has_p and not has_c:
        status = "MISSING_DIAGNOSIS"
    else:
        status = "UNCERTAIN"
        
    return score, status

# =====================================================
# BASIC NLP
# =====================================================

def tokenize(text):
    return re.findall(r'[\u0600-\u06FF\w]+', text.lower())

def split_sentences(text):
    sentences = re.split(r'[.!?؟]\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 6]

# =====================================================
# ENTROPY (Adjusted for Mobile)
# =====================================================

def compute_entropy(text):
    words = tokenize(text)
    if len(words) < 2:
        return 0.0

    freq = Counter(words)
    total = len(words)

    h = 0.0
    for c in freq.values():
        p = c / total
        h -= p * math.log(p)

    max_h = math.log(len(freq))
    result = min(1.0, h / max_h) if max_h > 0 else 0.0

    # تخفيف النصوص القصيرة
    if len(words) < 10:
        result *= 0.55
    elif len(words) < 20:
        result *= 0.75

    return result

# =====================================================
# 🔥 CAUSAL-AWARE DRIFT (FIXED)
# =====================================================

CAUSAL_PAIRS = [
    ("حرارة", "التهاب"),
    ("ألم", "التهاب"),
    ("التهاب", "استئصال"),
    ("كسر", "تثبيت"),
    ("appendicitis", "appendectomy"),
]

def hybrid_drift(s1, s2):
    w1 = set(tokenize(s1))
    w2 = set(tokenize(s2))

    if not w1 or not w2:
        return 0.5, 0.5

    # Jaccard
    overlap = len(w1 & w2)
    total = len(w1 | w2)
    base_sim = overlap / total

    # 🔥 Causal bonus
    bonus = 0.0
    s1_l, s2_l = s1.lower(), s2.lower()

    for a, b in CAUSAL_PAIRS:
        if a in s1_l and b in s2_l:
            bonus += 0.25

    sim = min(1.0, base_sim + bonus)
    drift = 1 - sim

    return drift, sim

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

    for i in range(len(sentences) - 1):
        s1, s2 = sentences[i], sentences[i+1]

        drift, sim = hybrid_drift(s1, s2)

        drifts.append(drift)
        sims.append(sim)

        # Expected (محسّن)
        expected = 0.5 + (0.1 if len(s2.split()) > 5 else -0.05)

        # تعزيز طبي
        if "التهاب" in s2 or "استئصال" in s2:
            expected += 0.15

        expected = max(0.3, min(0.85, expected))

        # CTL
        ctl = min(1.0, abs(expected - sim) * risk)

        # 🔥 MRL Context Window
        if domain == "Medical":
            context = " ".join(sentences[max(0, i-1):i+2])
            m_conf, m_status = get_medical_confidence(context)

            if m_status == "VALID_FLOW":
                ctl *= 0.25
            elif m_status == "MISSING_DIAGNOSIS":
                ctl *= 1.25

        tensions.append(ctl)

    # Stats
    D = np.mean(drifts)
    SC = np.mean(sims)

    C_base = math.exp(-(ALPHA * H + BETA * D + GAMMA * (1 - SC)))

    # Royal CTL (p90)
    CTL = np.percentile(tensions, 90)

    # Stability
    stability = np.std(drifts) * 0.12

    # 🔥 FINAL (FIXED)
    FINAL = C_base * (1 - CTL)
    FINAL *= (1 - stability)

    # 🔥 MRL Integration (Soft Boost)
    if domain == "Medical":
        m_conf, _ = get_medical_confidence(text)
        FINAL = FINAL * (0.75 + 0.25 * m_conf)

    FINAL = max(0.0, min(1.0, FINAL))

    # Status
    if FINAL >= SAFE_THRESHOLD:
        status = "STABLE"
    elif FINAL >= DRIFT_THRESHOLD:
        status = "DRIFT"
    else:
        status = "CRITICAL"

    return {
        "score": round(FINAL, 4),
        "status": status,
        "entropy": round(H, 4),
        "drift": round(D, 4),
        "coherence": round(SC, 4),
        "ctl": round(CTL, 4),
        "stability": round(stability, 4)
    }

# =====================================================
# QUICK TEST
# =====================================================

if __name__ == "__main__":
    text = "يعاني المريض من ارتفاع في درجة الحرارة مع ألم حاد في الربع السفلي الأيمن. تشير هذه الأعراض إلى التهاب الزائدة الدودية، وبناءً على ذلك نوصي بإجراء استئصال جراحي فوري."
    
    result = analyze_mobile(text, "Medical")
    
    print("\n👑 CDEWS v10.3 Mobile — FIXED")
    print("Score:", result["score"], "| Status:", result["status"])
    print("H:", result["entropy"], "D:", result["drift"], "CTL:", result["ctl"])
