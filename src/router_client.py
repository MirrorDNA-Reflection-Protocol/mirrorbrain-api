"""Router Client — Routes requests through MirrorGate Router.

Replaces direct Ollama calls with Router-mediated calls.
The Router enforces policy gates, audit logging, and run artifacts.

When Router is unavailable, falls back to direct Ollama access.
"""

import httpx
from typing import Optional

ROUTER_URL = "http://localhost:8097"
OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEOUT = 30.0


def _router_available() -> bool:
    """Check if the MirrorGate Router is reachable."""
    try:
        r = httpx.get(f"{ROUTER_URL}/health", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False


def policy_check(action: str, tier: str = "T1") -> dict:
    """Check policy before an action. Returns {allowed, tier, reason}."""
    try:
        r = httpx.post(
            f"{ROUTER_URL}/policy/check",
            json={"action": action, "tier": tier},
            timeout=5.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # If Router is down, allow by default (local-first)
        return {"allowed": True, "tier": tier, "reason": f"router unavailable: {e}"}


def audit_append(event: str, data: Optional[dict] = None) -> None:
    """Append an audit event via Router. Fire-and-forget."""
    try:
        httpx.post(
            f"{ROUTER_URL}/audit/append",
            json={"event": event, "data": data or {}},
            timeout=3.0,
        )
    except Exception:
        pass  # Don't break the app if audit fails


def vault_write_draft(title: str, content: str, project: Optional[str] = None, tags: Optional[list] = None) -> dict:
    """Write a draft to Vault via Router."""
    try:
        r = httpx.post(
            f"{ROUTER_URL}/vault/write_draft",
            json={"title": title, "content": content, "project": project, "tags": tags or []},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def vault_read(pointer: str) -> dict:
    """Read from Vault via Router."""
    try:
        r = httpx.post(
            f"{ROUTER_URL}/vault/read",
            json={"pointer": pointer},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def knowledge_search(source: str, query: str, tier: str = "T1") -> list:
    """Search knowledge via Router."""
    try:
        r = httpx.post(
            f"{ROUTER_URL}/knowledge/search",
            json={"source": source, "query": query, "tier": tier},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []


def get_analytics(project: Optional[str] = None) -> dict:
    """Get analytics summary from Router."""
    try:
        url = f"{ROUTER_URL}/analytics/summary"
        if project:
            url += f"?project={project}"
        r = httpx.get(url, timeout=10.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def score_run(run_id: str, project: str) -> dict:
    """Score a run for confidence/stability/trust."""
    try:
        r = httpx.post(
            f"{ROUTER_URL}/run/score",
            json={"run_id": run_id, "project": project},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def replay_run(run_id: str, project: str, policy_override: Optional[dict] = None) -> dict:
    """Replay a historical run in sandbox mode."""
    try:
        r = httpx.post(
            f"{ROUTER_URL}/replay/run",
            json={"run_id": run_id, "project": project, "policy_override": policy_override},
            timeout=15.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_health() -> dict:
    """Get Router health including kill switch and policy version."""
    try:
        r = httpx.get(f"{ROUTER_URL}/health", timeout=3.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "status": "unreachable"}


def call_ollama_via_router(system_prompt: str, user_query: str, brain_context: str, model: str = "qwen2.5:7b") -> str:
    """Call Ollama, routing through Router for audit + policy.

    Flow:
    1. Check policy via Router
    2. If allowed, call Ollama directly (Router doesn't proxy LLM calls)
    3. Audit the interaction via Router

    Falls back to direct Ollama if Router is unavailable.
    """
    full_prompt = f"{system_prompt}{brain_context}\n\nUser question: {user_query}"

    # Policy check (non-blocking if Router is down)
    policy = policy_check("twin_invoke")

    if not policy.get("allowed", True):
        return f"Action denied by policy: {policy.get('reason', 'unknown')}"

    # Call Ollama directly (Router is governance layer, not LLM proxy)
    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150,
                },
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        result = response.json().get("response", "").strip()
    except Exception as e:
        result = f"I'm having trouble connecting right now. ({str(e)[:50]})"

    # Audit the interaction
    audit_append("twin_invoke", {
        "model": model,
        "query_length": len(user_query),
        "response_length": len(result),
        "policy_tier": policy.get("tier", "T1"),
    })

    return result
