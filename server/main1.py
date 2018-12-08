# -*- coding: utf-8 -*-
from    flask           import Flask, render_template, json, request,redirect,session, abort, jsonify

# This is necessary for the connection to mysql to support special characters
import sys
from re import search
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/Uploads'
app.secret_key = 'whyy would I tell you my secret key?'
app.debug = True


# Secret page!
@app.route('/admin')
def admin():
    user     = str(session.get('user'))

    if (user == 'Resonant Digit' or
        user == 'Roberto'        or
        user == 'Dovile'):

        return render_template('admin.html')

    else:
        return render_template('error.html', error='Unauthorized access', goTo = 
"/")

# ################################################# MAIN  
###########################
@app.route('/')
def main():
    return render_template('index.html')
# ################################################# MAIN  
###########################

# First page, before userhome
@app.route('/home')
def home():

    return render_template('index.html')


# About page
@app.route('/about')
def about():

    return render_template('about.html')



# Start:
# This part is completly ignored by google cloud.
# Just use it for local development.
# Google clound only needs the methods and line 20 to run.
if __name__ == "__main__":

    # app.run(host='0.0.0.0',port=5665)
    app.run()
    # app.run(host='192.168.8.106',port=5665) # MacBook-Pro 

