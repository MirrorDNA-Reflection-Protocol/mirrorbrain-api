# MirrorBrain API — Claude Code Instructions

## What This Is

FastAPI backend for brain.activemirror.ai — the Cognitive Engine for MirrorDNA:
- BrainScan quiz (8 questions → brain archetype)
- AI Twins (Guardian, Scout, Synthesizer, Mirror)
- Resonance matching between brains
- Brain storage and visualization data

## Key Files

```
src/
├── main.py       # FastAPI application (entry point)
├── schemas.py    # Pydantic models
├── quiz.py       # BrainScan quiz logic
├── twins.py      # AI Twin engine
├── resonance.py  # Brain resonance matching
└── storage.py    # Brain persistence

tests/
└── test_api.py   # API tests
```

## Running

```bash
cd ~/repos/mirrorbrain-api
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```

## Testing

```bash
pytest tests/ -v
```

## API Endpoints

### Quiz
- `GET /api/quiz/questions` — Get all questions
- `POST /api/quiz/submit` — Submit answers, get brain analysis
- `GET /api/archetypes` — List brain archetypes

### Brain CRUD
- `GET /api/brain/:id` — Get brain data
- `GET /api/brain/:id/stats` — Get statistics
- `PUT /api/brain/:id` — Update brain
- `DELETE /api/brain/:id` — Delete brain
- `GET /api/brains` — List public brains
- `GET /api/brains/leaderboard` — Top brains
- `GET /api/brains/search?q=` — Search brains

### Twins
- `GET /api/twins` — List twin types
- `POST /api/brain/:id/twin/:type?query=` — Invoke a twin

### Resonance
- `GET /api/brain/:id/compare/:id2` — Compare two brains
- `POST /api/resonance` — Calculate resonance

### Famous
- `GET /api/famous` — List famous brain examples
- `GET /api/famous/:name` — Get famous brain

## Brain Archetypes

- 🔷 **Architect** — Systems thinker, builds frameworks
- 🟣 **Explorer** — Curiosity-driven, wide connections
- 🟢 **Builder** — Execution-focused, ships fast
- 🟡 **Analyst** — Deep diver, precision matters
- 🔵 **Connector** — Bridges people and ideas
- 🟠 **Creative** — Unexpected links, artistic
- ⚪ **Scholar** — Knowledge accumulator, thorough
- 🔴 **Strategist** — Big picture, long-term

## AI Twins

- **Guardian** — Protects focus, filters noise
- **Scout** — Explores, finds opportunities
- **Synthesizer** — Merges ideas, builds frameworks
- **Mirror** — Reflects, reveals blind spots

## Dimensions

Each brain has 5 dimensions (0-1 scale):
- `topology` — Connectedness, cross-domain thinking
- `velocity` — Speed of thought, iteration rate
- `depth` — How deep you go into topics
- `entropy` — Tolerance for chaos, unexpected paths
- `evolution` — Growth orientation, adaptability

## Deployment

For Vercel:
```bash
vercel --prod
```

For self-hosted:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
