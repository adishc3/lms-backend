from app.db.session import SessionLocal


def test_assignment_submit_and_grade_flow(client):
    # register instructor
    client.post("/auth/register", json={"email": "inst2@example.com", "password": "pass"})
    inst_token = client.post("/auth/login", data={"username": "inst2@example.com", "password": "pass"}).json()["access_token"]
    from app.db.session import SessionLocal as SL
    from app.models.user import User, Role
    with SL() as db:
        u = db.query(User).filter(User.email == "inst2@example.com").first()
        u.role = Role.instructor
        db.commit()

    # create course
    course = client.post(
        "/courses/",
        json={"title": "Assign Course", "description": "Course"},
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert course.status_code == 201
    course_id = course.json()["id"]

    # create assignment
    assign = client.post(f"/assignments/courses/{course_id}", json={"title": "A1", "description": "desc"}, headers={"Authorization": f"Bearer {inst_token}"})
    assert assign.status_code == 201
    assignment_id = assign.json()["id"]

    # register student and enroll
    client.post("/auth/register", json={"email": "s2@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "s2@example.com", "password": "pass"}).json()["access_token"]
    client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {token}"})

    # submit assignment
    sub = client.post(f"/assignments/{assignment_id}/submit", json={"content": "my answer"}, headers={"Authorization": f"Bearer {token}"})
    assert sub.status_code == 200
    submission_id = sub.json()["id"]

    # grade as instructor
    graded = client.post(f"/assignments/{assignment_id}/submissions/{submission_id}/grade", params={"grade": 85}, headers={"Authorization": f"Bearer {inst_token}"})
    assert graded.status_code == 200
    assert graded.json()["grade"] == 85

    # export gradebook
    resp = client.get(f"/assignments/courses/{course_id}/gradebook", headers={"Authorization": f"Bearer {inst_token}"})
    assert resp.status_code == 200
    assert "assignment_id" in resp.text
