from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_mail import Message, Mail
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
mail = Mail(app)

#placeholder routes

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/index')
def index():
    return render_template('pages/placeholder.home.html')

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


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

#legitimate routes

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
	
@app.route('/commissaryOrder/<order>')
def commissaryOrder(order):
	data = {
        'countries': order
    }
	"""
	msg = Message("Hello",sender="futianpsm@gmail.com",recipients=["jap00031@students.stir.ac.uk"])
	msg.body = order
	msg.html = "<b>testing</b>"
	mail.send(msg)
	"""
	
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

#Error handlers.

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)