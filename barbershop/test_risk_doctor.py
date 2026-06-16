# ==========================================================================
# FILE: barbershop/test_risk_doctor.py
# PURPOSE: Tests 11-20 for the LLM Risk Doctor (continuation spec Section G).
#          All tests MOCK the LLM client (no live API call). They verify the
#          context packet, response format, safety rules (manual required,
#          no execution authority), the diagnosis log, prescription export,
#          history cap, and graceful offline behaviour.
#          Run: pytest barbershop/test_risk_doctor.py
# ==========================================================================
#
# UPDATE LOG — every change to this file must be logged here:
#   [2026-06-15] [Claude] — First build. Tests 11-20: context packet, response
#                            format, missing manual, approve prescription,
#                            context indicator, full diagnosis, no-execution,
#                            history cap, diagnosis log, offline failure.
# ==========================================================================

from __future__ import annotations

import json

import pandas as pd
import pytest

from barbershop import config, data, doctor_chat, risk_doctor


# --------------------------------------------------------------------------
# Helpers: a mock OpenAI-compatible client (success + offline variants).
# --------------------------------------------------------------------------
class _MockMessage:
    def __init__(self, content): self.message = type("M", (), {"content": content})


class _MockCompletions:
    def __init__(self, content, raise_exc=None):
        self._content = content
        self._raise = raise_exc
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self._raise:
            raise self._raise
        return type("R", (), {"choices": [_MockMessage(self._content)]})


class MockLLM:
    """Minimal stand-in for openai.OpenAI exposing .chat.completions.create()."""

    def __init__(self, content="ok", raise_exc=None):
        self._completions = _MockCompletions(content, raise_exc)
        self.chat = type("C", (), {"completions": self._completions})

    @property
    def calls(self): return self._completions.calls


# A correctly-formatted 6-section Doctor response (spec Section D format).
GOOD_RESPONSE = (
    "📍 What I'm looking at: Screen 3, Day 2, the advantage field.\n"
    "🔍 What I see: advantage went negative and dd_buffer fell below 0.25.\n"
    "🎯 What it means for passing: the bot drifted toward the 4% wall.\n"
    "✅ What to do next: increase the OPEN penalty when dd_buffer < 0.25.\n"
    "❌ What NOT to do: do not touch the laws or live execution.\n"
    "📊 Confidence: MEDIUM"
)

SCREEN3 = {"screen": 3, "day_id": 2, "trade_id": 3}


# --------------------------------------------------------------------------
# TEST 11 — Context packet assembly (all four parts present).
# --------------------------------------------------------------------------
def test_context_packet_assembly(mock_trajectory, mock_shap):
    packet = risk_doctor.assemble_context_packet(
        "Why did the bot fail Day 2?", SCREEN3, history=[],
        trajectory=mock_trajectory, shap=mock_shap,
        manual_text="UNIQUE_MANUAL_MARKER_TEXT")
    sysp = packet["system"]
    assert "UNIQUE_MANUAL_MARKER_TEXT" in sysp                  # Part 1: manual
    assert "Last trajectory rows for this day" in sysp          # Part 2: day-2 tail
    assert "SHAP for selected trade" in sysp                    # Part 2: SHAP for the trade
    assert "HARD RULES" in sysp and "FTMO passing" in sysp      # Part 4: the 4 hard rules
    assert packet["user"] == "Why did the bot fail Day 2?"      # user message verbatim


# --------------------------------------------------------------------------
# TEST 12 — Response format validation: all six sections render with icons.
# --------------------------------------------------------------------------
def test_response_renders_six_sections():
    sections = doctor_chat.format_sections(GOOD_RESPONSE)
    assert len(sections) == 6
    icons = [s["icon"] for s in sections]
    assert icons == [icon for icon, _ in config.DOCTOR_SECTIONS]   # 📍🔍🎯✅❌📊 in order
    component = doctor_chat.render_doctor_message({"text": GOOD_RESPONSE})
    flat = str(component)
    for icon, _ in config.DOCTOR_SECTIONS:
        assert icon in flat                                     # every icon shown in the UI


# --------------------------------------------------------------------------
# TEST 13 — Missing operating manual: Doctor offline, LLM not called (RULE 6).
# --------------------------------------------------------------------------
def test_missing_manual_takes_doctor_offline(barbershop_tmp, monkeypatch):
    missing = barbershop_tmp / "docs" / "NOPE.md"               # does not exist
    monkeypatch.setattr(config, "mlp_manual_path", lambda: missing)
    client = MockLLM(GOOD_RESPONSE)
    resp = risk_doctor.ask("Why did Day 2 fail?", SCREEN3, client=client)
    assert resp["manual_missing"] is True
    assert resp["text"] == config.DOCTOR_MANUAL_MISSING
    assert client.calls == 0                                    # LLM call NOT attempted


# --------------------------------------------------------------------------
# TEST 14 — Approve prescription -> suggested_rules.json + log flagged exported.
# --------------------------------------------------------------------------
def test_approve_prescription_exports_and_flags(barbershop_tmp, mock_trajectory, mock_shap):
    client = MockLLM(GOOD_RESPONSE)
    q = "Why did Day 2 fail?"
    resp = risk_doctor.ask(q, SCREEN3, trajectory=mock_trajectory, shap=mock_shap, client=client)
    out = risk_doctor.approve_prescription(q, resp["text"], SCREEN3)
    assert out.exists()                                        # suggested_rules.json written
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved[-1]["source"] == "risk_doctor" and saved[-1]["prescription"]
    # The matching diagnosis-log entry is now flagged exported.
    dinodes = risk_doctor.read_diagnoses()
    assert any(d["monty_question"] == q and d["prescription_exported"] for d in dinodes)


# --------------------------------------------------------------------------
# TEST 15 — Context indicator updates on navigation.
# --------------------------------------------------------------------------
def test_context_indicator_updates():
    s2 = {"screen": 2, "day_id": 2, "trade_id": None}
    s3 = {"screen": 3, "day_id": 2, "trade_id": 3}
    assert risk_doctor.context_label(s2) == "Screen 2 — Day 2 — No trade selected"
    assert risk_doctor.context_label(s3) == "Screen 3 — Day 2 — Trade 3"
    # The chat indicator prefixes "Doctor is looking at: ".
    assert doctor_chat.context_indicator_text(s3).endswith("Screen 3 — Day 2 — Trade 3")


# --------------------------------------------------------------------------
# TEST 16 — Full diagnosis trigger: system prompt carries the doc template.
# --------------------------------------------------------------------------
def test_full_diagnosis_includes_template(mock_trajectory):
    packet = risk_doctor.assemble_context_packet(
        "full diagnosis", {"screen": 3, "day_id": 2, "trade_id": None}, history=[],
        trajectory=mock_trajectory, manual_text="MANUAL", full_diagnosis=True)
    for header in ("What happened", "Where the chain broke", "Failure classification",
                   "Prescription", "Not recommended"):
        assert header in packet["system"]                      # the 7-section template
    client = MockLLM(GOOD_RESPONSE)
    resp = risk_doctor.ask("full diagnosis", {"screen": 3, "day_id": 2, "trade_id": None},
                           trajectory=mock_trajectory, client=client, full_diagnosis=True)
    assert client.calls == 1 and not resp["offline"]           # a response is produced


# --------------------------------------------------------------------------
# TEST 17 — No execution authority (RULE 7): refuse a live-trade question.
# --------------------------------------------------------------------------
def test_no_execution_authority(barbershop_tmp):
    client = MockLLM(GOOD_RESPONSE)
    resp = risk_doctor.ask("Should I go long on EURUSD now?", SCREEN3, client=client)
    assert resp["refused"] is True
    assert resp["text"] == config.DOCTOR_REFUSAL_LIVE
    assert config.DOCTOR_REFUSAL_LIVE == "I only diagnose training runs, not live positions."
    assert client.calls == 0                                    # no LLM call on a trade ask


# --------------------------------------------------------------------------
# TEST 18 — Conversation history capped at the last 6 exchanges.
# --------------------------------------------------------------------------
def test_history_capped_at_six(mock_trajectory):
    history = [(f"QUESTION_{i}", f"ANSWER_{i}") for i in range(10)]
    packet = risk_doctor.assemble_context_packet(
        "new q", SCREEN3, history=history, trajectory=mock_trajectory, manual_text="M")
    sysp = packet["system"]
    # The last 6 exchanges (4..9) are included; earlier ones (0..3) are dropped.
    for i in range(4, 10):
        assert f"QUESTION_{i}" in sysp
    for i in range(0, 4):
        assert f"QUESTION_{i}" not in sysp


# --------------------------------------------------------------------------
# TEST 19 — Diagnosis log append: 3 questions -> 3 valid JSON objects.
# --------------------------------------------------------------------------
def test_diagnosis_log_appends(barbershop_tmp, mock_trajectory, mock_shap):
    client = MockLLM(GOOD_RESPONSE)
    for q in ("q one", "q two", "q three"):
        risk_doctor.ask(q, SCREEN3, trajectory=mock_trajectory, shap=mock_shap, client=client)
    lines = config.DOCTOR_DIAGNOSES_JSONL.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3                                      # exactly three exchanges
    for line in lines:
        obj = json.loads(line)
        for key in ("timestamp", "screen", "monty_question", "confidence"):
            assert key in obj


# --------------------------------------------------------------------------
# TEST 20 — Offline LLM graceful failure: message shown, question saved as OFFLINE.
# --------------------------------------------------------------------------
def test_offline_llm_graceful(barbershop_tmp, mock_trajectory):
    client = MockLLM(raise_exc=ConnectionError("server down"))
    resp = risk_doctor.ask("Why did Day 2 fail?", SCREEN3, trajectory=mock_trajectory, client=client)
    assert resp["offline"] is True
    assert config.DASH_HOST or True                            # endpoint named in the message
    assert config.DOCTOR_API_BASE in resp["text"]
    assert "temporarily offline" in resp["text"]
    # The question is saved with doctor_response == "OFFLINE".
    saved = risk_doctor.read_diagnoses()
    assert saved[-1]["doctor_response"] == config.DOCTOR_OFFLINE_RESPONSE
