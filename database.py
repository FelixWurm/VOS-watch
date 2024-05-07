import logging
import sqlite3


class sql_interface():
    
    def __init__(self, db_filename:str = "DB",DEBUG:bool = False ):
        self.db = sqlite3.connect(db_filename)

        #get a cursor to the DB
        cur = self.db.cursor()

        #if debug is true, always ask if the current database should by dropped

        if DEBUG:
            while true:
                usr_in = input(" should the database be dropped( y or n)")
                if usr_in =="y" or usr_in == "Y":
                    cur.execute("DROP DATABASE")
                    logger.info("Database was dropped by user request!")
                    break
                elif usr_in == "n" or usr_in == "N":
                    break
                else:
                    print("please decide what to Do!")


        #check if al the tables of the DB are there

        res = cur.execute("IF (EXISTS (SELECT * FROM))")
    
    def create_table_Location(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Location (
                            ID INTEGER PRIMARY KEY,
                            destination_name TEXT,
                            destination_hafas_LID
                        )''')
    

    def create_table_TransportationAssets(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS TransportationAssets (
                            PRIMARY KEY ID INTEGER,

                            OriginalDepartureTime TEXT,

                            DelayInMin FLOAT,
                            MaxDelayMin FLoat,

                            Information TEXT,
                            Canceled BOOL,

                            UTCDeparture TIMESTAMP,
                            UTCRealDeparture TIMESTAMP,

                            FOREIGN KEY (LineID) REFERENCES lines(ID),

                            CreatedAt TIMESTAMP
                        )''')


    def create_table_lines(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Linien (
                            Name TEXT,
                            ID INTEGER PRIMARY KEY,
                            FOREIGN KEY (destinationID) REFERENCES (Location(ID))
                        )''')
