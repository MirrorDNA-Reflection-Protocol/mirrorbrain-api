"""Tests for MirrorBrain API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.schemas import BrainArchetype


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealth:
    """Test health endpoints."""

    def test_root(self, client):
        """Root returns health."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health(self, client):
        """Health endpoint works."""
        response = client.get("/health")
        assert response.status_code == 200


class TestQuiz:
    """Test quiz endpoints."""

    def test_get_questions(self, client):
        """Get quiz questions."""
        response = client.get("/api/quiz/questions")
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 8

    def test_submit_quiz(self, client):
        """Submit quiz and get result."""
        submission = {
            "answers": [
                {"question_id": 1, "answer_index": 0},
                {"question_id": 2, "answer_index": 1},
                {"question_id": 3, "answer_index": 2},
                {"question_id": 4, "answer_index": 2},
                {"question_id": 5, "answer_index": 1},
                {"question_id": 6, "answer_index": 0},
                {"question_id": 7, "answer_index": 3},
                {"question_id": 8, "answer_index": 1},
            ]
        }
        response = client.post("/api/quiz/submit", json=submission)
        assert response.status_code == 200
        data = response.json()
        assert "brain_id" in data
        assert "archetype" in data
        assert "dimensions" in data
        assert "node_count" in data

    def test_submit_incomplete_quiz(self, client):
        """Incomplete quiz fails."""
        submission = {
            "answers": [
                {"question_id": 1, "answer_index": 0},
            ]
        }
        response = client.post("/api/quiz/submit", json=submission)
        assert response.status_code == 400

    def test_get_archetypes(self, client):
        """Get all archetypes."""
        response = client.get("/api/archetypes")
        assert response.status_code == 200
        data = response.json()
        assert "architect" in data
        assert "explorer" in data


class TestBrain:
    """Test brain CRUD endpoints."""

    @pytest.fixture
    def brain_id(self, client):
        """Create a brain and return ID."""
        submission = {
            "answers": [
                {"question_id": i, "answer_index": i % 4}
                for i in range(1, 9)
            ]
        }
        response = client.post("/api/quiz/submit", json=submission)
        return response.json()["brain_id"]

    def test_get_brain(self, client, brain_id):
        """Get brain by ID."""
        response = client.get(f"/api/brain/{brain_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["brain_id"] == brain_id

    def test_get_brain_not_found(self, client):
        """Get nonexistent brain fails."""
        response = client.get("/api/brain/BRAIN-nonexistent")
        assert response.status_code == 404

    def test_get_brain_stats(self, client, brain_id):
        """Get brain stats."""
        response = client.get(f"/api/brain/{brain_id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "density" in data
        assert "avg_connections" in data

    def test_update_brain(self, client, brain_id):
        """Update brain properties."""
        response = client.put(f"/api/brain/{brain_id}?public=true")
        assert response.status_code == 200

    def test_delete_brain(self, client, brain_id):
        """Delete brain."""
        response = client.delete(f"/api/brain/{brain_id}")
        assert response.status_code == 200

        # Verify deleted
        response = client.get(f"/api/brain/{brain_id}")
        assert response.status_code == 404


class TestTwins:
    """Test twin endpoints."""

    @pytest.fixture
    def brain_id(self, client):
        """Create a brain and return ID."""
        submission = {
            "answers": [
                {"question_id": i, "answer_index": 0}
                for i in range(1, 9)
            ]
        }
        response = client.post("/api/quiz/submit", json=submission)
        return response.json()["brain_id"]

    def test_list_twins(self, client):
        """List available twins."""
        response = client.get("/api/twins")
        assert response.status_code == 200
        data = response.json()
        assert len(data["twins"]) == 4

    def test_invoke_guardian(self, client, brain_id):
        """Invoke Guardian twin."""
        response = client.post(
            f"/api/brain/{brain_id}/twin/guardian?query=Should I focus on this?"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["twin_type"] == "guardian"

    def test_invoke_scout(self, client, brain_id):
        """Invoke Scout twin."""
        response = client.post(
            f"/api/brain/{brain_id}/twin/scout?query=What opportunities exist?"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["twin_type"] == "scout"

    def test_invoke_synthesizer(self, client, brain_id):
        """Invoke Synthesizer twin."""
        response = client.post(
            f"/api/brain/{brain_id}/twin/synthesizer?query=How do these connect?"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["twin_type"] == "synthesizer"

    def test_invoke_mirror(self, client, brain_id):
        """Invoke Mirror twin."""
        response = client.post(
            f"/api/brain/{brain_id}/twin/mirror?query=What am I missing?"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["twin_type"] == "mirror"

    def test_invoke_invalid_twin(self, client, brain_id):
        """Invalid twin type fails."""
        response = client.post(
            f"/api/brain/{brain_id}/twin/invalid?query=test"
        )
        assert response.status_code == 400


class TestResonance:
    """Test resonance endpoints."""

    @pytest.fixture
    def brain_ids(self, client):
        """Create two brains and return IDs."""
        ids = []
        for i in range(2):
            submission = {
                "answers": [
                    {"question_id": q, "answer_index": (q + i) % 4}
                    for q in range(1, 9)
                ]
            }
            response = client.post("/api/quiz/submit", json=submission)
            ids.append(response.json()["brain_id"])
        return ids

    def test_compare_brains(self, client, brain_ids):
        """Compare two brains."""
        response = client.get(f"/api/brain/{brain_ids[0]}/compare/{brain_ids[1]}")
        assert response.status_code == 200
        data = response.json()
        assert "level" in data
        assert "overlap_score" in data
        assert "collaboration_potential" in data

    def test_resonance_endpoint(self, client, brain_ids):
        """Calculate resonance via POST."""
        response = client.post("/api/resonance", json={
            "brain_id_1": brain_ids[0],
            "brain_id_2": brain_ids[1]
        })
        assert response.status_code == 200


class TestFamous:
    """Test famous brains endpoints."""

    def test_list_famous(self, client):
        """List famous brains."""
        response = client.get("/api/famous")
        assert response.status_code == 200
        data = response.json()
        assert "einstein" in data["famous"]

    def test_get_famous(self, client):
        """Get famous brain."""
        response = client.get("/api/famous/einstein")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Albert Einstein"

    def test_get_famous_not_found(self, client):
        """Unknown famous brain fails."""
        response = client.get("/api/famous/unknown")
        assert response.status_code == 404
