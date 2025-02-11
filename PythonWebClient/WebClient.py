# Source:   https://johanneskinzig.de 15.10.2020
# modified: W. Eick 27.10.2020

import requests
from bs4 import BeautifulSoup
import json
import settings  # login data

# Daten anfordern
def requestData():
    S7PLC.login(settings.WEB_USERNAME, settings.PASSWORD)
    Motorschütz, Motorschutzschalter = S7PLC.getData()
    print("Motorschütz=" + str(Motorschütz), "Motorschutzschalter=" + str(Motorschutzschalter))
    S7PLC.logout()

# Daten senden, um den Motor zu schalten
def sendData(start, stop):
    S7PLC.login(settings.WEB_USERNAME, settings.PASSWORD)
    S7PLC.postData(start,stop)
    Motorschütz, Motorschutzschalter = S7PLC.getData()
    print("Motorschütz=" + str(Motorschütz), "Motorschutzschalter=" + str(Motorschutzschalter))
    S7PLC.logout()

class S7ApiClient():
    def __init__(self, host, uri_api, path_to_certfile):
        # S7ApiClient initialisieren
        self.url_post_login = 'https://' + str(host) + '/FormLogin'
        self.url_post_logout = self.url_post_login + '?LOGOUT'
        self.url_api = str(uri_api)
        self.s7certfile = str(path_to_certfile)
        self.auth_cookie = None
        self.s7auth_cookie = None
	# http header initialisieren, sonst weist die S7 die Anfrage ab
        self.http_headers = {
            'Host': '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': '',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '45',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
            }
        self.http_headers['Host'] = str(host)
        self.http_headers['Referer'] = 'https://' + str(host) + '/Portal/Portal.mwsl'

    # einloggen vor der Anforderung
    def login(self, username, password):
        print("Logging in ...")
        session = requests.Session()
        payload_login = {'Login': username, 'Password': password, 'Redirection': ''}
        response = session.post(self.url_post_login, data=payload_login, headers=self.http_headers, verify=self.s7certfile)
        print('Status Code: ' + str(response.status_code))
        webpage_html = response.content
        
        # Authentication cookie aus der Antwort extrahieren (in payload anstatt in http header)
        webpage_soup = BeautifulSoup(webpage_html,features="lxml")
        auth_cookie_part = webpage_soup.find('input', attrs={'name': 'Cookie'})
        auth_cookie_part = str(auth_cookie_part)
        try:
            self.auth_cookie = auth_cookie_part.split('"')[5]
            print("Authentication cookie: ", self.auth_cookie)
            print("Login Done")
        except:
            print("Login failed!")
        
        # Cookie für Anforderung vorbereiten
        self.s7auth_cookie = dict(siemens_ad_session=self.auth_cookie, coming_from_login='true')

    # nach der Anforderung ausloggen
    def logout(self):
        payload_logout = {'Cookie': self.auth_cookie, 'Redirection': ''}
        session = requests.Session()
        logout = session.post(self.url_post_logout, cookies=self.s7auth_cookie, headers=self.http_headers, data=payload_logout, verify=self.s7certfile)
        print('Status Code: ' + str(logout.status_code))
        print('Logout Done')

    # Anforderung der Daten 
    def getData(self):
        session = requests.Session()
        payload = session.get(self.url_api, cookies=self.s7auth_cookie, verify=self.s7certfile)
        content_json = json.loads(payload.text)
        print("Empfangen: " + str(content_json))
        return content_json['Motorschütz'], content_json['Motorschutzschalter']

    # Daten senden
    def postData(self, start, stop):
        session = requests.Session()
        payload = {'"Datenbaustein_Motorschaltung".WebStart': str(start).lower(), '"Datenbaustein_Motorschaltung".WebStop': str(stop).lower()}
        action = session.post(self.url_api, data=payload, cookies=self.s7auth_cookie, verify=self.s7certfile)
        print("Status Code: " + str(action.status_code))


S7PLC = S7ApiClient(settings.PLC_IP, settings.PLC_API_URI, settings.CERT_PATH)
