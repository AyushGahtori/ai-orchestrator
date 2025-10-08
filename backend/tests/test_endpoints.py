import os
import tempfile
from fastapi.testclient import TestClient
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.app import app

client = TestClient(app)

API_KEY = {'X-API-KEY': os.getenv('DEMO_API_KEY','demo_key')}


def test_upload_task():
    payload = {"name":"test","dataset":"mnist","description":"desc","creator_agent":"generator"}
    r = client.post('/upload_task', json=payload, headers=API_KEY)
    assert r.status_code == 200
    assert 'task_id' in r.json()


def test_upload_results_and_code():
    # create task
    r = client.post('/upload_task', json={"name":"t2"}, headers=API_KEY)
    tid = r.json()['task_id']

    # upload results
    r2 = client.post('/upload_results', json={"task_id": tid, "accuracy":0.5}, headers=API_KEY)
    assert r2.status_code == 200

    # upload code (file_content)
    r3 = client.post('/upload_code', data={'task_id':tid,'version':'v1','agent':'coder','file_content':'print(1)'}, headers=API_KEY)
    assert r3.status_code == 200