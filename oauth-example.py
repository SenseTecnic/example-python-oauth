# requires the following packages installed.
# Flask, Flask-OAuthlib
# to test locally with out SSL, set environment variable DEBUG=true
 
from flask import Flask, request, url_for, session, jsonify, redirect, Response
import json
from flask_oauthlib.client import OAuth

#TODO: Configure your app secret and key
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
SENSOR_NAME = ''

app = Flask(__name__)

app.secret_key = CONSUMER_SECRET
oauth = OAuth(app)
 
wotkit = oauth.remote_app('wotkit',
    base_url='https://wotkit.sensetecnic.com/api/',
    request_token_url=None,
    access_token_url='https://wotkit.sensetecnic.com/api/oauth/token',
    authorize_url='https://wotkit.sensetecnic.com/api/oauth/authorize',
    consumer_key=CONSUMER_KEY, 
    consumer_secret=CONSUMER_SECRET, 
    request_token_params={'scope': ['all']}, #Request access to all.
    access_token_params={'scope': ['all']} #Request access to all.
)
 
@wotkit.tokengetter
def get_wotkit_token(token=None):
    return session.get('wotkit_token')

@app.route('/oauth-authorized')
@wotkit.authorized_handler
def oauth_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['wotkit_token'] = (resp['access_token'], '')
    return redirect('/')


@app.route('/login')
def login():
    return wotkit.authorize(callback=url_for('oauth_authorized', _external=True))
 
@app.route('/')
def hello():
    if 'wotkit_token' in session:
        users = wotkit.get('v1/sensors/'+SENSOR_NAME)
        return Response(json.dumps(users.data), content_type='application/json')
    return redirect(url_for('login'))
 


if __name__ == "__main__":
    app.run()
