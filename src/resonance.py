"""Resonance matching between brains."""

from __future__ import annotations

from .schemas import Brain, ResonanceLevel, ResonanceResult


def calculate_overlap(brain1: Brain, brain2: Brain) -> float:
    """Calculate dimension overlap between two brains."""
    dims1 = brain1.dimensions
    dims2 = brain2.dimensions

    overlap = 0.0
    for dim in dims1:
        if dim in dims2:
            # Calculate similarity (1 - absolute difference)
            diff = abs(dims1[dim] - dims2[dim])
            overlap += (1 - diff)

    # Normalize to 0-1
    return overlap / len(dims1) if dims1 else 0.0


def find_shared_dimensions(brain1: Brain, brain2: Brain, threshold: float = 0.7) -> list[str]:
    """Find dimensions where both brains score similarly high."""
    shared = []
    dims1 = brain1.dimensions
    dims2 = brain2.dimensions

    for dim in dims1:
        if dim in dims2:
            if dims1[dim] > threshold and dims2[dim] > threshold:
                shared.append(dim)

    return shared


def find_complementary_dimensions(brain1: Brain, brain2: Brain, threshold: float = 0.5) -> list[str]:
    """Find dimensions where one brain is strong and the other is weak."""
    complementary = []
    dims1 = brain1.dimensions
    dims2 = brain2.dimensions

    for dim in dims1:
        if dim in dims2:
            # One high, one low = complementary
            if (dims1[dim] > 0.7 and dims2[dim] < 0.4) or (dims2[dim] > 0.7 and dims1[dim] < 0.4):
                complementary.append(dim)

    return complementary


def determine_resonance_level(overlap: float, shared: list[str], complementary: list[str]) -> ResonanceLevel:
    """Determine resonance level based on overlap and patterns."""
    if overlap >= 0.9 and len(shared) >= 4:
        return ResonanceLevel.MERGED
    elif overlap >= 0.75 and len(shared) >= 3:
        return ResonanceLevel.ENTANGLED
    elif overlap >= 0.6 or len(shared) >= 2:
        return ResonanceLevel.RESONANT
    else:
        return ResonanceLevel.AWARE


def calculate_collaboration_potential(brain1: Brain, brain2: Brain, shared: list[str], complementary: list[str]) -> float:
    """Calculate collaboration potential based on shared and complementary strengths."""
    # High collaboration if they share some dimensions but also complement each other
    shared_bonus = len(shared) * 0.15
    complementary_bonus = len(complementary) * 0.2

    # Same archetype can be good (deep collaboration) or limiting (similar blind spots)
    archetype_factor = 0.1 if brain1.archetype == brain2.archetype else 0.15

    potential = min(1.0, shared_bonus + complementary_bonus + archetype_factor)
    return round(potential, 2)


def calculate_resonance(brain1: Brain, brain2: Brain) -> ResonanceResult:
    """Calculate full resonance between two brains."""
    overlap = calculate_overlap(brain1, brain2)
    shared = find_shared_dimensions(brain1, brain2)
    complementary = find_complementary_dimensions(brain1, brain2)
    level = determine_resonance_level(overlap, shared, complementary)
    collab_potential = calculate_collaboration_potential(brain1, brain2, shared, complementary)

    return ResonanceResult(
        brain_id_1=brain1.brain_id,
        brain_id_2=brain2.brain_id,
        level=level,
        overlap_score=round(overlap, 3),
        shared_dimensions=shared,
        complementary_dimensions=complementary,
        collaboration_potential=collab_potential
    )
