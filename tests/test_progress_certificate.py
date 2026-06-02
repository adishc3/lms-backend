from app.db.session import SessionLocal


def test_certificate_issued_on_course_completion(client):
    # Register instructor and create course with two lessons
    client.post("/auth/register", json={"email": "inst@example.com", "password": "pass"})
    inst_token = client.post("/auth/login", data={"username": "inst@example.com", "password": "pass"}).json()["access_token"]
    # promote to instructor
    from app.db.session import SessionLocal as SL
    from app.models.user import User, Role
    with SL() as db:
        user = db.query(User).filter(User.email == "inst@example.com").first()
        user.role = Role.instructor
        db.commit()
    # create course
    course = client.post(
        "/courses/",
        json={"title": "Cert Course", "description": "Course"},
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert course.status_code == 201
    course_id = course.json()["id"]

    # create two lessons
    l1 = client.post(f"/courses/{course_id}/lessons", json={"title": "L1", "content": "c"}, headers={"Authorization": f"Bearer {inst_token}"})
    l2 = client.post(f"/courses/{course_id}/lessons", json={"title": "L2", "content": "c"}, headers={"Authorization": f"Bearer {inst_token}"})
    assert l1.status_code == 201 and l2.status_code == 201
    l1_id = l1.json()["id"]
    l2_id = l2.json()["id"]

    # register student and enroll
    client.post("/auth/register", json={"email": "s1@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "s1@example.com", "password": "pass"}).json()["access_token"]
    enroll = client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {token}"})
    assert enroll.status_code == 200

    # mark first lesson complete
    resp1 = client.post(f"/courses/{course_id}/lessons/{l1_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert resp1.status_code == 200

    # certificate should not exist yet
    from app.models.certificate import Certificate

    with SessionLocal() as db:
        cert = db.query(Certificate).filter(Certificate.course_id == course_id).first()
        assert cert is None

    # mark second lesson complete
    resp2 = client.post(f"/courses/{course_id}/lessons/{l2_id}/complete", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200

    # now certificate should exist
    with SessionLocal() as db:
        cert = db.query(Certificate).filter(Certificate.course_id == course_id).first()
        assert cert is not None
