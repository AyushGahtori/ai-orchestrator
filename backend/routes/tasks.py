from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.models import TaskCreate, TaskUpdate
from backend.utils.auth import require_api_key

router = APIRouter()


@router.post("/upload_task")
def upload_task(payload: TaskCreate, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (name, dataset, description, creator_agent, status) VALUES (?,?,?,?,?)",
        (payload.name, payload.dataset, payload.description, payload.creator_agent, "created"),
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"task_id": task_id}


@router.get("/get_tasks")
def get_tasks(authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"tasks": rows}


@router.get("/get_task/{task_id}")
def get_task(task_id: int, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(r)


@router.put("/update_task/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status=? WHERE id=?", (payload.status, task_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}
