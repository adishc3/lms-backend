def test_admin_logs_and_user_import(client):
    # create admin
    client.post("/auth/register", json={"email": "admin_logs@example.com", "password": "pass"})
    token = client.post("/auth/login", data={"username": "admin_logs@example.com", "password": "pass"}).json()["access_token"]
    
    # set role to admin
    from app.db.session import SessionLocal as SL
    from app.models.user import User, Role
    with SL() as db:
        u = db.query(User).filter(User.email == "admin_logs@example.com").first()
        u.role = Role.admin
        db.commit()
    
    # list users (creates log)
    r = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    
    # list logs
    r = client.get("/admin/logs", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    logs = r.json()
    assert isinstance(logs, list)