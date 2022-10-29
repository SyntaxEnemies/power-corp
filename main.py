from flask import Flask, render_template, session

app = Flask(__name__)
app.secret_key = 'eTgcGqlZFO5cBIedkYoc'
app.config.from_envvar('CONFIG_FILE')

dbconfig = {k: v for k, v in app.config.items() if k.startswith('DB')}
print(dbconfig)

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
