from sqlalchemy.orm import Session
from app.models.event import Event


def get_event(db: Session, event_id: int) -> Event | None:
    return db.query(Event).filter(Event.id == event_id).first()


def list_events(db: Session, course_id: int | None = None) -> list[Event]:
    query = db.query(Event)
    if course_id is not None:
        query = query.filter(Event.course_id == course_id)
    return query.order_by(Event.starts_at.asc()).all()


def create_event(db: Session, course_id: int, event_in) -> Event:
    event = Event(**event_in.model_dump(), course_id=course_id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(db: Session, event: Event, event_in) -> Event:
    for field, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event):
    db.delete(event)
    db.commit()
