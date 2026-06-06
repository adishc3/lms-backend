from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.crud.user import get_user


def list_organizations(db: Session):
    return db.query(Organization).all()


def get_organization(db: Session, organization_id: int):
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_organization_by_name(db: Session, name: str):
    return db.query(Organization).filter(Organization.name == name).first()


def create_organization(db: Session, organization_in):
    organization = Organization(name=organization_in.name)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def assign_user_to_organization(db: Session, user_id: int, organization_id: int):
    user = get_user(db, user_id)
    organization = get_organization(db, organization_id)
    if user is None or organization is None:
        return None
    user.organization_id = organization_id
    db.commit()
    db.refresh(user)
    return user
