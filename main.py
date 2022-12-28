import datetime
from random import randint
from typing import Literal

from flask import Flask, render_template, session, flash, redirect, url_for, request

import crud
from authutils import get_hash, check_hash, require_login
from mailutils import create_mail_handler, obfuscate_mail_addr, compose_html_mail
from validations import (range_validator, type_validator, regex_validator,
                         compare_validator, is_decimal_str, non_empty, is_email, is_correct_date,
                         is_username, is_password, ValidationError)

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')
# print(app.config)

# TODO: Perform this initialization asynchronously.
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
    # Check if already logged in.
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            form_username = request.form['username'][:64]
            form_password = request.form['password'][:64]
        except KeyError as e:
            print(str(e))
            raise ValidationError('One or more fields were left blank.')

        # Fetch user's record (if it exists) from the database.
        user = crud.get_user(form_username)

        # Check if any record was found corresponding to given username
        # and match given password's hash against one from the record.
        if user and check_hash(form_password, user['password']):
            # print(user)
            session['logged_in'] = True
            session['uid'] = user['id']
            # FIXME: flask flashes not visible in userpages
            # msg = 'Login successful for {}'.format(user['username'])
            # flash(msg)
            return redirect(url_for('dashboard'))
        flash('Incorrect username or password.')
    return render_template('login.html', the_title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register() -> 'html | Redirect':
    """Render and accept account registration forms."""
    if request.method == 'POST':
        try:
            # Validating Basic User Information
            if not non_empty(request.form['fname'][:128]):
                raise ValidationError('Invalid first name.')
            if not non_empty(request.form['lname'][:128]):
                raise ValidationError('Invalid last name.')

            if not range_validator(int(request.form['age']), 18, 150):
                raise ValidationError('Your age is inappropriate for registration.')

            genders = ('Male', 'Female', 'Unsaid')
            if not type_validator(request.form['gender'], genders):
                raise ValidationError('Unknown gender type.')

            if not is_email(request.form['email'][:256]):
                raise ValidationError('Invalid email address provided.')

            if not is_decimal_str(request.form['mobile-num'], 10):
                raise ValidationError('Invalid phone number.')

            if not non_empty(request.form['addr'][:256]):
                raise ValidationError('Invalid address.')

            # Basic registration particulars
            basic_info = {'first_name': request.form['fname'][:128],
                          'last_name':  request.form['lname'][:128],
                          'age':        int(request.form['age']),
                          'address':    request.form['addr'][:256],
                          'gender':     request.form['gender'],
                          'mobile_num': int(request.form['mobile-num']),
                          'email':      request.form['email'][:256], }

            # Validating given card details
            if not regex_validator(request.form['card-name'][:32],
                                   r'[A-Z]+ [A-Z]+'):
                raise ValidationError('Enter a valid card name.')

            card_types = ('Credit', 'Debit')
            if not type_validator(request.form['card-type'], card_types):
                raise ValidationError('Unknown card type.')

            if not is_decimal_str(request.form['card-number'], 16):
                raise ValidationError('Invalid card number.')
            if not is_decimal_str(request.form['card-cvv'], 3):
                raise ValidationError('Invalid CVV.')

            if not is_correct_date(request.form['card-expiry'], '%Y-%m'):
                raise ValidationError('Card is already expired or invalid card expiry date.')

            # Add day to card expiry date before storing in DB.
            # YYYY-MM -> YYYY-MM-DD where DD is last day of month MM.
            exp_date = datetime.datetime.strptime(request.form['card-expiry'], '%Y-%m')

            # Calculate last day of month:
            # 1. Move up one day to first day of next month.
            # 2. Go back 1 day to last day of original month.

            # December is an exception as no month next to it.
            if exp_date.month == 12:
                exp_date = exp_date.replace(day=31)
            else:
                exp_date = (exp_date.replace(month=exp_date.month+1)
                            - datetime.timedelta(days=1))

            # credit/debit card details
            card_info = {'name':   request.form['card-name'][:32],
                         'type':   request.form['card-type'],
                         'number': int(request.form['card-number']),
                         'cvv':    int(request.form['card-cvv']),
                         'expiry': exp_date}

        except KeyError as e:
            print(str(e))
            raise ValidationError('One or more fields were left blank.')
        except ValueError as e:
            print(str(e))
            raise ValidationError('Invalid value for a numeric field. ')

        # Generate random six digit OTP to verify email.
        # TODO: Store in server-side session
        verify_info = {'otp': randint(100000, 999999)}

        # Store registration data in browser's session cookie for later
        # lookup when storing in DB after verification.
        session['reg'] = {}
        session['reg']['basic'] = basic_info
        session['reg']['card'] = card_info
        session['reg']['verify'] = verify_info
        print(session['reg'])

        return redirect(url_for('verify'))
    return render_template('register.html', the_title='New Connection')


@app.route('/verify', methods=['GET', 'POST'])
def verify() -> 'Redirect':
    """Verify registration by sending OTP on email."""
    # Check if registration is initiated.
    if 'reg' in session:
        # Obfuscated email used in OTP email and OTP input webpage.
        user_mail_addr = obfuscate_mail_addr(session['reg']['basic']['email'])

        # FIXME: Resend not working.
        if request.method == 'GET' and 'sent' not in session['reg']['verify']:
            # TODO: Asynchronous sending of OTP
            # TODO: Separate email conversation for each OTP mail
            # Construct email attachment from HTML template.
            msg_subject = '[{}] - Confirm email with OTP'
            msg_subject = msg_subject.format(session['reg']['verify']['otp'])
            # print('[MAIL] Subject: ', msg_subject)

            message = compose_html_mail(sender=app.config['MAIL_ADDRESS'],
                                        receiver=session['reg']['basic']['email'],
                                        subject=msg_subject,
                                        template='otp.html',
                                        # template arguments
                                        user=session['reg']['basic']['first_name'],
                                        user_mail=user_mail_addr,
                                        otp=session['reg']['verify']['otp'])

            # TODO: Handle edge case where mail_handler may be None
            mail_handler.sendmail(app.config['MAIL_ADDRESS'],
                                  session['reg']['basic']['email'],
                                  message)

            print('[OTP] Sent: ', session['reg']['verify']['otp'])
            flash('Check for OTP on registered email.')

            session['reg']['verify']['sent'] = True
            session.modified = True

        elif request.method == "POST":
            form_otp = ''
            otp_digits = request.form.getlist('digits[]')

            for digit in otp_digits:
                # Check if each digit in OTP is a numeric character.
                if is_decimal_str(digit, 1):
                    # Concatenate all digits into OTP string.
                    form_otp += digit
                else:
                    raise ValidationError('Invalid OTP entered.')

            print('[OTP] Received: ', form_otp)
            if int(form_otp) == session['reg']['verify']['otp']:
                session['reg']['verify']['verified'] = True
                session['reg']['verify'].pop('sent')
                session.modified = True
                return redirect(url_for('set_credentials'))

            msg = 'Incorrect OTP entered.'
            print(msg)
            flash(msg)

        return render_template('verify_email.html',
                               the_title='Verify Email',
                               mail=user_mail_addr)

    flash('Please fill out the registration before verification.')
    return redirect(url_for('register'))


@app.route('/signup', methods=['GET', 'POST'])
def set_credentials() -> 'html | Redirect':
    """Set login credentials for a verified registration."""
    # Check if registered and verified.
    if 'reg' in session and 'verify' in session['reg']:
        if 'verified' in session['reg']['verify']:
            if request.method == 'POST':
                try:
                    form_username = request.form['username'][:64]
                    if not is_username(form_username):
                        errmsg = ('Username can only contain alphabets, '
                                  'numerals, underscores, hyphens and periods.')
                        raise ValidationError(errmsg)

                    form_password = request.form['password'][:64]
                    if not is_password(form_password):
                        errmsg = ('Password must contain at least 8 characters '
                                  'with at least a lowercase alphabet, an '
                                  'uppercase alphabet, a numeral and one of '
                                  '@$!%*?&.')
                        raise ValidationError(errmsg)

                    if not compare_validator(form_password,
                                             request.form['confirm-password']):
                        raise ValidationError('Passwords do not match.')

                except KeyError as e:
                    print(str(e))
                    raise ValidationError('One or more fields were left blank.')

                if compare_validator(form_password, form_username):
                    raise ValidationError('Username cannot be the password.')

                session['reg']['basic']['username'] = form_username
                session['reg']['basic']['password'] = get_hash(form_password)

                # Commit the registration into a database record.
                crud.add_user(session['reg']['basic'], session['reg']['card'])

                # Flash registration completion message to user.
                msg = ('Dear {user}, your request for a new '
                       'connection has been received. You can '
                       'expect further developments within 24 hours.')
                flash(msg.format(user=session['reg']['basic']['first_name']))

                # Remove data stored in session cookie during registration.
                session.pop('reg')
                return redirect(url_for('home'))
            return render_template('signup.html',
                                   the_title='Set Login Credentials')

        flash('Please verify your email.')
        return redirect(url_for('verify'))

    flash('Please register and verify yourself before account signup.')
    return redirect(url_for('register'))


@app.route('/user/dashboard', methods=['GET'])
@require_login
def dashboard() -> 'html':
    """Render a logged in user's dashboard."""
    return render_template('user/home.html', the_title='Dashboard')


@app.route('/user/payments', methods=['GET'])
@require_login
def show_payments() -> 'html':
    """Present a (logged in) user with their past payments."""
    # TODO: Store uid in server-side session.
    payments = crud.get_payments(session['uid'])
    col_titles = ('#', 'Bill Amount', 'Time', 'Mode', 'Note')
    return render_template('user/payments.html', the_title='Payment History',
                           theads=col_titles, payments=payments)


@app.route('/logout', methods=["GET"])
def logout() -> 'html | Redirect':
    """Logout if logged in then redirect to homepage."""
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('home'))


@app.errorhandler(ValidationError)
def invalid_form(err_msg) -> 'Redirect':
    """Clear an invalidly filled form and flash the validation issue.

    Return a redirect back to the same URL which makes the browser clear
    the form and indicate error in form validation to user using a
    flash message.
    """
    print(str(err_msg))
    flash(str(err_msg))
    return redirect(request.url)


@app.errorhandler(404)
def page_not_found(e) -> tuple[str, Literal[404]]:
    """Render custom 404 template."""
    print(e)
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
