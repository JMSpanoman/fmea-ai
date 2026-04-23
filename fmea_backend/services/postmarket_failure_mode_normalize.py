"""
Rule-based normalization for MAUDE / NLP failure-mode phrases.

Groups semantically similar free-text themes under a single canonical key for aggregation
and FMEA gap matching. Replace or extend ``_PHRASE_TO_CANON`` via DB-backed rules later
(IMPLEMENTATION_RULES: admin-editable mappings). Embedding / clustering can reuse
``canonicalize_failure_mode_key`` as a first-stage bucket or bypass it entirely.

REGULATORY:
    Normalization is a deterministic heuristic — not clinical validation of equivalence.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# (canonical_key, synonym_phrases) — all compared after whitespace collapse + lowercasing.
_SYNONYM_GROUPS: List[Tuple[str, List[str]]] = [
    (
        "incomplete dose delivery",
        [
            "failed to deliver full dose",
            "incomplete injection",
            "partial dose delivered",
            "under-delivery",
            "under delivery",
            "incomplete dose",
            "partial dose",
            "did not receive full dose",
        ],
    ),
    (
        "unexpected shutdown during use",
        [
            "unexpected shutdown",
            "device shut down during use",
            "power loss during therapy",
            "stopped during infusion",
        ],
    ),
    (
        "false occlusion alarm",
        [
            "false occlusion",
            "false alarm occlusion",
            "nuisance occlusion alarm",
        ],
    ),
]


def _norm_text(s: str) -> str:
    t = re.sub(r"\s+", " ", str(s).strip().lower())
    return t


def _build_phrase_to_canonical() -> Dict[str, str]:
    m: Dict[str, str] = {}
    for canon, syns in _SYNONYM_GROUPS:
        ck = _norm_text(canon)
        m[ck] = ck
        for s in syns:
            sk = _norm_text(s)
            if sk:
                m[sk] = ck
    return m


_PHRASE_TO_CANON = _build_phrase_to_canonical()


def canonicalize_failure_mode_key(normalized_lower_key: str) -> str:
    """
    Map a lowercased, whitespace-normalized failure-mode / risk phrase to a canonical bucket.

    Falls through to the input string when no synonym group matches.
    """
    k = _norm_text(normalized_lower_key)
    if not k:
        return ""
    if k in _PHRASE_TO_CANON:
        return _PHRASE_TO_CANON[k]
    # Longest synonym contained in k (phrase-level soft match)
    best: str = ""
    best_canon = ""
    for phrase, canon in _PHRASE_TO_CANON.items():
        if len(phrase) >= 8 and phrase in k and len(phrase) > len(best):
            best = phrase
            best_canon = canon
    if best_canon:
        return best_canon
    return k
