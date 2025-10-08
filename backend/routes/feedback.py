from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.models import FeedbackUpload
from backend.utils.auth import require_api_key

router = APIRouter()


@router.post("/upload_feedback")
def upload_feedback(payload: FeedbackUpload, authorized: bool = Depends(require_api_key)):
    # Save feedback as a message from evaluator -> coder
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (task_id, sender, receiver, role, content) VALUES (?,?,?,?,?)",
        (payload.task_id, payload.evaluator, 'coder', 'feedback', payload.feedback),
    )
    conn.commit()
    conn.close()
    return {"posted": True}


@router.get("/get_feedback/{task_id}")
def get_feedback(task_id: int, authorized: bool = Depends(require_api_key)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM messages WHERE task_id=? AND role='feedback' ORDER BY created_at DESC", (task_id,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"feedback": rows}
