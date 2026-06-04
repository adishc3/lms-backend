import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the backend root is in the python path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.security import get_password_hash
# Note: Ensure your Course and Lesson models are correctly imported here
try:
    from app.models.course import Course
    from app.models.lesson import Lesson
    from app.models.user import User, Role
except ImportError:
    print("Error: Could not find Course, Lesson, or User models. Please ensure Phase 2 models are implemented.")
    sys.exit(1)

# Fix protocol prefix for Neon/SQLAlchemy compatibility as we did in env.py
database_url = str(settings.DATABASE_URL) if settings.DATABASE_URL else ""
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create engine and session
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_dummy_data():
    db = SessionLocal()
    print(f"Connecting to database host: {engine.url.host}")
    
    try:
        # 0. Ensure an instructor exists to own the courses
        instructor = db.query(User).filter(User.email == "instructor@demo.com").first()
        if not instructor:
            print("Creating demo instructor...")
            instructor = User(
                email="instructor@demo.com",
                full_name="Demo Instructor",
                hashed_password=get_password_hash("instructor123"),
                role=Role.instructor,
                is_active=True,
            )
            db.add(instructor)
            db.flush()

        # Define the dataset
        data_payload = [
            {
                "title": "Full-Stack Web Development with FastAPI",
                "description": "Learn to build high-performance APIs and modern frontends.",
                "lessons": [
                    {"title": "Introduction to SQLAlchemy", "content": "Mastering ORMs for database interactions."},
                    {"title": "Neon DB Integration", "content": "Connecting to serverless Postgres effectively."},
                    {"title": "Cloudinary Asset Management", "content": "Handling image and video uploads in the cloud."},
                ]
            },
            {
                "title": "DevOps & Cloud Infrastructure",
                "description": "Master CI/CD pipelines, Docker, and Vercel deployments.",
                "lessons": [
                    {"title": "Docker Containers 101", "content": "Understanding containerization basics."},
                    {"title": "GitHub Actions Workflow", "content": "Automating your deployment pipeline."},
                    {"title": "Monitoring & Logging", "content": "Keeping track of application health."},
                    {"title": "Infrastructure as Code", "content": "Managing cloud resources with scripts."},
                ]
            },
            {
                "title": "Python for Data Science",
                "description": "Dive deep into data analysis using Pandas, NumPy, and Matplotlib.",
                "lessons": [
                    {"title": "NumPy Fundamentals", "content": "High-performance array processing."},
                    {"title": "Data Cleaning with Pandas", "content": "Preparing messy data for analysis."},
                    {"title": "Data Visualization", "content": "Creating impactful charts and graphs."},
                ]
            },
            {
                "title": "Ethical Hacking & Cybersecurity",
                "description": "Learn the basics of network security and penetration testing.",
                "lessons": [
                    {"title": "Network Protocols", "content": "How data moves across the web safely."},
                    {"title": "Web App Vulnerabilities", "content": "Identifying SQL injection and XSS."},
                    {"title": "Cryptography Basics", "content": "The science of secure communication."},
                    {"title": "Incident Response", "content": "What to do when a breach occurs."},
                ]
            },
            {
                "title": "UI/UX Design Essentials",
                "description": "Build beautiful and user-friendly interfaces.",
                "lessons": [
                    {"title": "Design Principles", "content": "Balance, contrast, and typography."},
                    {"title": "Figma Prototyping", "content": "Creating interactive wireframes."},
                    {"title": "User Research Methods", "content": "Understanding your audience's needs."},
                ]
            }
        ]

        for item in data_payload:
            new_course = Course(
                title=item["title"], 
                description=item["description"],
                owner_id=instructor.id
            )
            db.add(new_course)
            db.flush()  # Obtain ID without full commit

            for l_data in item["lessons"]:
                new_lesson = Lesson(title=l_data["title"], content=l_data["content"], course_id=new_course.id)
                db.add(new_lesson)

        db.commit()
        print(f"Successfully added {len(data_payload)} courses and their lessons to Neon DB!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_dummy_data()