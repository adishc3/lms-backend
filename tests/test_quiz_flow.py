def register(client, email, password):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_quiz_creation_and_attempt_round_trip(client):
    register(client, "instructor@example.com", "strongpass")
    from app.db.session import SessionLocal
    from app.models.user import User, Role
    with SessionLocal() as db:
        instructor = db.query(User).filter(User.email == "instructor@example.com").first()
        instructor.role = Role.instructor
        db.commit()
    instructor_token = login(client, "instructor@example.com", "strongpass").json()["access_token"]

    course = client.post(
        "/courses/",
        json={"title": "Test Course", "description": "Course for quizzes"},
        headers={"Authorization": f"Bearer {instructor_token}"},
    )
    assert course.status_code == 201
    course_id = course.json()["id"]

    register(client, "student@example.com", "strongpass")
    student_token = login(client, "student@example.com", "strongpass").json()["access_token"]
    enroll = client.post(
        f"/courses/{course_id}/enroll",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert enroll.status_code == 200

    quiz_payload = {
        "title": "Basic Quiz",
        "description": "A simple quiz",
        "course_id": course_id,
        "questions": [
            {
                "text": "What is 2 + 2?",
                "options": [
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": True},
                ],
            }
        ],
    }

    quiz_response = client.post(
        "/quizzes/",
        json=quiz_payload,
        headers={"Authorization": f"Bearer {instructor_token}"},
    )
    assert quiz_response.status_code == 201
    quiz_data = quiz_response.json()
    assert quiz_data["title"] == "Basic Quiz"
    question = quiz_data["questions"][0]
    option_id = question["options"][1]["id"]

    list_response = client.get(
        f"/quizzes/course/{course_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    attempt_response = client.post(
        f"/quizzes/{quiz_data['id']}/attempts",
        json={"answers": [{"question_id": question["id"], "selected_option_id": option_id}]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert attempt_response.status_code == 201
    attempt_data = attempt_response.json()
    assert attempt_data["score"] == 1
    assert attempt_data["total"] == 1
