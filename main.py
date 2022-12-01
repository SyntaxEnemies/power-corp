from random import randint
from re import fullmatch
from typing import Literal

from flask import Flask, render_template, session, flash, redirect, url_for, request

import crud
from authutils import get_hash, check_hash, require_login
from mailutils import create_mail_handler, obfuscate_mail_address, compose_html_mail

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')
# print(app.config)

mail_handler = create_mail_handler(sender_email=app.config['MAIL_ADDRESS'],
                                   password=app.config['MAIL_PASSWORD'],
                                   port=app.config['SMTP_PORT'],
                                   smtp_server=app.config['SMTP_SERVER'])


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home() -> 'html':
    """Render the webapp homepage."""
    return render_template('home.html', the_title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login() -> 'html | Redirect':
    """Login a user or redirect to dashboard if already logged in."""
    # check if already logged in
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']

        # Return candidate user's record from the database (if any)
        user = crud.get_user(input_username)

        if user:
            # print(user)
            # match given password's hash against one from the record
            if check_hash(input_password, user['password']):
                session['logged_in'] = True
                # msg = 'Login successful for {}'.format(user['username'])
                # flash(msg)
                return redirect(url_for('dashboard'))
                # return '<h2>{}</h2> '.format(msg)
            flash('Invalid password')
            # return '<h2>Invalid password</h2>'
        else:
            flash('Invalid username')
            # return '<h2>Invalid username</h2>'
    return render_template('login.html', the_title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register() -> 'html | Redirect':
    """Render and accept account registration forms."""
    if request.method == 'POST':
        # store registration form in cookie for lookup in later requests
        # Basic registration particulars
        session['reg'] = {}
        session['reg']['basic'] = {'first_name': request.form['fname'],
                                   'last_name':  request.form['lname'],
                                   'age':        request.form['age'],
                                   'address':    request.form['addr'],
                                   'gender':     request.form['gender'],
                                   'mobile_num': request.form['mobile_num'],
                                   'email':      request.form['email'], }
        # credit/debit card details
        session['reg']['card'] = {'name':   request.form['card-name'],
                                  'type':   request.form['card-type'],
                                  'number': request.form['card-number'],
                                  'cvv':    request.form['card-cvv'],
                                  'expiry': request.form['card-expiry']}

        # random six digit OTP to verify email
        session['reg']['verify'] = {'otp': randint(100000, 999999)}
        print(session['reg'])

        return redirect(url_for('verify'))
    return render_template('register.html', the_title='New Connection')


@app.route('/verify', methods=['GET', 'POST'])
def verify() -> 'Redirect':
    """Verify registration by sending OTP on email."""
    # Check if registration is initiated
    if 'reg' in session:
        # construct html email message
        msg_subject = '[{}] - Confirm email with OTP'
        msg_subject = msg_subject.format(session['reg']['verify']['otp'])
        print('[ THE_MESSAGE_SUBJECT_IS ]: ', msg_subject)

        message = compose_html_mail(sender=app.config['MAIL_ADDRESS'],
                                    receiver=session['reg']['basic']['email'],
                                    subject=msg_subject,
                                    template='otp.html',
                                    user=session['reg']['basic']['first_name'],
                                    mail=obfuscate_mail_address(session['reg']['basic']['email']),
                                    otp=session['reg']['verify']['otp'])

        mail_handler.sendmail(app.config['MAIL_ADDRESS'],
                              session['reg']['basic']['email'],
                              message)

        if request.method == 'POST':
            input_otp = ''
            # Sort and concatenate the digits from the OTP input form
            for k, v in sorted(request.form.items()):
                if fullmatch('d[0-9]+', k):
                    input_otp += v
            input_otp = int(input_otp)

            if input_otp == session['reg']['verify']['otp']:
                session['reg']['verify']['verified'] = True
                session.modified = True
                return redirect(url_for('set_credentials'))

            flash('Incorrect OTP')
        return render_template('verify_email.html',
                                the_title='Verify Email',
                                mail=obfuscate_mail_address(session['reg']['basic']['email'])
                                )
    return redirect(url_for('register'))


@app.route('/signup', methods=['GET', 'POST'])
def set_credentials() -> 'html | Redirect':
    """Set login credentials for a verified registration."""
    # Check if registered and verified
    if 'reg' in session and 'verify' in session['reg']:
        if 'verified' in session['reg']['verify']:
            if request.method == 'POST':
                session['reg']['basic']['username'] = request.form['uname']
                session['reg']['basic']['password'] = get_hash(request.form['passwd'])

                # Commit the registration into a database record
                crud.add_user(session['reg']['basic'], session['reg']['card'])

                # Confirmation message to user
                msg = ('Dear {user}, your request for a new'
                       'connection has been received. You can'
                       'expect further developments within 24 hours')
                flash(msg.format(user=session['reg']['basic']['first_name']))

                # Remove no longer needed data session cookie
                session.pop('reg')
                return redirect(url_for('home'))
            return render_template('signup.html', the_title='Set Account Credentials')

        flash('Please verify your email.')
        return redirect(url_for('verify'))
    return redirect(url_for('register'))


@app.route('/dashboard', methods=["GET"])
@require_login
def dashboard() -> 'html':
    """Render a logged in user's dashboard."""
    return render_template('user/home.html')


@app.route('/logout', methods=["GET"])
def logout() -> 'html | Redirect':
    """Logout if logged in then go to homepage."""
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('home'))


# @app.errorhandler(KeyError)
# def invalid_form(e) -> 'Redirect':
#     flash('Please fill all the required fields and try again')
#     print(e)
#     return redirect(request.url)


@app.errorhandler(404)
def page_not_found(e) -> tuple[str, Literal[404]]:
    """Render custom 404 template."""
    print(e)
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
