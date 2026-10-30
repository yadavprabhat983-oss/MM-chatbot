from app.services.safety_service import safety_service

def test_crisis_detection_triggers_lifeline_resources():
    crisis_inputs = [
        "I feel hopeless and I want to kill myself",
        "Thinking about suicide tonight",
        "I want to end my life, please help",
    ]
    for prompt in crisis_inputs:
        is_crisis, response = safety_service.check_crisis(prompt)
        assert is_crisis is True, f"Failed to detect crisis in: {prompt}"
        assert response is not None
        assert "988" in response
        assert "741741" in response
        assert "not have to carry this alone" in response

def test_safe_inputs_do_not_trigger_crisis():
    safe_inputs = [
        "I had a stressful day at work and feel tired.",
        "Can you recommend a breathing exercise for anxiety?",
        "How do I write a Python function?",
    ]
    for prompt in safe_inputs:
        is_crisis, response = safety_service.check_crisis(prompt)
        assert is_crisis is False
        assert response is None

def test_emotional_support_system_prompt_structure():
    prompt = safety_service.get_emotional_system_prompt()
    assert "empathetic" in prompt.lower()
    assert "5-4-3-2-1" in prompt
    assert "box breathing" in prompt.lower()
    assert "not a human, therapist" in prompt
