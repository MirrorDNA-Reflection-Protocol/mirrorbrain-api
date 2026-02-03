"""Consent Proof Logging — Legal audit trail for user consent."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class ConsentProof(BaseModel):
    """A logged consent proof."""
    id: Optional[int] = None
    proof_hash: str = Field(..., description="Mirror Proof hash (e.g., ⟡A3F2-8C1D)")
    timestamp: int = Field(..., description="Unix timestamp when consent was given")
    version: str = Field(..., description="Consent version (e.g., 1.0)")
    acks: List[str] = Field(default_factory=list, description="Acknowledgments checked")
    page: str = Field(default="/", description="Page where consent was given")
    fingerprint: str = Field(default="", description="Hashed browser fingerprint")
    user_agent: str = Field(default="", description="User agent string")
    screen: Optional[str] = Field(default=None, description="Screen resolution")
    timezone: Optional[str] = Field(default=None, description="User timezone")
    language: Optional[str] = Field(default=None, description="Browser language")
    referrer: Optional[str] = Field(default=None, description="Referrer URL")
    consent_type: str = Field(default="full", description="full or quick")
    feature: Optional[str] = Field(default=None, description="Feature for quick consent")
    logged_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ConsentLogRequest(BaseModel):
    """Request body for logging consent."""
    hash: Optional[str] = None  # Full consent
    proof_hash: Optional[str] = None  # Alternative field name
    timestamp: int
    version: str = "1.0"
    acks: List[str] = Field(default_factory=list)
    page: str = "/"
    fingerprint: str = ""
    user_agent: str = ""
    screen: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    referrer: Optional[str] = None
    type: Optional[str] = None  # For quick consent
    feature: Optional[str] = None  # For quick consent
    logged_at: Optional[str] = None


class ConsentStats(BaseModel):
    """Consent statistics."""
    total_consents: int
    full_consents: int
    quick_consents: int
    unique_fingerprints: int
    consents_today: int
    consents_this_week: int
    top_pages: List[Dict[str, Any]]
    version_breakdown: Dict[str, int]


class ConsentStorage:
    """SQLite storage for consent proofs."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consent_proofs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proof_hash TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    acks TEXT,
                    page TEXT,
                    fingerprint TEXT,
                    user_agent TEXT,
                    screen TEXT,
                    timezone TEXT,
                    language TEXT,
                    referrer TEXT,
                    consent_type TEXT DEFAULT 'full',
                    feature TEXT,
                    logged_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Index for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprint ON consent_proofs(fingerprint)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON consent_proofs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_version ON consent_proofs(version)")
            conn.commit()

    def log(self, proof: ConsentProof) -> int:
        """Log a consent proof. Returns the ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO consent_proofs
                (proof_hash, timestamp, version, acks, page, fingerprint,
                 user_agent, screen, timezone, language, referrer,
                 consent_type, feature, logged_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proof.proof_hash,
                proof.timestamp,
                proof.version,
                json.dumps(proof.acks),
                proof.page,
                proof.fingerprint,
                proof.user_agent,
                proof.screen,
                proof.timezone,
                proof.language,
                proof.referrer,
                proof.consent_type,
                proof.feature,
                proof.logged_at
            ))
            conn.commit()
            return cursor.lastrowid

    def get_by_fingerprint(self, fingerprint: str) -> List[ConsentProof]:
        """Get all consents for a fingerprint."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM consent_proofs WHERE fingerprint = ? ORDER BY timestamp DESC",
                (fingerprint,)
            )
            return [self._row_to_proof(row) for row in cursor.fetchall()]

    def get_stats(self) -> ConsentStats:
        """Get consent statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Total counts
            total = conn.execute("SELECT COUNT(*) as c FROM consent_proofs").fetchone()["c"]
            full = conn.execute("SELECT COUNT(*) as c FROM consent_proofs WHERE consent_type = 'full'").fetchone()["c"]
            quick = conn.execute("SELECT COUNT(*) as c FROM consent_proofs WHERE consent_type = 'quick'").fetchone()["c"]

            # Unique fingerprints
            unique = conn.execute("SELECT COUNT(DISTINCT fingerprint) as c FROM consent_proofs").fetchone()["c"]

            # Time-based
            now = datetime.now()
            today_start = int(datetime(now.year, now.month, now.day).timestamp() * 1000)
            week_start = int((datetime(now.year, now.month, now.day).timestamp() - 7*24*60*60) * 1000)

            today = conn.execute(
                "SELECT COUNT(*) as c FROM consent_proofs WHERE timestamp >= ?",
                (today_start,)
            ).fetchone()["c"]

            week = conn.execute(
                "SELECT COUNT(*) as c FROM consent_proofs WHERE timestamp >= ?",
                (week_start,)
            ).fetchone()["c"]

            # Top pages
            pages = conn.execute("""
                SELECT page, COUNT(*) as count
                FROM consent_proofs
                GROUP BY page
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()

            # Version breakdown
            versions = conn.execute("""
                SELECT version, COUNT(*) as count
                FROM consent_proofs
                GROUP BY version
            """).fetchall()

            return ConsentStats(
                total_consents=total,
                full_consents=full,
                quick_consents=quick,
                unique_fingerprints=unique,
                consents_today=today,
                consents_this_week=week,
                top_pages=[{"page": r["page"], "count": r["count"]} for r in pages],
                version_breakdown={r["version"]: r["count"] for r in versions}
            )

    def _row_to_proof(self, row: sqlite3.Row) -> ConsentProof:
        """Convert a database row to a ConsentProof."""
        return ConsentProof(
            id=row["id"],
            proof_hash=row["proof_hash"],
            timestamp=row["timestamp"],
            version=row["version"],
            acks=json.loads(row["acks"]) if row["acks"] else [],
            page=row["page"],
            fingerprint=row["fingerprint"],
            user_agent=row["user_agent"],
            screen=row["screen"],
            timezone=row["timezone"],
            language=row["language"],
            referrer=row["referrer"],
            consent_type=row["consent_type"],
            feature=row["feature"],
            logged_at=row["logged_at"]
        )


# Singleton instance
_consent_storage: Optional[ConsentStorage] = None


def get_consent_storage(db_path: Optional[Path] = None) -> ConsentStorage:
    """Get the singleton consent storage instance."""
    global _consent_storage
    if _consent_storage is None:
        if db_path is None:
            db_path = Path.home() / ".mirrordna" / "brain" / "consent.db"
        _consent_storage = ConsentStorage(db_path)
    return _consent_storage
