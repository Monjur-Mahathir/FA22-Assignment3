from flask import Flask, jsonify, request
import requests, json
import numpy as np
from datetime import date, datetime
from datetime import timedelta
from pymongo import MongoClient



user_auth = {'Authorization':'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhSRFQiLCJzdWIiOiJCNEYzNVEiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBycHJvIHJudXQgcnNsZSByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNjkzNDg4MDQxLCJpYXQiOjE2NjE5NTIwNDF9.uk4UyLwyQeLjnoE6jxKPNCxfkzs0mFTq_09cfuyV74U'}

app = Flask(__name__)
client = MongoClient("mongodb+srv://mahathir:Utsho1Ratri2!@cluster0.8dz3hgk.mongodb.net/?retryWrites=true&w=majority")
db = client["FA22Comp590"]

@app.route("/myjoke", methods=["GET"])
def mymethod():
    joke = "Why did everyone cross the road? Ha! ha, ha!"
    ret = {'category' : 'very funny', 'value' : joke}
    return jsonify(ret)

@app.route("/heartrate/last", methods=["GET"])
def last_heartrate():
    fitbit_web_api_request_url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1sec.json"
    resp = requests.get(fitbit_web_api_request_url, headers=user_auth).json()
    current_time = datetime.now()
    fitbit_last_time = resp['activities-heart'][0]['dateTime'] + ' ' +resp['activities-heart-intraday']['dataset'][-1]['time']
    offset = str(current_time -  datetime.strptime(fitbit_last_time, '%Y-%m-%d %H:%M:%S'))
    print(offset)
    splitted_str = offset.split(':')
    offset_str = splitted_str[0] + ' hours, ' + splitted_str[1] + ' minutes and ' + splitted_str[2] + ' seconds'
    ret = {'heart-rate' : resp['activities-heart-intraday']['dataset'][-1]['value'], 'time-offset': offset_str}
    return jsonify(ret)

@app.route("/steps/last", methods=["GET"])
def last_step():
    fitbit_web_api_request_url = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json"
    resp = requests.get(fitbit_web_api_request_url, headers=user_auth).json()
    print(resp)
    fitbit_web_api_request_url_1 = "https://api.fitbit.com/1/user/-/activities/distance/date/today/1d.json"
    dis_resp = requests.get(fitbit_web_api_request_url_1, headers=user_auth).json()
    print(dis_resp)
    current_time = datetime.now()
    fitbit_last_time = resp['activities-steps'][0]['dateTime'] + ' ' +resp['activities-steps-intraday']['dataset'][-1]['time']
    offset = str(current_time -  datetime.strptime(fitbit_last_time, '%Y-%m-%d %H:%M:%S'))
    splitted_str = offset.split(':')
    offset_str = splitted_str[0] + ' hours, ' + splitted_str[1] + ' minutes and ' + splitted_str[2] + ' seconds'
    ret = {'step-count' : resp['activities-steps'][0]['value'], 'distance':dis_resp['activities-distance'][0]['value'] ,'time-offset': offset_str}
    return jsonify(ret)

@app.route("/sleep/<date>", methods=["GET"])
def sleep_log(date):
    fitbit_web_api_request_url = "https://api.fitbit.com/1.2/user/-/sleep/date/" + str(date) + ".json"
    resp = requests.get(fitbit_web_api_request_url, headers=user_auth).json()
    ret = {'deep': resp['summary']['stages']['deep'], 'light': resp['summary']['stages']['light'], 'rem': resp['summary']['stages']['rem'], 'wake': resp['summary']['stages']['wake']}
    return jsonify(ret)

@app.route("/activity/<date>", methods=["GET"])
def get_activity(date):
    fitbit_web_api_request_url = "https://api.fitbit.com/1/user/-/activities/minutesSedentary/date/" + str(date) +"/1d.json"
    resp_sedentary = requests.get(fitbit_web_api_request_url, headers=user_auth).json()
    
    fitbit_web_api_request_url = "https://api.fitbit.com/1/user/-/activities/minutesLightlyActive/date/" + str(date) +"/1d.json"
    resp_light_active = requests.get(fitbit_web_api_request_url, headers=user_auth).json()
    
    fitbit_web_api_request_url = "https://api.fitbit.com/1/user/-/activities/minutesFairlyActive/date/" + str(date) +"/1d.json"
    resp_fairly_active = requests.get(fitbit_web_api_request_url, headers=user_auth).json()
        
    fitbit_web_api_request_url = "https://api.fitbit.com/1/user/-/activities/minutesVeryActive/date/" + str(date) +"/1d.json"
    resp_highly_active = requests.get(fitbit_web_api_request_url, headers=user_auth).json()

    ret = {'very-active' : int(resp_highly_active['activities-minutesVeryActive'][0]['value']), 'lightly-active':int(resp_light_active['activities-minutesLightlyActive'][0]['value']) ,'sedentary': int(resp_sedentary['activities-minutesSedentary'][0]['value'])}
    return jsonify(ret)

@app.route("/sensors/env", methods=["GET"])
def get_env_from_sensor():
    rows = db.env.find({})
    row = -1
    firstTime = True
    for x in rows:
        if firstTime:
            firstTime = False
            timestamp = x["timestamp"]
            row = x
        else:
            if x["timestamp"] >= timestamp:
                timestamp = x["timestamp"]
                row = x
    if row == -1:
        ret = {'error': 'No data available'}
        return jsonify(ret)
    ret = {'temp': row['temp'], 'humidity': row['humidity'], 'timestamp': row['timestamp']}
    return jsonify(ret)

@app.route("/sensors/pose", methods=["GET"])
def get_pose_from_sensor():
    rows = db.pose.find({})
    row = -1
    firstTime = True
    for x in rows:
        if firstTime:
            firstTime = False
            timestamp = x["timestamp"]
            row = x
        else:
            if x["timestamp"] >= timestamp:
                timestamp = x["timestamp"]
                row = x
    if row == -1:
        ret = {'error': 'No data available'}
        return jsonify(ret)
    ret = {'presence': row['presence'], 'pose': row['pose'], 'timestamp': row['timestamp']}
    return jsonify(ret)

@app.route("/post/env", methods=['POST'])
def create_row_in_env():
    request_data = request.get_json()
    temp = request_data['temp']
    humidity = request_data['humidity']
    #timestamp = request_data['timestamp']
    timestamp = datetime.now()
    create_row_data = {'temp': str(temp),'humidity':str(humidity),'timestamp':str(timestamp)}
    db.env.insert_one(create_row_data)
    return '''<h1>Data inserted</h1>'''

@app.route("/post/pose", methods=['POST'])
def create_row_in_pose():
    request_data = request.get_json()
    presence = request_data['presence']
    pose = request_data['pose']
    #timestamp = request_data['timestamp']
    timestamp = datetime.now()
    create_row_data = {'presence': str(presence),'pose':str(pose),'timestamp':str(timestamp)}
    db.pose.insert_one(create_row_data)
    return '''<h1>Data inserted</h1>'''
    
    
if __name__ == '__main__':
    app.run(debug=True)
