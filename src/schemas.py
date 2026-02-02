"""Pydantic schemas for MirrorBrain API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class BrainArchetype(str, Enum):
    """The 8 brain archetypes from BrainScan."""
    ARCHITECT = "architect"
    EXPLORER = "explorer"
    BUILDER = "builder"
    ANALYST = "analyst"
    CONNECTOR = "connector"
    CREATIVE = "creative"
    SCHOLAR = "scholar"
    STRATEGIST = "strategist"


class TwinType(str, Enum):
    """AI Twin types."""
    GUARDIAN = "guardian"
    SCOUT = "scout"
    SYNTHESIZER = "synthesizer"
    MIRROR = "mirror"


class TwinMode(str, Enum):
    """Twin interaction modes."""
    SINGLE = "single"      # One twin responds
    COUNCIL = "council"    # All 4 twins respond
    DEBATE = "debate"      # Two twins argue
    RELAY = "relay"        # Chain: Guardian → Scout → Synthesizer → Mirror


class ResonanceLevel(str, Enum):
    """Resonance levels between brains."""
    AWARE = "aware"
    RESONANT = "resonant"
    ENTANGLED = "entangled"
    MERGED = "merged"


# --- Quiz Models ---

class QuizAnswer(BaseModel):
    """A single quiz answer."""
    question_id: int
    answer_index: int


class QuizSubmission(BaseModel):
    """Complete quiz submission."""
    answers: list[QuizAnswer]
    user_id: Optional[str] = None


class QuizResult(BaseModel):
    """Result of quiz analysis."""
    brain_id: str = Field(default_factory=lambda: f"BRAIN-{uuid.uuid4().hex[:8]}")
    archetype: BrainArchetype
    archetype_name: str
    archetype_emoji: str
    description: str
    strengths: list[str]
    dimensions: dict[str, float]  # topology, velocity, depth, entropy, evolution
    node_count: int
    connection_count: int
    created_at: datetime = Field(default_factory=datetime.now)


# --- Brain Models ---

class BrainNode(BaseModel):
    """A node in the brain graph."""
    id: str
    label: str
    category: str
    weight: float = 1.0
    connections: list[str] = []


class BrainGraph(BaseModel):
    """Full brain graph structure."""
    brain_id: str
    nodes: list[BrainNode]
    edges: list[tuple[str, str, float]]  # source, target, weight
    metadata: dict = {}


class Brain(BaseModel):
    """Complete brain profile."""
    brain_id: str
    user_id: Optional[str] = None
    archetype: BrainArchetype
    dimensions: dict[str, float]
    node_count: int
    connection_count: int
    graph: Optional[BrainGraph] = None
    twins: list[TwinType] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    public: bool = False


class BrainStats(BaseModel):
    """Brain statistics."""
    brain_id: str
    archetype: BrainArchetype
    node_count: int
    connection_count: int
    density: float
    avg_connections: float
    dimensions: dict[str, float]


# --- Twin Models ---

class TwinRequest(BaseModel):
    """Request to invoke a Twin."""
    brain_id: str
    twin_type: TwinType
    query: str
    context: Optional[dict] = None


class TwinResponse(BaseModel):
    """Response from a Twin."""
    twin_type: TwinType
    brain_id: str
    response: str
    reasoning: Optional[str] = None
    suggestions: list[str] = []
    resonance_hints: list[str] = []


class CouncilResponse(BaseModel):
    """Response from all 4 twins (Council mode)."""
    brain_id: str
    query: str
    guardian: TwinResponse
    scout: TwinResponse
    synthesizer: TwinResponse
    mirror: TwinResponse
    synthesis: Optional[str] = None  # Meta-synthesis of all perspectives


class DebateTurn(BaseModel):
    """A single turn in a debate."""
    twin_type: TwinType
    response: str
    responding_to: Optional[str] = None


class DebateResponse(BaseModel):
    """Response from a twin debate."""
    brain_id: str
    query: str
    twin_1: TwinType
    twin_2: TwinType
    turns: list[DebateTurn]
    conclusion: Optional[str] = None


class RelayStage(BaseModel):
    """A stage in the relay chain."""
    twin_type: TwinType
    input_context: str
    response: str


class RelayResponse(BaseModel):
    """Response from relay mode (chained twins)."""
    brain_id: str
    query: str
    stages: list[RelayStage]
    final_output: str


class TwinMemoryEntry(BaseModel):
    """A single entry in twin conversation history."""
    timestamp: datetime
    twin_type: TwinType
    mode: TwinMode
    query: str
    response: str
    brain_context: Optional[dict] = None


class TwinHistory(BaseModel):
    """Twin conversation history for a brain."""
    brain_id: str
    entries: list[TwinMemoryEntry]
    total_interactions: int


# --- Resonance Models ---

class ResonanceRequest(BaseModel):
    """Request to check resonance between brains."""
    brain_id_1: str
    brain_id_2: str


class ResonanceResult(BaseModel):
    """Resonance analysis result."""
    brain_id_1: str
    brain_id_2: str
    level: ResonanceLevel
    overlap_score: float
    shared_dimensions: list[str]
    complementary_dimensions: list[str]
    collaboration_potential: float


# --- API Response Models ---

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    message: str
    recoverable: bool = True
