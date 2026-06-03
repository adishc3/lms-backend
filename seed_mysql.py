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
    
    # Create a set of sample courses (10) each with 4 lessons
    sample_courses = [
        ("Introduction to Python", "Learn Python fundamentals including variables, loops, and functions."),
        ("Web Development Basics", "Build your first web application with HTML, CSS, and JavaScript."),
        ("Data Science Foundations", "Intro to data analysis, pandas, and basic statistics."),
        ("Databases 101", "Relational databases, SQL queries, and schema design."),
        ("APIs with FastAPI", "Build and document REST APIs using FastAPI and Pydantic."),
        ("Machine Learning Intro", "Supervised and unsupervised learning basics."),
        ("DevOps Essentials", "CI/CD, containers, and deployment basics."),
        ("Frontend with React", "Component-based UI development with React and hooks."),
        ("Version Control with Git", "Branching, merging, and collaboration workflows."),
        ("Testing with Pytest", "Write reliable tests and use fixtures and mocks.")
    ]

    lesson_templates = [
        ("Overview", "An overview of the topic and learning objectives."),
        ("Getting Started", "Setup and first steps to get hands-on quickly."),
        ("Core Concepts", "Key concepts and patterns to understand."),
        ("Hands-on Exercise", "Practical exercise to reinforce learning.")
    ]

    courses_created = []
    for title, description in sample_courses:
        course = Course(title=title, description=description, owner_id=instructor.id)
        db.add(course)
        db.flush()
        # create 4 lessons per course
        for ltitle, lcontent in lesson_templates:
            lesson = Lesson(title=ltitle, content=lcontent, course_id=course.id)
            db.add(lesson)
        courses_created.append(course)

    db.commit()
    db.close()
    print("Seed data created successfully!")
    print("Users: instructor@demo.com / instructor123, student@demo.com / student123")

if __name__ == "__main__":
    seed()