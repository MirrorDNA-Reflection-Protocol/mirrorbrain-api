"""AI Twins — Guardian, Scout, Synthesizer, Mirror."""

from __future__ import annotations

from typing import Optional, Dict

from .schemas import TwinType, TwinRequest, TwinResponse, Brain


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

        if request.twin_type == TwinType.GUARDIAN:
            return self._invoke_guardian(request, brain)
        elif request.twin_type == TwinType.SCOUT:
            return self._invoke_scout(request, brain)
        elif request.twin_type == TwinType.SYNTHESIZER:
            return self._invoke_synthesizer(request, brain)
        elif request.twin_type == TwinType.MIRROR:
            return self._invoke_mirror(request, brain)
        else:
            raise ValueError(f"Unknown twin type: {request.twin_type}")

    def _invoke_guardian(self, request: TwinRequest, brain: Optional[Brain]) -> TwinResponse:
        """Guardian Twin — Protects boundaries, filters noise, maintains focus."""
        alignment_hints = []
        suggestions = []

        if brain:
            dims = brain.dimensions
            if dims.get("depth", 0) > 0.7:
                alignment_hints.append("This brain prefers deep focus over breadth")
                suggestions.append("Consider going deeper rather than wider")
            if dims.get("velocity", 0) > 0.7:
                alignment_hints.append("This brain values speed and iteration")
                suggestions.append("Start with a quick prototype")

        return TwinResponse(
            twin_type=TwinType.GUARDIAN,
            brain_id=request.brain_id,
            response=f"Guardian analysis of: {request.query[:100]}...",
            reasoning="Assessing alignment with cognitive patterns and protecting focus boundaries.",
            suggestions=suggestions or ["Maintain focus on core objectives"],
            resonance_hints=alignment_hints or ["Proceed with awareness"]
        )

    def _invoke_scout(self, request: TwinRequest, brain: Optional[Brain]) -> TwinResponse:
        """Scout Twin — Explores territory, finds connections, surfaces opportunities."""
        exploration_hints = []
        suggestions = []

        if brain:
            dims = brain.dimensions
            if dims.get("topology", 0) > 0.6:
                exploration_hints.append("High topology — look for cross-domain connections")
                suggestions.append("Explore adjacent fields for unexpected insights")
            if dims.get("entropy", 0) > 0.6:
                exploration_hints.append("High entropy — embrace productive chaos")
                suggestions.append("Allow for serendipitous discoveries")

        return TwinResponse(
            twin_type=TwinType.SCOUT,
            brain_id=request.brain_id,
            response=f"Scout exploration of: {request.query[:100]}...",
            reasoning="Scanning for opportunities, connections, and unexplored territories.",
            suggestions=suggestions or ["Explore the edges of the known"],
            resonance_hints=exploration_hints or ["Territory mapped, proceed"]
        )

    def _invoke_synthesizer(self, request: TwinRequest, brain: Optional[Brain]) -> TwinResponse:
        """Synthesizer Twin — Merges ideas, creates coherence, builds frameworks."""
        synthesis_hints = []
        suggestions = []

        if brain:
            dims = brain.dimensions
            if dims.get("topology", 0) > 0.5 and dims.get("depth", 0) > 0.5:
                synthesis_hints.append("Good balance for framework building")
                suggestions.append("Create a unifying structure for these ideas")
            if dims.get("evolution", 0) > 0.6:
                synthesis_hints.append("Evolution-oriented — optimize for growth")
                suggestions.append("Build synthesis that can evolve over time")

        return TwinResponse(
            twin_type=TwinType.SYNTHESIZER,
            brain_id=request.brain_id,
            response=f"Synthesizer processing: {request.query[:100]}...",
            reasoning="Merging disparate elements into coherent frameworks.",
            suggestions=suggestions or ["Look for the unifying thread"],
            resonance_hints=synthesis_hints or ["Synthesis possible"]
        )

    def _invoke_mirror(self, request: TwinRequest, brain: Optional[Brain]) -> TwinResponse:
        """Mirror Twin — Reflects, questions, reveals blind spots."""
        reflection_hints = []
        suggestions = []

        if brain:
            dims = brain.dimensions
            if dims.get("entropy", 0) < 0.3:
                reflection_hints.append("Low entropy — may be missing unexpected angles")
                suggestions.append("What would surprise you here?")
            if dims.get("depth", 0) < 0.3:
                reflection_hints.append("Low depth — surface-level understanding risk")
                suggestions.append("What assumptions haven't you examined?")
            if dims.get("velocity", 0) < 0.3:
                reflection_hints.append("Low velocity — action may be delayed")
                suggestions.append("What's stopping you from starting now?")

        return TwinResponse(
            twin_type=TwinType.MIRROR,
            brain_id=request.brain_id,
            response=f"Mirror reflection on: {request.query[:100]}...",
            reasoning="Holding up a mirror to reveal what you might not see.",
            suggestions=suggestions or ["What are you not seeing?"],
            resonance_hints=reflection_hints or ["Look again, look deeper"]
        )


# Singleton instance
_twin_engine: Optional[TwinEngine] = None


def get_twin_engine() -> TwinEngine:
    """Get the singleton twin engine."""
    global _twin_engine
    if _twin_engine is None:
        _twin_engine = TwinEngine()
    return _twin_engine
