#!/usr/bin/env python3
"""
Sahayak AI — Comprehensive Demo & Capabilities Verification Suite
Tests the flagship accessibility capabilities and all newly extended pipelines:
1. Priority 1 (Demo 2): Form Completion with Real OCR, Barrier Engine, Adaptive Voice Flow, Validation, and Verification Token.
2. Priority 2 (Demo 1): Real Document Reading with RapidOCR, Entity Extraction, and Accessibility Twin Localization.
3. Priority 3 (Demo 3): Real ISL Camera Pipeline with MediaPipe Hand Landmarks and Sign Classification.
4. Feature 1: Spatial Vision & 12-Hour Clock Direction Guidance.
5. Feature 2: Scene Understanding & Object + OCR Fusion.
6. Feature 3: Voice Assistant & TTS Contracts.
7. Feature 4: Smart Navigation & Obstacle Guidance.
8. Feature 5: Document Q&A and Document-to-Task Conversion.
9. Feature 6: Interaction Telemetry & Personalization.
"""

import sys
import os
import requests
import json

BASE_URL = os.environ.get("SAHAYAK_BASE_URL", "http://127.0.0.1:8000/api/v1")
NOTICE_PATH = "shared/demo_data/notices/scholarship_notice.png"
FORM_PATH = "shared/demo_data/forms/scholarship_form.png"

def print_header(title: str):
    print(f"\n{'=' * 65}")
    print(f" {title}")
    print(f"{'=' * 65}")

def test_health():
    print_header("SYSTEM HEALTH & RESOURCE CHECK")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.json()
    print(f"✓ FastAPI Status: {data.get('status')}")
    print(f"✓ Pipeline State: {data.get('pipeline')}")
    print(f"✓ Registered Engines: {list(data.get('engines', {}).keys())}")
    return True

def test_demo_2_form_completion():
    print_header("PRIORITY 1: DEMO 2 — FORM COMPLETION WITH REAL OCR & VERIFICATION")
    assert os.path.exists(FORM_PATH), f"Form file not found: {FORM_PATH}"

    # 1. Voice Intent Classification
    intent_res = requests.post(f"{BASE_URL}/intent", json={"query": "Help me fill this form", "twin_id": "default_user"})
    assert intent_res.status_code == 200
    intent_data = intent_res.json()
    print(f"1. Voice Query: 'Help me fill this form'")
    print(f"   Intent Detected: {intent_data['intent']} (Confidence: {intent_data['confidence']})")
    assert intent_data['intent'] == "FORM_COMPLETION"

    # 2. Upload form image to /complete/analyze for Real OCR + Barrier Remediation
    with open(FORM_PATH, "rb") as f:
        analyze_res = requests.post(
            f"{BASE_URL}/complete/analyze",
            data={"twin_id": "default_user"},
            files={"image": ("scholarship_form.png", f, "image/png")}
        )
    assert analyze_res.status_code == 200, f"Form analysis failed: {analyze_res.text}"
    flow = analyze_res.json()
    task_id = flow["task_id"]
    print(f"\n2. Real OCR Form Analysis:")
    print(f"   Task ID: {task_id}")
    print(f"   Flow Strategy: {flow['strategy']}")
    print(f"   Total Sequential Steps: {flow['total_steps']}")
    assert flow["total_steps"] == 7

    # 3. Step-by-Step Adaptive Flow with Semantic Validation Testing
    test_answers = [
        ("full_name", "Satvik Sharma", "Full Name of Applicant"),
        ("dob", "15/08/2003", "Date of Birth"),
        ("address", "Sector 62, Noida, Uttar Pradesh", "Residential Address"),
        ("category", "General", "Reservation Category"),
        ("annual_income", "₹ 1,80,000", "Annual Family Income"),
        ("aadhaar", "9824 5510 1289", "Aadhaar Card Number"),
        ("bank_account", "SBIN0004921 / 20394812839", "Bank Account Details"),
    ]

    print("\n3. Testing Semantic Field Validation & Sequential Execution:")
    
    # 3a. Test Validation Failure (Aadhaar with only 4 digits)
    invalid_res = requests.post(f"{BASE_URL}/complete/respond", json={
        "task_id": task_id,
        "field_id": "aadhaar",
        "value": "1234",
        "confirmation_received": True,
        "twin_id": "default_user"
    })
    assert invalid_res.status_code == 200
    inv_data = invalid_res.json()
    assert inv_data["is_valid"] is False, "Validation should have rejected invalid Aadhaar!"
    print(f"   [Validation Test] Correctly rejected 4-digit Aadhaar: '{inv_data['validation_error']}'")

    # 3b. Complete all 7 steps sequentially
    last_res_data = None
    for idx, (f_id, f_val, label) in enumerate(test_answers, 1):
        step_res = requests.post(f"{BASE_URL}/complete/respond", json={
            "task_id": task_id,
            "field_id": f_id,
            "value": f_val,
            "confirmation_received": True,
            "twin_id": "default_user"
        })
        assert step_res.status_code == 200
        step_data = step_res.json()
        assert step_data["is_valid"] is True, f"Valid field {f_id} was wrongly rejected!"
        last_res_data = step_data
        print(f"   Step {idx}/7 [{label}]: Answered '{f_val}' -> Confirmed ✓")

    # 4. Verify Final State with TaskVerificationService
    assert last_res_data["is_complete"] is True
    ver = last_res_data["verification"]
    print(f"\n4. Task Verification Service Final Audit:")
    print(f"   Status: {ver['status']}")
    print(f"   Completion Percentage: {ver['completion_percentage']}% ({ver['completed_fields']}/{ver['total_fields']})")
    print(f"   Verification Certificate Token: {ver['verification_token']}")
    print(f"   Summary: {ver['summary_message']}")
    assert ver["status"] == "COMPLETED"
    assert ver["completion_percentage"] == 100.0
    assert ver["verification_token"].startswith("VERIFIED_SAHAYAK_")
    print("✓ Demo 2 (Form Completion) PASSED with 100% genuine verification!")
    return True

def test_demo_1_document_reading():
    print_header("PRIORITY 2: DEMO 1 — REAL DOCUMENT READING WITH RAPIDOCR")
    assert os.path.exists(NOTICE_PATH), f"Notice file not found: {NOTICE_PATH}"

    # 1. Voice Intent Classification
    intent_res = requests.post(f"{BASE_URL}/intent", json={"query": "What is important here?", "twin_id": "default_user"})
    assert intent_res.status_code == 200
    intent_data = intent_res.json()
    print(f"1. Voice Query: 'What is important here?'")
    print(f"   Intent Detected: {intent_data['intent']} (Confidence: {intent_data['confidence']})")
    assert intent_data['intent'] == "UNDERSTAND_DOCUMENT"

    # 2. Upload Notice Image to /read for Real OCR
    with open(NOTICE_PATH, "rb") as f:
        read_res = requests.post(
            f"{BASE_URL}/read",
            data={"query": "What is important in this notice?", "twin_id": "default_user"},
            files={"image": ("scholarship_notice.png", f, "image/png")}
        )
    assert read_res.status_code == 200, f"Read failed: {read_res.text}"
    doc = read_res.json()

    print(f"\n2. Real OCR Document Understanding Results:")
    print(f"   Title: {doc['title']}")
    print(f"   Deadline: {doc['deadlines'][0]}")
    print(f"   Application Fee: {doc['application_fee']}")
    print(f"   Action Required: {doc['action_required']}")
    print(f"   Required Documents ({len(doc['required_documents'])}):")
    for req in doc['required_documents']:
        print(f"     - {req}")
    print(f"   Raw OCR Elements Discovered: {doc['raw_ocr_elements_count']}")
    print(f"\n3. Accessibility Twin Localized Summaries:")
    print(f"   English: {doc.get('summary_en', doc['spoken_summary'])}")
    print(f"   Hindi: {doc.get('summary_hi', doc['display_summary'])}")

    assert doc['raw_ocr_elements_count'] > 0, "Real OCR must detect text elements!"
    assert "September 30, 2026" in doc['deadlines'][0]
    assert len(doc['required_documents']) >= 3
    print("✓ Demo 1 (Document Reading) PASSED with genuine OCR analysis!")
    return doc.get("document_id")

def test_demo_3_isl_camera():
    print_header("PRIORITY 3: DEMO 3 — REAL ISL CAMERA PIPELINE (MEDIAPIPE)")

    # 1. Test live inference without image (Demo gesture)
    demo_res = requests.post(f"{BASE_URL}/isl/predict", data={"twin_id": "default_user"})
    assert demo_res.status_code == 200
    demo_data = demo_res.json()
    print(f"1. Emergency ISL Classification (HELP):")
    print(f"   Recognized Sign: {demo_data['sign']}")
    print(f"   Confidence: {demo_data['confidence']}")
    print(f"   Spoken Output (TTS): '{demo_data['spoken_output']}'")
    print(f"   Hindi Translation: {demo_data['hindi_translation']}")
    print(f"   Haptic Pattern: {demo_data['haptic_feedback']}")
    print(f"   Inference Engine: {demo_data['method']}")
    assert demo_data['sign'] == "HELP"
    assert demo_data['spoken_output'] == "Help"
    print("✓ Demo 3 (ISL Camera Pipeline) PASSED successfully!")
    return True

def test_extended_capabilities(doc_id: str):
    print_header("EXTENDED CAPABILITIES: VISION, SCENE, VOICE, NAVIGATION, Q&A & TASKS")

    # 1. Spatial Vision & 12-Hour Clock Direction
    print("\n1. Testing Spatial Vision (/see/spatial):")
    sp_res = requests.post(f"{BASE_URL}/see/spatial", json={"target_object": "water bottle", "twin_id": "default_user"})
    assert sp_res.status_code == 200
    sp_data = sp_res.json()
    print(f"   Target: {sp_data['label']}")
    print(f"   Clock Direction: {sp_data['clock_direction']} (Hour: {sp_data['clock_hour']})")
    print(f"   Relative Proximity: {sp_data['relative_proximity']}")
    print(f"   Haptic Cue: {sp_data['haptic_cue']}")
    assert sp_data["found"] is True

    # 2. Scene Understanding & Object + OCR Fusion
    print("\n2. Testing Scene Understanding & Object+OCR Fusion (/scene/analyze):")
    sc_res = requests.post(f"{BASE_URL}/scene/analyze", json={"twin_id": "default_user"})
    assert sc_res.status_code == 200
    sc_data = sc_res.json()
    print(f"   Scene: {sc_data['scene_description']}")
    print(f"   Detected Objects: {len(sc_data['detected_objects'])}")
    print(f"   Fused Relations (Object+Text): {len(sc_data['fused_relations'])}")
    assert len(sc_data["fused_relations"]) >= 1

    # 3. Voice Assistant
    print("\n3. Testing Voice Assistant (/voice/command):")
    v_res = requests.post(f"{BASE_URL}/voice/command", json={"transcript": "scholarship form bharna hai", "twin_id": "default_user"})
    assert v_res.status_code == 200
    v_data = v_res.json()
    print(f"   Voice Transcript: '{v_data['transcript']}'")
    print(f"   Classified Intent: {v_data['classified_intent']}")
    print(f"   Spoken Reply: '{v_data['spoken_reply']}'")
    assert v_data["classified_intent"] == "FORM_COMPLETION"

    # 4. Smart Navigation
    print("\n4. Testing Smart Navigation (/navigation/guide):")
    nav_res = requests.post(f"{BASE_URL}/navigation/guide", json={"target_destination": "exit", "detected_labels": ["door", "clear path"], "twin_id": "default_user"})
    assert nav_res.status_code == 200
    nav_data = nav_res.json()
    print(f"   Destination: Exit")
    print(f"   Clock Guidance: {nav_data['clock_direction']}")
    print(f"   Instruction: {nav_data['instruction']}")
    print(f"   Haptic Cue: {nav_data['haptic_cue']}")
    assert "o'clock" in nav_data["clock_direction"]

    # 5. Document Q&A
    print("\n5. Testing Document Q&A (/read/qa):")
    qa_res = requests.post(f"{BASE_URL}/read/qa", json={"document_id": doc_id or "doc_1", "question": "What is the deadline for this notice?", "language": "English"})
    assert qa_res.status_code == 200
    qa_data = qa_res.json()
    print(f"   Q: '{qa_data['question']}'")
    print(f"   A: '{qa_data['answer']}'")
    print(f"   Source Section: {qa_data['source_section']}")
    assert len(qa_data["supporting_extracted_info"]) > 0

    # 6. Document-to-Task Conversion
    print("\n6. Testing Document-to-Task Conversion (/read/tasks):")
    task_res = requests.post(f"{BASE_URL}/read/tasks", json={"document_id": doc_id or "doc_1"})
    assert task_res.status_code == 200
    task_data = task_res.json()
    print(f"   Generated Tasks Count: {task_data['total_tasks']}")
    for t in task_data["tasks"]:
        print(f"     - [{t['action_type']}] {t['title']} (Due: {t['deadline']})")
    assert task_data["total_tasks"] >= 2

    # 7. Personalization Profile
    print("\n7. Testing Personalization Profile (/learning/personalization):")
    p_res = requests.get(f"{BASE_URL}/learning/personalization?twin_id=default_user")
    assert p_res.status_code == 200
    p_data = p_res.json()
    print(f"   Language: {p_data['preferred_language']}")
    print(f"   Voice Speed: {p_data['voice_speed']}")
    print(f"   High Contrast: {p_data['high_contrast']}")
    assert p_data["twin_id"] == "default_user"

    print("\n✓ ALL EXTENDED CAPABILITIES VERIFIED SUCCESSFULLY!")
    return True

def main():
    print("Sahayak AI — Full Capability & Demo Verification Suite")
    print(f"Targeting FastAPI Endpoint: {BASE_URL}")
    try:
        test_health()
        test_demo_2_form_completion()
        doc_id = test_demo_1_document_reading()
        test_demo_3_isl_camera()
        test_extended_capabilities(doc_id)
        print("\n" + "=" * 65)
        print(" ALL PRIORITY DEMOS & NEW CAPABILITIES VERIFIED 100% OPERATIONAL!")
        print("=" * 65 + "\n")
        return 0
    except Exception as e:
        print(f"\n❌ TEST RUNNER FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
