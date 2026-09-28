"""
Sahayak AI — End-to-End Pipeline Smoke Test
Validates that all AI engines and services import correctly and execute cleanly.
"""

import sys
import os
import pytest

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    TaskType,
    VisualPreferences,
    MotorPreferences,
    ComprehensionPreferences,
    VerificationStatus,
)
from ai.accessibility.twin import AccessibilityTwinService
from ai.intent.intent_engine import IntentEngine
from ai.task.task_engine import TaskEngine
from ai.barrier.barrier_engine import BarrierEngine
from ai.compiler.flow_compiler import AccessibleTaskFlowCompiler
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from ai.ocr.ocr_engine import DocumentOCREngine
from ai.vision.directional_finder import DirectionalFinder
from ai.scene.scene_fusion import SceneFusion
from ai.isl.sign_classifier import ISLInterpreterService
from ai.verification.verification_service import TaskVerificationService
from ai.learning.learning_service import AccessibilityLearningService


def test_accessibility_twin_service():
    service = AccessibilityTwinService()
    twin = service.get_twin("default_user")
    assert twin is not None
    assert twin.language in [LanguagePreference.HINDI, LanguagePreference.ENGLISH]
    assert twin.comprehension.simplified_language is True


def test_intent_engine():
    engine = IntentEngine()
    twin = AccessibilityTwinService().get_twin("default_user")

    task_type, conf, rationale = engine.classify_intent("What is important in this notice?", twin)
    assert task_type == TaskType.UNDERSTAND_DOCUMENT
    assert conf > 0.5

    task_type2, conf2, _ = engine.classify_intent("Please help me fill the scholarship form", twin)
    assert task_type2 == TaskType.FORM_COMPLETION
    assert conf2 > 0.5

    task_type3, conf3, _ = engine.classify_intent("Where is my bottle?", twin)
    assert task_type3 == TaskType.FIND_OBJECT
    assert conf3 > 0.5

    # Multilingual Hindi & Hinglish tests
    analysis_hi = engine.analyze_intent("मुझे नोटिस समझा दो", twin)
    assert analysis_hi["task_type"] == TaskType.UNDERSTAND_DOCUMENT
    assert analysis_hi["entities"]["detected_language"] == "hi"

    analysis_form = engine.analyze_intent("scholarship form bharna hai", twin)
    assert analysis_form["task_type"] == TaskType.FORM_COMPLETION

    analysis_find = engine.analyze_intent("where is my water bottle?", twin)
    assert analysis_find["task_type"] == TaskType.FIND_OBJECT
    assert analysis_find["entities"]["target_object"] in ["bottle", "water bottle"]


def test_task_engine_decomposition():
    task_engine = TaskEngine()
    task_id = task_engine.create_generic_task(
        task_type=TaskType.UNDERSTAND_DOCUMENT,
        title="Scholarship Circular",
        total_steps=3,
    )
    assert task_id.startswith("task_understand_document_")
    
    milestones = task_engine.decompose_task("Analyze circular", TaskType.UNDERSTAND_DOCUMENT)
    assert len(milestones) == 3
    assert milestones[0]["action"] == "OCR_SCAN"

    task = task_engine.advance_step(task_id, {"extracted": "deadlines"})
    assert task["completed_steps"] == 1
    assert task["status"] == "IN_PROGRESS"


def test_barrier_and_flow_compiler():
    twin = AccessibilityTwinService().get_twin("default_user")
    twin.visual.high_contrast = True
    twin.comprehension.simplified_language = True

    barrier_engine = BarrierEngine()
    barriers = barrier_engine.detect_barriers(
        task_type=TaskType.FORM_COMPLETION,
        task_context={"raw_input": "National Merit Scholarship"},
        twin=twin,
    )
    assert isinstance(barriers, list)
    assert len(barriers) > 0

    compiler = AccessibleTaskFlowCompiler()
    flow = compiler.compile_form_flow(
        task_id="scholarship_task_01",
        twin=twin,
        barriers=barriers,
    )
    assert flow is not None
    assert flow.total_steps == len(flow.steps)
    assert len(flow.steps) > 0
    assert flow.steps[0].spoken_prompt is not None


def test_directional_finder():
    finder = DirectionalFinder(frame_width=640, frame_height=480)
    # Target in center
    guidance = finder.compute_spatial_guidance(
        bbox=(280, 200, 360, 320),
        label="water bottle",
        language="English",
    )
    assert guidance["relative_direction"] == "straight ahead"
    assert guidance["clock_hour"] == 12
    assert "elevation" in guidance
    assert "water bottle" in guidance["spoken_guidance"]

    # Target to top-right (around 1 or 2 o'clock)
    guidance_tr = finder.compute_spatial_guidance(
        bbox=(450, 50, 520, 150),
        label="keys",
        language="Hindi",
    )
    assert guidance_tr["clock_hour"] in [1, 2]
    assert guidance_tr["haptic_cue"] == "PULSE_RIGHT"


def test_scene_fusion():
    fusion = SceneFusion()
    objects = [
        {"label": "medicine bottle", "bbox": (100, 100, 300, 400)},
        {"label": "book", "bbox": (400, 100, 600, 400)},
    ]
    texts = [
        {"text": "Paracetamol 500mg", "bbox": (120, 150, 280, 200), "confidence": 0.95}
    ]
    fused = fusion.fuse(objects, texts)
    assert len(fused["objects"]) == 2
    
    # Text should be fused into medicine bottle
    med = [o for o in fused["objects"] if o["label"] == "medicine bottle"][0]
    assert "Paracetamol" in med["text"]

    # Search fused scene
    results = fusion.search_fused_scene(fused, target_label="medicine", target_text="500mg")
    assert len(results) == 1
    assert results[0]["label"] == "medicine bottle"


def test_ocr_and_isl_engines():
    ocr = DocumentOCREngine()
    doc_info = ocr.extract_document_info()
    assert "document_title" in doc_info
    assert len(doc_info["key_deadlines"]) > 0

    # Custom notice text parsing
    custom_notice = "Department of Technical Education Notice. Last date is 15 October 2026. Please bring Aadhaar Card and Marksheet."
    extracted = ocr.extract_document_info(raw_text=custom_notice)
    assert any("October" in d or "15" in d for d in extracted["key_deadlines"])
    assert "Aadhaar Card" in extracted["required_documents"]
    assert "readability" in extracted
    assert extracted["readability"]["readability_score"] > 0

    isl = ISLInterpreterService()
    sign_res = isl.predict_sign()
    assert sign_res["sign"] == "HELP"

    # Test landmark recognition (simulate open hand / help)
    # wrist at (0.5, 0.9), all tips higher (y < pip)
    landmarks_open = [
        (0.5, 0.9),  # 0 wrist
        (0.4, 0.7), (0.35, 0.6), (0.3, 0.5), (0.25, 0.4), # thumb 1..4
        (0.45, 0.6), (0.45, 0.5), (0.45, 0.4), (0.45, 0.2), # index 5..8 (tip at 0.2)
        (0.5, 0.6), (0.5, 0.5), (0.5, 0.4), (0.5, 0.15), # middle 9..12 (tip at 0.15)
        (0.55, 0.6), (0.55, 0.5), (0.55, 0.4), (0.55, 0.22), # ring 13..16 (tip at 0.22)
        (0.6, 0.6), (0.6, 0.5), (0.6, 0.4), (0.6, 0.25), # pinky 17..20 (tip at 0.25)
    ]
    sign_open = isl.predict_sign(landmarks=landmarks_open)
    assert sign_open["sign"] == "HELP"
    assert sign_open["extended_fingers_count"] == 4

    alpha_a = isl.predict_alphabet("A")
    assert alpha_a["sign"] == "A"


def test_verification_and_learning():
    verifier = TaskVerificationService()
    # 1. Test complete valid form
    result = verifier.verify_form_task(
        task_id="task_123",
        total_fields=3,
        completed_fields={
            "full_name": {"value": "Alice Sharma"},
            "email": {"value": "alice@example.com"},
            "phone": {"value": "9876543210"},
        },
        required_field_ids=["full_name", "email", "phone"],
    )
    assert result.status == VerificationStatus.COMPLETED
    assert result.verification_token is not None

    # 2. Test invalid field causing blocked status
    blocked_result = verifier.verify_form_task(
        task_id="task_123",
        total_fields=3,
        completed_fields={
            "full_name": {"value": "Alice Sharma"},
            "email": {"value": "invalid_email_no_at"},
            "phone": {"value": "123"}, # too short
        },
        required_field_ids=["full_name", "email", "phone"],
    )
    assert blocked_result.status == VerificationStatus.BLOCKED

    # 3. Test document verification
    doc_result = verifier.verify_document_understanding(
        task_id="doc_task_01",
        extracted_info={"document_title": "Scholarship Notice", "key_deadlines": ["30 Sept 2026"]}
    )
    assert doc_result.status == VerificationStatus.COMPLETED

    # 4. Test learning service with real interaction telemetry
    learning = AccessibilityLearningService()
    learning.record_interaction(
        step_id="step_name",
        modality_used="voice",
        duration_seconds=3.2,
        retries=0,
        success=True,
    )
    learning.record_interaction(
        step_id="step_upload",
        modality_used="touch",
        duration_seconds=18.5,
        retries=3,
        success=False,
    )

    heatmap = learning.get_interaction_heatmap()
    assert len(heatmap) == 2
    # step_upload should be RED/HIGH complexity
    upload_item = [h for h in heatmap if h.interaction_point == "step_upload"][0]
    assert upload_item.complexity == "HIGH"
    assert upload_item.color == "RED"

    rec = learning.get_personalization_recommendation()
    assert "proposed_adaptation" in rec
    assert rec["consent_required"] is True
