from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.cruds.user import create_user, get_user_by_email, authenticate_user
from app.core.auth import create_access_token, get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.parser import parser
from app.schemas.graph import ParseTaskStatus, GraphMLResult

router = APIRouter()

@router.post("/sign-up/")
def sign_up(email: str, password: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, email, password)
    token = create_access_token(data={"sub": user.email})
    return {"id": user.id, "email": user.email, "token": token}

@router.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"id": user.id, "email": user.email, "access_token": access_token}

@router.get("/users/me/")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

@router.post("/parse_website/", response_model=dict)
def parse_website(url: str, max_depth: int = 3, format: str = "graphml", current_user: User = Depends(get_current_user)):
    if format != "graphml":
        raise HTTPException(status_code=400, detail="Only graphml format is supported")
    task_id = parser.parse_website(url, max_depth)
    return {"task_id": task_id}

@router.get("/parse_status/", response_model=ParseTaskStatus)
def parse_status(task_id: str, current_user: User = Depends(get_current_user)):
    status = parser.get_task_status(task_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")
    return status