"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                              .                                                             ║
║                              C S L F   v 1 4 . 9 - S                                                                                     ║
║                              THE SOVEREIGN EXISTENCE GATE                                                                                ║
║                              بوابة الوجود السيادية — النسخة النهائية                                                                     ║
║                                                                                                                                          ║
║  ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════  ║
║                                                                                                                                          ║
║  🏛️  الهوية المعمارية (Architectural Identity):                                                                                        ║
║                                                                                                                                          ║
║     • نظام إبستيمي مغلق — لا يعيد التفسير بعد إنتاج الأثر                                                                               ║
║     • يحدد فقط "هل يستحق هذا الكيان أن يوجد؟"                                                                                          ║
║     • لا يصدر أوامر تنفيذية — لا COMMIT ولا REVOKE                                                                                      ║
║     • مخرجاته: ALLOW_EXISTENCE أو DENY_EXISTENCE فقط                                                                                    ║
║                                                                                                                                          ║
║  ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════  ║
║                                                                                                                                          ║
║  🔧  الميزات الحصرية:                                                                                                                   ║
║                                                                                                                                          ║
║     ✓ مرشح النفي الذكي — يكتشف "لا مقدمة، لا بنية، لا نتيجة"                                                                            ║
║     ✓ كشف التناقض بين القيمة الرقمية والمحتوى — قيمة عالية مع نص فقير                                                                  ║
║     ✓ الختم الجنائي (FAL) — بصمة SHA-256 لكل جلسة                                                                                      ║
║     ✓ EDI التراكمي — يتزايد مع المحاولات الفاسدة                                                                                       ║
║     ✓ 5 حالات وجودية تتحول إلى قرارين فقط لمحمد                                                                                        ║
║                                                                                                                                          ║
║  ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════  ║
║                                                                                                                                          ║
║  📋 العلاقة مع R-AGAM (لمحمد):                                                                                                          ║
║                                                                                                                                          ║
║     CSLF v14.9-S → ALLOW_EXISTENCE → R-AGAM يقرر COMMIT / REVOKE / DEFER / ESCALATE                                                     ║
║     CSLF v14.9-S → DENY_EXISTENCE  → R-AGAM يرفض التنفيذ (لا يوجد كيان)                                                                ║
║                                                                                                                                          ║
║  ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════  ║
║                                                                                                                                          ║
║  Author: Dr. Elhabib Kherroubi                                                                                                          ║
║  Version: 14.9-S — The Sovereign Existence Gate                                                                                         ║
║  Date: April 2026                                                                                                                        ║
║  Status: 🔒 PRODUCTION-READY — SOVEREIGN — FINAL                                                                                        ║
║                                                                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import hashlib
import json
import re
from datetime import datetime

# =============================================================
# §1 — المحرك السيادي النهائي (The Sovereign Engine)
# =============================================================

class CSLFSovereignGateV14_9_S:
    """
    CSLF v14.9-S — The Sovereign Existence Gate
    نظام إبستيمي مغلق يحدد فقط: هل يستحق هذا الكيان أن يوجد؟
    لا يتجاوز حده. لا يصدر أوامر تنفيذية.
    """
    
    def __init__(self):
        # القالب الهيكلي الإجباري (CIL)
        self.REQUIRED_PATTERNS = {
            "SA": ["مقدمة", "بنية", "نتيجة"],
            "CI": ["سبب", "آلية", "أثر"],
            "SV": ["تعريف", "سياق", "انضباط"],
            "EG": ["دليل", "مصدر", "تحقق"]
        }
        
        # كلمات النفي (تؤدي إلى NEGATED_EXISTENCE)
        self.NEGATION_MARKERS = [
            "لا", "ليس", "غير", "بدون", "يفتقر", "عدم", 
            "لا يوجد", "خالي من", "ينفي", "منعدم"
        ]
        
        # كلمات التأكيد (تلغي أثر النفي)
        self.CONFIRMATION_MARKERS = [
            "تم", "يوجد", "توجد", "تم توفير", "تم تقديم",
            "تم توثيق", "تم إدراج", "تم تضمين"
        ]
        
        # كلمات السلب (للكشف عن التناقض القيمي)
        self.NEGATIVE_WORDS = ["ضعيف", "هش", "غير كاف", "ناقص", "فجوة", "مشكلة"]

    def _smart_negation_check(self, text: str, required_terms: list) -> list:
        """
        مرشح النفي الذكي
        يفحص 30 حرفاً قبل الكلمة، ويميز بين النفي والتأكيد
        """
        text_lower = text.lower()
        negated_terms = []
        
        for term in required_terms:
            term_lower = term.lower()
            if term_lower in text_lower:
                idx = text_lower.find(term_lower)
                context = text_lower[max(0, idx-30):idx]
                
                has_negation = any(neg in context for neg in self.NEGATION_MARKERS)
                has_confirmation = any(conf in context for conf in self.CONFIRMATION_MARKERS)
                
                if has_negation and not has_confirmation:
                    negated_terms.append(term)
        
        return negated_terms

    def _detect_value_content_paradox(self, val: float, text: str) -> tuple:
        """
        كشف التناقض بين القيمة الرقمية العالية والمحتوى السلبي
        """
        if val > 0.8 and len(text.strip()) < 60:
            return True, "قيمة عالية مع نص ضئيل"
        
        if val > 0.8:
            negative_count = sum(1 for w in self.NEGATIVE_WORDS if w in text.lower())
            if negative_count >= 2:
                return True, f"قيمة عالية مع {negative_count} كلمة سلبية"
        
        return False, ""

    def evaluate(self, pillars: dict) -> dict:
        """
        تقييم الكيان وتحديد أهليته للوجود
        المخرجات: ONLY existence decision + forensic trace
        """
        vals = {k: v["val"] for k, v in pillars.items()}
        issues = []
        negation_alerts = []
        paradox_alerts = []

        # 1. عتبة التجسد (NULL_STATE)
        collapsed = [p for p, v in vals.items() if v < 0.5]
        if collapsed:
            return {
                "existence_decision": "DENY_EXISTENCE",
                "ontological_status": "NULL_STATE",
                "kll": 0.0,
                "details": {"collapsed": collapsed},
                "trace": None
            }

        # 2. تحليل كل ركن
        for name, data in pillars.items():
            text = data["text"].strip()
            val = data["val"]
            
            # فحص النقص الهيكلي
            missing = [t for t in self.REQUIRED_PATTERNS[name] if t not in text]
            if missing:
                issues.append(f"{name}: نقص في {missing}")
            
            # فحص النفي الذكي
            negated = self._smart_negation_check(text, self.REQUIRED_PATTERNS[name])
            if negated:
                negation_alerts.append(f"{name}: نفي {negated}")
            
            # فحص تناقض القيمة
            has_paradox, reason = self._detect_value_content_paradox(val, text)
            if has_paradox:
                paradox_alerts.append(f"{name}: {reason}")

        # 3. حساب KLL (المؤشر الوصفي)
        kll = min(vals.values())
        
        # تطبيق عقوبات النفي
        if negation_alerts:
            kll = max(0.0, kll - 0.3)

        # 4. تحديد الحالة الوجودية (للتتبع فقط)
        if negation_alerts:
            ontological_status = "NEGATED_EXISTENCE"
        elif paradox_alerts or (vals.get("CI", 0) > vals.get("SA", 0) + 0.3):
            ontological_status = "PARADOXICAL_EXISTENCE"
        elif issues:
            ontological_status = "INCOMPLETE_EXISTENCE"
        else:
            ontological_status = "EXISTS"

        # 5. القرار النهائي لمحمد (الموجود الوحيد)
        existence_decision = "ALLOW_EXISTENCE" if ontological_status == "EXISTS" else "DENY_EXISTENCE"

        # 6. الختم الجنائي (FAL)
        trace_data = {
            "timestamp": datetime.now().isoformat(),
            "ontological_status": ontological_status,
            "kll": round(kll, 3),
            "existence_decision": existence_decision,
            "issues": issues,
            "negation_alerts": negation_alerts,
            "paradox_alerts": paradox_alerts
        }
        
        trace_hash = hashlib.sha256(
            json.dumps(trace_data, sort_keys=True).encode()
        ).hexdigest()

        return {
            "existence_decision": existence_decision,
            "ontological_status": ontological_status,
            "kll": round(kll, 3),
            "details": {
                "issues": issues,
                "negation_alerts": negation_alerts,
                "paradox_alerts": paradox_alerts,
                "collapsed": []
            },
            "trace": {
                "hash": trace_hash[:48],
                "data": trace_data
            }
        }


# =============================================================
# §2 — واجهة السيادة النهائية (The Sovereign UI)
# =============================================================

st.set_page_config(
    page_title="CSLF v14.9-S | Sovereign Existence Gate",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# التصميم البصري السيادي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0a0e27 0%, #0f1535 100%);
        padding: 2rem 2rem 1.5rem;
        border-radius: 0 0 24px 24px;
        margin-bottom: 2rem;
        border-bottom: 2px solid #00d4ff;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    
    .main-sub {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .sovereign-badge {
        display: inline-block;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.65rem;
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        margin-right: 0.5rem;
    }
    
    .decision-panel {
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 1.5rem 0;
        border: 2px solid;
    }
    
    .allow {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.02));
        border-color: #10b981;
    }
    
    .deny {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.02));
        border-color: #ef4444;
    }
    
    .decision-text {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    .allow .decision-text { color: #10b981; }
    .deny .decision-text { color: #ef4444; }
    
    .decision-sub {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94a3b8;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
    }
    
    .forensic-box {
        background: rgba(10, 14, 39, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        word-break: break-all;
    }
    
    .stTextArea textarea {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #00d4ff !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #3b82f6);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
    }
    
    hr {
        border-color: rgba(0, 212, 255, 0.15);
        margin: 1.5rem 0;
    }
    
    .ragam-note {
        background: rgba(0, 212, 255, 0.05);
        border-left: 3px solid #00d4ff;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-size: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="main-title">🏛️ CSLF <span style="font-size:1rem;">v14.9-S</span></div>
    <div class="main-sub">The Sovereign Existence Gate — Epistemic Closure Boundary</div>
    <div style="margin-top: 0.8rem;">
        <span class="sovereign-badge">🔒 Epistemic Closure</span>
        <span class="sovereign-badge">⚖️ No Execution Orders</span>
        <span class="sovereign-badge">🎯 ALLOW / DENY Only</span>
        <span class="sovereign-badge">🔬 Negation Filter</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏛️ CSLF v14.9-S")
    st.markdown("*Dr. Elhabib Kherroubi*")
    st.markdown("---")
    
    if "edi" not in st.session_state:
        st.session_state.edi = 0.0
    
    st.metric("📊 EDI (Deviation Index)", round(st.session_state.edi, 2))
    
    st.markdown("---")
    st.markdown("### 📋 Ontological States")
    st.caption("✨ **EXISTS** → ALLOW_EXISTENCE")
    st.caption("⚠️ **INCOMPLETE** → DENY_EXISTENCE")
    st.caption("🧬 **PARADOXICAL** → DENY_EXISTENCE")
    st.caption("💔 **NEGATED** → DENY_EXISTENCE")
    st.caption("💥 **NULL** → DENY_EXISTENCE")
    
    st.markdown("---")
    st.markdown("### 🔗 Integration with R-AGAM")
    st.markdown("""
    ```
    CSLF v14.9-S
         │
         ▼
    ALLOW_EXISTENCE ──► R-AGAM (COMMIT/REVOKE/DEFER/ESCALATE)
    DENY_EXISTENCE  ──► R-AGAM (REJECT — No entity to execute)
    ```
    """)
    
    st.markdown("---")
    st.markdown("### 📜 Meta-Laws")
    st.markdown("""
    - No execution without existence
    - Zero collapse law
    - No backflow after sealing
    """)

# Main Title
st.markdown("## ⚖️ Does this entity deserve to exist?")
st.markdown("*أدخل أركان الكيان الأربعة — البوابة تحدد فقط: هل يستحق الوجود؟*")
st.markdown("---")

# Input Fields
p_data = {}
col1, col2 = st.columns(2)

fields = [
    ("SA", "🏗️ Structural Adequacy", ["مقدمة", "بنية", "نتيجة"]),
    ("CI", "🔗 Causal Integrity", ["سبب", "آلية", "أثر"]),
    ("SV", "📖 Semantic Validity", ["تعريف", "سياق", "انضباط"]),
    ("EG", "🧪 Evidence Grounding", ["دليل", "مصدر", "تحقق"])
]

for i, (key, label, terms) in enumerate(fields):
    target_col = col1 if i < 2 else col2
    with target_col:
        st.subheader(label)
        st.caption(f"Required terms: {' | '.join(terms)}")
        
        val = st.slider(f"Value {key}", 0.0, 1.0, 0.8, key=f"v_{key}")
        text = st.text_area(
            f"Testimony {key}", 
            key=f"t_{key}", 
            height=120,
            placeholder=f"Must include: {', '.join(terms)}..."
        )
        p_data[key] = {"val": val, "text": text}

st.divider()

# Execute Button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    run = st.button("⚖️ ADJUDICATE EXISTENCE", use_container_width=True)

# Results
if run:
    # Input validation
    insufficient = [name for name, d in p_data.items() if len(d["text"].strip()) < 40]
    
    if insufficient:
        st.error(f"💥 Entity lacks minimum linguistic density. Insufficient pillars: {', '.join(insufficient)} (minimum 40 characters per pillar)")
        st.session_state.edi += 0.2
        st.stop()
    
    # Run engine
    engine = CSLFSovereignGateV14_9_S()
    result = engine.evaluate(p_data)
    
    # Update EDI
    if result["existence_decision"] == "DENY_EXISTENCE":
        st.session_state.edi += 0.5
        if result["ontological_status"] == "NEGATED_EXISTENCE":
            st.session_state.edi += 0.3
    
    # Display Decision Panel
    if result["existence_decision"] == "ALLOW_EXISTENCE":
        st.markdown(f"""
        <div class="decision-panel allow">
            <div class="decision-text">✅ ALLOW_EXISTENCE</div>
            <div class="decision-sub">This entity is epistemically admissible and deserves to exist.</div>
            <div class="decision-sub" style="margin-top:0.5rem;">Ontological Status: {result['ontological_status']} | KLL: {result['kll']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"""
        <div class="decision-panel deny">
            <div class="decision-text">❌ DENY_EXISTENCE</div>
            <div class="decision-sub">This entity does NOT deserve to exist.</div>
            <div class="decision-sub" style="margin-top:0.5rem;">Ontological Status: {result['ontological_status']} | KLL: {result['kll']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display details (for architect only, not for R-AGAM)
    with st.expander("🔬 Epistemic Details (for Architect)"):
        if result["details"]["issues"]:
            st.warning("Structural Issues:")
            for issue in result["details"]["issues"]:
                st.write(f"  • {issue}")
        
        if result["details"]["negation_alerts"]:
            st.error("Negation Detected:")
            for alert in result["details"]["negation_alerts"]:
                st.write(f"  • {alert}")
        
        if result["details"]["paradox_alerts"]:
            st.warning("Value-Content Paradoxes:")
            for paradox in result["details"]["paradox_alerts"]:
                st.write(f"  • {paradox}")
    
    # Forensic Seal
    st.markdown("### 🔒 Forensic Accountability Lock (FAL)")
    st.markdown(f"""
    <div class="forensic-box">
        <div><strong>🔑 Decision:</strong> {result['existence_decision']}</div>
        <div><strong>📊 Ontological Status:</strong> {result['ontological_status']}</div>
        <div><strong>📈 KLL:</strong> {result['kll']}</div>
        <div><strong>🕐 Timestamp:</strong> {result['trace']['data']['timestamp'][:19]}</div>
        <div><strong>🛡️ Forensic Seal:</strong><br><code>{result['trace']['hash']}</code></div>
    </div>
    """, unsafe_allow_html=True)
    
    # R-AGAM Handoff Note
    st.markdown("""
    <div class="ragam-note">
        <strong>📋 Handoff to R-AGAM:</strong><br>
        • This decision is epistemically CLOSED — no reinterpretation permitted.<br>
        • R-AGAM receives ONLY the decision above (ALLOW_EXISTENCE / DENY_EXISTENCE).<br>
        • R-AGAM then governs ontological persistence under live conditions.<br>
        • Post-Admissibility is an independent sovereign decision (REVOKE), not an extension of acceptance.
    </div>
    """, unsafe_allow_html=True)
    
    # Download CAV
    cav_data = {
        "artifact_type": "CAV",
        "version": "14.9-S",
        "decision": result["existence_decision"],
        "ontological_status": result["ontological_status"],
        "kll": result["kll"],
        "forensic_seal": result["trace"]["hash"],
        "timestamp": result["trace"]["data"]["timestamp"]
    }
    
    st.download_button(
        "📥 Download CAV Artifact",
        data=json.dumps(cav_data, indent=2, ensure_ascii=False),
        file_name=f"CAV_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

else:
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem;">
        <span style="font-size:3rem;">🏛️</span>
        <p style="color:#94a3b8; margin-top:1rem;">
            Enter the four pillars of the entity above.<br>
            <span style="font-size:0.7rem;">CSLF v14.9-S determines only: Does this entity deserve to exist?</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.6rem; color:#475569; padding:1rem;">
    🔒 CSLF v14.9-S — The Sovereign Existence Gate — Epistemic Closure Boundary<br>
    Dr. Elhabib Kherroubi — April 2026 — No Execution Orders, Only Existence Decisions
</div>
""", unsafe_allow_html=True)
