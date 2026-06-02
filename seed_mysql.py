import os

def seed():
    os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")
    
    from app.db.session import SessionLocal, engine, Base
    from app.models.user import User, Role
    from app.models.course import Course
    from app.models.lesson import Lesson
    from app.models.quiz import Quiz, Question, Option, QuizAttempt, AttemptAnswer
    from app.models.enrollment import Enrollment
    from app.models.ai_usage import AIUsageLog
    from app.core.security import get_password_hash
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    instructor = User(
        email="instructor@demo.com",
        full_name="Demo Instructor",
        hashed_password=get_password_hash("instructor123"),
        role=Role.instructor,
        is_active=True,
    )
    student = User(
        email="student@demo.com",
        full_name="Demo Student",
        hashed_password=get_password_hash("student123"),
        role=Role.student,
        is_active=True,
    )
    db.add(instructor)
    db.add(student)
    db.flush()
    
    course1 = Course(
        title="Introduction to Python",
        description="Learn Python fundamentals including variables, loops, and functions.",
        owner_id=instructor.id,
    )
    course2 = Course(
        title="Web Development Basics",
        description="Build your first web application with HTML, CSS, and JavaScript.",
        owner_id=instructor.id,
    )
    db.add(course1)
    db.add(course2)
    db.flush()
    
    lesson1 = Lesson(
        title="Variables and Data Types",
        content="Python has several built-in data types: integers, floats, strings, and booleans. Variables store data that can be used throughout your program.",
        course_id=course1.id,
    )
    lesson2 = Lesson(
        title="Control Flow - If Statements",
        content="If statements allow you to execute code conditionally based on boolean expressions. Use elif for additional conditions and else as a catch-all.",
        course_id=course1.id,
    )
    lesson3 = Lesson(
        title="HTML Structure",
        content="HTML documents have a tree structure with head and body sections. Common elements include headings (h1-h6), paragraphs (p), and links (a).",
        course_id=course2.id,
    )
    db.add(lesson1)
    db.add(lesson2)
    db.add(lesson3)
    
    db.commit()
    db.close()
    print("Seed data created successfully!")
    print("Users: instructor@demo.com / instructor123, student@demo.com / student123")

if __name__ == "__main__":
    seed()