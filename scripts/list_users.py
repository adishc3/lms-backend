from app.db.session import SessionLocal
from app.models.user import User
s = SessionLocal()
users = s.query(User).all()
for u in users:
    print(u.id, u.email, u.role, u.hashed_password)
s.close()
