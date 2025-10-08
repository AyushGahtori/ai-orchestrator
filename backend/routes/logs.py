from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.models import ResultUpload, MessageUpload
from backend.utils.auth import require_api_key
from backend.utils.file_manager import save_log_file
import uuid
from fastapi.responses import FileResponse
from pathlib import Path
import os

router = APIRouter()


@router.post("/upload_results")
def upload_results(payload: ResultUpload, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO results (task_id, accuracy, loss, raw_logs, run_time) VALUES (?,?,?,?,?)",
        (payload.task_id, payload.accuracy, payload.loss, payload.raw_logs, payload.run_time),
    )
    run_id = cur.lastrowid
    # save logs if present
    if payload.raw_logs:
        save_log_file(payload.task_id, str(run_id), f"run_{run_id}.log", payload.raw_logs)
    conn.commit()
    conn.close()
    return {"run_id": run_id}


@router.get("/get_results/{task_id}")
def get_results(task_id: int, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM results WHERE task_id=? ORDER BY created_at DESC", (task_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"results": rows}


@router.get("/get_latest_results/{task_id}")
def get_latest_results(task_id: int, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM results WHERE task_id=? ORDER BY created_at DESC LIMIT 1",
        (task_id,),
    )
    r = cur.fetchone()
    conn.close()
    if not r:
        return {"latest": None}
    return {"latest": dict(r)}


@router.post("/upload_message")
def upload_message(payload: MessageUpload, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (task_id, sender, receiver, role, content) VALUES (?,?,?,?,?)",
        (payload.task_id, payload.sender, payload.receiver, payload.role, payload.content),
    )
    conn.commit()
    conn.close()
    return {"posted": True}


@router.get("/get_messages/{task_id}")
def get_messages(task_id: int, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages WHERE task_id=? ORDER BY created_at ASC", (task_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"messages": rows}



@router.get('/get_logs/{task_id}')
def get_logs(task_id: int, authorized: bool = Depends(require_api_key)):
    base = Path(__file__).resolve().parents[2] / 'storage' / 'logs' / str(task_id)
    if not base.exists():
        return {"logs": []}
    results = []
    for f in sorted(base.iterdir()):
        if not f.is_file():
            continue
        stat = f.stat()
        with f.open('r', encoding='utf-8', errors='ignore') as fh:
            preview = ''.join([next(fh) for _ in range(50)]) if stat.st_size>0 else ''
        results.append({"filename": f.name, "modified": stat.st_mtime, "preview": preview})
    return {"logs": results}


@router.get('/download_log/{task_id}/{filename}')
def download_log(task_id: int, filename: str, authorized: bool = Depends(require_api_key)):
    base = Path(__file__).resolve().parents[2] / 'storage' / 'logs' / str(task_id)
    path = base / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail='Log not found')
    return FileResponse(path, media_type='text/plain', filename=path.name)
