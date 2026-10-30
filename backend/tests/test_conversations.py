def test_create_and_list_conversations(client):
    # 1. Create conversation
    res = client.post("/api/conversations", json={"title": "Test Chat"})
    assert res.status_code == 201
    created = res.json()
    assert created["title"] == "Test Chat"
    conv_id = created["id"]

    # 2. List conversations
    res_list = client.get("/api/conversations")
    assert res_list.status_code == 200
    items = res_list.json()
    assert any(c["id"] == conv_id for c in items)

    # 3. Get single conversation
    res_single = client.get(f"/api/conversations/{conv_id}")
    assert res_single.status_code == 200
    detail = res_single.json()
    assert detail["id"] == conv_id
    assert "messages" in detail

    # 4. Delete conversation
    res_del = client.delete(f"/api/conversations/{conv_id}")
    assert res_del.status_code == 204

    # 5. Confirm 404 after deletion
    res_not_found = client.get(f"/api/conversations/{conv_id}")
    assert res_not_found.status_code == 404
