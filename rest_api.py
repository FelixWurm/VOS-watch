from flask  import Flask
from flask_restful import Resource, Api
from flask_cors import CORS

import database


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
        return{"VERSION" : "0.1", "DELAY":str(db_res[0]), "ATA":str(db_res[1])}
    
api.add_resource(basic, "/")

if __name__ == "__main__":
    app.run(debug=True)    