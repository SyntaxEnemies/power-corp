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
        session['registration'] = {'first_name': request.form['fname'],
                                   'last_name':  request.form['lname'],
                                   'age':        request.form['age'],
                                   'address':    request.form['addr'],
                                   'gender':     request.form['gender'],
                                   'mobile_num': request.form['mobile_num'],
                                   'email':      request.form.get('email'), }

        # random six digit OTP to verify email
        session['verification'] = {'otp': randint(100000, 999999)}
        return redirect(url_for('send_otp'))

        # print(session['registration'])
    return render_template('register.html', the_title='New Connection')


@app.route('/otp/send', methods=['GET', 'POST'])
def send_otp() -> 'Redirect':
    """Send/Resend HTML message containing OTP on registration email."""
    # Check if registration is initiated
    if 'registration' in session:
        # construct html email message
        msg_subject = '[{}] - Confirm email with OTP'
        msg_subject = msg_subject.format(session['verification']['otp'])
        print('[ THE_MESSAGE_SUBJECT_IS ]: ', msg_subject)

        message = compose_html_mail(sender=app.config['MAIL_ADDRESS'],
                                    receiver=session['registration']['email'],
                                    subject=msg_subject,
                                    template='otp.html',
                                    user=session['registration']['first_name'],
                                    mail=obfuscate_mail_address(session['registration']['email']),
                                    otp=session['verification']['otp'])

        mail_handler.sendmail(app.config['MAIL_ADDRESS'],
                              session['registration']['email'],
                              message)

        return redirect(url_for('check_otp'))
    return redirect(url_for('register'))


@app.route('/otp/check', methods=['GET', 'POST'])
def check_otp() -> 'html':
    """Verify user if OTP is corrected."""
    if 'registration' in session:
        if request.method == 'POST':
            input_otp = ''
            # Sort and concatenate the digits from the OTP input form
            for k, v in sorted(request.form.items()):
                if fullmatch('d[0-9]+', k):
                    input_otp += v
            input_otp = int(input_otp)

            if input_otp == session['verification']['otp']:
                session['verification']['verified'] = True
                session.modified = True
                return redirect(url_for('set_credentials'))

            flash('Incorrect OTP')
        return (render_template('verify_email.html',
                                the_title='Verify Email',
                                mail=obfuscate_mail_address(session['registration']['email'])
                                ))
    return redirect(url_for('register'))


@app.route('/signup', methods=['GET', 'POST'])
def set_credentials() -> 'html | Redirect':
    """Set login credentials for a verified registration."""
    # Check if registered and verified
    if 'registration' in session and 'verification' in session:
        if 'verified' in session['verification']:
            if request.method == 'POST':
                session['registration']['username'] = request.form['uname']
                session['registration']['password'] = get_hash(request.form['passwd'])

                # Commit the registration into a database record
                crud.add_user(session['registration'])

                # Confirmation message to user
                msg = ('Dear {user}, your request for a new'
                       'connection has been received. You can'
                       'expect further developments within 24 hours')
                flash(msg.format(user=session['registration']['first_name']))

                # Remove no longer needed data session cookie
                session.pop('registration')
                session.pop('verification')
                return redirect(url_for('home'))
            return render_template('signup.html', the_title='Set Account Credentials')

        flash('Please verify your email.')
        return redirect(url_for('send_otp'))
    return redirect(url_for('register'))


@app.route('/dashboard', methods=["GET"])
@require_login
def dashboard() -> 'html':
    """Render a logged in user's dashboard."""
    return render_template('user_home.html')


@app.route('/logout', methods=["GET"])
def logout() -> 'html | Redirect':
    """Logout if logged in then go to homepage."""
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('home'))


@app.errorhandler(KeyError)
def invalid_form(e) -> 'Redirect':
    flash('Please fill all the required fields and try again')
    print(e)
    return redirect(request.url)


@app.errorhandler(404)
def page_not_found(e) -> tuple[str, Literal[404]]:
    """Render custom 404 template."""
    print(e)
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
