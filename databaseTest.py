

import database

db = database.sql_interface(DEBUG=True)

cur = db.get_cursor()
db.create_table_Location(cur)
db.create_table_lines(cur)
