import pytest
from apiGateway import *
from flask import jsonify
import json
import time


@pytest.fixture(scope='module', autouse=True)
def setup_plc_connection():  # wird nur einmal vor allen Tests aufgerufen
    with app.app_context():
        connect_plcs()  
        time.sleep(50)  # Warte 50 Sekunden, um sicherzustellen, dass die Verbindung abgeschlossen ist
    yield 

def test_connect_plcs():
    assert len(opc_clients) > 0

def test_login_fail():
    data =  {
                "username": "opcUser",
                "password": "testWrongPwd"
            }
    with app.app_context():
        response = app.test_client().post('/user/login', json=data)
        assert response.status_code == 401
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"status": "error", "message": "Invalid credentials"}

def test_login_success():
    data =  {
                "username": "opcUser",
                "password": "opcUser123"
            }
    with app.app_context():
        response = app.test_client().post('/user/login', json=data)
        assert response.status_code == 200
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"message": "Welcome opcUser!", "status": "success", "token": "123456"}