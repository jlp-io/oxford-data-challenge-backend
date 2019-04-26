from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import pandas as pd
import model.mockdb_interface as db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
CORS(app)
app.config.from_object('config')
dataset = pd.read_csv('model/diet-compositions-by-commodity-categories-fao-2017.csv', low_memory=False)
keys = dataset.columns.values.tolist()

def create_response(data={}, status=200, message=''):
    response = {
        'success': 200 <= status < 300,
        'code': status,
        'message': message,
        'data': data
    }
    return jsonify(response), status

@app.route('/start')
def start():
    entities_raw = list()
    entities_clean = list()
    for i in range(0,len(dataset['Entity'])):
        entities_raw.append(dataset['Entity'][i])
    entities_clean = list(set(entities_raw))
    data = {
        'countries': entities_clean
    }
    return create_response(data);

@app.route('/getCountryData/<country>')
def get_country_data(country):
    country_data = list()
    for i in range(0,len(dataset['Entity'])):
        if dataset['Entity'][i] == country:
            #ds = dataset.ix[i].to_json()
            #ds = dataset.ix[i]
            ds = list(dataset.ix[i])
            for i in range(0,len(ds)):
                typeVal = type(ds[i]).__name__
                if typeVal == 'int64':
                    ds[i] = ds[i].item()
                if typeVal == 'float64':
                    ds[i] = ds[i].item()
            ds_dict = dict()
            for i in range(0,len(ds)):
                ds_dict.update({keys[i]: ds[i]})
            print(ds)
            country_data.append(ds)
    data = {
    }
    data['keys'] = keys
    data['countryData'] = country_data
    return create_response(data)

@app.route('/getUniversityEarnings', methods=['GET'])
def get_university_list():
    df = pd.DataFrame(data_set, columns = ['providerName'])
    data = {
        'name': str(df)
    }
    return create_response(data)

@app.route('/')
def about():
    return render_template('templates/pages/index.html')

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)

@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

@app.route('/mirror/<name>')
def mirror(name):
    data = {
        'name': name
    }
    return create_response(data)

@app.route('/users', methods = ['GET'])
def users():
    if ('team' in request.args):
        team = request.args.get('team')
        data = db.get('users')
        ret = []
        for item in data:
            if (item['team'] == team):
                ret.append(item)
        return create_response(ret)
    else:
        data = db.get('users')
        return create_response(data)

@app.route('/users/<userID>', methods = ['GET'])
def usersID(userID):
    data = db.get('users')
    if (int(userID) > len(data) or int(userID) <= 0):
        return create_response({}, 404, 'No such user exists!')
    else:
        user = data[int(userID)-1]
        return create_response(user)

@app.route('/users', methods = ['POST'])
def createUser():
    if all(k in request.get_json() for k in ('team', 'name', 'age')):
        newUser = request.get_json()
        print(newUser)
        createdUser = db.create('users', newUser)
        return create_response(createdUser, 201, 'User created successfully')
    else:
        return create_response({}, 422, 'User couldn\'t be created!')

@app.route('/users/<userID>', methods = ['PUT'])
def updateUser(userID):
    request_json = request.get_json()
    data = {}
    try:
        data['name'] = request_json['name']
    except:
        pass
    try:
        data['age'] = request_json['age']
    except:
        pass
    try:
        data['team'] = request_json['team']
    except:
        pass
    updatedUser = db.updateById('users', int(userID), data)
    if (updatedUser is None):
        return create_response({}, 404, 'No such user!')
    else:
        return create_response(updatedUser)

@app.route('/users/<userID>', methods = ['DELETE'])
def deleteUser(userID):
    if (db.getById('users',int(userID)) is None):
        return create_response({}, 404, 'Couldn\'t delete!')
    else:
        db.deleteById('users', int(userID))
        return create_response({}, 200, 'Delete successful!')

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

if __name__ == '__main__':
    app.run()