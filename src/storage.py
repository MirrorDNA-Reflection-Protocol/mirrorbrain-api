"""Brain storage — in-memory with optional persistence."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from .schemas import Brain, BrainStats


class BrainStorage:
    """Storage for brain data."""

    def __init__(self, data_path: Optional[Path] = None):
        self._brains: Dict[str, Brain] = {}
        self._data_path = data_path
        if data_path:
            data_path.mkdir(parents=True, exist_ok=True)
            self._load_all()

    def _load_all(self) -> None:
        """Load all brains from disk."""
        if not self._data_path:
            return
        for file in self._data_path.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    brain = Brain(**data)
                    self._brains[brain.brain_id] = brain
            except Exception:
                pass  # Skip invalid files

    def _save(self, brain: Brain) -> None:
        """Save a brain to disk."""
        if not self._data_path:
            return
        file = self._data_path / f"{brain.brain_id}.json"
        with open(file, "w") as f:
            json.dump(brain.model_dump(mode="json"), f, indent=2, default=str)

    def _delete_file(self, brain_id: str) -> None:
        """Delete a brain file from disk."""
        if not self._data_path:
            return
        file = self._data_path / f"{brain_id}.json"
        if file.exists():
            file.unlink()

    def save(self, brain: Brain) -> Brain:
        """Save or update a brain."""
        brain.updated_at = datetime.now()
        self._brains[brain.brain_id] = brain
        self._save(brain)
        return brain

    def get(self, brain_id: str) -> Optional[Brain]:
        """Get a brain by ID."""
        return self._brains.get(brain_id)

    def delete(self, brain_id: str) -> bool:
        """Delete a brain."""
        if brain_id in self._brains:
            del self._brains[brain_id]
            self._delete_file(brain_id)
            return True
        return False

    def list_all(self, public_only: bool = False) -> List[Brain]:
        """List all brains."""
        brains = list(self._brains.values())
        if public_only:
            brains = [b for b in brains if b.public]
        return sorted(brains, key=lambda b: b.created_at, reverse=True)

    def list_by_archetype(self, archetype: str) -> List[Brain]:
        """List brains by archetype."""
        return [b for b in self._brains.values() if b.archetype.value == archetype]

    def get_stats(self, brain_id: str) -> Optional[BrainStats]:
        """Get stats for a brain."""
        brain = self.get(brain_id)
        if not brain:
            return None

        density = brain.connection_count / brain.node_count if brain.node_count > 0 else 0
        avg_connections = brain.connection_count / brain.node_count if brain.node_count > 0 else 0

        return BrainStats(
            brain_id=brain.brain_id,
            archetype=brain.archetype,
            node_count=brain.node_count,
            connection_count=brain.connection_count,
            density=round(density, 4),
            avg_connections=round(avg_connections, 2),
            dimensions=brain.dimensions
        )

    def search(self, query: str) -> List[Brain]:
        """Search brains (placeholder — would use vector search in production)."""
        query_lower = query.lower()
        results = []
        for brain in self._brains.values():
            if brain.public:
                if query_lower in brain.archetype.value.lower():
                    results.append(brain)
        return results

    def get_leaderboard(self, limit: int = 10) -> List[Brain]:
        """Get top brains by node count (public only)."""
        public_brains = [b for b in self._brains.values() if b.public]
        return sorted(public_brains, key=lambda b: b.node_count, reverse=True)[:limit]


# Singleton instance
_storage: Optional[BrainStorage] = None


def get_storage(data_path: Optional[Path] = None) -> BrainStorage:
    """Get the singleton storage instance."""
    global _storage
    if _storage is None:
        _storage = BrainStorage(data_path)
    return _storage
