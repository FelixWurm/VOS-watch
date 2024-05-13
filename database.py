import logging
import sqlite3

logger = logging.getLogger(__name__)

class sql_interface():
    
    def __init__(self, db_filename:str = "DB",DEBUG:bool = False ):
        self.db = sqlite3.connect(db_filename)

        #get a cursor to the DB
        cur = self.db.cursor()

        #if debug is true, always ask if the current database should by dropped

        if DEBUG:
            while True:
                usr_in = input(" should the database be dropped( y or n)")
                if usr_in =="y" or usr_in == "Y":
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cur.fetchall()

                    # Drop each table
                    for table in tables:
                        table_name = table[0]
                        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
                        print(f"Dropped table: {table_name}")

                    logger.info("Database was dropped by user request!")
                    break
                elif usr_in == "n" or usr_in == "N":
                    break
                else:
                    print("please decide what to Do!")

        
        self.create_table_Location(cur)
        self.create_table_directions()
        self.create_table_Lines(cur)
        self.create_table_TransportationAssets(cur)

        #cur.execute("CREATE UNIQUE CLUSTERED INDEX INDEX ON TABLE (col1,col2)")

        cur.close()
        self.db.commit()

        logger.info("Crate all SQL Tables ")


    
    def create_table_Location(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Locations (
                            ID INTEGER PRIMARY KEY,
                            Name TEXT,
                            hafas_LID TEXT UNIQUE
                        )''')
    

    def create_table_TransportationAssets(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS TransportationAssets (
                            ID INTEGER PRIMARY KEY,

                            DelayInMin FLOAT,
                            MaxDelayMin FLoat,

                            Information TEXT,
                            Canceled BOOL,

                            UTCDeparture TIMESTAMP,
                            UTCRealDeparture TIMESTAMP,
                            CreatedAt TIMESTAMP,

                            LineID INTEGER,
                            FOREIGN KEY (LineID) REFERENCES Lines(ID)

                        )''')


    def create_table_Lines(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Lines (
                            ID INTEGER PRIMARY KEY,
                            Name TEXT,
                            destinationID INTEGER REFERENCES Location(ID),
                            direction_ID INTEGER,
                            FOREIGN KEY (direction_ID) REFERENCES directions(ID)
                            UNIQUE (Name, destinationID)
                            
                        )''')
    
    def create_table_directions(self):
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Directions(
                        ID INTEGER NOT NULL,
                        information_text TEXT,
                        direction_text TEXT UNIQUE,
                        PRIMARY KEY (ID)
                        )''')
        #insert the default options

        if cursor.rowcount != 0:
            for direction in ['North', 'West', 'South', 'East', 'North-West', 'South-East','North-East','South-West']:
                try:
                    cursor.execute('''INSERT INTO directions (direction_text) VALUES (?)''', (direction,))
                except sqlite3.IntegrityError:
                    logger.info("Hot start detected")
                    break

        cursor.close()
        self.db.commit()
    
    def get_cursor(self):
        return self.db.cursor()
    

    def add_location(self,StationName:str, StationLID:str=None):
        cur = self.db.cursor()
        try:
            cur.execute("INSERT INTO Locations (Name, hafas_LID) VALUES (?,?)",(StationName,StationLID))
        except sqlite3.IntegrityError as ER:
            logger.info(f"Station <{StationName}> with StationLTD <{StationLID}> already Exists! {ER}")
        
        cur.close()
        self.db.commit()



    def add_line(self, Name:str,destination:str, hafas_LID):
        #check if a line is there
        cur = self.db.cursor()

        cur.execute("SELECT ID FROM Lines WHERE destinationID = ((SELECT ID FROM Locations WHERE hafas_LID=?) AND Name = ?)",(hafas_LID,Name))
        res = cur.fetchall()

        if res == []:
            self.add_location(destination,hafas_LID)

            cur.execute("INSERT INTO Lines(Name, destinationID) VALUES (?, (SELECT ID from locations WHERE hafas_LID = ?))", (Name,hafas_LID))
        
        cur.close()
        self.db.commit()
            

    def add_TransportationAsset(self,lineName:str, ID:int,hafas_dest_LID:str,DestinationName:str,Delay_min,Information:str,canceled:bool,utcDeparture:float,utcRealDeparture:float):
        cur = self.db.cursor()
        try:
            cur.execute("SELECT ID FROM TransportationAssets WHERE ID=?",(ID, ))
            existing_asset = cur.fetchone()
            if existing_asset:
                cur.execute("UPDATE TransportationAssets SET DelayInMin=?,Canceled=?,UTCRealDeparture=? WHERE ID=?",(Delay_min, canceled,utcRealDeparture,existing_asset[0]))
            else:
                #check if line is there, if not add it to the code
                self.add_line(lineName, DestinationName,hafas_dest_LID)
                cur.execute("INSERT INTO TransportationAssets(ID,DelayInMin,Information,Canceled,UTCDeparture,UTCRealDeparture,CreatedAt,LineID) VALUES (?,?,?,?,?,?,(unixepoch()),(SELECT ID from Lines WHERE (Name=? AND destinationID=(SELECT ID FROM Locations WHERE hafas_LID = ?))))",(ID,Delay_min,Information,canceled,utcDeparture,utcRealDeparture,lineName,hafas_dest_LID))

        except Exception as EX:
            logger.error("Could not add TransportationAsset to Database!")
            print(EX)
            print(ID)
            
        cur.close()
        self.db.commit()