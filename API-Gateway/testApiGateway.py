from apiGateway import app
from flask import jsonify
import json

def test_login_fail():
    data =  {
                "username": "opcUser",
                "password": "testWrongPwd"
            }
    response = app.test_client().post('/user/login', json=data)
    assert response.status_code == 401
    response = json.loads(response.data.decode('utf-8'))
    assert response == jsonify({"status": "error", "message": "Invalid credentials"})