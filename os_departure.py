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
import prettytable

import argparse

import logging

from datetime import datetime 
import time
import pytz

import hafas_query
import database

import json
import traceback

import os


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logging.critical("PROGRAM STARTED!")

#Not used right now
parser  = argparse.ArgumentParser(prog = "Osnabrueck Bus-Delay watchdog", description="Program to track the BusLines in the town in Onsabruek, and store them in a DB to make them available thru a website.")
parser.add_argument("-db", "--db-filename")
parser.add_argument("-c", "--count", help="Number of the next departures, leave empty for auto")
parser.add_argument("-a", help="Automatic mode")
parser.add_argument("-s", "--station", help="Name of the departure station")


import re
re_bus_is_canceld = re.compile("[A-z :0-9]*Fällt aus")

#DEBUG
DEBUG = True

    
def hour_min_to_utc_timestamp(hour, minute, seconds = False, timezone_name:str="Europe/Amsterdam"):
    # Get current UTC time
    # Create a timezone object for the local timezone
    local_timezone = pytz.timezone(timezone_name)

    # Get the current time in the local timezone
    local_time = datetime.now(local_timezone)

    # Create a new datetime object with the provided hour and minute
    if seconds == None:
        target_time = local_time.replace(hour=hour, minute=minute,microsecond=0)
    elif seconds == False:
        target_time = local_time.replace(hour=hour, minute=minute,second = 0, microsecond=0)
    else:
        target_time = local_time.replace(hour=hour, minute=minute,second = seconds, microsecond=0)

    # Convert the local time to UTC
    utc_time = target_time.astimezone(pytz.utc)

    # Convert the UTC time to a timestamp
    utc_timestamp = (utc_time - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

    return utc_timestamp


def hour_min_to_localTimezone_timestamp(hour, minute, seconds = False):

    # Create a timezone object for the local timezone
    #local_timezone = pytz.timezone(timezone_name:str="Europe/Amsterdam")

    # Get the current time in the local timezone
    Timestamp = datetime.now()

    # Create a new datetime object with the provided hour and minute
    if seconds == None:
        Timestamp = Timestamp.replace(hour=hour, minute=minute,microsecond=0)
    elif seconds == False:
        Timestamp = Timestamp.replace(hour=hour, minute=minute,second = 0, microsecond=0)
    else:
        Timestamp = Timestamp.replace(hour=hour, minute=minute,second = seconds, microsecond=0)

    return Timestamp



def analyse_data(json_data, db:database.sql_interface, observed_location:str, observed_Location_LID:str):
    print('Departure times for ' + station_name)

    table = prettytable.PrettyTable()
    table.field_names = ['Line' ,'Destination', 'Original Departure time', 'Delay (in min)', 'Information', 'Canceled',"Delay Information"]
    table.align = 'l'

    first_ID_Edit = None
    last_ID_Edit = None


    # iterate over all departures
    for i, item in enumerate(json_data['svcResL'][0]['res']['jnyL']):
        # prodX is used as the foreign key for the departure and references to the array position in producs (bus Lines)
        line = json_data['svcResL'][0]['res']['common']['prodL'][item['prodL'][0]['prodX']]['name']
        
        #vehicle_id =int(''.join(item["jid"].split("|")))
        vehicle_id =item["jid"].split("|")
        if int(vehicle_id[2]) < 10:
            vehicle_id[2] = "0"+vehicle_id[2]
        vehicle_id = int(''.join(vehicle_id))


        destination = item['dirTxt']
        destination_LID = json_data['svcResL'][0]['res']['common']["locL"][item["prodL"][0]["tLocX"]]["lid"]
        destination_pCLs = json_data['svcResL'][0]['res']['common']["locL"][item["prodL"][0]["tLocX"]]["pCls"]  #Code to represents what typ of transportation can drive from a station
        try:
            line_PID = json_data['svcResL'][0]['res']['common']['prodL'][item['prodL'][0]['prodX']]["pid"]
            line_ID = json_data['svcResL'][0]['res']['common']['prodL'][item['prodL'][0]['prodX']]["prodCtx"]["lineId"]
        except:
            pass

        # parse planned departure time
        planned_dep_time_minute = int(item['stbStop']['dTimeS'][2:4])
        planned_dep_time_hour = int(item['stbStop']['dTimeS'][0:2])
        departure = item['stbStop']['dTimeS'][0:2] + ':' + item['stbStop']['dTimeS'][2:4]

        planed_dep_time = hour_min_to_localTimezone_timestamp(planned_dep_time_hour, planned_dep_time_minute, False)

        # parse real departure time
        if 'dTimeR' in item['stbStop']:
            real_dep_time_minute = int(item['stbStop']['dTimeR'][2:4])
            real_dep_time_hour = int(item['stbStop']['dTimeR'][0:2])
            # calculate delay
            delay_hours = real_dep_time_hour - planned_dep_time_hour
            delay_minutes =  real_dep_time_minute - planned_dep_time_minute

            real_dep_time   =hour_min_to_localTimezone_timestamp(real_dep_time_hour, real_dep_time_minute, None)
            delay_information_available = True
        
        else:
            real_dep_time   = None
            
            delay_hours = 0
            delay_minutes = 0
            delay_information_available = False

        # calculate delay in minutes
        delay = delay_hours*60+delay_minutes

        # check if there are any warnings like the bus has fewer stops 
        #try block because sometime some Lines are missing the msgL tag. there is a possibility that the information is located somewhere else (old system mby?)
        try:
            if item["msgL"] != None:
                bus_info_array = []
                bus_is_canceled_ = False
                for msg in item["msgL"]:
                    if msg["type"] == "REM":
                        # Type A semas to indicate tat the following information is about the firm that owns the bus. Because this information is not relevant it is skipped. 
                        info = json_data['svcResL'][0]['res']['common']['remL'][msg['remX']]
                        if info["type"] != "A":  
                        #if True:                          
                            if re_bus_is_canceld.match(info["txtN"]):
                                bus_is_canceled_ = True
                            else:
                                bus_info_array.append(info["txtN"])

                            
                    elif msg["type"] == "HIM":
                        #type of message that contains extra information that may not by necessary. 
                        info = json_data['svcResL'][0]['res']['common']['himL'][msg['himX']]["head"]
                        detail_info = json_data['svcResL'][0]['res']['common']['himL'][msg['himX']]["text"]

                    else:
                        logger.info("interesting! type is not REM but {}\n {}", msg["type"],msg)
        except KeyError:
            print("no detailed information for this line found!")
            bus_info_array = []
            bus_is_canceled_ = False
            #bus_info_array.append("NO INFORMATION FOUND")
        except Exception as ex:
            print(ex)
            print("unknown error query exit!")
            return
                
        table.add_row([line, destination, departure, delay, bus_info_array, bus_is_canceled_,delay_information_available])

        #Save the data to the Database
        res = db.add_TransportationAsset(line,vehicle_id,destination_LID,destination,str(bus_info_array),bus_is_canceled_,planed_dep_time,real_dep_time,observed_location,observed_Location_LID)

        #save the first an the last ID from the dataset
        if first_ID_Edit == None:
            first_ID_Edit = res
        else:
            last_ID_Edit = res


    print(table)
    return(first_ID_Edit, last_ID_Edit)



def calculateNextParameters(db:database.sql_interface, ID_Tuple,current_fetch_count:int):
    print(ID_Tuple)
    #calculate next fetch length (minumum is 5, add extra if train is i the past. add 2  remove one. Maximum is 30, however more may be necessary)
    fetch_count_grow_rate = 2
    fetch_count_shrinke_rate = 1
    min_fetch_count = 5
    max_fetch_count = 50
    fetch_lookahead_target_sec = 15*60

    next_fetch_count = 0
    #sec_to_last_currently_loaded_departure = float(db.get_time(ID_Tuple[1])[0]) - time.mktime(datetime.now().timetuple())
    sec_to_last_currently_loaded_departure = (db.get_time(ID_Tuple[1])[0] - datetime.now()).total_seconds()
    if sec_to_last_currently_loaded_departure < fetch_lookahead_target_sec:
        #if we are fetching to many departures
        if current_fetch_count < max_fetch_count:
            next_fetch_count = current_fetch_count + fetch_count_grow_rate
        else:
            sec_to_last_currently_loaded_departure = max_fetch_count
    else:
        if current_fetch_count > min_fetch_count:
            next_fetch_count = current_fetch_count - fetch_count_shrinke_rate
        else:
            next_fetch_count = min_fetch_count

    #calculate fetch delay (default 15 seconds unless next bus is more that 30 min away, or next bus within 2 min)
    #next bus comes in 6h -> wait 3, then 1.5, then 45min, then 22.5 min, then 11.25 and so on. if its lower then two min check every 15 seconds (adjustable) (however max delay is one hour to detect potential changes...)
    min_interval_sec = 20
    highress_switch_sec = 180

    max_intervall_sec = 60*60
    
    #sec_to_next_departure =  float(datetime.now("Europe/Amsterdam")) - float(json_array[0]["planed_dep_time"])
    #sec_to_next_departure = float(db.get_time(ID_Tuple[0])[0]) - time.mktime(datetime.now().timetuple())
    sec_to_next_departure = (db.get_time(ID_Tuple[0])[0] - datetime.now()).total_seconds()
    sec_to_next_interval = 0
    
    if sec_to_next_departure <= highress_switch_sec:
        sec_to_next_interval = min_interval_sec
    else:
        sec_to_next_interval = sec_to_next_departure / 2
        if sec_to_next_interval > max_intervall_sec:
            sec_to_next_interval = max_intervall_sec
        
    logger.info(f"next request in {sec_to_next_interval} seconds")
    logger.info(f"next number of fetched departures is {next_fetch_count}")

    return(sec_to_next_interval,next_fetch_count)




if __name__ == "__main__":
    err_count = 0
    while err_count < 3:
        #args = parser.parse_args()
        db = database.sql_interface(DEBUG=False)

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


        station_query_results = hafas_query.hafas_search_station(f"Osnabrück {station_query}")

        # throw an error if we do not have any stations found
        if len(station_query_results['svcResL'][0]['res']['match']['locL']) != 1:
            print('ERROR: No station was found in Osnabrück for your search string!')
            exit(1)

        station_lid = station_query_results['svcResL'][0]['res']['match']['locL'][0]['lid']
        station_name = station_query_results['svcResL'][0]['res']['match']['locL'][0]['name']

        #add station to locations table
        db.add_location(station_name, station_lid)

        print(station_lid)

        # Query departure times

        #set to default start values
        
        next_query_settings = (30,15)
        consecutiveErrorCount = 0
        while True:
            os.system('clear')
            logger.info("Start_query...")
            try:
                json_data = hafas_query.hafas_departure_query(station_lid, next_query_settings[1])
                
                if json_data:
                    ID_tuple = analyse_data(json_data, db,station_name,station_lid)
                    next_query_settings = calculateNextParameters(db,ID_tuple,next_query_settings[1])
                else:
                    logger.error("No response from server")

                time.sleep(next_query_settings[0])
                consecutiveErrorCount = 0

            except KeyboardInterrupt:
                exit("Program exits due to user input!")
            
            except Exception as EX:
                logger.error(f"{traceback.format_exc()}   :   {EX}")
                logger.info("Delay for 10 sec")
                time.sleep(10)
                consecutiveErrorCount += 1
                if consecutiveErrorCount > 5 :
                    logger.error("Failed to restore program shuting down...")
                    err_count +=1
                    break