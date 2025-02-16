import subprocess
import os
import traceback
import sys
import json
import logging
from pathlib import Path
from app import app
from app.forms import HomeForm
from app.modules.sensorModel import *
from app.modules.fieldsModel import *
from flask import render_template, make_response, request, send_from_directory
from flask_jsonpify import jsonify
from flask_cors import cross_origin
from bson.json_util import dumps
from logging.handlers import RotatingFileHandler
from app.modules.trendsModel import *


info_file_handler = RotatingFileHandler('logs/info.log',maxBytes=10240,backupCount=10)
info_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
info_logger = logging.getLogger("app")
info_logger.addHandler(info_file_handler)
info_logger.setLevel(logging.INFO)

error_file_handler = RotatingFileHandler('logs/error.log',maxBytes=10240,backupCount=10)
error_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
error_logger = logging.getLogger("app")
error_logger.addHandler(error_file_handler)
error_logger.setLevel(logging.WARNING)

""" ROUTES START HERE"""
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.png', mimetype="image/vnd.microsoft.icon")

@app.route('/',methods=['GET'])
def home():
    return render_template('fields.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/config')
def config():
    return render_template('config.html')

@app.route('/sensors')
def sensors():
    return render_template('sensors.html')

""" ROUTES END HERE """

""" END POINTS START HERE """

''' Get All sensors '''
@app.route("/getSensors", methods=['GET'])
@cross_origin()
def getSensors():
    sensors = []
    sensorsCollection = SensorsCollection()
    for sensor in sensorsCollection.getSensors():
        print(sensor.toString())
        sensors.append(sensor.toString())
    sensorsCollection.close()
    return make_response(jsonify(sensors), 200,{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET',
        'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With'        
        })

''' Update sensor '''
@app.route("/editSensor", methods=['POST'])
@cross_origin()
def editSensor():
    sensorData = request.get_json()
    saveMsgs = []
    saveMsg = ""

    print(sensorData)

    sensorsCollection = SensorsCollection()
    for sensor in sensorData['sensors']:
        print(sensor)
        if(sensorsCollection.updateSensor(sensor['mac'], sensor['field'])):
            saveMsg = "Change Successful for Sensor at MAC: " + sensor['mac']
        else:
            saveMsg = "No change was made on sensor: " + sensor['mac']

        saveMsgs.append(saveMsg);

    sensorsCollection.close()
    return response(saveMsgs, 200)

    ''' Get All fields '''
@app.route("/getFields", methods=['GET'])
@cross_origin()
def getFields():
    fields = []
    fieldsCollection = FieldsCollection()
    for field in fieldsCollection.getFields():
        trendModel = Trends()
        result = trendModel.filterByField(field.name)
        fields.append(result)
    print(fields)
    fieldsCollection.close()
    return make_response(jsonify(fields), 200,{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET',
        'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With'        
        }) 

@app.route("/getSensorFields", methods=['GET'])
@cross_origin()
def getSensorFields():
    fields = []
    fieldsCollection = FieldsCollection()
    for field in fieldsCollection.getFields():
        print(field.toString())
        fields.append(field.toString())
    fieldsCollection.close()
    return response(fields, 200)


@app.route("/setFields", methods=['POST'])
def setFields():

    fields = FieldsCollection()
    fields.removeAllFields()
    fields.setFields(request.get_json())

    succes = {
        "message" : "Save Sucessful"
    }

    return response(succes, 200)

""" END POINTS END HERE """


""" TEST END POINTS START HERE """

''' Test end point for filter sensor reports by sensor'''
@app.route('/filterBySensor', methods=['GET'])
@cross_origin()
def filterBySensor():
    jsonArray = []
    trendModel = Trends()
    for entry in trendModel.filterBySensor("C4:7C:8D:67:0E:D9"):
        #print(entry)
        jsonArray.append(entry.toString())
    trendModel.close()

    print(make_response(jsonify(jsonArray),200,{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET'
        }))
    return make_response(jsonify(jsonArray),200,{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET',
        'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With'
        })

    ''' Test end point for filter sensor reports by field'''
@app.route('/filterByField', methods=['GET'])
@cross_origin()
def filterByField():
    trendModel = Trends()
    result = trendModel.filterByField("Field 1")
    trendModel.close()
    return make_response(jsonify(result),200,{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET',
        'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With'
        })

    ''' Test end point for slope calculation'''
@app.route('/slope', methods=['GET'])
@cross_origin()
def slope():
    trendModel = Trends()
    slopeValue = trendModel.calculateSlope([1,2,3,4,5], [5,4,6,5,6]) 
    trendModel.close()

    return make_response(jsonify({'slope': slopeValue}),200,{
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET',
        'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With'
        })
""" TEST ENDPOINTS END HERE """


""" ERROR HANDLERS START HERE """

@app.errorhandler(500)
def internal_error(error):
    error_logger.warning("500 Internal Server Error")
    errorObj = {
        'status': 500,
        'error' : traceback.format_exc()
    }
    return response(errorObj,500)


@app.errorhandler(404)
def resource_not_found(error):
    error_logger.warning("404 Error Resource Not Found")
    errorObj = {
        'status': 404,
        'error' : traceback.format_exc()
    }
    return response(errorObj, 404)

@app.errorhandler(405)
def method_not_allowed(error):
    error_logger.warning("405 Error: Method Nnot Allowed")
    errorObj = {
        'status' : 405,
        'error' : traceback.format_exc()
    }
    return response(errorObj, 405)

def response(jsonObject, statusCode):
    responseSettingObj = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods' : 'PUT,GET',
        'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With',
        'Cache-Control': 'no-cache, no-store'
    }
    return make_response(jsonify(jsonObject),statusCode,responseSettingObj)

