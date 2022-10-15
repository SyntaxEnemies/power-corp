from flask import Flask, render_template

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')

@app.route("/")
@app.route("/home")
def home() -> 'html':
    return render_template('home.html')


@app.route("/login")
def login() -> 'html':
    return render_template('login_base.html')


@app.route("/logout")
def logout() -> 'html':
    return render_template('logout.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug='True')
