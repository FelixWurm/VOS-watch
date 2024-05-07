if __name__ == "__main__":
    print("this file can not by used this way!")
    exit(1)


import json
import requests
import logging

# API Endpoint
url = 'https://fahrplan.vos.info/bin/mgate.exe'

def hafas_search_station(station_query:str):
    payload = json.loads('{"id":"zugcwvduies3y4cc","ver":"1.32","lang":"deu","auth":{"type":"AID","aid":"PnYowCQP7Tp1V"},"client":{"id":"SWO","type":"WEB","name":"webapp","l":"vs_swo"},"formatted":false,"svcReqL":[{"req":{"input":{"field":"S","loc":{"name":"'+ station_query +'?","type":"S","dist":1000},"maxLoc":1}},"meth":"LocMatch","id":"1|6|"}]}')
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    return json.loads(response.text.encode('utf8'))




def hafas_departure_query(station_lid:str, ncols):
    payload = json.loads('{"id":"nsk88vbu226fy6c4","ver":"1.32","lang":"deu","auth":{"type":"AID","aid":"PnYowCQP7Tp1V"},"client":{"id":"SWO","type":"WEB","name":"webapp","l":"vs_swo"},"formatted":false,"svcReqL":[{"req":{"stbLoc":{"name":"Osnabrück Kalkhügel","lid":"'+ station_lid +'"},"jnyFltrL":[{"type":"PROD","mode":"INC","value":1023}],"type":"DEP","sort":"PT","maxJny":'+ str(ncols) +'},"meth":"StationBoard","id":"1|9|"}]}')
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    return json.loads(response.text.encode('utf8'))