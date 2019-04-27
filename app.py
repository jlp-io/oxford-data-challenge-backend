from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_heroku import Heroku
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
app.config['DEBUG'] = True
CORS(app)
heroku = Heroku(app)
#app.config.from_object('config')
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

@app.route('/')
def something():
    return render_template('index.html')

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
    app.run(debug=True)