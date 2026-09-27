"""
Sahayak AI — AI Pipeline Orchestrator
Single entry point that coordinates all 7-stage pipeline stages
and selects the appropriate AI capabilities per task/intent.
Does NOT bypass existing engines.
"""
from typing import Optional, Dict, Any, List
from shared.schemas.models import (
    AccessibilityTwin, TaskType, LanguagePreference
)
from ai.accessibility.twin import AccessibilityTwinService
from ai.intent.intent_engine import IntentEngine
from ai.barrier.barrier_engine import BarrierEngine
from ai.task.task_engine import TaskEngine
from ai.compiler.flow_compiler import AccessibleTaskFlowCompiler
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from ai.verification.verification_service import TaskVerificationService
from ai.learning.learning_service import AccessibilityLearningService
from ai.voice.voice_command import VoiceCommandProcessor
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.navigation_engine import NavigationEngine
from ai.recovery.failure_detector import FailureDetector
from ai.recovery.recovery_engine import RecoveryEngine
from ai.ocr.document_qa import DocumentQAEngine


class AIPipeline:
    """
    Orchestrates the full Sahayak AI pipeline:

    Input
     → Accessibility Twin
     → Intent Detection
     → Barrier Analysis
     → Task Engine
     → Flow Compiler
     → Capability Selection (OCR / Vision / ISL / Voice / Scene / Navigation)
     → Assistance
     → Verification
     → Learning

    All existing engines are reused — no bypassing.
    """

    def __init__(self):
        # Existing 7-stage engines
        self.twin_service = AccessibilityTwinService()
        self.intent_engine = IntentEngine()
        self.barrier_engine = BarrierEngine()
        self.task_engine = TaskEngine()
        self.flow_compiler = AccessibleTaskFlowCompiler()
        self.assistance_engine = AccessibilityAssistanceEngine()
        self.verification_service = TaskVerificationService()
        self.learning_service = AccessibilityLearningService()

        # New capability engines
        self.voice_processor = VoiceCommandProcessor()
        self.scene_engine = SceneUnderstandingEngine()
        self.navigation_engine = NavigationEngine()
        self.failure_detector = FailureDetector()
        self.recovery_engine = RecoveryEngine()
        self.doc_qa_engine = DocumentQAEngine()

    def run(
        self,
        query: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        image_bytes: Optional[bytes] = None,
        twin_id: str = "default_user",
        task_type_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full AI pipeline for an arbitrary user request.

        Args:
            query: text query (shortcut for voice)
            audio_bytes: raw audio for STT
            image_bytes: camera frame or document scan
            twin_id: user identifier
            task_type_override: force a specific TaskType (for testing)

        Returns:
            structured pipeline result with all stage outputs
        """
        result: Dict[str, Any] = {"twin_id": twin_id, "pipeline_stages": []}

        # Stage 1: Accessibility Twin
        twin = self.twin_service.get_twin(twin_id)
        result["twin"] = {"language": twin.language.value, "input_modality": twin.preferred_input.value}
        result["pipeline_stages"].append("twin")

        # Stage 2: Intent (via Voice layer if audio, else direct)
        if audio_bytes or query:
            voice_result = self.voice_processor.process(
                audio_bytes=audio_bytes,
                text_input=query,
                twin=twin,
            )
            intent_data = voice_result.get("intent_analysis", {})
            result["voice"] = voice_result.get("voice_command", {})
        else:
            intent_data = {"intent": "SEE", "confidence": 0.80}
            result["voice"] = None
        result["intent"] = intent_data
        result["pipeline_stages"].append("intent")

        # Resolve task type
        intent_label = intent_data.get("intent", "SEE")
        if task_type_override:
            intent_label = task_type_override
        try:
            task_type = TaskType(intent_label)
        except ValueError:
            task_type = TaskType.SEE

        # Stage 3: Barrier Detection
        barriers = self.barrier_engine.detect_barriers(
            task_type=task_type,
            task_context={},
            twin=twin,
        )
        result["barriers"] = [{"category": b.category.value, "severity": b.severity.value} for b in barriers]
        result["pipeline_stages"].append("barriers")

        # Stage 4+5: Task Engine + Flow Compiler
        task_id = self.task_engine.create_generic_task(task_type=task_type, title=query or "")
        task = self.task_engine.get_task(task_id)
        flow = self.flow_compiler.compile_form_flow(task_id, twin, barriers)
        result["task_id"] = task_id
        result["pipeline_stages"].extend(["task_engine", "flow_compiler"])

        # Stage 6: Capability Selection based on TaskType
        capability_output: Dict[str, Any] = {}
        failures: List[Dict[str, Any]] = []

        if task_type == TaskType.UNDERSTAND_DOCUMENT:
            doc_result = self.assistance_engine.assist_understand_document(image_bytes, query or "", twin)
            capability_output["document"] = doc_result
            failure = self.failure_detector.check_ocr(doc_result)
            if failure:
                failures.append(failure)

        elif task_type == TaskType.FIND_OBJECT:
            nav_result = self.navigation_engine.navigate(image_bytes=image_bytes, target_label=query, twin=twin)
            capability_output["navigation"] = nav_result

        elif task_type == TaskType.COMMUNICATE:
            isl_result = self.assistance_engine.assist_sign_communication(image_bytes, twin)
            capability_output["isl"] = isl_result
            failure = self.failure_detector.check_isl(isl_result)
            if failure:
                failures.append(failure)

        elif task_type == TaskType.SEE:
            scene = self.scene_engine.analyze(image_bytes=image_bytes, twin=twin, task_type=task_type)
            capability_output["scene"] = {
                "summary": scene.summary,
                "objects": len(scene.objects),
                "hazards": scene.hazards,
            }

        result["capabilities"] = capability_output
        result["pipeline_stages"].append("capabilities")

        # Stage 7: Recovery if failures detected
        if failures:
            recovery_actions = self.recovery_engine.recover_many(failures)
            result["recovery"] = [a.model_dump() for a in recovery_actions]
        else:
            result["recovery"] = []
        result["pipeline_stages"].append("recovery")

        # Stage 8: Learning
        self.learning_service.record_interaction(
            step_id=task_type.value,
            modality_used=twin.preferred_input.value,
            duration_seconds=1.0,
            retries=len(failures),
            success=len(failures) == 0,
        )
        result["learning_recorded"] = True
        result["pipeline_stages"].append("learning")

        return result
