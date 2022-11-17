from flask import Flask, render_template, session, flash, redirect, url_for, request
from random import randint
from auth import get_hash, check_hash, require_login
import crud
from typing import Literal
from mailutils import MailHandler, obfuscate_mail_address, compose_html_mail


app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')
# print(app.config)


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home() -> 'html':
    return render_template('home.html', the_title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login() -> 'html | Redirect':
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    else:
        if request.method == 'POST':
            input_username = request.form['username']
            input_password = request.form['password']
            user = crud.get_user(input_username)

            if user:
                # print(user)
                if check_hash(input_password, user['password']):
                    session['logged_in'] = True
                    msg = 'Login successful for {}'.format(user['username'])
                    flash(msg)
                    return redirect(url_for('dashboard'))
                    # return '<h2>{}</h2>'.format(msg)
                else:
                    flash('Invalid password')
                    return redirect(url_for('login'))
                    # return '<h2>Invalid password</h2>'
            else:
                flash('Invalid username')
                return redirect(url_for('login'))
                # return '<h2>Invalid username</h2>'
        return render_template('login.html', the_title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register() -> 'html | Redirect':
    if request.method == 'POST':
        session['registration'] = {'first_name': request.form['fname'],
                                   'last_name':  request.form['lname'],
                                   'age':        request.form['age'],
                                   'address':    request.form['addr'],
                                   'gender':     request.form['gender'],
                                   'mobile_num': request.form['mobile_num'],
                                   'email':      request.form.get('email'), }

        # random six digit otp to verify email
        session['registration']['otp'] = randint(1000, 9999)

        # construct html email message
        msg_subject = '[{}] - Confirm email with OTP'
        msg_subject = msg_subject.format(session['registration']['otp'])

        message = compose_html_mail(sender=app.config['MAIL_ADDRESS'],
                                    receiver=session['registration']['email'],
                                    subject=msg_subject,
                                    template='otp.html',
                                    user=session['registration']['first_name'],
                                    mail=obfuscate_mail_address(
                                        session['registration']['email']),
                                    otp=session['registration']['otp'])

        with MailHandler(sender_email=app.config['MAIL_ADDRESS'],
                         password=app.config['MAIL_PASSWORD'],
                         port=app.config['SMTP_PORT'],
                         smtp_server=app.config['SMTP_SERVER']) as server:

            server.sendmail(app.config['MAIL_ADDRESS'],
                            session['registration']['email'],
                            message)

        return redirect(url_for('set_credentials'))
        # print(registration)

    return render_template('register.html', the_title='New Connection')


@app.route('/signup', methods=['GET', 'POST'])
def set_credentials() -> 'html | str':
    if 'registration' in session:
        if request.method == 'POST':
            session['registration']['username'] = request.form['uname']
            session['registration']['password'] = get_hash(request.form['passwd'])

            crud.add_user(session['registration'])
            msg = ( 'Dear {user}, your request for a new connection'
                    'has been received. You can expect'
                    'further developments within 24 hours' )
            flash(msg.format(user=session['registration']['first_name']))
            return redirect(url_for('home'))
            # return '<h2>Successfully added {} </h2>'.format(session['registration']['first_name'])
    else:
        return redirect(url_for('register'))
    return render_template('signup.html', the_title='Set Account Credentials')


@app.route('/dashboard', methods=["GET"])
@require_login
def dashboard() -> 'html':
    return render_template('user_home.html')


@app.route('/logout', methods=["GET"])
def logout() -> 'html | Redirect':
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('home'))

@app.route('/verify/mail')
def verify_mail():
    return(render_template('verify_email.html',
                           the_title='Verify Email',
                           mail=session['registration']['email']))


@app.errorhandler(KeyError)
def invalid_form(e) -> 'Redirect':
    if 'registration' in session:
        session.pop('registration')
    flash('Please fill all the required fields and try again')
    print(e)
    return redirect(request.url)


@app.errorhandler(404)
def page_not_found(e) -> tuple[str, Literal[404]]:
    print(e)
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
