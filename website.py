from flask import Flask, render_template, request, url_for, redirect, flash
import pickle, os, re
from valid_email.valid_email import valid_email as email_is_valid

# define the app instance.
app = Flask(__name__)
app.secret_key = 'random string'


def team_exists(team_name):
    f = open('database.dat', 'rb')
    try:
        while True:
            d = pickle.load(f)
    except EOFError:
        f.close()
    uniques = d.values()
    for i in uniques:
        if team_name.upper() == i[2].upper():
            return 1
    return 0

def phone_no_is_valid(phno): 
      
    # 1) Begins with 0 or 91 
    # 2) Then contains 7 or 8 or 9. 
    # 3) Then contains 9 digits 
    Pattern = re.compile("(0/91)?[7-9][0-9]{9}") 
    return Pattern.match(phno) 

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
            return redirect(url_for('people'))
        else:
            return "Wrong Password."

@app.route('/close_session')
def close():
    if session_active():
        change_session_status()
    return redirect(url_for('home'))

# create route for registering to hackdata.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('home.html')
    if request.method == 'POST':
        name = request.form['name']
        college = request.form['college']
        team_name = request.form['team_name']
        phno = request.form['phone_no']
        email = request.form['email']
        password = request.form['key']

        details = [name, college, team_name, phno, password]
        if '' in details:
            flash("Please fill in all the details.", "warning")
            return render_template('home.html')

        if email_is_valid(email) and phone_no_is_valid(phno):

            f = open('database.dat', 'rb')
            fw = open('temp.dat', 'wb')
            unique_email = 0
            unique_team = 0

            try:
                while True:
                    d = {}
                    d = pickle.load(f)
                    if email not in d and not team_exists(team_name):
                        d.update({email:details})
                        pickle.dump(d, fw)
                        unique_email = 1
                        unique_team = 1
                    else:
                        pickle.dump(d, fw)
                        if email in d:
                            unique_email = 0
                        else:
                            unique_email = 1
                        if team_exists(team_name):
                            unique_team = 0
                        else:
                            unique_team = 1
            except EOFError:
                f.close()
            fw.close()
            os.remove('database.dat')
            os.rename('temp.dat', 'database.dat')

            if unique_email and unique_team:
                # now create a file for the participants
                # store the current directory.
                cwd = os.getcwd()
                os.chdir(os.path.join(cwd, 'users'))
                f = open(email+'.dat', 'wb')
                pickle.dump({email:[name, college, team_name, phno, password]}, f)
                f.close()
                os.chdir(cwd)
                flash('You have registered for hackdata 3.0 successfully.', 'info')
                return render_template('home.html')
            elif not unique_email and unique_team:
                flash("Email already registered.", "warning")
                return render_template('home.html')
            elif unique_email and not unique_team:
                flash("Same team name already exists.", "warning")
                return render_template('home.html')
            else:
                flash('Both team name and email already exists.', 'warning')
                return render_template('home.html')
        else:
            flag_email = 0
            flag_phno = 0
            if not email_is_valid(email):
                flag_email = 1
            if not phone_no_is_valid(phno):
                flag_phno = 1

            if flag_email and not flag_phno:
                flash('Email is not valid!!', 'warning')
            elif not flag_email and flag_phno:
                flash('Phone number is not valid!!', 'warning')
            else:
                flash('Phone number and Email is not valid!!', 'warning')

            return render_template('home.html')

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
        return render_template('participants.html', data=string)
    else:
        return render_template('master_login.html')

@app.route('/format')
def delete_all():
    if session_active():
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
        return redirect(url_for('people'))
    else:
        return render_template('master_login.html')

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
