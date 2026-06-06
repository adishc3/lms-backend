from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user, require_admin
from app.crud.organization import (
    create_organization,
    get_organization,
    get_organization_by_name,
    list_organizations,
    assign_user_to_organization,
)
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationAssignUser

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[OrganizationRead])
def read_organizations(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    return list_organizations(db)


@router.post("/", response_model=OrganizationRead)
def create_organization_endpoint(
    organization_in: OrganizationCreate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = get_organization_by_name(db, organization_in.name)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Organization already exists")
    return create_organization(db, organization_in)


@router.get("/{organization_id}", response_model=OrganizationRead)
def read_organization(
    organization_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    organization = get_organization(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/{organization_id}/assign-user")
def assign_user(
    organization_id: int,
    assignment: OrganizationAssignUser,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = assign_user_to_organization(db, assignment.user_id, organization_id)
    if not user:
        raise HTTPException(status_code=404, detail="User or organization not found")
    return {"detail": "User assigned to organization", "user_id": user.id, "organization_id": user.organization_id}
