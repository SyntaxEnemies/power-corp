from flask import Flask, render_template, session, flash, redirect, url_for, request
from auth import get_hash, check_hash
# from crud import get_user
import crud

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')
# print(app.config)


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home() -> 'html':
    return render_template('home.html', the_title='Home')


@app.route('/register', methods=['GET', 'POST'])
def new_user() -> 'html':
    if request.method == 'POST':
        new_user = {'first_name': request.form['fname'],
                    'last_name':  request.form['lname'],
                    'age':        request.form['age'],
                    'address':    request.form['addr'],
                    'gender':     request.form['gender'],
                    'username':   request.form['uname'],
                    'password':   get_hash(request.form['passwd']),
                    'mobile_num': request.form['mobile_num'],
                    'email':      request.form.get('email'), }
        print(new_user)
        crud.add_user(new_user)

        # msg = ( 'Dear {user}, your request for a new connection'
        #         'has been received. You can expect'
        #         'further developments within 24 hours' )
        # flash(msg.format(user=new_user['first_name']))
        # return redirect(url_for('home'))
        return '<h2>Successfully added {} </h2>'.format(new_user['first_name'])

    return render_template('register.html', the_title='New Connection')


@app.route('/login', methods=['GET', 'POST'])
def login() -> 'html | Redirect':
    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']
        user = crud.get_user(input_username)

        if user:
            if check_hash(input_password, user[8]):
                session['logged_in'] = True
                msg = 'Login successful for {}'.format(user[7])
                # flash(msg)
                # return redirect(url_for('dashboard'))
                return '<h2>{}</h2>'.format(msg)
            else:
                flash('Invalid password')
                return redirect(url_for('login'))
                # return '<h2>Invalid password</h2>'
        else:
            flash('Invalid username')
            return redirect(url_for('login'))
            # return '<h2>Invalid username</h2>'
    return render_template('login.html', the_title='Login')


@app.route('/logout', methods=['GET'])
def logout() -> 'html':
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
