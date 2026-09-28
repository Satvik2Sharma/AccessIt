import pytest
from ai.orchestrator.ai_pipeline import AIPipeline

def test_pipeline_form_completion():
    pipeline = AIPipeline()
    result = pipeline.run(query="Help me fill this form", twin_id="default_user")
    assert "intent" in result
    assert result["intent"]["intent"] == "FORM_COMPLETION"
    assert "barriers" in result
    assert "learning_recorded" in result
    assert result["learning_recorded"] is True

def test_pipeline_document_reading():
    pipeline = AIPipeline()
    result = pipeline.run(query="What is important in this notice?", twin_id="default_user")
    assert result["intent"]["intent"] == "UNDERSTAND_DOCUMENT"
    assert "capabilities" in result
    assert "document" in result["capabilities"]

def test_pipeline_no_query_defaults_to_see():
    pipeline = AIPipeline()
    result = pipeline.run(twin_id="default_user")
    assert "intent" in result
    assert "pipeline_stages" in result
    assert "twin" in result

def test_pipeline_recovery_on_failure():
    pipeline = AIPipeline()
    result = pipeline.run(query="Read this notice", twin_id="default_user")
    assert "recovery" in result
    # May have 0 or more recovery actions depending on OCR confidence
    assert isinstance(result["recovery"], list)

def test_pipeline_all_stages_recorded():
    pipeline = AIPipeline()
    result = pipeline.run(query="Help me fill this form", twin_id="default_user")
    stages = result["pipeline_stages"]
    for expected in ["twin", "intent", "barriers", "task_engine", "flow_compiler"]:
        assert expected in stages
