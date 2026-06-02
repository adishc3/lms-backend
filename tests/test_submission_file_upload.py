def test_submission_file_upload_flow(client):
    # create instructor, course, lesson, student, assignment
    client.post("/auth/register", json={"email": "inst_upload@example.com", "password": "pass"})
    inst_token = client.post("/auth/login", data={"username": "inst_upload@example.com", "password": "pass"}).json()["access_token"]
    from app.db.session import SessionLocal as SL
    from app.models.user import User, Role
    with SL() as db:
        u = db.query(User).filter(User.email == "inst_upload@example.com").first()
        u.role = Role.instructor
        db.commit()

    course = client.post(
        "/courses/",
        json={"title": "Upload Course", "description": "Course"},
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    course_id = course.json()["id"]
    l1 = client.post(f"/courses/{course_id}/lessons", json={"title": "L1", "content": "c"}, headers={"Authorization": f"Bearer {inst_token}"})

    assign = client.post(f"/assignments/courses/{course_id}", json={"title": "A1", "description": "d", "due_date": None, "max_score": 100}, headers={"Authorization": f"Bearer {inst_token}"})
    assignment_id = assign.json()["id"]

    client.post("/auth/register", json={"email": "student_upload@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "student_upload@example.com", "password": "pass"}).json()["access_token"]
    client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {token}"})

    # submit with file
    data = {"content": "Please find my work"}
    files = {"file": ("homework.txt", b"hello world", "text/plain")}
    r = client.post(f"/assignments/{assignment_id}/submit", data=data, files=files, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    j = r.json()
    assert j.get("file_path") is not None
