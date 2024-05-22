import logging
import psycopg2
import json
import os

import datetime
import traceback


logger = logging.getLogger(__name__)

class sql_interface():
    

    def connect_db(self) -> psycopg2.connect:
        try:
            db = psycopg2.connect(database = "vos_watch", user = self.db_user, password=self.db_pass, host="localhost")
            return db;
        except Exception as EX:
            logger.error(f"Failed to connect to the Database Aboding start! : {EX}")
            exit()
    

    def __init__(self,DEBUG:bool = False):

        self.get_db_details()

        #connect to the DB
        try:
            self.db = psycopg2.connect(database = "vos_watch", user = self.db_user, password=self.db_pass, host="localhost")
        except Exception as EX:
            logger.error(f"Failed to connect to the Database Aboding start! : {EX}")
            exit()

        #db = self.connect_db()

        #if debug is true, always ask if the current database should by dropped

        if DEBUG:
            while True:
                usr_in = input(" should the database be dropped( y or n)")
                if usr_in =="y" or usr_in == "Y":
                    self.initDatabase()
                    break
                elif usr_in == "n" or usr_in == "N":
                    break
                else:
                    print("please decide what to Do!")

        #get a cursor to the DB
        cur = self.db.cursor()
        
        self.create_table_Location(cur)
        self.create_table_directions()
        self.create_table_Lines(cur)
        self.create_table_TransportationAssets(cur)

        #cur.execute("CREATE UNIQUE CLUSTERED INcreate_table_LocationDEX INDEX ON TABLE (col1,col2)")

        cur.close()
        self.db.commit()

        logger.info("Crate all SQL Tables ")

        
    def initDatabase(self):
        #close connection to DB
        self.db.close()
        
        #open local connection to postgres
        db = psycopg2.connect(user = self.db_user, password=self.db_pass, host="localhost")
        cur = db.cursor()
        db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        #drop Database then create new database
        cur.execute("DROP DATABASE vos_watch")
        cur.execute("CREATE DATABASE vos_watch")
        cur.close()
        db.commit()
        
        #reconnect to the database
        self.db = self.connect_db()
        cur = self.db.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    def get_db_details(self, rec = 0):
        #check if a db_credential.json File exits, if not prompt the user to input his data
        try:
            with open("db_credential.json","rt") as file:
                data = json.load(file)
                self.db_user = data["db_user"]
                self.db_pass = data["db_pass"]

        except (KeyError, json.decoder.JSONDecodeError, FileNotFoundError):
            try:
                os.remove("db_credential.json")
            except FileNotFoundError:
                pass
            except Exception as EX:
                logger.critical(f"unown issue while trying to remove file {EX}")
            self.db_user = input("Please input your Database Username:")
            self.db_pass = input("Please input the Database Password:")
            with open("db_credential.json","wt") as file:
                json.dump({"db_pass":self.db_pass, "db_user":self.db_user},file)

    

    def create_table_Location(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Locations (
                            ID SERIAL PRIMARY KEY,
                            Name TEXT,
                            hafas_LID TEXT UNIQUE
                        )''')
    
        self.db.commit()
    

    def create_table_TransportationAssets(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS TransportationAssets (
                            ID BIGINT PRIMARY KEY,
                            MeasuredFromLocationID INTEGER REFERENCES Locations(ID),
                                              
                            Information TEXT,
                            Canceled BOOL, 
                            noDelayInoAvailable BOOL,

                            Departure TIMESTAMP(0),
                            RealDeparture TIMESTAMP(0),
                            CreatedAt TIMESTAMP DEFAULT NOW(),
                            LastEdit TIMESTAMP DEFAULT NOW(),

                            Delay TIME GENERATED ALWAYS AS (RealDeparture - Departure) STORED,                       
                            Max_Delay TIME(0) GENERATED ALWAYS AS (
                                CASE 
                                    WHEN (RealDeparture - Departure) > INTERVAL '0' THEN (RealDeparture - Departure)
                                    ELSE NULL
                                END
                            ) STORED,
                       
                            LineID INTEGER,
                       
                            FOREIGN KEY (LineID) REFERENCES Lines(ID)
                            
                        )''')


    def create_table_Lines(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Lines (
                            ID SERIAL PRIMARY KEY,
                            Name TEXT,
                            destinationID INTEGER REFERENCES Locations(ID),
                            direction_ID INTEGER,
                            FOREIGN KEY (direction_ID) REFERENCES directions(ID)                            
                        )''')
    
    def create_table_directions(self):
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Directions(
                        ID SERIAL NOT NULL,
                        information_text TEXT,
                        direction_text TEXT UNIQUE,
                        PRIMARY KEY (ID)
                        )''')
        #insert the default options

        if cursor.rowcount != 0:
            for direction in ['North', 'West', 'South', 'East', 'North-West', 'South-East','North-East','South-West']:
                try:
                    cursor.execute('''INSERT INTO directions (direction_text) VALUES (%s)''', (direction,))
                except psycopg2.errors.UniqueViolation:
                    logger.info("Hot start detected")
                    break

        cursor.close()
        self.db.commit()
    
    

    def create_table_Information(self):
        cur = self.db.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS AdditionalInformationLink(
                        ID REFERENCES TransportationAssets.ID

                    )''')
        
    
    def create_table_Information(self):
        #head for short form, body for detailed information
        cur = self.db.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS AdditionalInformations(
                        ID PRIMARY KEY,
                        head TEXT,
                        body TEXT
                    )''')    

        cur.close()
        self.db.commit()
    
    def get_cursor(self):
        return self.db.cursor()
    

    def add_location(self,StationName:str, StationLID:str=None):
        cur = self.db.cursor()
        try:
            cur.execute("SELECT * FROM Locations WHERE hafas_LID = %s",(StationLID, ))
            res = cur.fetchall()
            if res and res !=[]:
                cur.execute("INSERT INTO Locations (Name, hafas_LID) VALUES (%s,%s)",(StationName,StationLID))
        except psycopg2.errors.UniqueViolation as ER:
            logger.info(f"Station <{StationName}> with StationLTD <{StationLID}> already Exists! {ER}")
        
        cur.close()
        self.db.commit()



    def add_line(self, Name:str,destination:str, hafas_LID):
        #check if a line is there
        cur = self.db.cursor()

        cur.execute("SELECT ID FROM Lines WHERE destinationID = (SELECT ID FROM Locations WHERE hafas_LID=%s) AND Name = %s",(hafas_LID,Name))
        res = cur.fetchall()
        if not res:
            self.add_location(destination,hafas_LID)
            cur.execute("INSERT INTO Lines(Name, destinationID) VALUES (%s, (SELECT ID from locations WHERE hafas_LID = %s))", (Name,hafas_LID))
        
        cur.close()
        self.db.commit()
            

    def add_TransportationAsset(self,lineName:str, ID:int,hafas_dest_LID:str,DestinationName:str,Information:str,canceled:bool,Departure:datetime.datetime,RealDeparture:datetime.datetime,observed_station_name:str, observed_station_hafas_LID):
        cur = self.db.cursor()
        try:
            cur.execute("SELECT ID FROM TransportationAssets WHERE ID=%s",(ID, ))
            existing_asset = cur.fetchone()
            if existing_asset:
                cur.execute("UPDATE TransportationAssets SET Canceled=%s,RealDeparture=%s, LastEdit=NOW() WHERE ID=%s",(canceled,RealDeparture,existing_asset[0]))
            else:
                #check if line is there, if not add it to the code
                self.add_line(lineName, DestinationName,hafas_dest_LID)
                self.add_location(observed_station_name, observed_station_hafas_LID)
                cur.execute("INSERT INTO TransportationAssets(ID,Information,Canceled,Departure,RealDeparture,LineID,MeasuredFromLocationID) VALUES (%s,%s,%s,%s,%s,(SELECT ID from Lines WHERE (Name=%s AND destinationID=(SELECT ID FROM Locations WHERE hafas_LID = %s))), (SELECT ID FROM Locations WHERE hafas_LID = %s))",(ID,Information,canceled,Departure,RealDeparture,lineName,hafas_dest_LID, observed_station_hafas_LID))

        except Exception as EX:
            logger.error("Could not add TransportationAsset to Database!")
            logger.error(f"{traceback.format_exc()}   :   {EX}")
            print(EX)
            print(ID)
            
        cur.close()
        self.db.commit()
        return(ID)

    def get_time(self,ID:str):
        cur = self.db.cursor()
        cur.execute("SELECT Departure, RealDeparture FROM TransportationAssets WHERE ID = %s", (ID, ))
        res = cur.fetchone()
        cur.close()
        return(res)
    
    def get_average(self, ToLookBack:int=15, ToLookFuture = 5) -> tuple[datetime.timedelta,int,int,int,int]:
        with self.db.cursor() as cur:
            cur.execute("SELECT AVG(Delay),COUNT(*), COUNT(*) FILTER(WHERE Delay <= INTERVAL '3 minutes'), COUNT(*) FILTER(WHERE Delay > INTERVAL '3 minutes' AND Delay <= INTERVAL '8 minutes'), COUNT(*) FILTER(WHERE Delay > INTERVAL '8 minutes') FROM Transportationassets WHERE Delay IS NOT NULL AND RealDeparture > NOW() - INTERVAL '%s minutes' AND Departure < NOW() + INTERVAL '%s minutes'", (ToLookBack,ToLookFuture ))
            result = cur.fetchall()
            print(result)
            result = result[0]
            if result != [] and result:
                try:
                    return(result[0], result[1],result[2],result[3],result[4])
                    
                except:
                    return None
                
                finally:
                    cur.close()
                    self.db.commit()
                
            
        return None
    
    def get_departure_table(self, ToLookBack:int=15, ToLookFuture = 5):
        pass
        with self.db.cursor() as cur:
            cur.execute('''

SELECT ta.Delay, ta.Departure, l.name
FROM 
    (SELECT Delay, LineID, Departure
     FROM transportationassets 
     WHERE Departure > NOW() - INTERVAL '15 minutes' 
     AND Departure < NOW() + INTERVAL '5 minutes') ta
INNER JOIN lines l ON ta.LineID = l.id;
            ''', (ToLookBack, ToLookFuture))
            result = cur.fetchall()
            self.db.commit()
            return result;  


            

"""
SELECT ta.Delay, ta.Departure, l.name
FROM 
    (SELECT Delay, LineID, Departure
     FROM transportationassets 
     WHERE Departure > NOW() - INTERVAL '15 minutes' 
     AND Departure < NOW() + INTERVAL '5 minutes') ta
INNER JOIN lines l ON ta.LineID = l.id;


ALTER TABLE transportationassets
ADD COLUMN DelayMax TIME(0) GENERATED ALWAYS AS ( RealDeparture - Departure) STORED;


"""