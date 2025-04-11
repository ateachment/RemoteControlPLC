import pytest
from apiGateway import *
from flask import jsonify
import json
import time

## PLCs verbinden ############################################################################

@pytest.fixture(scope='module', autouse=True)
def setup_plc_connection():  # wird nur einmal vor allen Tests aufgerufen
    with app.app_context():
        connect_plcs()  
        time.sleep(40)  # Warte 40 Sekunden, um sicherzustellen, dass die Verbindung abgeschlossen ist
    yield 

def test_connect_plcs():
    assert len(opc_clients) > 0


## Login #####################################################################################

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

## Info/Control ##############################################################################

def test_info_fail():
    with app.app_context():
        response = app.test_client().get('/info/wrongToken')
        assert response.status_code == 403
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"message": "Invalid token","status": "error"}

def test_info_success():
    with app.app_context():
        response = app.test_client().get('/info/' + generateToken())
        assert response.status_code == 200
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"opc_clients": [["172.17.10.19:4840","online"]], "status": "success"}

def test_control_fail():
    data =  {
                "token": "wrongToken",
                "user_opc_clients": [
                    "192.168.178.25:4840",
                    "172.17.16.19:4840"
                ],
                "command": "start"
            }
    with app.app_context():
        response = app.test_client().post('/control', json=data)
        assert response.status_code == 403
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"message": "Invalid token, PLC(s) offline or incorrectly named", "status": "error"}

def test_control_successON():
    data =  {
                "token": "123456",
                "user_opc_clients": [
                    "192.168.178.25:4840",
                    "172.17.10.19:4840"
                ],
                "command": "start"
            }
    with app.app_context():
        response = app.test_client().post('/control', json=data)
        assert response.status_code == 200
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"opc_clients": [["172.17.10.19:4840", { "Motorschütz": True, "Motorschutzschalter": True }]], "status": "success"}

def test_control_successOFF():
    data =  {
                "token": "123456",
                "user_opc_clients": [
                    "192.168.178.25:4840",
                    "172.17.10.19:4840"
                ],
                "command": "stop"
            }
    with app.app_context():
        response = app.test_client().post('/control', json=data)
        assert response.status_code == 200
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"opc_clients": [["172.17.10.19:4840", { "Motorschütz": False, "Motorschutzschalter": True }]], "status": "success"}




## Logout ####################################################################################

def test_logout_fail():
    with app.app_context():
        response = app.test_client().delete('/user/logout/wrongToken')
        assert response.status_code == 403
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"message": "Invalid token","status": "error"}

def test_logout_success():
    with app.app_context():
        response = app.test_client().delete('/user/logout/' + generateToken())
        assert response.status_code == 200
        jsonData = json.loads(response.data.decode('utf-8'))
        assert jsonData == {"message": "Byebye opcUser!","status": "success"}