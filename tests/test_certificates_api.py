def test_certificate_download_and_verify_flow(client):
    # create instructor, course, lessons, student, complete lessons to get certificate
    client.post("/auth/register", json={"email": "inst3@example.com", "password": "pass"})
    inst_token = client.post("/auth/login", data={"username": "inst3@example.com", "password": "pass"}).json()["access_token"]
    from app.db.session import SessionLocal as SL
    from app.models.user import User, Role
    with SL() as db:
        u = db.query(User).filter(User.email == "inst3@example.com").first()
        u.role = Role.instructor
        db.commit()

    course = client.post(
        "/courses/",
        json={"title": "Cert Course 2", "description": "Course"},
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    course_id = course.json()["id"]
    l1 = client.post(f"/courses/{course_id}/lessons", json={"title": "L1", "content": "c"}, headers={"Authorization": f"Bearer {inst_token}"})
    l2 = client.post(f"/courses/{course_id}/lessons", json={"title": "L2", "content": "c"}, headers={"Authorization": f"Bearer {inst_token}"})
    l1_id = l1.json()["id"]
    l2_id = l2.json()["id"]

    client.post("/auth/register", json={"email": "s3@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "s3@example.com", "password": "pass"}).json()["access_token"]
    client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {token}"})

    client.post(f"/courses/{course_id}/lessons/{l1_id}/complete", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/courses/{course_id}/lessons/{l2_id}/complete", headers={"Authorization": f"Bearer {token}"})

    # fetch certificate id from DB
    from app.db.session import SessionLocal
    from app.models.certificate import Certificate
    with SessionLocal() as db:
        cert = db.query(Certificate).filter(Certificate.course_id == course_id).first()
        assert cert is not None
        cert_id = cert.certificate_id

    # verify
    v = client.get(f"/certificates/verify/{cert_id}")
    assert v.status_code == 200
    # download
    d = client.get(f"/certificates/download/{cert_id}")
    assert d.status_code == 200
    assert d.headers["content-type"] == "application/pdf"
