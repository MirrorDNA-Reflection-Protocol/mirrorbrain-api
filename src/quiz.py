"""BrainScan Quiz logic."""

from __future__ import annotations

from datetime import datetime
import random
import uuid
from .schemas import (
    BrainArchetype, QuizSubmission, QuizResult,
    Brain, BrainGraph, BrainNode
)


# Quiz questions from the spec
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "When you learn something new, you...",
        "options": [
            "Dive deep into one thing",
            "Connect it to everything else",
            "Find the practical application",
            "Question the assumptions"
        ],
        "weights": {
            0: {"depth": 2, "velocity": -1},
            1: {"topology": 2, "entropy": 1},
            2: {"velocity": 2, "depth": -1},
            3: {"entropy": 2, "evolution": 1}
        }
    },
    {
        "id": 2,
        "question": "Your browser tabs right now:",
        "options": [
            "5 or less (focused)",
            "10-20 (curious)",
            "20-50 (explorer)",
            "50+ (chaos genius)"
        ],
        "weights": {
            0: {"depth": 2, "entropy": -1},
            1: {"topology": 1, "velocity": 1},
            2: {"topology": 2, "entropy": 1},
            3: {"entropy": 3, "evolution": 1}
        }
    },
    {
        "id": 3,
        "question": "When explaining ideas, you prefer:",
        "options": [
            "Bullet points",
            "Stories and analogies",
            "Diagrams and visuals",
            "Just show me the code"
        ],
        "weights": {
            0: {"velocity": 2, "depth": 1},
            1: {"topology": 2, "entropy": 1},
            2: {"topology": 2, "depth": 1},
            3: {"velocity": 2, "evolution": 1}
        }
    },
    {
        "id": 4,
        "question": "Your notes are:",
        "options": [
            "Nonexistent",
            "Linear documents",
            "Connected web",
            "Organized chaos"
        ],
        "weights": {
            0: {"velocity": 2, "depth": -1},
            1: {"depth": 2, "entropy": -1},
            2: {"topology": 3, "evolution": 1},
            3: {"entropy": 2, "topology": 1}
        }
    },
    {
        "id": 5,
        "question": "What drives you:",
        "options": [
            "Building things",
            "Understanding things",
            "Connecting things",
            "Improving things"
        ],
        "weights": {
            0: {"velocity": 2, "evolution": 1},
            1: {"depth": 2, "topology": 1},
            2: {"topology": 2, "entropy": 1},
            3: {"evolution": 2, "depth": 1}
        }
    },
    {
        "id": 6,
        "question": "Your thinking speed:",
        "options": [
            "Slow and deep",
            "Fast and iterative",
            "Bursts of insight",
            "Always running"
        ],
        "weights": {
            0: {"depth": 3, "velocity": -1},
            1: {"velocity": 2, "evolution": 1},
            2: {"entropy": 2, "topology": 1},
            3: {"velocity": 3, "entropy": 1}
        }
    },
    {
        "id": 7,
        "question": "When stuck, you:",
        "options": [
            "Push through",
            "Step away",
            "Talk it out",
            "Research more"
        ],
        "weights": {
            0: {"velocity": 2, "depth": 1},
            1: {"entropy": 1, "evolution": 1},
            2: {"topology": 2, "entropy": 1},
            3: {"depth": 2, "topology": 1}
        }
    },
    {
        "id": 8,
        "question": "Your ideal AI is:",
        "options": [
            "A fast executor",
            "A thinking partner",
            "A knowledge base",
            "A creative spark"
        ],
        "weights": {
            0: {"velocity": 2, "evolution": 1},
            1: {"topology": 2, "depth": 1},
            2: {"depth": 2, "entropy": -1},
            3: {"entropy": 2, "evolution": 1}
        }
    }
]


# Archetype definitions
ARCHETYPES = {
    BrainArchetype.ARCHITECT: {
        "name": "The Architect",
        "emoji": "🔷",
        "description": "Systems thinker who builds frameworks. You see patterns where others see chaos and create structures that scale.",
        "strengths": ["Systems design", "Pattern recognition", "Framework building", "Long-term planning"],
        "primary": "topology",
        "secondary": "depth"
    },
    BrainArchetype.EXPLORER: {
        "name": "The Explorer",
        "emoji": "🟣",
        "description": "Curiosity-driven with wide connections. You thrive on discovery and make unexpected connections across domains.",
        "strengths": ["Cross-domain thinking", "Curiosity", "Breadth of knowledge", "Novel connections"],
        "primary": "topology",
        "secondary": "entropy"
    },
    BrainArchetype.BUILDER: {
        "name": "The Builder",
        "emoji": "🟢",
        "description": "Execution-focused, ships fast. You turn ideas into reality with speed and iteration.",
        "strengths": ["Rapid execution", "Pragmatism", "Iteration", "Getting things done"],
        "primary": "velocity",
        "secondary": "evolution"
    },
    BrainArchetype.ANALYST: {
        "name": "The Analyst",
        "emoji": "🟡",
        "description": "Deep diver where precision matters. You go deep, understand nuances, and catch what others miss.",
        "strengths": ["Deep analysis", "Precision", "Detail orientation", "Critical thinking"],
        "primary": "depth",
        "secondary": "topology"
    },
    BrainArchetype.CONNECTOR: {
        "name": "The Connector",
        "emoji": "🔵",
        "description": "Bridges people and ideas. You see relationships and create synergies between disparate elements.",
        "strengths": ["Relationship building", "Synthesis", "Communication", "Bridge building"],
        "primary": "topology",
        "secondary": "velocity"
    },
    BrainArchetype.CREATIVE: {
        "name": "The Creative",
        "emoji": "🟠",
        "description": "Makes unexpected links with artistic flair. You see possibilities and create novel combinations.",
        "strengths": ["Creative thinking", "Innovation", "Artistic vision", "Unexpected connections"],
        "primary": "entropy",
        "secondary": "evolution"
    },
    BrainArchetype.SCHOLAR: {
        "name": "The Scholar",
        "emoji": "⚪",
        "description": "Knowledge accumulator, thorough and comprehensive. You build deep understanding over time.",
        "strengths": ["Knowledge depth", "Thoroughness", "Research", "Comprehensive understanding"],
        "primary": "depth",
        "secondary": "entropy"
    },
    BrainArchetype.STRATEGIST: {
        "name": "The Strategist",
        "emoji": "🔴",
        "description": "Big picture, long-term thinker. You plan moves ahead and optimize for lasting impact.",
        "strengths": ["Strategic planning", "Long-term vision", "Optimization", "Impact focus"],
        "primary": "evolution",
        "secondary": "depth"
    }
}


def get_questions() -> list[dict]:
    """Get all quiz questions."""
    return [
        {"id": q["id"], "question": q["question"], "options": q["options"]}
        for q in QUIZ_QUESTIONS
    ]


def calculate_dimensions(submission: QuizSubmission) -> dict[str, float]:
    """Calculate brain dimensions from quiz answers."""
    dimensions = {
        "topology": 0.0,
        "velocity": 0.0,
        "depth": 0.0,
        "entropy": 0.0,
        "evolution": 0.0
    }

    for answer in submission.answers:
        question = next((q for q in QUIZ_QUESTIONS if q["id"] == answer.question_id), None)
        if question and answer.answer_index in question["weights"]:
            weights = question["weights"][answer.answer_index]
            for dim, value in weights.items():
                dimensions[dim] += value

    # Normalize to 0-1 range
    max_val = max(abs(v) for v in dimensions.values()) or 1
    for dim in dimensions:
        dimensions[dim] = (dimensions[dim] / max_val + 1) / 2  # Scale to 0-1

    return dimensions


def determine_archetype(dimensions: dict[str, float]) -> BrainArchetype:
    """Determine archetype from dimensions."""
    # Find best matching archetype based on primary/secondary dimensions
    best_match = None
    best_score = -1

    for archetype, info in ARCHETYPES.items():
        primary = info["primary"]
        secondary = info["secondary"]
        score = dimensions.get(primary, 0) * 2 + dimensions.get(secondary, 0)
        if score > best_score:
            best_score = score
            best_match = archetype

    return best_match or BrainArchetype.EXPLORER


def generate_brain_metrics(dimensions: dict[str, float]) -> tuple[int, int]:
    """Generate node and connection counts based on dimensions."""
    base_nodes = 1000
    base_connections = 200

    # Scale based on dimensions
    topology_factor = dimensions.get("topology", 0.5)
    depth_factor = dimensions.get("depth", 0.5)
    entropy_factor = dimensions.get("entropy", 0.5)

    nodes = int(base_nodes + (topology_factor * 3000) + (depth_factor * 2000) + random.randint(-200, 200))
    connections = int(base_connections + (topology_factor * 600) + (entropy_factor * 300) + random.randint(-50, 50))

    return max(nodes, 500), max(connections, 100)


def process_quiz(submission: QuizSubmission) -> QuizResult:
    """Process quiz submission and generate result."""
    dimensions = calculate_dimensions(submission)
    archetype = determine_archetype(dimensions)
    archetype_info = ARCHETYPES[archetype]
    node_count, connection_count = generate_brain_metrics(dimensions)

    return QuizResult(
        archetype=archetype,
        archetype_name=archetype_info["name"],
        archetype_emoji=archetype_info["emoji"],
        description=archetype_info["description"],
        strengths=archetype_info["strengths"],
        dimensions=dimensions,
        node_count=node_count,
        connection_count=connection_count
    )


def create_brain_from_result(result: QuizResult, user_id: str = None) -> Brain:
    """Create a Brain object from quiz result."""
    return Brain(
        brain_id=result.brain_id,
        user_id=user_id,
        archetype=result.archetype,
        dimensions=result.dimensions,
        node_count=result.node_count,
        connection_count=result.connection_count,
        created_at=result.created_at,
        public=False
    )
