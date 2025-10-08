from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import tasks, code, logs, feedback, containers, admin
from backend.database import init_db
from dotenv import load_dotenv
import os

load_dotenv()

API_TITLE = os.getenv('API_TITLE', 'AI Orchestrator')

app = FastAPI(title=API_TITLE)

# CORS for local development / frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('CORS_ORIGINS', '*')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    # initialize sqlite db and tables
    init_db()


# include routers
app.include_router(tasks.router, prefix="", tags=["tasks"])
app.include_router(code.router, prefix="", tags=["code"])
app.include_router(logs.router, prefix="", tags=["logs"])
app.include_router(feedback.router, prefix="", tags=["feedback"])
app.include_router(containers.router, prefix="", tags=["containers"])
app.include_router(admin.router, prefix="", tags=["admin"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=int(os.getenv('PORT', 8000)), reload=True)
