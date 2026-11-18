import json

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SUBMISSIONS_FILE": str(tmp_path / "submissions.json"),
    })
    return app.test_client()


def valid_form():
    return {
        "name": "Ali",
        "registration_number": "FA24-BCS-001",
        "assignment_title": "DevOps Lab",
        "submission_url": "https://github.com/example/assignment",
    }


def test_complete_details_and_valid_url_are_saved_and_displayed(client):
    response = client.post("/submit", data=valid_form(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Assignment submitted successfully." in response.data
    assert b"DevOps Lab" in response.data
    assert b"FA24-BCS-001" in response.data


def test_missing_registration_number_is_rejected(client):
    data = valid_form()
    data["registration_number"] = ""
    response = client.post("/submit", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"All fields are required." in response.data
    assert b"DevOps Lab" not in response.data


def test_invalid_submission_url_is_rejected_and_not_saved(client):
    data = valid_form()
    data["submission_url"] = "not-a-valid-url"
    response = client.post("/submit", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please enter a valid HTTP or HTTPS submission URL." in response.data
    assert b"DevOps Lab" not in response.data
