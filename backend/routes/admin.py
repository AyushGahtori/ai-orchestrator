from fastapi import APIRouter, Depends
from backend.database import get_conn
from backend.utils.auth import require_api_key

router = APIRouter()


@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


@router.get("/stats")
def stats(authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'")
    completed_tasks = cur.fetchone()[0]
    cur.execute("SELECT AVG(accuracy) FROM results")
    avg_accuracy = cur.fetchone()[0]
    cur.execute("SELECT AVG(run_time) FROM results")
    avg_runtime = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM containers WHERE status='running'")
    active_containers = cur.fetchone()[0]
    conn.close()
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "avg_accuracy": avg_accuracy,
        "avg_runtime": avg_runtime,
        "active_containers": active_containers,
    }
