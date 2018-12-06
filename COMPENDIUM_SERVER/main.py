# -*- coding: utf-8 -*-
from    __future__      import unicode_literals
from    flask           import Flask, render_template, json, request, redirect, session, abort, jsonify
from    werkzeug        import generate_password_hash, check_password_hash
from    io_lib          import io_debug
from    io_lib          import io_mysql
from    io_lib          import parse_class
from    firebase_admin  import messaging, credentials 
import  firebase_admin
import  os
import  re
import  uuid
import  argparse
import  flask
import  logging

# This is necessary for the connection to mysql to support special characters
import sys
from re import search
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/Uploads'
app.secret_key = 'why would I tell you my secret key?'
app.debug = True
# defult initialization for objects.
# currently doing a verbose mode for unittest, will try
# to control these from unittest later.
io_print = io_debug.io_debug(True, None).io_print
database = io_mysql.io_mysql(True, None, True)
database.configure_credentials('root', 'password', 'compendium')

# Setup io_mysql and io_print if we are at cloud.
CLOUD_LOGGING = os.environ.get('ENABLE_CLOUD_LOGGING')

if CLOUD_LOGGING:
    # dont' use io_debug, use directly logging.debug for now.
    # https://cloud.google.com/appengine/docs/standard/python/logs/
    io_print = logging.debug
    database  = io_mysql.io_mysql(True, None, True)
    database.io_print = logging.debug

# ===========  GOOGLE FIREBASE INITIALIZATION OF SDK =============
# =======For Android notifications
# cred = credentials.Certificate('boletinbc.json')
# default_app = firebase_admin.initialize_app(cred)
# To use the Python Admin SDK in the Google App Engine standard environment, 
# you'll need some extra configuration.
# https://google-auth.readthedocs.io/en/latest/user-guide.html#the-app-engine-standard-environment
# https://firebase.google.com/docs/admin/setup

# Secret page!
@app.route('/admin')
def admin():
    global io_print
    user        = str(session.get('user'))

    if (user == 'Resonant Digit' or
        user == 'Roberto'        or
        user == 'Dovile'):
        io_print('Logged as admin')
        return render_template('admin.html')

    else:
        return render_template('error.html', error='Unauthorized access', goTo = "/")

# ################################################# MAIN  ###########################
@app.route('/')
def main():
    return render_template('index.html')
# ################################################# MAIN  ###########################

# First page, before userhome
@app.route('/home')
def home():

    return render_template('index.html')

# SignIn
@app.route('/showSignIn')
def showSignin():
    return render_template('signin.html')

# SignUp
@app.route('/showSignUp')
def showSignUp():
    error = request.args.get('error')
    if str(error) == 'None':
        error = ''
    return render_template('registro.html', error = error)

# The main page, with the user's cases
@app.route('/userHome/<path:path>/',methods=['GET','POST'])
def userHome(path):
    io_print('\nEntering UserHome: ' + str(path))
    try:
        return render_template('usuarioInicio.html',
                username        = userName,
                data            = newcasesdata,
                notificaciones  = str(totalNotificaciones),
                color           = color)
    except Exception as e:
        return render_template('error.html', error = 'Error: ' + str(e), goTo = "/")
    finally:
        database.disconnect()
# About page
@app.route('/about')
def about():

    return render_template('about.html')


# Profile page
@app.route('/profile',               methods=['POST','GET'])
def profile():

    userName = session.get('user')
    userID   = session.get('email')

    print userID

    if request.method == 'GET':

        if userName and userID:

            query   = ("SELECT  * "
            "FROM userinfo "
            "WHERE user_email = '" + str(userID) + "' ")

            database.connect()
            data = database.execute(query)

            if data:
                database.disconnect()
                return render_template('profile.html', name = userName, mail = userID, data = data)

    elif request.method == 'POST':
        name        = request.form['nameTitle']
        newmail     = request.form['mail']
        birthday    = request.form['birthday']
        location1   = request.form['location1']
        birthday    = request.form['birthday']
        activity    = request.form['activity']

        companyName = request.form['companyName']
        companyType = request.form['companyType']
        companyMail = request.form['companyMail']
        location2   = request.form['location2']
        companyRFC  = request.form['companyRFC']

        query =("UPDATE userinfo "
                "SET user_name        = '" + str(name)       + "' ,"
                "    user_email       = '" + str(newmail)    + "' ,"
                "    location         = '" + str(location1)  + "' ,"
                "    birthday         = '" + str(birthday)   + "' ,"
                "    activity         = '" + str(activity)   + "' ,"
                "    company_name     = '" + str(companyName)+ "' ,"
                "    company_type     = '" + str(companyType)+ "' ,"
                "    company_mail     = '" + str(companyMail)+ "' ,"
                "    company_location = '" + str(location2)  + "' ,"
                "    company_tax_no   = '" + str(companyRFC) + "' "
                "WHERE user_email  =    '" + str(userID) + "';")

        database.connect()
        data  =database.execute(query, True)

        query   = ("SELECT  * "
            "FROM userinfo "
            "WHERE user_email = '" + str(newmail) + "' ")

        data = database.execute(query)

        if data:
            database.disconnect()

            session['user' ]    = name
            session['email']    = newmail

            return render_template('profile.html', name = userName, mail = newmail, data = data)

        else:
            return render_template('profile.html', name = userName, mail = newmail, data = '{}')

# Exit this session
@app.route('/logout')
def logout():
    session.pop('user',None)
    session.pop('email',None)
    return redirect('/')

# Check info against the databse
@app.route('/validateLogin',        methods=['GET','POST'])
def validateLogin():
    try:
        # Post comes from web explorer, get comes from android
        if request.method   == 'POST':
            _username = request.form['inputEmail']
            _password = request.form['inputPassword']

        elif request.method == 'GET':
            # From Android
            _username = request.args.get('name')
            _password = request.args.get('password')
            _email    = request.args.get('email')

        io_print('\n\tLogin data')
        io_print('\t\tUser: ' + _username)
        io_print('\t\tPass: ' + _password)

        database.connect()
        data = database.sp_validate_login(_username)
        database.disconnect()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                io_print('\tValid Password!\n')
                session['user']  = data[0][1]
                session['email'] = data[0][2]
                path = 'userHome/'+str(session['user'])
                if request.method == 'POST':
                    # Return with a 302 because we are redirecting
                    return redirect(path, code=302)
                elif request.method == 'GET':
                    return session['user']
            else:
                if request.method == 'POST':
                    return render_template('error.html',error = 'Wrong Email address or Password.', goTo = "/"),503
                elif request.method == 'GET':
                    return 'Error: Wrong email or Password'
        else:
            if request.method == 'POST':
                return render_template('error.html',error = 'Wrong Email address or Password.', goTo = "/"),503
            elif request.method == 'GET':
                content = {'Error: Wrong email or Password'}
                #TODO: Do this for other request
                return content, status.HTTP_503_SERVICE_UNAVAILABLE

    except Exception as e:
        if request.method == 'POST':

            # FOR PRODUCTION DO NOT SHOW TRANSPARENT ERROR. JUST A CODE 503 (Service Unavailable)
            return render_template('error.html', error = 'ERROR EN VALIDACIÓN', goTo = "/"), 503
            # return render_template('error.html',error = 'ERROR: ' + str(e))

        elif request.method == 'GET':
            return 'error.html: ' + str(e)
        # return render_template('loginerror.html',error = 'Unauthorized Access')
        # TODO: what'up with this in the return?

# Fetch users data
@app.route('/getProfiles',             methods=['GET'])
def getProfiles():

    database.connect()

    data = database.execute('select * from user_info')

    database.disconnect()

    return json.dumps(data)



# Sign UP button calls POST
@app.route('/signUp',               methods=['POST','GET'])
def signUp():

    if request.method == 'GET': 
        name       = request.args.get('example')
    elif request.method == 'POST':

        name       = request.form['name']
        email      = request.form['email']
        password   = request.form['password']
        description= request.form['description']

    try:
        # Validate the received values
        if name and email and password:
            # MySQL process
            database.connect()

            hashed_password = generate_password_hash(password)

            if database.sp_create_user(name,email,hashed_password, description):
                print 'success'
                io_print("Successfully created a new user in DB...")

                return 'Successfully registered ' + name + ' with email: ' + email
            # User is already in database, since this is the same fuction to log in or sign up from FB, we choose what to do:
            else:
                return 'Error: User already exists!', status.HTTP_503_SERVICE_UNAVAILABLE
                
        else:
            return json.dumps({'html':'<span>Error: Enter the required fields</span>'})
    except Exception as e:
        io_print('Catch signup error: ' + str(e))
        return 'Error: ' + str(e)
    finally:
        if database:
            database.disconnect()

# Register the Android Token
@app.route('/registerToken',        methods = ['GET'])
def registerToken():
    if request.method == 'GET':

        userID  = request.args.get('email')
        token   = request.args.get('token')

        try:
            return 'Successfully stored token to user: ' + str(userID)
        except Exception as e:
            io_print("Error in registering Token: " + str(e))
            return e
        finally:
            database.disconnect()

# Upload images
@app.route('/upload',               methods=['GET', 'POST'])
def upload():
    # file upload handler code will be here
    if request.method == 'POST':
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        return json.dumps({'filename':f_name})

# Error handling
@app.route('/error',                methods=['GET','POST'])
def error():
    return render_template('error.html', error = 'TEST ERROR', goTo = "/")

############### PARSE UTILITY  ###########################################
filterKeys = [" Vs ", " Vs. "]
def filterContenido(contenido):
    global filterKeys
    #io_print(contenido)
    for key in filterKeys:
        if len(contenido.split(key)) == 2:
            autor, demandado = contenido.split(key)
            #cSplit = demandado.split(",")
            #if len(cSplit) == 3:
                #demandado, tmp, tmp2 = cSplit
            return autor, demandado
            # #check with .
            # cSplit = demandado.split(".")
            # if len(cSplit) == 3:
            #     demandado, tmp, tmp2 = cSplit
            #     return autor, demandado
            # elif len(cSplit) == 4:
            #     demandado, tmp1, tmp2, tmp3 = cSplit
            #     return autor, demandado
    return contenido, 'n/a'
############### PARSE UTILITY  ###########################################

# Start:
# This part is completly ignored by google cloud.
# Just use it for local development.
# Google clound only needs the methods and line 20 to run.
if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()

    args_parser.add_argument(   "-d",
                                "--debug",
                                help="print debug statements",
                                action="store_true",
                                default = False)

    args = args_parser.parse_args()

    IO_DEBUG = args.debug

    io_print = io_debug.io_debug(IO_DEBUG, None).io_print

    database = io_mysql.io_mysql(IO_DEBUG, None, True)

    app.run(host='0.0.0.0',port=5665)
    # app.run(host='192.168.8.106',port=5665) # MacBook-Pro 
