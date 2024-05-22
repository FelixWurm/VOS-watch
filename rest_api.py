from flask  import Flask
from flask_restful import Resource, Api
from flask_cors import CORS

import database

version = "0.1"

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


api = Api(app)

CORS(app)

#connect to database
db = database.sql_interface()

class basic(Resource):

    def get(self):
        db_res = db.get_average()
        #ATA = Analyse transportation asset
        if db_res != None:
            return{"VERSION" : version,"ERR":False ,"DELAY":str(db_res[0]), "ATA":str(db_res[1]), "C0_3":str(db_res[2]), "C3_8":str(db_res[3]),"C8+":str(db_res[4])}
        else:
            return{"VERSION" : version, "ERR" : True}

api.add_resource(basic, "/")

if __name__ == "__main__":
    app.run(debug=True)    