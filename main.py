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
    flash("yeah baby")
    return render_template('home.html', the_title='Home')

@app.route("/login", methods=['GET', 'POST'])

def login() -> 'html | Redirect':
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = crud.get_user(username)

        if user:
            if check_hash(password, user[8]):
                session['logged_in'] = True
                msg = 'Login successful for ' + username
                flash(msg)
                return redirect(url_for('dashboard'))
                # return "<h2>{}</h2>".format(msg)
            else:
                flash('Invalid password')
                return redirect(url_for('login'))
                # return '<h2>Invalid password</h2>'
        else:
            flash('Invalid username')
            return redirect(url_for('login'))
            # return '<h2>Invalid username</h2>'
    return render_template('login.html', the_title="Login")

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard() -> 'html':
    return render_template('temp.html')

@app.route('/register', methods=["GET", "POST"])
def register() -> 'html':
    return '<h2>You have successfully requested a connection.</h2>'

@app.route('/logout', methods=["GET"])
def logout() -> 'html':
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
