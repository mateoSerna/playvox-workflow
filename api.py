from flask import Flask
from flask_restful import Api

from database.db import initialize_db
from resources import UsersResource, WorkflowResource

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://playvox:playvox@playvox-database/playvox'
}
api = Api(app)

initialize_db(app)

api.add_resource(UsersResource, '/users/')
api.add_resource(WorkflowResource, '/workflow/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
