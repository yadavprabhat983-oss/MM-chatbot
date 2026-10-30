import base64

def test_chat_standard_flow(client):
    payload = {
        "message": "Hello, can you help me organize my notes?",
        "search_web": False,
        "emotional_mode": False
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    assert "reply" in data
    assert len(data["reply"]) > 0

    conv_id = data["conversation_id"]

    # Verify conversation was saved with messages
    conv_res = client.get(f"/api/conversations/{conv_id}")
    assert conv_res.status_code == 200
    conv_data = conv_res.json()
    assert len(conv_data["messages"]) == 2  # user + assistant

def test_chat_with_web_search(client):
    payload = {
        "message": "What are the latest AI breakthroughs?",
        "search_web": True,
        "emotional_mode": False
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["citations"]) > 0
    assert any(c["source_type"] == "web" for c in data["citations"])

def test_chat_with_emotional_mode(client):
    payload = {
        "message": "I'm feeling really anxious about my exam tomorrow.",
        "search_web": False,
        "emotional_mode": True
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["emotional_mode_active"] is True
    assert "reply" in data

def test_chat_crisis_interception(client):
    payload = {
        "message": "I want to kill myself",
        "search_web": False,
        "emotional_mode": True
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "988" in data["reply"]
    assert "not have to carry this alone" in data["reply"]

def test_chat_with_image_attachment(client):
    # Dummy 1x1 png in base64
    dummy_b64 = base64.b64encode(b"dummy image data").decode("utf-8")
    payload = {
        "message": "Analyze this screenshot for me",
        "attachments": [
            {
                "type": "image",
                "filename": "screenshot.png",
                "content_base64": dummy_b64,
                "mime_type": "image/png"
            }
        ]
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["attachments_processed"]) == 1
