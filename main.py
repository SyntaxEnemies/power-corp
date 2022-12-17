import datetime
from random import randint
from re import fullmatch
from typing import Literal

from flask import Flask, render_template, session, flash, redirect, url_for, request

import crud
from authutils import get_hash, check_hash, require_login
from mailutils import create_mail_handler, obfuscate_mail_address, compose_html_mail
from validations import (range_validator, type_validator, regex_validator,
                         compare_validator, is_decimal_str, non_empty, is_email, is_correct_date,
                         is_username, is_password, ValidationError)

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
        try:
            form_username = request.form['username'][:64]
            form_password = request.form['password'][:64]
        except KeyError as e:
            print(str(e))
            raise ValidationError('One or more fields were left blank.')

        # Return candidate user's record from the database (if any)
        user = crud.get_user(form_username)

        if user:
            # print(user)
            # match given password's hash against one from the record
            if check_hash(form_password, user['password']):
                session['logged_in'] = True
                # FIXME: flask flashes not visible in userpages
                # msg = 'Login successful for {}'.format(user['username'])
                # flash(msg)
                # return '<h2>{}</h2> '.format(msg)
                return redirect(url_for('dashboard'))
        # return '<h2>Incorrect username or password.</h2>'
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

            genders = ('male', 'female', 'unsaid')
            if not type_validator(request.form['gender'], genders):
                raise ValidationError('Unknown gender type.')

            if not is_email(request.form['email'][:256]):
                raise ValidationError('Invalid email address provided.')

            if not is_decimal_str(request.form['mobile_num'], 10):
                raise ValidationError('Invalid phone number.')

            if not non_empty(request.form['addr'][:256]):
                raise ValidationError('Invalid address.')

            # Basic registration particulars
            basic_info = {'first_name': request.form['fname'][:128],
                          'last_name':  request.form['lname'][:128],
                          'age':        int(request.form['age']),
                          'address':    request.form['addr'][:256],
                          'gender':     request.form['gender'],
                          'mobile_num': int(request.form['mobile_num']),
                          'email':      request.form['email'][:256], }

            # Validating given card details
            if not regex_validator(request.form['card-name'][:32], r'[A-Z]+ [A-Z]+'):
                raise ValidationError('Enter a valid card name.')

            card_types = ('credit', 'debit')
            if not type_validator(request.form['card-type'], card_types):
                raise ValidationError('Unknown card type.')

            if not is_decimal_str(request.form['card-number'], 16):
                raise ValidationError('Invalid card number.')
            if not is_decimal_str(request.form['card-cvv'], 3):
                raise ValidationError('Invalid CVV.')

            if not is_correct_date(request.form['card-expiry'], '%Y-%m'):
                raise ValidationError('Card is already expired or invalid card expiry date.')

            # Add day to card expiry date before storing in DB.
            exp_date = datetime.datetime.strptime(request.form['card-expiry'], '%Y-%m')

            # Calculate last day of month:
            # 1. Move up one day to first day of next month.
            # 2. Go back 1 day to last day of original month.

            #    December is an exception.
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

        # random six digit OTP to verify email
        verify_info = {'otp': randint(100000, 999999)}

        # store registration form in cookie for lookup in later requests
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
    # Check if registration is initiated
    if 'reg' in session:
        # FIXME: Email being resent for every wrong/invalid OTP.
        # TODO: Separate email conversation for each OTP mail
        # construct html email message
        msg_subject = '[{}] - Confirm email with OTP'
        msg_subject = msg_subject.format(session['reg']['verify']['otp'])
        print('[ THE_MESSAGE_SUBJECT_IS ]: ', msg_subject)

        message = compose_html_mail(sender=app.config['MAIL_ADDRESS'],
                                    receiver=session['reg']['basic']['email'],
                                    subject=msg_subject,
                                    template='otp.html',
                                    # Template arguments
                                    user=session['reg']['basic']['first_name'],
                                    # TODO: Make more readable
                                    mail=obfuscate_mail_address(session['reg']['basic']['email']),
                                    otp=session['reg']['verify']['otp'])

        mail_handler.sendmail(app.config['MAIL_ADDRESS'],
                              session['reg']['basic']['email'],
                              message)

        if request.method == 'POST':
            form_otp = ''
            # Sort dict with otp digits to preserve order
            print(request.form)
            for k, v in sorted(request.form.items()):
                # Validate OTP dict's keys and values.
                if regex_validator(k, 'digit[1-6]') and is_decimal_str(v, 1):
                    # Concatenate the digits from the OTP input form
                    form_otp += v
                else:
                    raise ValidationError('Invalid OTP, OTP has been resent.')

            if int(form_otp) == session['reg']['verify']['otp']:
                session['reg']['verify']['verified'] = True
                session.modified = True
                return redirect(url_for('set_credentials'))

            flash('Incorrect OTP, OTP has been resent.')
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

                # Commit the registration into a database record
                crud.add_user(session['reg']['basic'], session['reg']['card'])

                # Confirmation message to user
                msg = ('Dear {user}, your request for a new '
                       'connection has been received. You can '
                       'expect further developments within 24 hours.')
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


@app.errorhandler(ValidationError)
def invalid_form(err_msg) -> 'Redirect':
    """Clear an invalid form and flash the validation issue.

    Return a redirect to the current form which makes the browser clear
    the form and display the indicated error in form validation to user
    using a flash message.
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
