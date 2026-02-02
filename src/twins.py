"""AI Twins — Guardian, Scout, Synthesizer, Mirror.

Powered by Ollama for real AI responses.
"""

from __future__ import annotations

import httpx
from typing import Optional, Dict

from .schemas import TwinType, TwinRequest, TwinResponse, Brain


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"


# Twin personalities / system prompts
TWIN_PROMPTS = {
    TwinType.GUARDIAN: """You are the Guardian, an AI twin focused on protecting focus and filtering noise.
Your role is to:
- Assess if something aligns with the user's goals
- Protect their time and attention from distractions
- Help them maintain boundaries
- Be direct and protective, like a wise advisor

Respond concisely (2-3 sentences max). Be warm but firm.""",

    TwinType.SCOUT: """You are the Scout, an AI twin focused on exploration and discovery.
Your role is to:
- Find unexpected connections between ideas
- Surface opportunities they might miss
- Explore adjacent possibilities
- Be curious and adventurous, always looking for new angles

Respond concisely (2-3 sentences max). Be enthusiastic but grounded.""",

    TwinType.SYNTHESIZER: """You are the Synthesizer, an AI twin focused on merging ideas into frameworks.
Your role is to:
- Find patterns across disparate concepts
- Build unifying structures
- Create coherence from chaos
- Be integrative and systematic, weaving threads together

Respond concisely (2-3 sentences max). Be insightful and structured.""",

    TwinType.MIRROR: """You are the Mirror, an AI twin focused on reflection and revealing blind spots.
Your role is to:
- Ask questions that reveal assumptions
- Show them what they might not see
- Challenge their thinking gently
- Be honest and reflective, like a trusted friend who tells hard truths

Respond concisely (2-3 sentences max). Be compassionate but direct.""",
}


def _build_brain_context(brain: Optional[Brain]) -> str:
    """Build context string from brain dimensions."""
    if not brain:
        return ""

    dims = brain.dimensions
    traits = []

    if dims.get("topology", 0) > 0.6:
        traits.append("thinks in connections and networks")
    if dims.get("velocity", 0) > 0.7:
        traits.append("prefers fast iteration")
    if dims.get("depth", 0) > 0.7:
        traits.append("goes deep into topics")
    if dims.get("entropy", 0) > 0.6:
        traits.append("comfortable with chaos")
    if dims.get("evolution", 0) > 0.6:
        traits.append("growth-oriented")

    if traits:
        return f"\n\nThis person's cognitive style: {', '.join(traits)}."
    return ""


def _call_ollama(system_prompt: str, user_query: str, brain_context: str) -> str:
    """Call Ollama API for response."""
    full_prompt = f"{system_prompt}{brain_context}\n\nUser question: {user_query}"

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150,  # Keep responses short
                }
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"I'm having trouble connecting right now. ({str(e)[:50]})"


class TwinEngine:
    """Engine for executing AI Twins."""

    def __init__(self):
        self._brains: Dict[str, Brain] = {}

    def register_brain(self, brain: Brain) -> None:
        """Register a brain for twin operations."""
        self._brains[brain.brain_id] = brain

    def get_brain(self, brain_id: str) -> Optional[Brain]:
        """Get a registered brain."""
        return self._brains.get(brain_id)

    def invoke_twin(self, request: TwinRequest) -> TwinResponse:
        """Invoke a twin and get a response."""
        brain = self.get_brain(request.brain_id)
        brain_context = _build_brain_context(brain)

        system_prompt = TWIN_PROMPTS.get(request.twin_type, TWIN_PROMPTS[TwinType.GUARDIAN])
        ai_response = _call_ollama(system_prompt, request.query, brain_context)

        # Build response with appropriate metadata
        if request.twin_type == TwinType.GUARDIAN:
            return self._build_guardian_response(request, brain, ai_response)
        elif request.twin_type == TwinType.SCOUT:
            return self._build_scout_response(request, brain, ai_response)
        elif request.twin_type == TwinType.SYNTHESIZER:
            return self._build_synthesizer_response(request, brain, ai_response)
        elif request.twin_type == TwinType.MIRROR:
            return self._build_mirror_response(request, brain, ai_response)
        else:
            raise ValueError(f"Unknown twin type: {request.twin_type}")

    def _build_guardian_response(self, request: TwinRequest, brain: Optional[Brain], ai_response: str) -> TwinResponse:
        """Build Guardian response."""
        hints = []
        suggestions = ["Stay focused on what matters most"]

        if brain:
            dims = brain.dimensions
            if dims.get("depth", 0) > 0.7:
                hints.append("Deep focus mode")
            if dims.get("velocity", 0) > 0.7:
                hints.append("Fast iteration preferred")

        return TwinResponse(
            twin_type=TwinType.GUARDIAN,
            brain_id=request.brain_id,
            response=ai_response,
            reasoning="Protecting your focus and boundaries.",
            suggestions=suggestions,
            resonance_hints=hints or ["Guardian active"]
        )

    def _build_scout_response(self, request: TwinRequest, brain: Optional[Brain], ai_response: str) -> TwinResponse:
        """Build Scout response."""
        hints = []
        suggestions = ["Explore adjacent possibilities"]

        if brain:
            dims = brain.dimensions
            if dims.get("topology", 0) > 0.6:
                hints.append("High connectivity")
            if dims.get("entropy", 0) > 0.6:
                hints.append("Chaos-friendly")

        return TwinResponse(
            twin_type=TwinType.SCOUT,
            brain_id=request.brain_id,
            response=ai_response,
            reasoning="Scouting new territory and connections.",
            suggestions=suggestions,
            resonance_hints=hints or ["Scout active"]
        )

    def _build_synthesizer_response(self, request: TwinRequest, brain: Optional[Brain], ai_response: str) -> TwinResponse:
        """Build Synthesizer response."""
        hints = []
        suggestions = ["Look for the unifying pattern"]

        if brain:
            dims = brain.dimensions
            if dims.get("topology", 0) > 0.5 and dims.get("depth", 0) > 0.5:
                hints.append("Framework builder")
            if dims.get("evolution", 0) > 0.6:
                hints.append("Growth-oriented")

        return TwinResponse(
            twin_type=TwinType.SYNTHESIZER,
            brain_id=request.brain_id,
            response=ai_response,
            reasoning="Synthesizing ideas into coherent frameworks.",
            suggestions=suggestions,
            resonance_hints=hints or ["Synthesizer active"]
        )

    def _build_mirror_response(self, request: TwinRequest, brain: Optional[Brain], ai_response: str) -> TwinResponse:
        """Build Mirror response."""
        hints = []
        suggestions = ["Question your assumptions"]

        if brain:
            dims = brain.dimensions
            if dims.get("entropy", 0) < 0.3:
                hints.append("Consider unexpected angles")
            if dims.get("depth", 0) < 0.3:
                hints.append("Go deeper")

        return TwinResponse(
            twin_type=TwinType.MIRROR,
            brain_id=request.brain_id,
            response=ai_response,
            reasoning="Reflecting back what you might not see.",
            suggestions=suggestions,
            resonance_hints=hints or ["Mirror active"]
        )


# Singleton instance
_twin_engine: Optional[TwinEngine] = None


def get_twin_engine() -> TwinEngine:
    """Get the singleton twin engine."""
    global _twin_engine
    if _twin_engine is None:
        _twin_engine = TwinEngine()
    return _twin_engine
