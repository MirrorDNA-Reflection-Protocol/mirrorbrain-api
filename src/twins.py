"""AI Twins — Guardian, Scout, Synthesizer, Mirror.

Powered by Ollama for real AI responses.
Supports: Single, Council, Debate, and Relay modes.
"""

from __future__ import annotations

import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import json

from .schemas import (
    TwinType, TwinMode, TwinRequest, TwinResponse, Brain,
    CouncilResponse, DebateResponse, DebateTurn,
    RelayResponse, RelayStage, TwinMemoryEntry, TwinHistory
)


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


MEMORY_PATH = Path("~/.mirrordna/brain/twin_memory").expanduser()


class TwinEngine:
    """Engine for executing AI Twins.

    Supports multiple modes:
    - Single: One twin responds
    - Council: All 4 twins respond to the same query
    - Debate: Two twins argue back and forth
    - Relay: Chain through all twins sequentially
    """

    def __init__(self):
        self._brains: Dict[str, Brain] = {}
        self._memory: Dict[str, List[TwinMemoryEntry]] = {}
        MEMORY_PATH.mkdir(parents=True, exist_ok=True)

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

    # ==================== Council Mode ====================

    def invoke_council(self, brain_id: str, query: str) -> CouncilResponse:
        """Invoke all 4 twins on the same query (Council mode)."""
        brain = self.get_brain(brain_id)
        brain_context = _build_brain_context(brain)

        # Get responses from all twins
        responses = {}
        for twin_type in TwinType:
            request = TwinRequest(brain_id=brain_id, twin_type=twin_type, query=query)
            responses[twin_type.value] = self.invoke_twin(request)

        # Generate meta-synthesis
        synthesis = self._synthesize_council(query, responses, brain_context)

        # Store in memory
        self._store_memory(brain_id, TwinMode.COUNCIL, query, synthesis)

        return CouncilResponse(
            brain_id=brain_id,
            query=query,
            guardian=responses["guardian"],
            scout=responses["scout"],
            synthesizer=responses["synthesizer"],
            mirror=responses["mirror"],
            synthesis=synthesis
        )

    def _synthesize_council(self, query: str, responses: Dict[str, TwinResponse], brain_context: str) -> str:
        """Create a meta-synthesis from all council responses."""
        council_summary = f"""The Council has spoken on: "{query}"

Guardian says: {responses['guardian'].response}
Scout says: {responses['scout'].response}
Synthesizer says: {responses['synthesizer'].response}
Mirror asks: {responses['mirror'].response}

As a wise counselor, synthesize these 4 perspectives into a unified insight. Be concise (2-3 sentences)."""

        return _call_ollama(council_summary, "", brain_context)

    # ==================== Debate Mode ====================

    def invoke_debate(self, brain_id: str, query: str, twin_1: TwinType, twin_2: TwinType, rounds: int = 3) -> DebateResponse:
        """Have two twins debate a topic."""
        brain = self.get_brain(brain_id)
        brain_context = _build_brain_context(brain)

        turns: List[DebateTurn] = []

        # Initial positions
        prompt_1 = TWIN_PROMPTS[twin_1]
        prompt_2 = TWIN_PROMPTS[twin_2]

        # First twin opens
        response_1 = _call_ollama(
            f"{prompt_1}\n\nYou're debating with {twin_2.value}. State your perspective.",
            query,
            brain_context
        )
        turns.append(DebateTurn(twin_type=twin_1, response=response_1, responding_to=None))

        # Debate rounds
        last_response = response_1
        for i in range(rounds):
            # Twin 2 responds
            response_2 = _call_ollama(
                f"{prompt_2}\n\nYou're debating with {twin_1.value}. They just said: \"{last_response}\"\n\nRespond with your perspective.",
                query,
                brain_context
            )
            turns.append(DebateTurn(twin_type=twin_2, response=response_2, responding_to=last_response))

            if i < rounds - 1:  # Twin 1 responds (except last round)
                response_1 = _call_ollama(
                    f"{prompt_1}\n\nYou're debating with {twin_2.value}. They just said: \"{response_2}\"\n\nRespond with your perspective.",
                    query,
                    brain_context
                )
                turns.append(DebateTurn(twin_type=twin_1, response=response_1, responding_to=response_2))
                last_response = response_1

        # Generate conclusion
        conclusion = self._conclude_debate(query, turns, brain_context)

        # Store in memory
        self._store_memory(brain_id, TwinMode.DEBATE, query, conclusion)

        return DebateResponse(
            brain_id=brain_id,
            query=query,
            twin_1=twin_1,
            twin_2=twin_2,
            turns=turns,
            conclusion=conclusion
        )

    def _conclude_debate(self, query: str, turns: List[DebateTurn], brain_context: str) -> str:
        """Generate a conclusion from the debate."""
        debate_summary = "\n".join([f"{t.twin_type.value}: {t.response}" for t in turns])

        conclusion_prompt = f"""A debate just occurred on: "{query}"

{debate_summary}

As a neutral observer, what's the key insight from this debate? Be concise (1-2 sentences)."""

        return _call_ollama(conclusion_prompt, "", brain_context)

    # ==================== Relay Mode ====================

    def invoke_relay(self, brain_id: str, query: str) -> RelayResponse:
        """Chain through all twins: Guardian filters → Scout explores → Synthesizer frames → Mirror challenges."""
        brain = self.get_brain(brain_id)
        brain_context = _build_brain_context(brain)

        stages: List[RelayStage] = []
        current_context = query

        relay_order = [
            (TwinType.GUARDIAN, "Filter and assess this for focus alignment"),
            (TwinType.SCOUT, "Explore opportunities and connections in what the Guardian passed"),
            (TwinType.SYNTHESIZER, "Build a framework from the Guardian's filter and Scout's exploration"),
            (TwinType.MIRROR, "Challenge and question the framework. What's missing?"),
        ]

        for twin_type, role_context in relay_order:
            prompt = TWIN_PROMPTS[twin_type]
            relay_prompt = f"{prompt}\n\n{role_context}.\n\nPrevious context: {current_context}"

            response = _call_ollama(relay_prompt, query, brain_context)

            stages.append(RelayStage(
                twin_type=twin_type,
                input_context=current_context,
                response=response
            ))

            current_context = f"{twin_type.value} said: {response}"

        # Final synthesis
        final_output = self._synthesize_relay(query, stages, brain_context)

        # Store in memory
        self._store_memory(brain_id, TwinMode.RELAY, query, final_output)

        return RelayResponse(
            brain_id=brain_id,
            query=query,
            stages=stages,
            final_output=final_output
        )

    def _synthesize_relay(self, query: str, stages: List[RelayStage], brain_context: str) -> str:
        """Create final output from relay chain."""
        relay_summary = "\n".join([f"{s.twin_type.value}: {s.response}" for s in stages])

        synthesis_prompt = f"""A relay of insights on: "{query}"

{relay_summary}

Distill this into one actionable insight. Be concise (1-2 sentences)."""

        return _call_ollama(synthesis_prompt, "", brain_context)

    # ==================== Memory ====================

    def _store_memory(self, brain_id: str, mode: TwinMode, query: str, response: str) -> None:
        """Store an interaction in memory."""
        entry = TwinMemoryEntry(
            timestamp=datetime.now(),
            twin_type=TwinType.GUARDIAN,  # Placeholder for multi-twin modes
            mode=mode,
            query=query,
            response=response
        )

        if brain_id not in self._memory:
            self._memory[brain_id] = []

        self._memory[brain_id].append(entry)

        # Persist to disk
        self._save_memory(brain_id)

    def _save_memory(self, brain_id: str) -> None:
        """Save memory to disk."""
        if brain_id not in self._memory:
            return

        memory_file = MEMORY_PATH / f"{brain_id}.json"
        entries = [
            {
                "timestamp": e.timestamp.isoformat(),
                "twin_type": e.twin_type.value,
                "mode": e.mode.value,
                "query": e.query,
                "response": e.response
            }
            for e in self._memory[brain_id]
        ]

        with open(memory_file, "w") as f:
            json.dump(entries, f, indent=2)

    def _load_memory(self, brain_id: str) -> List[TwinMemoryEntry]:
        """Load memory from disk."""
        memory_file = MEMORY_PATH / f"{brain_id}.json"

        if not memory_file.exists():
            return []

        try:
            with open(memory_file) as f:
                data = json.load(f)

            return [
                TwinMemoryEntry(
                    timestamp=datetime.fromisoformat(e["timestamp"]),
                    twin_type=TwinType(e["twin_type"]),
                    mode=TwinMode(e["mode"]),
                    query=e["query"],
                    response=e["response"]
                )
                for e in data
            ]
        except Exception:
            return []

    def get_history(self, brain_id: str) -> TwinHistory:
        """Get conversation history for a brain."""
        if brain_id not in self._memory:
            self._memory[brain_id] = self._load_memory(brain_id)

        entries = self._memory.get(brain_id, [])

        return TwinHistory(
            brain_id=brain_id,
            entries=entries,
            total_interactions=len(entries)
        )


# Singleton instance
_twin_engine: Optional[TwinEngine] = None


def get_twin_engine() -> TwinEngine:
    """Get the singleton twin engine."""
    global _twin_engine
    if _twin_engine is None:
        _twin_engine = TwinEngine()
    return _twin_engine
