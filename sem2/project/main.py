from fastapi import FastAPI
from app.api.endpoints import router
from app.db.database import engine
from app.models.user import Base

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(router)