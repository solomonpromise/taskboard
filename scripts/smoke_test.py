"""Smoke test a deployed Taskboard (book Chapter 31): python scripts/smoke_test.py https://staging.example.com

Checks the most important things in seconds: health, the page loads, a throwaway account can
sign up, create a task, see it, and sign out. Exit code 0 means pass.
Use it against staging or local copies; it creates a test account each run.
"""
import json
import secrets
import sys
import urllib.request
from http.cookiejar import CookieJar

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
jar = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def call(method, path, body=None):
    headers = {"Content-Type": "application/json"}
    csrf = next((c.value for c in jar if c.name == "csrf_token"), "")
    if method != "GET":
        headers["X-CSRF-Token"] = csrf
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    with opener.open(request, timeout=10) as response:
        text = response.read().decode()
        return response.status, (json.loads(text) if text and text.startswith(("{", "[")) else text)


def check(name, condition):
    print(("PASS " if condition else "FAIL ") + name)
    if not condition:
        sys.exit(1)


status, body = call("GET", "/health")
check("health endpoint reports ok", status == 200 and body.get("database") == "ok")
status, page = call("GET", "/")
check("web page loads", status == 200 and "<div id=\"root\">" in page)
email = f"smoke-{secrets.token_hex(4)}@example.com"
status, _ = call("POST", "/v1/auth/sign-up", {"name": "Smoke Test", "email": email,
                                               "password": "smoke test pass phrase " + secrets.token_hex(4)})
check("test account can sign up", status == 201)
status, task = call("POST", "/v1/tasks", {"title": "Smoke test task"})
check("task can be created", status == 201)
status, tasks = call("GET", "/v1/tasks")
check("task appears in the list", any(t["id"] == task["id"] for t in tasks["items"]))
status, _ = call("POST", "/v1/auth/sign-out")
check("sign out works", status == 204)
print("All smoke tests passed.")
