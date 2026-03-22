"""
Pluggable MAUDE-like adverse event signal source.

Default: deterministic simulation derived from project FMEA failure modes (no external API).
Uses SHA-256 digests (not Python hash()) so outputs are stable across processes for tests/CI.
Replace `get_maude_signal_provider()` to wire FDA MAUDE or other real-world feeds later.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


def _digest_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12], 16)


@runtime_checkable
class MaudeSignalProvider(Protocol):
    """Contract for MAUDE / post-market signal feeds."""

    def get_signals(
        self,
        *,
        project_id: str,
        device_name: str,
        intended_use: str,
        fmea_rows: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Returns signal dicts with at least:
        failure_mode, event_count, trend, severity
        Optional: recommended_monitoring_focus, source, notes
        """
        ...


# Generic placeholders when FMEA coverage is thin (deterministic per project).
_GENERIC_FAILURE_SEEDS: tuple[tuple[str, str], ...] = (
    ("Software anomaly — unexpected device behavior", "trend_review_and_regression_monitoring"),
    ("Electrical / energy-related patient harm scenario", "thermal_and_power_quality_monitoring"),
    ("Use-related error — labeling or IFU ambiguity", "human_factors_and_complaint_text_mining"),
    ("Biocompatibility / materials-related injury", "biocompatibility_and_supplier_change_control"),
    ("Sterility or packaging breach (if applicable)", "sterility_and_distribution_monitoring"),
)


class SimulatedMaudeSignalProvider:
    """
    Simulated MAUDE-style signals for development and demos.
    Deterministic from (project_id, failure_mode label, device_name).
    Returns at least 3 signals when possible by supplementing from generic seeds.
    """

    _TRENDS = ("increasing", "stable", "decreasing")
    _SEVERITIES = ("high", "medium", "low")

    def _monitoring_focus_for_failure_mode(self, failure_mode: str) -> str:
        low = (failure_mode or "").lower()
        if any(w in low for w in ("battery", "power", "thermal", "overheat", "charge")):
            return "Energy/power quality trending; correlate with lot, firmware revision, and charger accessories."
        if any(w in low for w in ("software", "firmware", "algorithm", "reset")):
            return "Software anomaly surveillance; regression monitoring after releases; field logs vs. revision."
        if any(w in low for w in ("fracture", "break", "lead", "catheter", "structural")):
            return "Mechanical integrity complaints; return goods analysis; supplier MDR and drawing changes."
        if any(w in low for w in ("infection", "steril", "bio", "material")):
            return "Biocompatibility and sterilization process monitoring; supplier change notifications."
        if any(w in low for w in ("label", "ifu", "use error", "misuse", "human")):
            return "Human factors signals; IFU/label change effectiveness; training and complaint text mining."
        return "Complaint coding review; periodic trending vs. FMEA failure mode and residual risk acceptance."

    def _one_signal(
        self,
        *,
        project_id: str,
        device_name: str,
        failure_mode: str,
        label_suffix: str,
        generic: bool,
    ) -> Dict[str, Any]:
        seed = f"{project_id}\0{failure_mode}\0{device_name}\0{label_suffix}"
        h = _digest_int(seed) % 1_000_000
        trend = self._TRENDS[h % 3]
        severity = self._SEVERITIES[(h // 11) % 3]
        base = 18 + (h % 220)
        if trend == "increasing":
            base += 35 + (h % 80)
        elif trend == "decreasing":
            base = max(8, base - (20 + (h % 40)))

        if generic:
            focus_key = _GENERIC_FAILURE_SEEDS[h % len(_GENERIC_FAILURE_SEEDS)][1]
            focus_map = {
                "trend_review_and_regression_monitoring": "Quarterly trending; spike investigation within 10 business days.",
                "thermal_and_power_quality_monitoring": "Lot-linked thermal/power excursions; field service correlation.",
                "human_factors_and_complaint_text_mining": "Complaint narratives + IFU revision impact checks.",
                "biocompatibility_and_supplier_change_control": "Supplier COA drift; biocompatibility re-eval triggers.",
                "sterility_and_distribution_monitoring": "Distribution stress; seal integrity sampling.",
            }
            focus = focus_map.get(
                focus_key, "Periodic signal review against FMEA themes and residual risk."
            )
        else:
            focus = self._monitoring_focus_for_failure_mode(failure_mode)

        return {
            "failure_mode": failure_mode,
            "event_count": int(base),
            "trend": trend,
            "severity": severity,
            "recommended_monitoring_focus": focus,
            "source": "simulated_maude_generic" if generic else "simulated_maude",
            "notes": (
                "Synthetic signal for PMS planning — replace with verified MAUDE extracts before regulatory use."
                if not generic
                else "Generic device-risk placeholder (thin FMEA) — deterministic simulation only."
            ),
        }

    def get_signals(
        self,
        *,
        project_id: str,
        device_name: str,
        intended_use: str,
        fmea_rows: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        _ = intended_use
        signals: List[Dict[str, Any]] = []
        seen: set[str] = set()

        for row in fmea_rows:
            fm = (row.get("failure_mode") or "").strip()
            if not fm or fm.lower() in seen:
                continue
            seen.add(fm.lower())
            signals.append(
                self._one_signal(
                    project_id=project_id,
                    device_name=device_name,
                    failure_mode=fm,
                    label_suffix=f"fmea:{len(signals)}",
                    generic=False,
                )
            )
            if len(signals) >= 20:
                break

        idx = 0
        while len(signals) < 3:
            gfm, _ = _GENERIC_FAILURE_SEEDS[idx % len(_GENERIC_FAILURE_SEEDS)]
            idx += 1
            if gfm.lower() in seen:
                continue
            seen.add(gfm.lower())
            signals.append(
                self._one_signal(
                    project_id=project_id,
                    device_name=device_name,
                    failure_mode=gfm,
                    label_suffix=f"generic:{idx}",
                    generic=True,
                )
            )

        return signals


_default_provider: Optional[MaudeSignalProvider] = None


def get_maude_signal_provider() -> MaudeSignalProvider:
    """Factory hook: swap implementation for real MAUDE API integration."""
    global _default_provider
    if _default_provider is None:
        _default_provider = SimulatedMaudeSignalProvider()
    return _default_provider


def set_maude_signal_provider(provider: Optional[MaudeSignalProvider]) -> None:
    """Test hook or DI override."""
    global _default_provider
    _default_provider = provider
