# VOS-watch
 
This is a Program to track the Delay of BusLines in Onsabrück from varios Stations, and display a Summery of the information on a website

## Ideen


## To-DO Liste

### HAFAS Query System

- Tabelle füt zusatzinformationen hinzufügen (auch type A Nachrichten)
- Programmargumente hinzufügen 
- Asset Type in Tabelle speichern oder sogar filtern! (Also bus, Bahn, ....)
- Entfernen der spalte Delay_min in TransportationAssets

Some of the information to the hafas protocol come from this side:
https://github.com/public-transport/transport-apis/blob/v1/data/de/vos-hafas-mgate.json

### API

- API bauen die in einem bestimmten zeitraum mit einer vorgegebenen auflösung eine zeitreihe zurückgibt.
- API bauen die eine art abfahrttafel darstellt.
- Sichern + vorbereiten für Serverumgebung
- Layout / Domain festlegen und beschaffen.

### Website

- Gauge Fixen
- Abfahrttabelle hinzufügen
- Design verbessern (verwenden von T)
- lineChart hinzufügen inklusive einstallmöglichkeiten (letzter tag, Woche, Monat)


## Installation Guidede

1. Dieses Git repo Klonen
2. Virteulles Python Enviroment anlegen
    - python -v .venv
    - alle Pakete installieren (Flask, flask-cors)
3. PostgresSql und TimescaleDB instalieren
    - <https://docs.timescale.com/self-hosted/latest/install/installation-linux/>
    - hab_file einstellungen absichern (alles außer lokal blockieren) [um die Datei zu finden :SHOW hba_file;]

4. Verwaltungs Software installieren und einrichten
    -NPM installieren
    -PM2
5. Website mit NGINX einrichten und Reverse Proxy für api einrichten,

## Trouble Shooting Hints

Datenbank kann nicht mit peer verbunden werden <https://stackoverflow.com/questions/69676009/psql-error-connection-to-server-on-socket-var-run-postgresql-s-pgsql-5432\>