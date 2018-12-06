# -*- coding: utf-8 -*-
from    __future__      import unicode_literals
import  io_debug
import  MySQLdb as mysql
import  os

IO_DEBUG = 0
# These environnment variables are configured in app.yaml
CLOUDSQL_CONNECTION_NAME    = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER               = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD           = os.environ.get('CLOUDSQL_PASSWORD')

# MySQL configurations
db_username       = 'root'
db_password       = 'password'
db_dbname         = 'compendium'
hostname          = 'localhost'
tablename         = 'userinfo'
#
# resoluciones (
# [0]  fecha_url,
# [1]  fecha_boletin,
# [2]  ciudad,
# [3]  juzgado,
# [4]  ramo,
# [5]  sala_secretaria,
# [6]  tipo,
# [7]  no_resolucion,
# [8]  no_expediente,
# [9]  contenido,
# [10]  firma);
#
DB_fecha_url      = 0
DB_fecha_boletin  = 1
DB_ciudad         = 2
DB_juzgado        = 3
DB_ramo           = 4
DB_ss             = 5
DB_tipo           = 6
DB_nr             = 7
DB_ne             = 8
DB_contenido      = 9
DB_firma          = 10
# ==========================    SQL     =============================
class io_mysql:
    io_print = None
    conn     = None



    def __init__(self, io_print, io_log, print_All):
        if print_All:
            self.io_print = io_debug.io_debug(io_print, io_log).io_print
        else:
            self.io_print = io_debug.io_debug(False, io_log).io_print
        return

    def configure_credentials(self, username, password, database):
        db_username = username
        db_password = password
        db_dbname   = database

        return

    def connect(self):
        try:
            # When deployed to App Engine, the 'SERVER_SOFTWARE' environment variable
            # will be set to 'Google App Engine/version'.
            if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
                # Connect using the unix socket located at
                # /cloudsql/cloudsql-connection-name.
                cloudsql_unix_socket = os.path.join(
                    '/cloudsql', CLOUDSQL_CONNECTION_NAME)

                self.conn = mysql.connect(
                    unix_socket = cloudsql_unix_socket,
                    user        = CLOUDSQL_USER,
                    passwd      = CLOUDSQL_PASSWORD,
                    db          = db_dbname,
                    use_unicode = True,
                    charset     = 'utf8')
                self.io_print(str(self.conn))
            # If the unix socket is unavailable, then try to connect using TCP. This
            # will work if you are running a local MySQL server or using the Clud SQL
            # proxy, for example:
            #
            #   $ cloud_sql_proxy -instances=abogangster-182717:europe-west3:boletin=tcp:3306
            #
            else:
                #self.io_print("local mysql")
                self.conn = mysql.connect(
                    host        = '127.0.0.1',
                    user        = db_username,
                    passwd      = db_password,
                    db          = db_dbname,
                    use_unicode = True,
                    charset     = 'utf8')
                self.io_print('\tConnected: '+str(self.conn)+'\n')
            return True
        except mysql.Error as err:
            self.io_print("Something went wrong: {}".format(err))
            raise

    def disconnect(self):
        try:
            if self.conn != None:
                self.conn.close()
                self.io_print("\tDisconnected: mysql database...\n")
                return
            raise Exception('No first connection created.')
        except (mysql.Error, Exception) as err:
            self.io_print('\t'+str(err))
            # We don't want to raise an exception here because calling this method and failing means,
            # that something went wrong on main and it was not able to reach a connect, this may be a
            # waterfall of errors, raising this may clutter the caller.
            #raise

    def execute(self, query, commit=False):
        # Execute can work in two ways:
        # 1) When we want to request data to mysql we use "commit" parameter as False.
        # 2) When we want to write data to mysql we use "commit" parameter as True.
        # return empty array of data if an error happened.
        try:
            cursor = self.conn.cursor()
            self.io_print('\t'+query)
            cursor.execute(query)
            if commit:
                data = self.conn.commit()
            else:
                data = cursor.fetchall()
            self.io_print('\tSuccessfull query: ' + str(data))
            cursor.close()
            return data
        except mysql.Error as err:
            self.io_print('\t[x]Something went wrong: {}'.format(err))
            raise

    def store_resolutions(self, DB_ENTRIES):
        try:
            cursor = self.conn.cursor()
            cursor.callproc('sp_insert_resolucion',(DB_ENTRIES[DB_fecha_url],
                                                    DB_ENTRIES[DB_fecha_boletin],
                                                    DB_ENTRIES[DB_ciudad],
                                                    DB_ENTRIES[DB_juzgado],
                                                    DB_ENTRIES[DB_ramo],
                                                    DB_ENTRIES[DB_ss],
                                                    DB_ENTRIES[DB_tipo],
                                                    DB_ENTRIES[DB_nr],
                                                    DB_ENTRIES[DB_ne],
                                                    DB_ENTRIES[DB_contenido],
                                                    DB_ENTRIES[DB_firma] ) )
            data = cursor.fetchall()
            if len(data) is 0:
                #print "SUCCESS COMMIT TO DB"
                self.conn.commit()
                cursor.close()
                return True
            else:
                self.io_print("error committing to DB")
                cursor.close()
                return False
        except mysql.Error as err:
            self.io_print("Something went wrong: {}".format(err))
            raise

    def sp_create_user(self, name, email, password,description):
        
        try:

            cursor = self.conn.cursor()
            print cursor
            cursor.callproc('sp_create_user_compendium',(name,email,password, description))
            data = cursor.fetchall()
            print data
            if len(data) == 0:
                self.io_print("Commit to DB")
                self.conn.commit()
                cursor.close()
                return True
            else:
                self.io_print("error committing to DB")
                cursor.close()
                return False
        except mysql.Error as err:
            self.io_print("Something went wrong: {}".format(err))
            raise

    def sp_insert_usercase(self, args):
        try:
            cursor = self.conn.cursor()
            cursor.callproc('sp_insert_usercase',(args))
            data = cursor.fetchall()
            if len(data) == 0:
                self.io_print("SUCCESS COMMIT TO DB")
                self.conn.commit()
                cursor.close()
                return True
            else:
                self.io_print("error committing to DB: " + data)
                cursor.close()
                return False
        except mysql.Error as err:
            self.io_print("Something went wrong: {}".format(err))
            raise

    def sp_delete_usercase(self, user, case, city, jury, field):
        try:
            cursor = self.conn.cursor()
            cursor.callproc('sp_delete_usercase',(user, case, city, jury, field))
            if len(cursor.fetchall()) == 0:
                self.io_print("\tSuccessfull commit...")
                self.conn.commit()
                cursor.close()
                return True
            else:
                self.io_print("\t[x]Error committing...")
                cursor.close()
                raise Exception('\t[!]Warning, wrong user validation...')
        except mysql.Error as err:
            raise

    def sp_validate_login(self, username):
        try:
            cursor = self.conn.cursor()
            cursor.callproc('sp_validateLogin',(username,))
            data = cursor.fetchall()
            if len(data) != 0:
                self.io_print("\tSuccessfull call to mysql procedure...")
                cursor.close()
                return data
            else:
                self.io_print("\t[x]Error committing...")
                cursor.close()
                raise Exception('\t[!]Warning, something went wrong executing mysql procedure...')
        except mysql.Error as err:
            raise
# ==========================    SQL     =============================
