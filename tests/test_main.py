from app.main import app

def test_health():
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"

def test_index():
    client = app.test_client()
    assert client.get("/").status_code == 200