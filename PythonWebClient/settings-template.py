# copy it with your credentials to settings.py

WEB_USERNAME = "yourWebUsernameOfPLC"        
PASSWORD = 'yourPW'                     # be careful

PLC_IP = "IpAdressOfYourPLC"
# url enthält den Applikationsname im TIA Portal:
# Eigenschaften -> Webserver -> Anwenderseiten -> Applikationsname: Motorsteuerung
# .io muss unter Eigenschaften -> Webserver -> Anwenderseiten -> Erweitert ->
# Datei mit dynamischem Inhalt aufgeführt werden: .htm; .html; .io
PLC_API_URI = "https://" + PLC_IP + "/awp//Motorsteuerung//api.io"
CERT_PATH = "MiniWebCA_Cer.crt"

# Proxies bleiben an der WvS-Schule leer, damit Python request nicht 
# versucht, den eingetragenen Windows-System-Proxy zu benutzen.
# Die SPS sind nicht über den Proxy der Stadt erreichbar.
proxies = {
    'http':'',
    'https':''
}