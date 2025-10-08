from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pathlib import Path
from backend.database import get_conn
from backend.models import CodeUpload
from backend.utils.auth import require_api_key
from backend.utils.file_manager import save_code_file, list_code_versions
import uuid

router = APIRouter()


@router.post("/upload_code")
async def upload_code(
    task_id: int = Form(...),
    version: str = Form(...),
    agent: str = Form(...),
    file: UploadFile = File(None),
    file_content: str = Form(None),
    authorized: bool = Depends(require_api_key),
):
    # Accept either file upload or raw content
    filename = None
    stored_path = None
    if file:
        content = await file.read()
        filename = file.filename
        stored_path = save_code_file(task_id, version, filename, content.decode("utf-8"))
    elif file_content:
        filename = f"code_{uuid.uuid4().hex[:8]}.py"
        stored_path = save_code_file(task_id, version, filename, file_content)
    else:
        raise HTTPException(status_code=400, detail="No file or content provided")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO code (task_id, version, agent, filename, stored_path) VALUES (?,?,?,?,?)",
        (task_id, version, agent, filename, stored_path),
    )
    conn.commit()
    conn.close()
    return {"stored_path": stored_path}


@router.get("/get_code/{task_id}")
def get_code_versions(task_id: int, authorized: bool = Depends(require_api_key)):
    versions = list_code_versions(task_id)
    return {"versions": versions}


@router.get("/get_code/{task_id}/{version}")
def get_code_file(task_id: int, version: str, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM code WHERE task_id=? AND version=?", (task_id, version))
    rows = cur.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Code version not found")
    items = [dict(r) for r in rows]
    conn.close()
    return {"items": items}


@router.delete("/delete_code/{code_id}")
def delete_code(code_id: int, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM code WHERE id=?", (code_id,))
    conn.commit()
    conn.close()
    return {"deleted": True}


@router.get('/download_code/{task_id}/{version}')
def download_code(task_id: int, version: str, authorized: bool = Depends(require_api_key)):
    # Find the stored_path from DB for the given task_id/version
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT stored_path FROM code WHERE task_id=? AND version=? LIMIT 1", (task_id, version))
    r = cur.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail='Code not found')
    path = Path(r[0])
    if not path.exists():
        raise HTTPException(status_code=404, detail='File missing on disk')
    return FileResponse(path, media_type='text/plain', filename=path.name)
