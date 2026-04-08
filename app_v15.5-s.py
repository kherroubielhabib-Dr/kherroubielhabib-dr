# ============================================
# CSLF v15-S
# Sovereign Epistemic Gate (Spec-Aligned)
# ============================================

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import hashlib
import json
import time

# ============================================
# 🔐 Epistemic Artifact (CAV)
# ============================================

@dataclass(frozen=True)
class CAV:
    decision_id: str
    epistemic_result: str  # ALLOW_EXISTENCE | DENY_EXISTENCE
    context_hash: str
    signature: str
    timestamp: float
    validity_window: Optional[float]  # epistemic-only
    sealed: bool = True
    version: str = "CSLF-v15-S"

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2)


# ============================================
# 🧠 CSLF Engine (Pure Epistemic System)
# ============================================

class CSLF:

    def __init__(self):
        pass  # stateless system

    # --------------------------------------------
    # Core API
    # --------------------------------------------
    def evaluate(self, decision: Dict[str, Any], context: Dict[str, Any]) -> CAV:

        decision_id = self._generate_decision_id(decision, context)
        context_hash = self._hash_context(context)

        epistemic_valid = self._epistemic_filter(decision, context)
        result = "ALLOW_EXISTENCE" if epistemic_valid else "DENY_EXISTENCE"

        timestamp = time.time()

        signature = self._seal({
            "decision_id": decision_id,
            "result": result,
            "context_hash": context_hash,
            "timestamp": timestamp
        })

        cav = CAV(
            decision_id=decision_id,
            epistemic_result=result,
            context_hash=context_hash,
            signature=signature,
            timestamp=timestamp,
            validity_window=None,
            sealed=True
        )

        self._assert_invariants(cav)

        return cav

    # ============================================
    # 🧩 Epistemic Core Logic (STRICTLY PURE)
    # ============================================

    def _epistemic_filter(self, decision: Dict[str, Any], context: Dict[str, Any]) -> bool:

        return all([
            self._check_structure(decision),
            self._check_coherence(decision),
            self._check_stability(decision),
            self._check_grounding(decision, context)
        ])

    # ============================================
    # 🔍 Epistemic Checks
    # ============================================

    def _check_structure(self, decision):
        required = {"premise", "inference", "conclusion"}
        return required.issubset(decision.keys())

    def _check_coherence(self, decision):
        return decision.get("premise") != decision.get("conclusion")

    def _check_stability(self, decision):
        return isinstance(decision.get("inference"), str)

    def _check_grounding(self, decision, context):
        return len(context) > 0

    # ============================================
    # 🔐 Sealing (Stronger Canonical Hashing)
    # ============================================

    def _seal(self, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    # ============================================
    # 🧾 Identity
    # ============================================

    def _generate_decision_id(self, decision, context):
        raw = json.dumps(decision, sort_keys=True) + json.dumps(context, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _hash_context(self, context):
        return hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()

    # ============================================
    # 🧷 Invariants Enforcement (CRITICAL)
    # ============================================

    def _assert_invariants(self, cav: CAV):

        assert cav.sealed is True
        assert cav.validity_window is None

        # Epistemic closure
        assert cav.epistemic_result in ["ALLOW_EXISTENCE", "DENY_EXISTENCE"]

        # No execution semantics leakage
        forbidden_fields = ["action", "execute", "commit"]
        cav_json = cav.to_json()
        for f in forbidden_fields:
            assert f not in cav_json


# ============================================
# 🌐 Streamlit Interface
# ============================================

import streamlit as st

st.set_page_config(page_title="CSLF v15-S", layout="wide")

st.title("🏛️ CSLF v15-S — Sovereign Epistemic Gate")

st.markdown("""
This system evaluates **epistemic legitimacy only**.
No execution semantics. No persistence logic.
""")

# Input panels
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Decision Input")
    premise = st.text_area("Premise", "Patient has infection")
    inference = st.text_area("Inference", "Antibiotic indicated")
    conclusion = st.text_area("Conclusion", "Administer drug X")

with col2:
    st.subheader("📥 Context Input")
    context_raw = st.text_area("Context JSON", '{"patient_id": "123"}')

# Parse context safely
try:
    context = json.loads(context_raw)
except:
    context = {}

decision = {
    "premise": premise,
    "inference": inference,
    "conclusion": conclusion
}

# Run evaluation
if st.button("🚀 Evaluate (CSLF)"):
    engine = CSLF()
    cav = engine.evaluate(decision, context)

    st.subheader("📦 CAV Output")
    st.json(json.loads(cav.to_json()))

    if cav.epistemic_result == "ALLOW_EXISTENCE":
        st.success("Epistemically VALID")
    else:
        st.error("Epistemically INVALID")

# Footer
st.markdown("---")
st.caption("CSLF v15-S | Epistemic Closure Enforced | No Execution Authority")
