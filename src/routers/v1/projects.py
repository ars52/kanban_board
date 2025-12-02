from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from sqlalchemy.orm import Session
from src.core.services.db import get_db
from src.crud.projects import get_all_projects, get_project, create_project, update_project, delete_project
from src.schemas.projects import ProjectCreate, ProjectOut, ProjectUpdate
from src.infrastructure.jaminstance import jam
from src.models.user import User

router_projects = APIRouter(prefix="/projects", tags=["projects"])


@router_projects.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return get_all_projects(db)


@router_projects.get("/{project_id}", response_model=ProjectOut)
def read_project(project_id: int, db: Session = Depends(get_db)):
    pr = get_project(db, project_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Project not found")
    return pr


@router_projects.post("/", response_model=ProjectOut)
def create_project_endpoint(data: ProjectCreate, request: Request, db: Session = Depends(get_db)):
    # Try to infer creator from Authorization Bearer token
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split('Bearer ')[-1] if auth_header else None
    created_by = None
    if token:
        try:
            payload = jam.verify_jwt_token(token)
            if 'user_id' in payload:
                created_by = payload['user_id']
            else:
                email = payload.get('sub')
                if email:
                    u = db.query(User).filter(User.email == email).first()
                    if u:
                        created_by = u.id
        except Exception:
            created_by = None

    # if created_by not found in token, fall back to provided value
    if not created_by:
        try:
            created_by = data.created_by
        except Exception:
            created_by = None

    if not created_by:
        raise HTTPException(status_code=422, detail='body.created_by : Field required')

    # build new ProjectCreate with enforced created_by
    payload = data.model_dump()
    payload['created_by'] = created_by
    new_data = ProjectCreate(**payload)
    return create_project(db, new_data)


@router_projects.put("/{project_id}", response_model=ProjectOut)
def update_project_endpoint(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    pr = update_project(db, project_id, data)
    if not pr:
        raise HTTPException(status_code=404, detail="Project not found")
    return pr


@router_projects.delete("/{project_id}", response_model=ProjectOut)
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    pr = delete_project(db, project_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Project not found")
    return pr
