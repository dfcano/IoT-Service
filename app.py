from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# this is a great comment!
# create an instance of flask
app = Flask(__name__)
# creating an API object
api = Api(app)
# create database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# sqlalchemy mapper
db = SQLAlchemy(app)
# Add Context
app.app_context().push()


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    date_joined = db.Column(db.Date, default= datetime.utcnow)


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Float)

    def __repr__(self):
        return f"{self.id} - {self.name} - {self.type} - {self.value}"

# For GET request to http://localhost:5000/


class GetSensor(Resource):
    def get(self):
        sensors = Sensor.query.all()
        emp_list = []
        for sen in sensors:
            sen_data = {'id': sen.id, 'name': sen.name, 'type': sen.type, 'value': sen.value}
            emp_list.append(sen_data)
        return {"sensors": emp_list}, 200

# For Post request to http://localhost:5000/add


class AddSensor(Resource):
    def post(self):
        if request.is_json:
            sen = Sensor(name=request.json['name'], type=request.json['type'],
                       value=request.json['value'])
            db.session.add(sen)
            db.session.commit()
            # return a json response
            return make_response(jsonify({'id': sen.id, 'name': sen.name, 'type': sen.type,
                                          'value': sen.value}), 201)
        else:
            return {'error': 'Request must be JSON'}, 400

# For put request to http://localhost:5000/update/?


class UpdateSensor(Resource):
    def put(self, id):
        if request.is_json:
            sen = Sensor.query.get(id)
            if sen is None:
                return {'error': 'not found'}, 404
            else:
                sen.name = request.json['name']
                sen.type = request.json['type']
                sen.value = request.json['value']
                db.session.commit()
                return 'Updated', 200
        else:
            return {'error': 'Request must be JSON'}, 400

# For delete request to http://localhost:5000/delete/?


class DeleteSensor(Resource):
    def delete(self, id):
        sen = Sensor.query.get(id)
        if sen is None:
            return {'error': 'not found'}, 404
        db.session.delete(sen)
        db.session.commit()
        return f'{id} is deleted', 200


class GetHealth(Resource):
    def get(self):
        return {"status": 'UP'}, 200


api.add_resource(GetSensor, '/')
api.add_resource(AddSensor, '/add')
api.add_resource(UpdateSensor, '/update/<int:id>')
api.add_resource(DeleteSensor, '/delete/<int:id>')
api.add_resource(GetHealth, '/health')

if __name__ == '__main__':
    app.run(debug=True)