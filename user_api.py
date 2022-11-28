import requests as req
import re, os, MySQLdb.cursors, style
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from configparser import ConfigParser

# config reader
conf = ConfigParser()
conf.read('config.ini')
API_CONF = conf["API"]
SQLDB = conf["SQLDB"]
API_KEY = API_CONF["api_key"]

# define web app and sub dirs with static files
app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24) #randomly generate a key every time the server restarts
app.config['MYSQL_HOST'] = SQLDB["host"]
app.config['MYSQL_USER'] = SQLDB["user"]
app.config['MYSQL_PASSWORD'] = SQLDB["password"]
app.config['MYSQL_DB'] = SQLDB["database"]
mysql = MySQL(app)

# sql setup
def get_user(cursor, username, password):
    # SQL-Injection prevention
    cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password, ))
    return cursor.fetchone()

def chk_user(cursor, username):
    cursor.execute('SELECT * FROM user WHERE username = %s', (username, ))
    return cursor.fetchone()

def add_user(cursor, username, password, access=1):
    cursor.execute('INSERT INTO user VALUES (%s,%s,%s)', (username, password, access))
    mysql.connection.commit()

def remove_user(cursor, username, password):
    cursor.execute('DELETE FROM user WHERE username = %s AND password = %s', (username, password, ))
    mysql.connection.commit()

# ERROR Handlers
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(error):
    return style.STATUS_ERR, 500

# ROOT
@app.route('/')
def index():
    if session.get("loggedin") == True:
        return redirect('/home')
    return redirect("/login")

@app.route('/home')
def home():
    if session.get("loggedin") == True:
        return render_template('index.html')
    return redirect("/login")

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    # NOTE: redirect bug fixed.
    # redirect id logged in
    if session.get('loggedin') == True: 
        return redirect('/home')

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = get_user(mysql.connection.cursor(MySQLdb.cursors.DictCursor), username, password)
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            return redirect('/home')
        else:
            msg = 'Incorrect username or password! Please try again.'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/removeuser', methods = ['GET', 'POST'])
def removeuser():
    msg = ''
    if session.get('loggedin') == True:    
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            if chk_user(mysql.connection.cursor(MySQLdb.cursors.DictCursor), username):
                if username == "admin":
                    msg = 'Cannot delete admin user.'
                else:
                    remove_user(mysql.connection.cursor(MySQLdb.cursors.DictCursor), username, password)
                    msg = 'Removed user.'
            elif not username or not password:
                msg = 'Form uncomplete.'
            else:
                msg = "User doesnt Exist."

        # return back the register.html with a message
        return render_template('removeuser.html', msg = msg)
    return redirect("/login")
                         
@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    # need auth to create new users
    if session.get('loggedin') == True:    
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            if chk_user(mysql.connection.cursor(MySQLdb.cursors.DictCursor), username):
                msg = 'Account already exists.'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must not contain numbers/special Chars.'
            elif not username or not password:
                msg = 'Form uncomplete.'
            else:
                add_user(mysql.connection.cursor(MySQLdb.cursors.DictCursor), username, password)
                msg = 'User has been added.'
        elif request.method == 'POST':
            msg = 'Form uncomplete.'
        # return back the register.html with a message
        return render_template('register.html', msg = msg)
    return redirect("/login")

# avoids CORS and prevents API-KEY from being exposed via webclient
@app.route('/get_server_list', methods = ['GET'])
def get_server_list():
    if session.get('loggedin') == True:   
        return req.get("https://0.0.0.0:1443/get_servers_info", json={"API_KEY":API_KEY, "request":{"list_servers":"all"}}, verify=False).json()
    return style.STATUS_NOAUTH

@app.route('/get_server_info', methods=['POST'])
def get_server_info():
    if session.get('loggedin') == True:   
        data = request.get_json()
        IP_Address = data.pop('info')
        return req.get("https://0.0.0.0:1443/get_servers_info", json={"API_KEY":API_KEY, "request":{"info":IP_Address}}, verify=False).json()
    return style.STATUS_NOAUTH

@app.route('/clear', methods=['POST'])
def clear():
    if session.get('loggedin') == True:
        data = request.get_json()
        clearitem = data.pop('clear')
        
        x = req.post("https://0.0.0.0:1443/clearit", json={"API_KEY":"glimpse", "request":{"clear":clearitem}}, verify=False)
        return style.STATUS_OK 
    return style.STATUS_NOAUTH

if __name__ == '__main__':
    # start application. note the 0.0.0.0 is to ensure the program takes on what IP the server is currently
    app.run(debug=eval(API_CONF["debug"]), threaded=True, host='0.0.0.0', port=8443, ssl_context=(API_CONF["cert_file"], API_CONF["key_file"]))