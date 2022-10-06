from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
@app.route("/homepage")
def home() -> 'html':
    return render_template('homepage.html')


@app.route("/login")
def login() -> 'html':
    return render_template('login_base.html')


@app.route("/logout")
def login() -> 'html':
    return render_template('logout.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug='True')
