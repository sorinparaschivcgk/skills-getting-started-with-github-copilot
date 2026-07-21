from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == activities["Chess Club"]["schedule"]
    assert data["Science Club"]["participants"] == activities["Science Club"]["participants"]


def test_signup_adds_participant_and_persists_in_follow_up_read(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]

    follow_up_response = client.get("/activities")
    assert email in follow_up_response.json()["Chess Club"]["participants"]


def test_signup_rejects_missing_activity(client):
    response = client.post("/activities/Missing Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_removes_participant_and_persists_in_follow_up_read(client):
    email = activities["Drama Club"]["participants"][0]

    response = client.delete("/activities/Drama Club/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Drama Club"}
    assert email not in activities["Drama Club"]["participants"]

    follow_up_response = client.get("/activities")
    assert email not in follow_up_response.json()["Drama Club"]["participants"]


def test_unregister_rejects_missing_activity(client):
    response = client.delete(
        "/activities/Missing Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_participant_not_signed_up(client):
    response = client.delete(
        "/activities/Drama Club/participants",
        params={"email": "absent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}