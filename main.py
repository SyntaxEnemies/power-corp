from flask import Flask, render_template, session, flash, redirect, url_for, request
from auth import get_hash, check_hash
# from crud import get_user
import crud

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')
# print(app.config)

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home() -> 'html':
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login() -> 'html | Redirect':
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = crud.get_user(username)

        if user:
            if check_hash(password, user[8]):
                msg = 'Login successful for ' + username
                # flash(msg)
                session['logged_in'] = True
                # return redirect(url_for('dashboard'))
                return "<h1>{}</h1>".format(msg)
            else:
                # flash('Invalid password')
                # return redirect(url_for('login'))
                return '<h1>Invalid password</h1>'
        else:
            # flash('Invalid username')
            # return redirect(url_for('login'))
            return '<h1>Invalid username</h1>'
    return render_template('login.html')

@app.route('/logout', methods=["GET"])
def logout() -> 'html':
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
