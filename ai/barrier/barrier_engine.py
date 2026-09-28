"""
Sahayak AI — Barrier Engine
Analyzes task complexity against the user's Accessibility Twin to detect interaction barriers.
"""

from typing import List, Dict, Any
from shared.schemas.models import (
    AccessibilityTwin,
    TaskType,
    Barrier,
    BarrierCategory,
    BarrierSeverity,
    LanguagePreference,
)


class BarrierEngine:
    def __init__(self):
        pass

    def detect_barriers(
        self,
        task_type: TaskType,
        task_context: Optional[Dict[str, Any]] = None,
        twin: Optional[AccessibilityTwin] = None
    ) -> List[Barrier]:
        """
        Analyzes task metadata and twin preferences to return identified barriers.
        """
        user_twin = twin or AccessibilityTwin(id="default_user")
        context = task_context or {}
        barriers: List[Barrier] = []

        # 1. Visual Barrier Detection
        if user_twin.visual.large_text or user_twin.visual.high_contrast:
            if task_type in [TaskType.FORM_COMPLETION, TaskType.UNDERSTAND_DOCUMENT, TaskType.READ]:
                barriers.append(
                    Barrier(
                        category=BarrierCategory.VISUAL,
                        severity=BarrierSeverity.HIGH,
                        description="Dense document layout with sub-12pt fine print and standard low contrast.",
                        remediation_strategy="Scale typography to 24pt, apply high-contrast card separation, isolate text items.",
                    )
                )

        # 2. Motor / Physical Input Barrier Detection
        if user_twin.motor.voice_input:
            if task_type == TaskType.FORM_COMPLETION:
                barriers.append(
                    Barrier(
                        category=BarrierCategory.MOTOR,
                        severity=BarrierSeverity.HIGH,
                        description="Physical form requires fine motor penmanship or precise virtual keyboard typing.",
                        remediation_strategy="Replace text input fields with hands-free voice dictation and conversational confirmation.",
                    )
                )

        # 3. Cognitive & Interaction Complexity Barrier Detection
        if user_twin.comprehension.one_step_at_a_time or user_twin.comprehension.simplified_language:
            if task_type == TaskType.FORM_COMPLETION:
                field_count = context.get("total_fields", 7)
                if field_count > 3:
                    barriers.append(
                        Barrier(
                            category=BarrierCategory.INTERACTION_COMPLEXITY,
                            severity=BarrierSeverity.HIGH,
                            description=f"Form contains {field_count} concurrent fields, inducing cognitive fatigue.",
                            remediation_strategy="Linearize the form into single-question cards presented one step at a time.",
                        )
                    )
            if task_type == TaskType.UNDERSTAND_DOCUMENT:
                barriers.append(
                    Barrier(
                        category=BarrierCategory.COGNITIVE,
                        severity=BarrierSeverity.MEDIUM,
                        description="Document contains formal bureaucratic terminology and dense eligibility clauses.",
                        remediation_strategy="Extract key deadlines and prerequisites into plain-language bullet points.",
                    )
                )

        # 4. Language Barrier Detection
        doc_language = context.get("document_language", "English")
        if user_twin.language == LanguagePreference.HINDI and doc_language != "Hindi":
            barriers.append(
                Barrier(
                    category=BarrierCategory.LANGUAGE,
                    severity=BarrierSeverity.HIGH,
                    description=f"Document language ({doc_language}) differs from user's primary preference (Hindi).",
                    remediation_strategy="Translate synthesized prompts and summaries into conversational Hindi.",
                )
            )

        # 5. Hearing Barrier Detection
        if user_twin.hearing.captions:
            if task_type == TaskType.COMMUNICATE:
                barriers.append(
                    Barrier(
                        category=BarrierCategory.HEARING,
                        severity=BarrierSeverity.HIGH,
                        description="Spoken communication lacks visual transcription.",
                        remediation_strategy="Provide real-time on-screen speech-to-text captions.",
                    )
                )

        return barriers
