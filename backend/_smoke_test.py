"""Smoke tests for generator service — no external calls needed."""
import sys, os, json
sys.path.insert(0, ".")

from models.request_models import GenerateRequest
from services.generator import generate_demo, generate_content, _is_demo_mode, _parse_json_response

req = GenerateRequest.from_dict({
    "idea": "morning yoga for beginners",
    "platform": "Instagram",
    "tone": "Inspirational",
})
print("Model OK:", req)

# ── generate_demo ─────────────────────────────────────────────────────────────
result = generate_demo(req)
expected_keys = {"caption", "videoScript", "hashtags", "visualConcept", "callToAction"}
assert set(result.keys()) == expected_keys, f"Wrong keys: {result.keys()}"
assert all(result[k] for k in expected_keys), "Some values are empty"
print("generate_demo keys OK:", list(result.keys()))

# ── _is_demo_mode ─────────────────────────────────────────────────────────────
os.environ.pop("DEMO_MODE", None)
assert _is_demo_mode() is True, "Unset should default to True"
os.environ["DEMO_MODE"] = "false"
assert _is_demo_mode() is False
os.environ["DEMO_MODE"] = "FALSE"
assert _is_demo_mode() is False
os.environ["DEMO_MODE"] = "true"
assert _is_demo_mode() is True
os.environ["DEMO_MODE"] = ""
assert _is_demo_mode() is True
print("_is_demo_mode OK")

# ── generate_content dispatches to demo when DEMO_MODE=true ───────────────────
os.environ["DEMO_MODE"] = "true"
r = generate_content(req)
assert set(r.keys()) >= expected_keys, f"Missing keys in demo dispatch: {r.keys()}"
print("generate_content (demo dispatch) OK")

# ── _parse_json_response ──────────────────────────────────────────────────────
payload = {"caption":"c","videoScript":"s","hashtags":"h","visualConcept":"v","callToAction":"a"}

# Attempt 1: raw valid JSON
r = _parse_json_response(json.dumps(payload), req)
assert r["caption"] == "c"
print("_parse_json_response attempt-1 (raw) OK")

# Attempt 2: markdown-fenced JSON
fenced = "```json\n" + json.dumps(payload) + "\n```"
r = _parse_json_response(fenced, req)
assert r["caption"] == "c"
print("_parse_json_response attempt-2 (fence strip) OK")

# Attempt 3: JSON buried in prose
prose = "Here is your content:\n\n" + json.dumps(payload) + "\n\nEnjoy!"
r = _parse_json_response(prose, req)
assert r["caption"] == "c"
print("_parse_json_response attempt-3 (regex extract) OK")

# Attempt 4: partial JSON (missing some keys) — should merge with demo
partial = json.dumps({"caption": "only caption here"})
r = _parse_json_response(partial, req)
assert r["caption"] == "only caption here"
assert "videoScript" in r and r["videoScript"]   # filled from demo
print("_parse_json_response attempt-4 (partial fill) OK")

# Fallback: pure garbage — should return demo content
r = _parse_json_response("this is total garbage with no JSON at all", req)
assert set(r.keys()) >= expected_keys
assert r["caption"]  # demo caption is non-empty
print("_parse_json_response fallback (garbage) OK")

print()
print("All checks passed.")
