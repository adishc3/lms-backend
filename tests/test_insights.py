def test_progress_summary_endpoint(client):
    # create student
    client.post("/auth/register", json={"email": "insights_student@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "insights_student@example.com", "password": "pass"}).json()["access_token"]
    
    r = client.get("/insights/progress-summary", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert "completion_stats" in data
    assert data["completion_stats"]["total_lessons"] >= 0


def test_recommended_courses_endpoint(client):
    # create instructor and course
    client.post("/auth/register", json={"email": "rec_inst@example.com", "password": "pass"})
    inst_token = client.post("/auth/login", data={"username": "rec_inst@example.com", "password": "pass"}).json()["access_token"]
    
    # set role to instructor
    from app.db.session import SessionLocal as SL
    from app.models.user import User, Role
    with SL() as db:
        u = db.query(User).filter(User.email == "rec_inst@example.com").first()
        u.role = Role.instructor
        db.commit()
    
    course = client.post(
        "/courses/",
        json={"title": "Recommended Course", "description": "Test"},
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    
    # create student
    client.post("/auth/register", json={"email": "rec_student@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "rec_student@example.com", "password": "pass"}).json()["access_token"]
    
    r = client.get("/insights/recommended-courses", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "recommendations" in r.json()