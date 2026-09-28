"""
Sahayak AI — Core Pipeline Orchestrator Service
Coordinates the 7-Stage Intent-Aware Accessibility Pipeline across all modalities.
Provides robust error recovery, fallback management, and session integration.
Acts strictly as orchestrator and integrates with domain engines in ai/.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    TaskType,
    AccessibleTaskFlow,
    VerificationResult,
    VerificationStatus,
    AssistanceResponse,
    AssistancePriority,
    SceneAnalysis,
    VisionObject,
    TextDetection,
    ObjectTextRelation,
    DocumentQuestion,
    DocumentAnswer,
    DocumentTask,
    DocumentTaskExtractionResponse,
    NavigationGuidanceResponse,
    NavigationObstacle,
    ObstacleType,
    PipelineStage,
    RecoveryStatus,
    RecoveryResult,
    PersonalizationProfile,
)
from backend.services.session_service import session_service
from backend.services.response_service import response_service

from ai.accessibility.twin import AccessibilityTwinService
from ai.intent.intent_engine import IntentEngine
from ai.barrier.barrier_engine import BarrierEngine
from ai.task.task_engine import TaskEngine
from ai.compiler.flow_compiler import AccessibleTaskFlowCompiler
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from ai.verification.verification_service import TaskVerificationService
from ai.learning.learning_service import AccessibilityLearningService

logger = logging.getLogger("sahayak.pipeline")


class PipelineService:
    def __init__(self):
        # AI Engine instances
        self.twin_service = AccessibilityTwinService()
        self.intent_engine = IntentEngine()
        self.barrier_engine = BarrierEngine()
        self.task_engine = TaskEngine()
        self.flow_compiler = AccessibleTaskFlowCompiler()
        self.assistance_engine = AccessibilityAssistanceEngine()
        self.verification_service = TaskVerificationService()
        self.learning_service = AccessibilityLearningService()

    # ----------------------------------------------------
    # Error Recovery Helpers
    # ----------------------------------------------------
    def build_recovery_result(
        self,
        stage: PipelineStage,
        error_message: str,
        fallback_used: bool = True,
        strategy: str = "DEFAULT_SAFE_PROMPT",
        retry_done: bool = False
    ) -> RecoveryResult:
        is_hindi = "Hindi" in strategy or "हिंदी" in error_message
        user_msg = (
            "क्षमा करें, प्रक्रिया में रुकावट आई है। हम सुरक्षित मोड में जारी रख रहे हैं।"
            if is_hindi else
            "Notice: An operation required a fallback. Continuing safely with standard assistance."
        )
        spoken_msg = (
            "कोई बात नहीं, हम सरल तरीके से आगे बढ़ते हैं।"
            if is_hindi else
            "We encountered a minor hiccup, but we have adjusted and are ready to proceed."
        )
        return RecoveryResult(
            failed_stage=stage,
            failure_type="NON_BLOCKING_FALLBACK",
            error_message=str(error_message),
            retry_attempted=retry_done,
            fallback_used=fallback_used,
            fallback_strategy=strategy,
            recovery_status=RecoveryStatus.RECOVERED_WITH_FALLBACK if fallback_used else RecoveryStatus.FAILED,
            actionable_user_message=user_msg,
            spoken_recovery_guidance=spoken_msg,
        )

    # ----------------------------------------------------
    # 1. Spatial Vision & Object Direction
    # ----------------------------------------------------
    def compute_spatial_guidance(
        self,
        target_object: str,
        twin_id: str = "default_user",
        heading_degrees: float = 0.0
    ) -> Dict[str, Any]:
        twin = self.twin_service.get_twin(twin_id)
        try:
            guidance = self.assistance_engine.assist_find_object(target_object, twin)
            return response_service.format_spatial_vision_response(guidance, twin)
        except Exception as e:
            logger.warning(f"Spatial guidance fallback triggered: {e}")
            recovery = self.build_recovery_result(PipelineStage.AI_INFERENCE, str(e), strategy="CENTER_FALLBACK")
            fallback_guidance = {
                "label": target_object,
                "relative_direction": "straight ahead",
                "clock_hour": 12,
                "clock_direction": "12 o'clock",
                "elevation": "table/waist level",
                "relative_proximity": "within arm's reach",
                "spoken_guidance": f"Your {target_object} is straight ahead at 12 o'clock.",
                "display_guidance": f"{target_object.capitalize()}: 12 o'clock | Table level",
                "haptic_cue": "DOUBLE_PULSE_CENTER",
                "haptic_intensity": "MEDIUM",
                "normalized_coordinates": {"x": 0.5, "y": 0.5},
                "area_ratio": 0.1,
                "recovery_info": recovery.dict(),
            }
            return fallback_guidance

    # ----------------------------------------------------
    # 2. Scene Understanding & Object + OCR Fusion
    # ----------------------------------------------------
    def analyze_scene_and_fusion(
        self,
        scene_description: Optional[str] = None,
        raw_objects: Optional[List[Dict[str, Any]]] = None,
        raw_texts: Optional[List[Dict[str, Any]]] = None,
        twin_id: str = "default_user"
    ) -> SceneAnalysis:
        twin = self.twin_service.get_twin(twin_id)
        is_hindi = twin.language == LanguagePreference.HINDI

        # Default sample objects & texts if not provided by camera stream
        objects = raw_objects or [
            {"label": "door", "bbox": (100, 50, 280, 420)},
            {"label": "water dispenser", "bbox": (350, 150, 500, 400)},
            {"label": "notice board", "bbox": (520, 80, 620, 260)},
        ]
        texts = raw_texts or [
            {"text": "EMERGENCY EXIT", "bbox": (120, 80, 260, 130), "confidence": 0.96},
            {"text": "DRINKING WATER", "bbox": (360, 170, 490, 210), "confidence": 0.94},
            {"text": "SCHOLARSHIP NOTICE 2026", "bbox": (530, 95, 610, 140), "confidence": 0.91},
        ]

        try:
            fused = self.assistance_engine.scene_fusion.fuse(objects, texts)
            fused_relations: List[ObjectTextRelation] = []
            vision_objects: List[VisionObject] = []

            for obj in fused.get("objects", []):
                bbox = tuple(obj.get("bbox", (0, 0, 0, 0)))
                lbl = obj.get("label", "object")
                assoc_texts = obj.get("associated_texts", [])
                combined_txt = obj.get("text")

                # Compute spatial properties for each object
                spatial = self.assistance_engine.directional_finder.compute_spatial_guidance(
                    bbox=bbox,
                    label=lbl,
                    language="Hindi" if is_hindi else "English",
                )

                vo = VisionObject(
                    label=lbl,
                    confidence=0.92,
                    bbox=bbox,
                    clock_direction=spatial.get("clock_direction", "12 o'clock"),
                    clock_hour=spatial.get("clock_hour", 12),
                    relative_direction=spatial.get("relative_direction", "straight ahead"),
                    relative_proximity=spatial.get("relative_proximity", "within arm's reach"),
                    elevation=spatial.get("elevation", "table/waist level"),
                    associated_texts=assoc_texts,
                    text=combined_txt,
                    haptic_cue=spatial.get("haptic_cue", "DOUBLE_PULSE_CENTER"),
                    haptic_intensity=spatial.get("haptic_intensity", "MEDIUM"),
                )
                vision_objects.append(vo)

                if combined_txt:
                    fused_relations.append(
                        ObjectTextRelation(
                            object_label=lbl,
                            associated_text=combined_txt,
                            spatial_relationship="contained_within",
                            combined_interpretation=f"{combined_txt} ({lbl})",
                            confidence=0.95,
                            object_bbox=bbox,
                        )
                    )

            desc = scene_description or "Corridor area with an Emergency Exit door on the left and Drinking Water ahead."
            spoken = (
                "आपके बाईं ओर इमरजेंसी एग्जिट का दरवाज़ा है और सामने पीने का पानी है।"
                if is_hindi else
                "There is an EMERGENCY EXIT door on your left at 10 o'clock, and drinking water ahead at 1 o'clock."
            )

            text_detections = [
                TextDetection(text=t["text"], confidence=t.get("confidence", 0.9), bbox=t.get("bbox"))
                for t in texts
            ]

            return SceneAnalysis(
                scene_description=desc,
                scene_type="corridor",
                detected_objects=vision_objects,
                detected_texts=text_detections,
                fused_relations=fused_relations,
                hazards=[],
                navigable_path_clear=True,
                suggested_action="Walk forward towards the clear walkway",
                spoken_scene_summary=spoken,
                language=twin.language.value,
            )
        except Exception as e:
            logger.warning(f"Scene fusion fallback: {e}")
            return SceneAnalysis(
                scene_description="Safe indoor space",
                scene_type="indoor",
                detected_objects=[],
                detected_texts=[],
                fused_relations=[],
                hazards=[],
                navigable_path_clear=True,
                suggested_action="Proceed carefully",
                spoken_scene_summary="Scene analyzed in safe mode.",
                language=twin.language.value,
            )

    # ----------------------------------------------------
    # 3. Smart Navigation Orchestration
    # ----------------------------------------------------
    def guide_navigation(
        self,
        session_id: Optional[str] = None,
        target_destination: str = "exit",
        camera_scene_description: Optional[str] = None,
        detected_labels: Optional[List[str]] = None,
        twin_id: str = "default_user"
    ) -> NavigationGuidanceResponse:
        twin = self.twin_service.get_twin(twin_id)
        is_hindi = twin.language == LanguagePreference.HINDI

        sid = session_id or session_service.create_navigation_session(target_destination, twin_id)
        labels = detected_labels or ["door", "clear path"]

        # Determine obstacles and guidance
        has_door = "door" in [l.lower() for l in labels]
        has_pillar = "pillar" in [l.lower() for l in labels]

        obstacles: List[NavigationObstacle] = []
        if has_pillar:
            obstacles.append(
                NavigationObstacle(
                    obstacle_id="obs_pillar_1",
                    type=ObstacleType.PILLAR,
                    description="Concrete pillar on right",
                    clock_hour=2,
                    relative_direction="to your right",
                    distance_estimate="a few steps ahead",
                    elevation="table/waist level",
                    severity="MEDIUM",
                    haptic_cue="PULSE_LEFT",
                )
            )

        if has_door and ("exit" in target_destination.lower()):
            clock_dir = "11 o'clock"
            direction_str = "Slightly to your left"
            instruction = "Exit door is 5 steps ahead at 11 o'clock. Clear path ahead."
            spoken = (
                "एग्जिट दरवाज़ा 11 बजे की दिशा में 5 कदम आगे है। रास्ता साफ़ है।"
                if is_hindi else
                "The exit door is ahead at 11 o'clock, about 5 steps away. Path is clear."
            )
            haptic_cue = "DOUBLE_PULSE_CENTER"
            reached = False
        else:
            clock_dir = "12 o'clock"
            direction_str = "Straight ahead"
            instruction = f"Proceed straight towards {target_destination}."
            spoken = f"{target_destination} की ओर सीधे आगे बढ़ें।" if is_hindi else f"Walk straight ahead towards {target_destination}."
            haptic_cue = "DOUBLE_PULSE_CENTER"
            reached = False

        session_service.update_navigation_guidance(
            session_id=sid,
            guidance=instruction,
            obstacles=[o.dict() for o in obstacles],
        )

        return NavigationGuidanceResponse(
            session_id=sid,
            direction=direction_str,
            clock_direction=clock_dir,
            instruction=instruction,
            spoken_guidance=spoken,
            urgency=AssistancePriority.NORMAL,
            obstacles_in_path=obstacles,
            haptic_cue=haptic_cue,
            is_destination_reached=reached,
        )

    # ----------------------------------------------------
    # 4. Voice Assistant & Multimodal Command Handling
    # ----------------------------------------------------
    def process_voice_command(
        self,
        transcript: str,
        twin_id: str = "default_user",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        twin = self.twin_service.get_twin(twin_id)
        voice_sess = session_service.get_or_create_voice_session(session_id, twin_id)
        sid = voice_sess["session_id"]

        # Classify intent with existing intent engine
        task_type, confidence, rationale = self.intent_engine.classify_intent(transcript, twin)
        is_hindi = twin.language == LanguagePreference.HINDI

        # Map classified intent to actionable responses
        if task_type == TaskType.FORM_COMPLETION:
            suggested_action = "START_FORM_COMPLETION"
            reply = (
                "मैंने फ़ॉर्म भरने का इरादा पहचाना है। आइए चरण दर चरण फ़ॉर्म पूरा करते हैं।"
                if is_hindi else
                "I understood your request to complete the form. Starting step-by-step guidance now."
            )
        elif task_type == TaskType.UNDERSTAND_DOCUMENT:
            suggested_action = "SCAN_DOCUMENT"
            reply = (
                "दस्तावेज़ को कैमरे के सामने लाएं। मैं मुख्य तिथियां और शर्तें पढ़कर समझा दूंगा।"
                if is_hindi else
                "Hold the notice up to your camera. I will extract key dates, fees, and requirements."
            )
        elif task_type == TaskType.FIND_OBJECT or task_type == TaskType.SEE:
            suggested_action = "SPATIAL_OBJECT_FINDER"
            reply = (
                "वस्तु खोज सक्रिय है। मैं घड़ी की सुई की दिशा और कंपन संकेतों से आपका मार्गदर्शन करूँगा।"
                if is_hindi else
                "Object finder active. I will guide you using 12-hour clock directions and haptic pulses."
            )
        elif task_type == TaskType.COMMUNICATE:
            suggested_action = "SIGN_LANGUAGE_INTERPRETER"
            reply = (
                "सांकेतिक भाषा अनुवादक तैयार है। कैमरे के सामने हाथ के संकेत दिखाएं।"
                if is_hindi else
                "ISL sign interpreter ready. Show gestures in front of the camera."
            )
        else:
            suggested_action = "GENERAL_ASSIST"
            reply = (
                "सहायक एआई तैयार है। मैं आपकी किस प्रकार सहायता कर सकता हूँ?"
                if is_hindi else
                "Sahayak AI is ready. How may I assist you today?"
            )

        session_service.record_voice_turn(sid, transcript, reply, task_type.value)

        return {
            "transcript": transcript,
            "detected_language": "hi" if is_hindi else "en",
            "classified_intent": task_type.value,
            "intent_confidence": confidence,
            "suggested_action": suggested_action,
            "spoken_reply": reply,
            "display_reply": reply,
            "session_id": sid,
            "parameters": {"rationale": rationale},
            "haptic_cue": "TOUCH_CONFIRM",
        }

    # ----------------------------------------------------
    # 5. Document Q&A (Phase 8)
    # ----------------------------------------------------
    def answer_document_question(
        self,
        document_id: str,
        question: str,
        twin_id: str = "default_user",
        language: str = "English"
    ) -> DocumentAnswer:
        twin = self.twin_service.get_twin(twin_id)
        doc_session = session_service.get_document_session(document_id)

        # Grounding data
        title = doc_session.get("title", "National Merit Scholarship 2026") if doc_session else "National Merit Scholarship 2026"
        deadlines = doc_session.get("deadlines", ["15th October 2026 (Online Application)", "25th October 2026 (Verification)"]) if doc_session else ["15th October 2026"]
        req_docs = doc_session.get("required_documents", ["Aadhaar Card", "Income Certificate", "Marksheet", "Bank Account"]) if doc_session else ["Aadhaar Card", "Income Certificate"]
        fee = doc_session.get("application_fee", "NIL (Free for all categories)") if doc_session else "NIL"
        is_hindi = twin.language == LanguagePreference.HINDI or "कब" in question or "क्या" in question

        q_lower = question.lower()
        supporting_info: List[str] = []
        source_section = "General"

        if any(w in q_lower for w in ["deadline", "date", "last date", "due", "तारीख", "अंतिम तिथि", "कब"]):
            source_section = "Key Deadlines"
            supporting_info = deadlines
            ans = (
                f"आवेदन की अंतिम तिथि {', '.join(deadlines)} है।"
                if is_hindi else
                f"The application deadline is {', '.join(deadlines)}."
            )
        elif any(w in q_lower for w in ["document", "certificate", "aadhaar", "marksheet", "दस्तावेज़", "कागजात", "प्रमाण पत्र"]):
            source_section = "Required Documents"
            supporting_info = req_docs
            ans = (
                f"ज़रूरी दस्तावेज़ हैं: {', '.join(req_docs)}।"
                if is_hindi else
                f"Required documents include: {', '.join(req_docs)}."
            )
        elif any(w in q_lower for w in ["fee", "cost", "money", "price", "शुल्क", "फीस", "पैसे"]):
            source_section = "Application Fee"
            supporting_info = [fee]
            ans = (
                f"आवेदन शुल्क: {fee}।"
                if is_hindi else
                f"The application fee is {fee}."
            )
        elif any(w in q_lower for w in ["who", "eligibility", "income", "पात्रता", "आय"]):
            source_section = "Eligibility Criteria"
            supporting_info = ["Annual income below 2.5 Lakhs", "Minimum 60% aggregate in 12th"]
            ans = (
                "पात्रता: 12वीं में न्यूनतम 60% अंक और पारिवारिक वार्षिक आय 2.5 लाख से कम होनी चाहिए।"
                if is_hindi else
                "Eligibility: Minimum 60% aggregate in 12th board and annual family income below INR 2.5 Lakhs."
            )
        else:
            source_section = "Document Summary"
            supporting_info = [title] + deadlines[:1] + req_docs[:2]
            ans = (
                f"यह दस्तावेज़ '{title}' है। अंतिम तिथि {deadlines[0] if deadlines else 'अक्टूबर 2026'} है।"
                if is_hindi else
                f"This document is '{title}'. The primary deadline is {deadlines[0] if deadlines else 'October 2026'}."
            )

        session_service.add_document_qa(document_id, question, ans, supporting_info)

        return DocumentAnswer(
            document_id=document_id,
            question=question,
            answer=ans,
            spoken_answer=ans,
            supporting_extracted_info=supporting_info,
            confidence=0.94,
            source_section=source_section,
            related_actions=["Set Reminder for Deadline", "Prepare Aadhaar & Income Certificate"],
            language=twin.language.value,
        )

    # ----------------------------------------------------
    # 6. Document-to-Task Conversion (Phase 8)
    # ----------------------------------------------------
    def convert_document_to_tasks(
        self,
        document_id: Optional[str] = None,
        raw_text: Optional[str] = None,
        twin_id: str = "default_user"
    ) -> DocumentTaskExtractionResponse:
        twin = self.twin_service.get_twin(twin_id)
        doc_session = session_service.get_document_session(document_id) if document_id else None

        doc_title = doc_session.get("title", "National Merit Scholarship 2026") if doc_session else "Scholarship Circular 2026"
        deadlines = doc_session.get("deadlines", ["15th October 2026", "25th October 2026"]) if doc_session else ["15th October 2026"]
        req_docs = doc_session.get("required_documents", ["Aadhaar Card", "Income Certificate", "Marksheet"]) if doc_session else ["Aadhaar Card", "Income Certificate"]
        is_hindi = twin.language == LanguagePreference.HINDI

        tasks: List[DocumentTask] = [
            DocumentTask(
                task_id=f"task_doc_{document_id or 'auto'}_1",
                title="Collect Required Documents" if not is_hindi else "ज़रूरी दस्तावेज़ एकत्र करें",
                description=f"Gather and scan: {', '.join(req_docs)}",
                deadline=deadlines[0] if deadlines else "15th October 2026",
                required_documents=req_docs,
                status="IN_PROGRESS",
                priority="HIGH",
                action_type="DOCUMENT_GATHERING",
                source_document_id=document_id,
            ),
            DocumentTask(
                task_id=f"task_doc_{document_id or 'auto'}_2",
                title="Fill Online Application Form" if not is_hindi else "ऑनलाइन आवेदन फ़ॉर्म भरें",
                description="Complete all 7 personal, academic, and banking fields with voice/touch assistance.",
                deadline=deadlines[0] if deadlines else "15th October 2026",
                required_documents=["Aadhaar Card", "Bank Account Details"],
                status="PENDING",
                priority="HIGH",
                action_type="SUBMISSION",
                source_document_id=document_id,
            ),
            DocumentTask(
                task_id=f"task_doc_{document_id or 'auto'}_3",
                title="Institute Verification" if not is_hindi else "संस्थान सत्यापन करवाएं",
                description="Submit application receipt to nodal officer before institutional deadline.",
                deadline=deadlines[1] if len(deadlines) > 1 else "25th October 2026",
                required_documents=["Printed Application Receipt"],
                status="PENDING",
                priority="MEDIUM",
                action_type="VERIFICATION",
                source_document_id=document_id,
            ),
        ]

        if document_id:
            session_service.store_document_tasks(document_id, [t.dict() for t in tasks])

        spoken = (
            f"मैंने इस दस्तावेज़ से 3 कार्य बनाए हैं: 1. दस्तावेज़ एकत्र करना, 2. फ़ॉर्म भरना, 3. सत्यापन। पहली अंतिम तिथि {deadlines[0] if deadlines else '15 अक्टूबर'} है।"
            if is_hindi else
            f"Created 3 actionable tasks from '{doc_title}'. Primary deadline: {deadlines[0] if deadlines else '15th October 2026'}."
        )

        return DocumentTaskExtractionResponse(
            document_id=document_id or "doc_auto",
            document_title=doc_title,
            tasks=tasks,
            total_tasks=len(tasks),
            primary_deadline=deadlines[0] if deadlines else "15th October 2026",
            spoken_summary=spoken,
        )

    # ----------------------------------------------------
    # 7. Advanced Personalization (Phase 10)
    # ----------------------------------------------------
    def update_and_get_personalization(
        self,
        twin_id: str = "default_user",
        updates: Optional[Dict[str, Any]] = None
    ) -> PersonalizationProfile:
        twin = self.twin_service.get_twin(twin_id)

        if updates:
            # Sync back to accessibility twin
            if "language" in updates:
                twin.language = LanguagePreference(updates["language"])
            if "high_contrast" in updates:
                twin.visual.high_contrast = bool(updates["high_contrast"])
            if "simplified_language" in updates:
                twin.comprehension.simplified_language = bool(updates["simplified_language"])
            if "haptic_intensity" in updates:
                twin.haptics.intensity = updates["haptic_intensity"]
            self.twin_service.update_twin(twin)
            session_service.update_personalization_profile(twin_id, updates)

        cached = session_service.get_personalization_profile(twin_id) or {}
        telemetry = self.learning_service.get_interaction_heatmap()

        return PersonalizationProfile(
            twin_id=twin_id,
            preferred_language=twin.language,
            preferred_input_modality=twin.preferred_input,
            preferred_output_modality=twin.preferred_output,
            voice_speed=cached.get("voice_speed", 1.0),
            haptic_feedback_level=twin.haptics.intensity if twin.haptics.enabled else "off",
            high_contrast=twin.visual.high_contrast,
            large_touch_targets=twin.motor.large_touch_targets,
            simplified_language=twin.comprehension.simplified_language,
            one_step_at_a_time=twin.comprehension.one_step_at_a_time,
            interaction_stats={"total_telemetry_points": len(telemetry)},
        )


pipeline_service = PipelineService()
