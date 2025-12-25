"""Tests for the FastAPI activities application."""

import pytest


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_get_activities_has_required_fields(self, client):
        """Test that activities have all required fields."""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]

        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_are_list(self, client):
        """Test that participants field is a list."""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity in data.items():
            assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """Test successful signup of a new participant."""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]

    def test_signup_new_participant_appears_in_list(self, client):
        """Test that newly signed up participant appears in activities list."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Soccer%20Club/signup?email={email}")

        response = client.get("/activities")
        data = response.json()
        assert email in data["Soccer Club"]["participants"]

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up the same participant twice fails."""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_success(self, client):
        """Test successful unregistration of an existing participant."""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregistered participant is removed from activities list."""
        email = "michael@mergington.edu"
        client.post(f"/activities/Chess%20Club/unregister?email={email}")

        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails."""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestActivityConstraints:
    """Tests for activity constraints and limits."""

    def test_activity_respects_max_participants(self, client):
        """Test that activities track max participants correctly."""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity in data.items():
            assert activity["max_participants"] > 0
            participants_count = len(activity["participants"])
            assert participants_count <= activity["max_participants"]

    def test_signup_and_unregister_integration(self, client):
        """Test signing up and then unregistering."""
        email = "testuser@mergington.edu"
        activity = "Art%20Club"

        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

        # Verify signup
        response = client.get("/activities")
        data = response.json()
        assert email in data["Art Club"]["participants"]

        # Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200

        # Verify unregistration
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Art Club"]["participants"]
