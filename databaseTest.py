

import database

db = database.sql_interface(DEBUG=True)

print(db.get_average())


#cur = db.get_cursor()

#db.add_line("test","testination","LID Thing of a String")
#test different line with same station
#db.add_line("test2","testination","LID Thing of a String")


