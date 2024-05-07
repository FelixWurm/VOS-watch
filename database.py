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
        self.create_table_directions(cur)
        self.create_table_lines(cur)
        self.create_table_TransportationAssets(cur)

    
    def create_table_Location(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Location (
                            ID INTEGER PRIMARY KEY,
                            name TEXT,
                            hafas_LID TEXT
                        )''')
    

    def create_table_TransportationAssets(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS TransportationAssets (
                            ID INTEGER PRIMARY KEY,

                            OriginalDepartureTime TEXT,

                            DelayInMin FLOAT,
                            MaxDelayMin FLoat,

                            Information TEXT,
                            Canceled BOOL,

                            UTCDeparture TIMESTAMP,
                            UTCRealDeparture TIMESTAMP,
                            CreatedAt TIMESTAMP,

                            LineID INTEGER,
                            FOREIGN KEY (LineID) REFERENCES lines(ID)

                        )''')


    def create_table_lines(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS lines (
                            ID INTEGER PRIMARY KEY,
                            Name TEXT,
                            destinationID INTEGER,
                            direction_ID INTEGER,
                            FOREIGN KEY (destinationID) REFERENCES Location(ID),
                            FOREIGN KEY (direction_ID) REFERENCES directions(ID)
                        )''')
    def create_table_directions(self,cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS directions(
                        ID INTEGER PRIMARY KEY,
                        information_text TEXT,
                        direction_text TEXT
                        )''')

    def get_cursor(self):
        return self.db.cursor()
    
