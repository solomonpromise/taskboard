def test_health_reports_database_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_frontend_index_is_never_cached(client):
    from app.main import FRONTEND_DIST
    if not FRONTEND_DIST.exists():
        return  # frontend not built in this environment
    r = client.get("/completed")
    assert r.status_code == 200 and r.headers["cache-control"] == "no-cache"


def test_unknown_api_paths_return_json_404(client):
    r = client.get("/v1/does-not-exist")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"
