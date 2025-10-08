from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.utils.auth import require_api_key
import uuid
import threading
import time

router = APIRouter()


def complete_job_later(container_id: str, delay: int = 10):
    def mark_done():
        conn = get_conn()
        cur = conn.cursor()
        # update status and append logs
        cur.execute("UPDATE containers SET status=?, logs=? WHERE id=?", ("completed", "Finished successfully", container_id))
        conn.commit()
        conn.close()

    timer = threading.Timer(delay, mark_done)
    timer.daemon = True
    timer.start()


@router.post("/spawn_container")
def spawn_container(task_id: int, authorized: bool = Depends(require_api_key)):
    container_id = f"ctr-{uuid.uuid4().hex[:8]}"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO containers (id, task_id, status, logs) VALUES (?,?,?,?)",
        (container_id, task_id, "running", "Starting container..."),
    )
    conn.commit()
    conn.close()
    # simulate a job that completes after 10 seconds
    complete_job_later(container_id, delay=10)
    return {"container_id": container_id, "status": "running", "note": "Simulated container job created"}


@router.get("/container_status/{container_id}")
def container_status(container_id: str, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM containers WHERE id=?", (container_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="Container not found")
    return dict(r)


@router.delete("/container/{container_id}")
def delete_container(container_id: str, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM containers WHERE id=?", (container_id,))
    conn.commit()
    conn.close()
    return {"deleted": True}
