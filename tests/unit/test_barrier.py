"""
Unit Tests for Barrier Engine & Accessible Flow Compiler
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import TaskType, BarrierCategory, BarrierSeverity
from ai.barrier.barrier_engine import BarrierEngine
from ai.compiler.flow_compiler import AccessibleTaskFlowCompiler
from ai.accessibility.twin import AccessibilityTwinService


def test_form_barrier_detection():
    twin = AccessibilityTwinService().get_twin("default_user")
    twin.visual.high_contrast = True
    twin.comprehension.simplified_language = True

    barrier_engine = BarrierEngine()
    barriers = barrier_engine.detect_barriers(
        task_type=TaskType.FORM_COMPLETION,
        task_context={"total_fields": 7, "document_type": "physical_form"},
        twin=twin,
    )
    assert isinstance(barriers, list)
    assert len(barriers) > 0


def test_flow_compilation_with_remediation():
    twin = AccessibilityTwinService().get_twin("default_user")
    barrier_engine = BarrierEngine()
    barriers = barrier_engine.detect_barriers(
        task_type=TaskType.FORM_COMPLETION,
        task_context={"total_fields": 7},
        twin=twin,
    )

    compiler = AccessibleTaskFlowCompiler()
    flow = compiler.compile_form_flow(
        task_id="task_test_101",
        twin=twin,
        barriers=barriers,
    )
    assert flow is not None
    assert flow.total_steps == 7
    assert len(flow.steps) == 7
    assert flow.steps[0].field_id == "full_name"
    assert flow.steps[0].spoken_prompt is not None


if __name__ == "__main__":
    test_form_barrier_detection()
    test_flow_compilation_with_remediation()
    print("All unit/test_barrier.py tests passed!")
