"""
*Bus station departure table api grabber for Osnabrück VOS bus services*

This scripts takes an bus station search string and the departure list length as arguements and plots the current departure times for that station
It may also work on other public transport platforms that are using the HAFAS API

author: Eric Lanfer <elanfer@chaostreff-osnabrueck.de>
license: GPLv3.0

Original found on https://gist.github.com/elanfer/dc825a4267a04ed746bfada5f12fcce2
Modified by Felix Wurm in 2024 to expad the functionality of the Script.
"""

import sys
import json
import requests
import prettytable

import sqlite3
import argparse

import logging

from datetime import datetime 
import pytz


logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log', level=logging.INFO)

#Not used right now
parser  = argparse.ArgumentParser(prog = "Osnabrueck Bus-Delay watchdog", description="Program to track the Buslines in the town in Onsabruek, and store them in a DB to make them available thru a website.")
parser.add_argument("-db", "--db-filename")
parser.add_argument("-c", "--count", help="Number of the next departures, leave empty for auto")
parser.add_argument("-a", help="Automatic mode")
parser.add_argument("-s", "--station", help="Name of the departure station")


import re
re_bus_is_canceld = re.compile("[A-z :0-9]*Fällt aus")


class sql_interface():
    def __init__(self, db_filename:str = "DB"):
        self.db = sqlite3.connect(db_filename)

        #get a cursor to the DB
        cur = self.db.cursor()

        #check if al the tables of the DB are there

        res = cur.execute("IF (EXISTS (SELECT * FROM))")


    
def hour_min_to_utc_timestamp(hour, minute, seconds = False, timezone_name:str="Europe/Amsterdam"):
    # Get current UTC time
    # Create a timezone object for the local timezone
    local_timezone = pytz.timezone(timezone_name)

    # Get the current time in the local timezone
    local_time = datetime.now(local_timezone)

    # Create a new datetime object with the provided hour and minute
    if seconds == None:
        target_time = local_time.replace(hour=hour, minute=minute)
    elif seconds == False:
        target_time = local_time.replace(hour=hour, minute=minute,second = 0, microsecond=0)
    else:
        target_time = local_time.replace(hour=hour, minute=minute,second = seconds, microsecond=0)

    # Convert the local time to UTC
    utc_time = target_time.astimezone(pytz.utc)

    # Convert the UTC time to a timestamp
    utc_timestamp = (utc_time - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

    return utc_timestamp



# API Endpoint
url = 'https://fahrplan.vos.info/bin/mgate.exe'

def main():
    # Check program arguments
    if len(sys.argv) == 3:
        ncols = sys.argv[2]
    elif len(sys.argv) == 2:
        ncols = '15'
    else:
        print('USAGE: get_departures.py STATION TABLELENGTH(default: 15)')

    # use search string from arguments to query the api for the correct station identifier
    try:
        station_query = sys.argv[1]
    except:
        print("Program running with default Station Osnabrück-neumarkt!")
        station_query = "Neumarkt Osnabrück"
        ncols = 15


    payload = json.loads('{"id":"zugcwvduies3y4cc","ver":"1.32","lang":"deu","auth":{"type":"AID","aid":"PnYowCQP7Tp1V"},"client":{"id":"SWO","type":"WEB","name":"webapp","l":"vs_swo"},"formatted":false,"svcReqL":[{"req":{"input":{"field":"S","loc":{"name":"Osnabrück '+ station_query +'?","type":"S","dist":1000},"maxLoc":1}},"meth":"LocMatch","id":"1|6|"}]}')
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    station_query_results = json.loads(response.text.encode('utf8'))

    # throw an error if we do not have any stations found
    if len(station_query_results['svcResL'][0]['res']['match']['locL']) != 1:
        print('ERROR: No station was found in Osnabrück for your search string!')
        exit(1)

    station_lid = station_query_results['svcResL'][0]['res']['match']['locL'][0]['lid']
    station_name = station_query_results['svcResL'][0]['res']['match']['locL'][0]['name']

    # Query departure times
    payload = json.loads('{"id":"nsk88vbu226fy6c4","ver":"1.32","lang":"deu","auth":{"type":"AID","aid":"PnYowCQP7Tp1V"},"client":{"id":"SWO","type":"WEB","name":"webapp","l":"vs_swo"},"formatted":false,"svcReqL":[{"req":{"stbLoc":{"name":"Osnabrück Kalkhügel","lid":"'+ station_lid +'"},"jnyFltrL":[{"type":"PROD","mode":"INC","value":1023}],"type":"DEP","sort":"PT","maxJny":'+ str(ncols) +'},"meth":"StationBoard","id":"1|9|"}]}')
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    json_data = json.loads(response.text.encode('utf8'))

    print('Departure times for ' + station_name)

    table = prettytable.PrettyTable()
    table.field_names = ['Line','ID' ,'Destination', 'Original Departure time', 'Delay (in min)', 'Information', 'Canceled', 'UTC Departure', 'UTC Real departure']
    table.align = 'l'
    json_array = []

    # itereate over all departures
    for i, item in enumerate(json_data['svcResL'][0]['res']['jnyL']):
        # prodX is used as the foreign key for the departure and references to the array position in producs (bus lines)
        line = json_data['svcResL'][0]['res']['common']['prodL'][item['prodL'][0]['prodX']]['name']
        
        #vehicle_id =int(''.join(item["jid"].split("|")))
        vehicle_id =item["jid"].split("|")
        if int(vehicle_id[2]) < 10:
            vehicle_id[2] = "0"+vehicle_id[2]
        vehicle_id = int(''.join(vehicle_id))


        destination = item['dirTxt']
        # parse planned departure time
        planned_dep_time_minute = int(item['stbStop']['dTimeS'][2:4])
        planned_dep_time_hour = int(item['stbStop']['dTimeS'][0:2])
        departure = item['stbStop']['dTimeS'][0:2] + ':' + item['stbStop']['dTimeS'][2:4]
        # parse real departure time
        if 'dTimeR' in item['stbStop']:
            real_dep_time_minute = int(item['stbStop']['dTimeR'][2:4])
            real_dep_time_hour = int(item['stbStop']['dTimeR'][0:2])
            # calculate delay
            delay_hours = real_dep_time_hour - planned_dep_time_hour
            delay_minutes =  real_dep_time_minute - planned_dep_time_minute
        else:
            delay_hours = 0
            delay_minutes = 0
        # calculate delay in minutes
        delay = delay_hours*60+delay_minutes

        #calculate original and new time in unix timestamp format
        planed_dep_time = hour_min_to_utc_timestamp(planned_dep_time_hour, planned_dep_time_minute, False)
        real_dep_time   =hour_min_to_utc_timestamp(real_dep_time_hour, real_dep_time_minute, None)


        # check if there are any warnings like the bus has fewer stops or 
        """
        The following code seams to by outdated and no longer working. Fix / new code below (info is now linked from the bus, not the line )
        if 'himIdL' in json_data['svcResL'][0]['res']['common']['prodL'][item['prodL'][0]['prodX']].keys():
            # iterate over all available warnings for the product/line and check if we have a custom text for that
            for msg_id in json_data['svcResL'][0]['res']['common']['prodL'][item['prodL'][0]['prodX']]['himIdL']:
                for message in json_data['svcResL'][0]['res']['common']['remL']:
                    # the warning id is not just an id, it begins with HIM_FREETEXT_ so we have to split it to get the integer value
                    if int(message['hid']) == int(msg_id.split('_')[2]):
                        # print short title, long version is in field text
                        messages_array.append(message['head'])
                        # print('  ' + message['text'])
        """
        
        if item["msgL"] != None:
            bus_info_array = []
            bus_is_canceled_ = False
            for msg in item["msgL"]:
                if msg["type"] == "REM":
                    # Type A semas to indicate tat the following information is about the firm that owns the bus. Because this information is not relevant it is skipped. 
                    info = json_data['svcResL'][0]['res']['common']['remL'][msg['remX']]
                    if info["type"] != "A":
                        bus_info_array.append(info["txtN"])
                        if re_bus_is_canceld.match(info["txtN"]):
                            bus_is_canceled_ = True
                else:
                    print("interesting! type is not REM but {}\n {}", msg["type"],msg)
        
                
        table.add_row([line,vehicle_id, destination, departure, delay, bus_info_array, bus_is_canceled_, planed_dep_time, real_dep_time])
        json_array.append([line,vehicle_id, destination, departure, delay, bus_info_array, planed_dep_time, real_dep_time])


    #calculate next fetch length (minumum is 5, add extra if train is i the past. add 2  remove one. Maximum is 30, however more may be necessary)
    fetch_count_grow_rate = 2
    fetch_count_shrinke_rate = 1
    min_fetch_count = 5
    max_fetch_count = 30
    fetch_lookahead_target_min = 15

    sec_to_last_currently_loaded_departure = 0
    
    #calculate fetch delay (default 15 seconds unless next bus is more that 30 min away, or next bus within 2 min)
    #next bus comes in 6h -> wait 3, then 1.5, then 45min, then 22.5 min, then 11.25 and so on. if its lower then two min check every 15 seconds (adjustable) (however max delay is one hour to detect potential changes...)
    min_interval_sec = 15
    highress_switch_sec = 120
    max_intervall_sec = 60*60
    
    sec_to_next_departure = 0

    sec_to_next_interval = 0

    if sec_to_next_departure <= highress_switch_sec:
        sec_to_next_interval = min_interval_sec
    else:
        sec_to_next_interval = sec_to_next_departure / 2
        if sec_to_next_interval > max_intervall_sec:
            sec_to_next_interval = max_intervall_sec
        
    print(sec_to_next_interval)

    print(table) 

    #save the jason as file
    with open("result.json", "wt") as file:
        file.write(str(json.dumps(json_data)))

    #print(json.dumps(json_array))


if __name__ == "__main__":
    main()