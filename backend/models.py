from pydantic import BaseModel
from typing import Optional


class TaskCreate(BaseModel):
    name: str
    dataset: Optional[str] = None
    description: Optional[str] = None
    creator_agent: Optional[str] = None


class TaskUpdate(BaseModel):
    status: str


class CodeUpload(BaseModel):
    task_id: int
    version: str
    agent: str
    file_content: Optional[str] = None


class ResultUpload(BaseModel):
    task_id: int
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    raw_logs: Optional[str] = None
    run_time: Optional[float] = None


class MessageUpload(BaseModel):
    task_id: int
    sender: str
    receiver: Optional[str] = None
    role: Optional[str] = None
    content: str


class FeedbackUpload(BaseModel):
    task_id: int
    evaluator: str
    feedback: str
