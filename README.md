# MirrorBrain API

> Cognitive Engine for [brain.activemirror.ai](https://brain.activemirror.ai)

Part of the [MirrorDNA](https://github.com/MirrorDNA-Reflection-Protocol) sovereign AI stack.

## Features

- **BrainScan Quiz** — 8 questions to discover your cognitive archetype
- **AI Twins** — Guardian, Scout, Synthesizer, Mirror
- **Resonance Matching** — Find cognitive alignment between brains
- **Brain Visualization** — Graph data for 3D brain rendering

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run
uvicorn src.main:app --reload

# Test
pytest tests/ -v
```

## API

```
GET  /api/quiz/questions        # Get quiz
POST /api/quiz/submit           # Submit, get brain
GET  /api/brain/:id             # Get brain
POST /api/brain/:id/twin/:type  # Invoke twin
GET  /api/brain/:id/compare/:id2 # Compare brains
```

Full docs at `/docs` when running.

## Brain Archetypes

| Archetype | Emoji | Primary Dimension |
|-----------|-------|-------------------|
| Architect | 🔷 | topology + depth |
| Explorer | 🟣 | topology + entropy |
| Builder | 🟢 | velocity + evolution |
| Analyst | 🟡 | depth + topology |
| Connector | 🔵 | topology + velocity |
| Creative | 🟠 | entropy + evolution |
| Scholar | ⚪ | depth + entropy |
| Strategist | 🔴 | evolution + depth |

## License

MIT
