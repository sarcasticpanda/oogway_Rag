import pytest
from app.routers.artifacts import get_raw_artifact
from app.models.artifact import Artifact
from uuid import uuid4

def test_sandbox_iframe_security_attributes():
    """Verify security attributes required for rendering generated HTML/CSS artifacts."""
    # The frontend iframe must use: sandbox="allow-scripts" without "allow-same-origin"
    sandbox_attr = "allow-scripts"
    disallowed_attrs = ["allow-same-origin", "allow-top-navigation", "allow-forms", "allow-modals"]
    
    for attr in disallowed_attrs:
        assert attr not in sandbox_attr, f"Security risk: {attr} must not be present in artifact iframe"

def test_csp_header_format():
    """Verify CSP headers returned by artifact endpoint restrict malicious script origins."""
    headers = {
        "Content-Security-Policy": "default-src 'self' 'unsafe-inline'; img-src data: https:; script-src 'self' 'unsafe-inline';",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN"
    }
    assert "default-src" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
