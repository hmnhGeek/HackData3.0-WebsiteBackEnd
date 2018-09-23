from flask import Flask, render_template, request, url_for
import pickle, os

# define the app instance.
app = Flask(__name__)

# check if session is active
def session_active():
    f = open('session.txt', 'r')
    logical_arg = f.read()
    f.close()

    return int(logical_arg)

def change_session_status():
    status = session_active()
    os.remove('session.txt')
    f = open('session.txt', 'w')

    if status:
        f.write('0')
    else:
        f.write('1')
    f.close()

def load_adminPassword():
    f = open('master.txt', 'r')
    p = f.read()
    f.close()
    return p

# define home
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_login')
def user_login():
    return render_template('user_login_page.html')

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, 'users'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        data = []

        if os.path.exists(email+'.dat'):
            f = open(email+'.dat', 'rb')
            try:
                while True:
                    d = {}
                    d = pickle.load(f)
                    passw = d[email][-1]
                    data.append(d[email])
            except EOFError:
                f.close()

            if passw == password:
                data = data[0]
                os.chdir(cwd)
                return render_template('user.html', data=data)
            else:
                os.chdir(cwd)
                return "Wrong password."
        else:
            os.chdir(cwd)
            return "No such account."
        

@app.route('/check_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_pass = request.form['admin_pass']

        if admin_pass == load_adminPassword():
            change_session_status()
            return url_for('people')
        else:
            return "Wrong Password."

@app.route('/close_session')
def close():
    if session_active():
        change_session_status()
    return '200'

# create route for registering to hackdata.
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        name = request.form['name']
        college = request.form['college']
        team_name = request.form['team_name']
        phno = request.form['phone_no']
        email = request.form['email']
        password = request.form['key']

        f = open('database.dat', 'rb')
        fw = open('temp.dat', 'wb')
        flag = 0

        try:
            while True:
                d = {}
                d = pickle.load(f)
                print "d = {}".format(d)
                if email not in d:
                    d.update({email:[name, college, team_name, phno, password]})
                    pickle.dump(d, fw)
                    flag = 1
                else:
                    pickle.dump(d, fw)
        except EOFError:
            f.close()
        fw.close()
        os.remove('database.dat')
        os.rename('temp.dat', 'database.dat')
        
        if flag:
            # now create a file for the participants
            # store the current directory.
            cwd = os.getcwd()
            os.chdir(os.path.join(cwd, 'users'))
            f = open(email+'.dat', 'wb')
            pickle.dump({email:[name, college, team_name, phno, password]}, f)
            f.close()
            os.chdir(cwd)
            return "done"
        else:
            return "Email already registered."

@app.route('/participants')
def people():
    if session_active():
        f = open('database.dat', 'rb')
        d = {}
        try:
            while True:
                d = pickle.load(f)
        except EOFError:
            f.close()
        string = ''
        for i in d:
            string += "<br><br><br>DETAILS OF EMAIL: {} <br>==============================<br><br>".format(i)
            for j in range(len(d[i])-1):
                string += d[i][j] + "<br>"
        return string
    else:
        return render_template('master_login.html')

@app.route('/format')
def delete_all():
    os.remove('database.dat')
    f = open('database.dat', 'wb')
    pickle.dump({}, f, protocol=2)
    f.close()

    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, 'users'))
    f = os.listdir('.')
    for File in f:
        os.remove(File)
    os.chdir(cwd)
    return "200"

@app.route('/rmtree')
def remove():
    return render_template('remove_page.html')

@app.route('/schedule_delete', methods=['GET', 'POST'])
def schedule_delete():
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, 'users'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if os.path.exists(email+'.dat'):
            f = open(email+'.dat', 'rb')
            try:
                while True:
                    d = {}
                    d = pickle.load(f)
                    passw = d[email][-1]
            except EOFError:
                f.close()

            if passw == password:
                os.remove(email+'.dat')
                os.chdir(cwd)
                # now delete from main record
                F = open('database.dat', 'rb')
                FW = open('temp.dat', 'wb')
                try:
                    while True:
                        D = {}
                        D = pickle.load(F)
                        del D[email]
                        pickle.dump(D, FW)
                except EOFError:
                    F.close()
                FW.close()
                os.remove('database.dat')
                os.rename('temp.dat', 'database.dat')
                return '200'
            else:
                os.chdir(cwd)
                return "Wrong password."
        else:
            os.chdir(cwd)
            return "No such account."
        
if __name__ == '__main__':
    app.run(debug=True)
