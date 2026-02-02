"""MirrorBrain API — FastAPI application for brain.activemirror.ai"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings

from .schemas import (
    Brain, BrainStats, QuizSubmission, QuizResult,
    TwinRequest, TwinResponse, ResonanceRequest, ResonanceResult,
    HealthResponse, ErrorResponse, TwinType, TwinMode,
    CouncilResponse, DebateResponse, RelayResponse, TwinHistory
)
from .quiz import get_questions, process_quiz, create_brain_from_result, ARCHETYPES
from .twins import get_twin_engine
from .resonance import calculate_resonance
from .storage import get_storage


class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "MirrorBrain API"
    version: str = "1.0.0"
    debug: bool = False
    data_path: str = "~/.mirrordna/brain/data"

    class Config:
        env_prefix = "MIRRORBRAIN_"


settings = Settings()

# Initialize FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Cognitive Engine API for brain.activemirror.ai — BrainScan, Twins, Resonance",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
data_path = Path(settings.data_path).expanduser()
storage = get_storage(data_path)
twin_engine = get_twin_engine()


# ==================== Health ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint — health check."""
    return HealthResponse(
        status="healthy",
        version=settings.version,
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.version,
        timestamp=datetime.now()
    )


# ==================== Quiz ====================

@app.get("/api/quiz/questions")
async def get_quiz_questions():
    """Get all quiz questions."""
    return {"questions": get_questions()}


@app.post("/api/quiz/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get brain analysis."""
    if len(submission.answers) != 8:
        raise HTTPException(status_code=400, detail="Must answer all 8 questions")

    result = process_quiz(submission)

    # Create and store brain
    brain = create_brain_from_result(result, submission.user_id)
    storage.save(brain)
    twin_engine.register_brain(brain)

    return result


@app.get("/api/archetypes")
async def get_archetypes():
    """Get all brain archetypes."""
    return {
        archetype.value: {
            "name": info["name"],
            "emoji": info["emoji"],
            "description": info["description"],
            "strengths": info["strengths"]
        }
        for archetype, info in ARCHETYPES.items()
    }


# ==================== Brain CRUD ====================

@app.get("/api/brain/{brain_id}", response_model=Brain)
async def get_brain(brain_id: str):
    """Get a brain by ID."""
    brain = storage.get(brain_id)
    if not brain:
        raise HTTPException(status_code=404, detail="Brain not found")
    return brain


@app.get("/api/brain/{brain_id}/stats", response_model=BrainStats)
async def get_brain_stats(brain_id: str):
    """Get brain statistics."""
    stats = storage.get_stats(brain_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Brain not found")
    return stats


@app.put("/api/brain/{brain_id}")
async def update_brain(brain_id: str, public: Optional[bool] = None):
    """Update brain properties."""
    brain = storage.get(brain_id)
    if not brain:
        raise HTTPException(status_code=404, detail="Brain not found")

    if public is not None:
        brain.public = public

    storage.save(brain)
    return {"success": True, "brain_id": brain_id}


@app.delete("/api/brain/{brain_id}")
async def delete_brain(brain_id: str):
    """Delete a brain."""
    if not storage.delete(brain_id):
        raise HTTPException(status_code=404, detail="Brain not found")
    return {"success": True, "brain_id": brain_id}


@app.get("/api/brains")
async def list_brains(
    sort: str = Query("recent", enum=["recent", "popular", "nodes"]),
    archetype: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List public brains."""
    if archetype and archetype != "all":
        brains = storage.list_by_archetype(archetype)
        brains = [b for b in brains if b.public]
    else:
        brains = storage.list_all(public_only=True)

    # Sort
    if sort == "nodes":
        brains = sorted(brains, key=lambda b: b.node_count, reverse=True)
    elif sort == "popular":
        brains = sorted(brains, key=lambda b: b.connection_count, reverse=True)
    # default: recent (already sorted by created_at)

    # Paginate
    start = (page - 1) * limit
    end = start + limit

    return {
        "brains": brains[start:end],
        "total": len(brains),
        "page": page,
        "limit": limit
    }


@app.get("/api/brains/leaderboard")
async def get_leaderboard(limit: int = Query(10, ge=1, le=50)):
    """Get top brains leaderboard."""
    return {"leaderboard": storage.get_leaderboard(limit)}


@app.get("/api/brains/search")
async def search_brains(q: str = Query(..., min_length=1)):
    """Search public brains."""
    results = storage.search(q)
    return {"results": results, "query": q}


# ==================== Twins ====================

@app.post("/api/brain/{brain_id}/twin/{twin_type}", response_model=TwinResponse)
async def invoke_twin(brain_id: str, twin_type: str, query: str):
    """Invoke an AI Twin."""
    try:
        twin = TwinType(twin_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid twin type: {twin_type}")

    brain = storage.get(brain_id)
    if brain:
        twin_engine.register_brain(brain)

    request = TwinRequest(
        brain_id=brain_id,
        twin_type=twin,
        query=query
    )

    response = twin_engine.invoke_twin(request)
    return response


@app.get("/api/twins")
async def list_twins():
    """List available twin types."""
    return {
        "twins": [
            {
                "type": TwinType.GUARDIAN.value,
                "name": "Guardian",
                "description": "Protects boundaries, filters noise, maintains focus"
            },
            {
                "type": TwinType.SCOUT.value,
                "name": "Scout",
                "description": "Explores territory, finds connections, surfaces opportunities"
            },
            {
                "type": TwinType.SYNTHESIZER.value,
                "name": "Synthesizer",
                "description": "Merges ideas, creates coherence, builds frameworks"
            },
            {
                "type": TwinType.MIRROR.value,
                "name": "Mirror",
                "description": "Reflects, questions, reveals blind spots"
            }
        ],
        "modes": [
            {
                "type": TwinMode.SINGLE.value,
                "name": "Single",
                "description": "Ask one twin for their perspective"
            },
            {
                "type": TwinMode.COUNCIL.value,
                "name": "Council",
                "description": "All 4 twins respond to the same question"
            },
            {
                "type": TwinMode.DEBATE.value,
                "name": "Debate",
                "description": "Two twins argue different perspectives"
            },
            {
                "type": TwinMode.RELAY.value,
                "name": "Relay",
                "description": "Chain through all twins: filter → explore → synthesize → challenge"
            }
        ]
    }


# ==================== Twin Modes ====================

@app.post("/api/brain/{brain_id}/council", response_model=CouncilResponse)
async def invoke_council(brain_id: str, query: str):
    """Invoke all 4 twins on the same query (Council mode)."""
    brain = storage.get(brain_id)
    if brain:
        twin_engine.register_brain(brain)

    return twin_engine.invoke_council(brain_id, query)


@app.post("/api/brain/{brain_id}/debate", response_model=DebateResponse)
async def invoke_debate(
    brain_id: str,
    query: str,
    twin_1: str = Query("guardian", enum=["guardian", "scout", "synthesizer", "mirror"]),
    twin_2: str = Query("mirror", enum=["guardian", "scout", "synthesizer", "mirror"]),
    rounds: int = Query(3, ge=1, le=5)
):
    """Have two twins debate a topic."""
    if twin_1 == twin_2:
        raise HTTPException(status_code=400, detail="Twins must be different")

    brain = storage.get(brain_id)
    if brain:
        twin_engine.register_brain(brain)

    return twin_engine.invoke_debate(
        brain_id, query,
        TwinType(twin_1), TwinType(twin_2),
        rounds
    )


@app.post("/api/brain/{brain_id}/relay", response_model=RelayResponse)
async def invoke_relay(brain_id: str, query: str):
    """Chain through all twins: Guardian → Scout → Synthesizer → Mirror."""
    brain = storage.get(brain_id)
    if brain:
        twin_engine.register_brain(brain)

    return twin_engine.invoke_relay(brain_id, query)


@app.get("/api/brain/{brain_id}/twin-history", response_model=TwinHistory)
async def get_twin_history(brain_id: str):
    """Get twin conversation history for a brain."""
    return twin_engine.get_history(brain_id)


# ==================== Resonance ====================

@app.get("/api/brain/{brain_id}/compare/{brain_id_2}", response_model=ResonanceResult)
async def compare_brains(brain_id: str, brain_id_2: str):
    """Compare two brains for resonance."""
    brain1 = storage.get(brain_id)
    brain2 = storage.get(brain_id_2)

    if not brain1:
        raise HTTPException(status_code=404, detail=f"Brain not found: {brain_id}")
    if not brain2:
        raise HTTPException(status_code=404, detail=f"Brain not found: {brain_id_2}")

    return calculate_resonance(brain1, brain2)


@app.post("/api/resonance", response_model=ResonanceResult)
async def calculate_resonance_endpoint(request: ResonanceRequest):
    """Calculate resonance between two brains."""
    brain1 = storage.get(request.brain_id_1)
    brain2 = storage.get(request.brain_id_2)

    if not brain1:
        raise HTTPException(status_code=404, detail=f"Brain not found: {request.brain_id_1}")
    if not brain2:
        raise HTTPException(status_code=404, detail=f"Brain not found: {request.brain_id_2}")

    return calculate_resonance(brain1, brain2)


# ==================== Famous Brains (Demo) ====================

FAMOUS_BRAINS = {
    "einstein": {
        "name": "Albert Einstein",
        "archetype": "architect",
        "dimensions": {"topology": 0.95, "velocity": 0.4, "depth": 0.98, "entropy": 0.7, "evolution": 0.85},
        "node_count": 12000,
        "connection_count": 2800
    },
    "davinci": {
        "name": "Leonardo da Vinci",
        "archetype": "explorer",
        "dimensions": {"topology": 0.99, "velocity": 0.6, "depth": 0.9, "entropy": 0.95, "evolution": 0.8},
        "node_count": 15000,
        "connection_count": 4200
    },
    "jobs": {
        "name": "Steve Jobs",
        "archetype": "builder",
        "dimensions": {"topology": 0.75, "velocity": 0.95, "depth": 0.7, "entropy": 0.6, "evolution": 0.9},
        "node_count": 8500,
        "connection_count": 1900
    }
}


@app.get("/api/famous")
async def list_famous_brains():
    """List famous brain examples."""
    return {"famous": list(FAMOUS_BRAINS.keys())}


@app.get("/api/famous/{name}")
async def get_famous_brain(name: str):
    """Get a famous brain example."""
    if name not in FAMOUS_BRAINS:
        raise HTTPException(status_code=404, detail="Famous brain not found")
    return FAMOUS_BRAINS[name]


# ==================== Entry Point ====================

def main():
    """Run the server."""
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
