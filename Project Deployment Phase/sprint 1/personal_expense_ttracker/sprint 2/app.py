from flask import Flask, render_template, request, redirect, session
import re
import ibm_db

dsn_hostname = "ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
dsn_uid = "nby71676"
dsn_pwd = "5Y2wjQ1D0vOzuzMN"

dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "bludb"
dsn_port = "31505"
dsn_protocol = "TCPIP"

dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY=SSL;"
    "SSLServerCertificate=DigiCertGlobalRootCA.crt;").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd)

try:
    conn = ibm_db.connect(dsn, "", "")
    print("connected to database: ", dsn_database,
          "as_user: ", "on_host: ", dsn_hostname)
except:
    print("Unable to connect: ", ibm_db.conn_errormsg())

app = Flask(__name__)

app.secret_key = 'a'

mysql = ""


# HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")


@app.route("/")
def add():
    return render_template("home.html")


# SIGN--UP--OR--REGISTER


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM register WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO register(username, email, password) VALUES (?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'

            return render_template('signup.html', msg=msg)

 # LOGIN--PAGE


@app.route("/signin")
def signin():
    return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    global userid
    msg = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM register WHERE username=? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin'] = True
            session['id'] = account["ID"]
            userid = account["ID"]
            session['username'] = account['USERNAME']

            return redirect('/home')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

# ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():

    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    print(date)
    print(type(date))


    insert_sql = "INSERT INTO expenses (userid, date, expensename, amount, paymode, category) VALUES (?, ?, ?, ?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, session['id'])
    ibm_db.bind_param(prep_stmt, 2, date)
    ibm_db.bind_param(prep_stmt, 3, expensename)
    ibm_db.bind_param(prep_stmt, 4, amount)
    ibm_db.bind_param(prep_stmt, 5, paymode)
    ibm_db.bind_param(prep_stmt, 6, category)
    ibm_db.execute(prep_stmt)
    msg = 'You have successfully registered !'
    print(date + " " + expensename + " " +
          amount + " " + paymode + " " + category)

    return redirect("/display")


# DISPLAY---graph


@app.route("/display")
def display():
    print(session["username"], session['id'])

   
    sql = "SELECT * FROM expenses WHERE userid=? ORDER By expenses.date DESC"
    stmt = ibm_db.prepare(conn, sql)
    # print(str(session['id']))
    ibm_db.bind_param(stmt, 1, str(session['id']))
    ibm_db.execute(stmt)
    tuple_t = ibm_db.fetch_tuple(stmt)
    expense = []
    while tuple_t != False:
        expense.append(list(tuple_t))
        tuple_t = ibm_db.fetch_tuple(stmt)
    print(expense)
    return render_template('display.html', expense=expense)


# delete---the--data

@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete(id):


    sql = "DELETE FROM expenses WHERE id=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)

    print('deleted successfully')
    return redirect("/display")


# UPDATE---DATA

@app.route('/edit/<id>', methods=['POST', 'GET'])
def edit(id):
   

    sql = "SELECT * FROM expenses WHERE id=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    tuple_t = ibm_db.fetch_tuple(stmt)
    # print()
    print(list(tuple_t))
    tuple_l = list(tuple_t)
    tuple_l[2] = tuple_l[2].strftime("%Y-%m-%d")
    print(tuple_l)
    return render_template('edit.html', expenses=tuple_l)


@app.route('/update/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':

        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        paymode = request.form['paymode']
        category = request.form['category']


        sql = "UPDATE expenses SET date = ?, expensename = ?, amount = ?, paymode = ?, category = ? WHERE expenses.id = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, date)
        ibm_db.bind_param(stmt, 2, expensename)
        ibm_db.bind_param(stmt, 3, amount)
        ibm_db.bind_param(stmt, 4, str(paymode))
        ibm_db.bind_param(stmt, 5, str(category))
        ibm_db.bind_param(stmt, 6, id)
        ibm_db.execute(stmt)
        # mysql.connection.commit()
        print('successfully updated')
        return redirect("/display")

 # limit


@app.route("/limit")
def limit():
    return redirect('/limitn')


@app.route("/limitnum", methods=['POST'])
def limitnum():
    if request.method == "POST":
        number = request.form['number']
 
        sql = "INSERT INTO limits (userid, limitss) VALUES (?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['id'])
        ibm_db.bind_param(stmt, 2, number)
        ibm_db.execute(stmt)

        return redirect('/limitn')


@app.route("/limitn")
def limitn():
  
    sql = "SELECT limitss FROM limits ORDER BY limits.id DESC LIMIT 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)

    s = ibm_db.fetch_tuple(stmt)
    s = list(s)[2]
    return render_template("limit.html", y=s)