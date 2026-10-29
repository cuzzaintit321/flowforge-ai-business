import os, tempfile, importlib
from pathlib import Path
from fastapi.testclient import TestClient

def test_demo_workflow():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['DATABASE_PATH']=str(Path(tmp)/'test.db')
        os.environ['ADMIN_PASSWORD']='local_test_password_that_is_long'
        os.environ['AI_MODE']='demo'
        import app.main as m
        importlib.reload(m)
        with TestClient(m.app) as client:
            assert client.get('/').status_code==200
            assert client.get('/studio').status_code==401
            import base64
            token=base64.b64encode(b'admin:local_test_password_that_is_long').decode()
            auth={'Authorization':'Basic '+token}
            assert client.get('/studio',headers=auth).status_code==200
            r=client.post('/run',headers=auth,data={'workflow_id':1,'customer_name':'Test Customer','customer_email':'test@example.com','incoming':'Can you build us a website?'},follow_redirects=False)
            assert r.status_code==303
            assert 'Thanks for reaching out' in client.get('/studio',headers=auth).text
            assert client.get('/health').json()['status']=='ok'
