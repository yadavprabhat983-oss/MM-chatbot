import io

def test_document_upload_and_lifecycle(client):
    # 1. Upload valid markdown document
    file_content = b"# Architecture Overview\n\nThis system uses PostgreSQL and pgvector for RAG."
    files = {"file": ("architecture.md", io.BytesIO(file_content), "text/markdown")}
    data = {"title": "Architecture Doc"}

    res = client.post("/api/documents/upload", files=files, data=data)
    assert res.status_code == 201
    doc = res.json()
    assert doc["title"] == "Architecture Doc"
    assert doc["status"] == "indexed"
    doc_id = doc["id"]

    # 2. Retrieve document detail
    res_get = client.get(f"/api/documents/{doc_id}")
    assert res_get.status_code == 200
    detail = res_get.json()
    assert "PostgreSQL and pgvector" in detail["content_text"]
    assert len(detail["versions"]) == 1

    # 3. Update document (should increment version and re-index)
    update_payload = {
        "title": "Architecture Doc V2",
        "content_text": "# Updated Architecture\n\nAdded multimodal capabilities and web search.",
        "change_summary": "Added multimodal info"
    }
    res_update = client.put(f"/api/documents/{doc_id}", json=update_payload)
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["title"] == "Architecture Doc V2"
    assert len(updated["versions"]) == 2
    assert updated["versions"][0]["version_number"] == 2

    # 4. AI-edit document
    ai_edit_payload = {
        "instruction": "Make the tone more concise",
        "action": "rewrite"
    }
    res_ai = client.post(f"/api/documents/{doc_id}/ai-edit", json=ai_edit_payload)
    assert res_ai.status_code == 200
    ai_res = res_ai.json()
    assert "proposed_text" in ai_res
    assert "diff_summary" in ai_res

    # 5. Download document
    res_dl = client.get(f"/api/documents/{doc_id}/download?format=md")
    assert res_dl.status_code == 200
    assert "attachment" in res_dl.headers.get("content-disposition", "")

    # 6. Delete document
    res_del = client.delete(f"/api/documents/{doc_id}")
    assert res_del.status_code == 204

    # 7. Verify 404
    assert client.get(f"/api/documents/{doc_id}").status_code == 404


def test_invalid_file_type_rejected(client):
    file_content = b"MZ\x90\x00\x03\x00\x00\x00Fake Binary"
    files = {"file": ("malicious.exe", io.BytesIO(file_content), "application/octet-stream")}
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]


def test_empty_document_rejected(client):
    files = {"file": ("empty.txt", io.BytesIO(b"   \n\t  "), "text/plain")}
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()
