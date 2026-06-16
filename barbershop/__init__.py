# ==========================================================================
# FILE: barbershop/__init__.py
# PURPOSE: Marks barbershop/ as a Python package — the Quantra visual
#          diagnostics layer (dashboard) + the LLM Risk Doctor. Read-only:
#          nothing in this package trains, trades, or mutates the policy.
# ==========================================================================
#
# UPDATE LOG — every change to this file must be logged here:
#   [2026-06-15] [Claude] — First build. Package marker for Barbershop v1.0.
# ==========================================================================

__all__ = ["config", "data", "figures", "adapter", "risk_doctor", "doctor_chat"]
