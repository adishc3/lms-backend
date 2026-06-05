from app.db.session import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

def seed():
    db = SessionLocal()
    
    # Check if demo users already exist
    instructor = db.query(User).filter(User.email == "instructor@demo.com").first()
    if not instructor:
        instructor = User(
            email="instructor@demo.com",
            full_name="Demo Instructor",
            hashed_password=get_password_hash("instructor123"),
            role=Role.instructor,
            is_active=True,
        )
        db.add(instructor)
    
    student = db.query(User).filter(User.email == "student@demo.com").first()
    if not student:
        student = User(
            email="student@demo.com",
            full_name="Demo Student",
            hashed_password=get_password_hash("student123"),
            role=Role.student,
            is_active=True,
        )
        db.add(student)
    
    db.commit()
    db.close()
    print("Seed data created successfully!")
    print("Users: instructor@demo.com / instructor123, student@demo.com / student123")

if __name__ == "__main__":
    seed()