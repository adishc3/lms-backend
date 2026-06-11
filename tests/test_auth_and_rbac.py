from app.db.session import SessionLocal
from app.models.user import User, Role


def register(client, email, password, full_name=None, role=None):
    payload = {"email": email, "password": password}
    if full_name:
        payload["full_name"] = full_name
    if role:
        payload["role"] = role
    return client.post("/auth/register", json=payload)


def login(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_register_with_role_selection(client):
    response = register(client, "instructor_new@example.com", "strongpass", role="instructor")
    assert response.status_code == 200
    assert response.json()["role"] == "instructor"

    response = register(client, "student_new@example.com", "strongpass", role="student")
    assert response.status_code == 200
    assert response.json()["role"] == "student"


def test_register_login_and_role_protection(client):
    response = register(client, "student@example.com", "strongpass")
    assert response.status_code == 200
    assert response.json()["email"] == "student@example.com"

    auth = login(client, "student@example.com", "strongpass")
    assert auth.status_code == 200
    token = auth.json()["access_token"]
    assert token

    protected = client.post(
        "/courses/",
        json={"title": "Unauthorized course", "description": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected.status_code == 403

    response = register(client, "instructor@example.com", "strongpass")
    assert response.status_code == 200
    with SessionLocal() as db:
        instructor = db.query(User).filter(User.email == "instructor@example.com").first()
        instructor.role = Role.instructor
        db.commit()
    instructor_auth = login(client, "instructor@example.com", "strongpass")
    instructor_token = instructor_auth.json()["access_token"]

    course_response = client.post(
        "/courses/",
        json={"title": "Instructor course", "description": "Instructor only"},
        headers={"Authorization": f"Bearer {instructor_token}"},
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]
    assert course_id

    response = register(client, "admin@example.com", "strongpass")
    assert response.status_code == 200
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        admin.role = Role.admin
        db.commit()

    admin_auth = login(client, "admin@example.com", "strongpass")
    admin_token = admin_auth.json()["access_token"]
    admin_users = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_users.status_code == 200
    assert any(u["email"] == "student@example.com" for u in admin_users.json())


def test_instructor_cannot_enroll_or_access_other_instructor_courses(client):
    instructor1 = register(client, "instructor1@example.com", "strongpass", role="instructor")
    assert instructor1.status_code == 200
    token1 = login(client, "instructor1@example.com", "strongpass").json()["access_token"]

    course1 = client.post(
        "/courses/",
        json={"title": "Instructor 1 Course", "description": "Course"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert course1.status_code == 201
    course1_id = course1.json()["id"]

    lesson1 = client.post(
        f"/courses/{course1_id}/lessons",
        json={"title": "Lesson 1", "content": "Content"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert lesson1.status_code == 201
    lesson1_id = lesson1.json()["id"]

    instructor2 = register(client, "instructor2@example.com", "strongpass", role="instructor")
    assert instructor2.status_code == 200
    token2 = login(client, "instructor2@example.com", "strongpass").json()["access_token"]

    enroll_result = client.post(
        f"/courses/{course1_id}/enroll",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert enroll_result.status_code == 403

    lessons_result = client.get(
        f"/courses/{course1_id}/lessons",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert lessons_result.status_code == 403

    lesson_result = client.get(
        f"/courses/{course1_id}/lessons/{lesson1_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert lesson_result.status_code == 403


def test_student_my_enrolled_courses(client):
    student = register(client, "student_my@example.com", "strongpass", role="student")
    assert student.status_code == 200
    token = login(client, "student_my@example.com", "strongpass").json()["access_token"]

    courses = client.get(
        "/courses/my/courses",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert courses.status_code == 200
    assert courses.json() == []


def test_course_list_includes_total_lessons(client):
    instructor = register(client, "instructor_total_lessons@example.com", "strongpass", role="instructor")
    assert instructor.status_code == 200
    token = login(client, "instructor_total_lessons@example.com", "strongpass").json()["access_token"]

    course_no_lessons = client.post(
        "/courses/",
        json={"title": "Empty Course", "description": "No lessons yet"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert course_no_lessons.status_code == 201
    course_no_lessons_id = course_no_lessons.json()["id"]

    course_with_lessons = client.post(
        "/courses/",
        json={"title": "Lesson Course", "description": "Has lessons"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert course_with_lessons.status_code == 201
    course_with_lessons_id = course_with_lessons.json()["id"]

    lesson = client.post(
        f"/courses/{course_with_lessons_id}/lessons",
        json={"title": "First Lesson", "content": "Lesson content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert lesson.status_code == 201

    course_list = client.get("/courses/")
    assert course_list.status_code == 200
    payload = course_list.json()

    assert any(c["id"] == course_no_lessons_id and c["total_lessons"] == 0 for c in payload)
    assert any(c["id"] == course_with_lessons_id and c["total_lessons"] == 1 for c in payload)
    assert sum(1 for c in payload if c["total_lessons"] == 0) == 1
