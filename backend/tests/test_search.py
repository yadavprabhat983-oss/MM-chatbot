def test_search_endpoint(client):
    res = client.post("/api/search", json={"query": "artificial intelligence", "max_results": 3})
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "artificial intelligence"
    assert len(data["results"]) > 0
    first = data["results"][0]
    assert "title" in first
    assert "url" in first
    assert "snippet" in first

def test_empty_search_handled_gracefully(client):
    res = client.post("/api/search", json={"query": "", "max_results": 3})
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 0
