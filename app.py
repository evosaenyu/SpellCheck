from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import current_user, LoginManager, UserMixin, login_user, logout_user
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import re
import logging
import datetime
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
logging.basicConfig(filename='appLog.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
login_manager = LoginManager()
login_manager.init_app(app)
users = {}
isLoggedIn = False

class User(UserMixin):
    pass
@login_manager.user_loader
def user_loader(uname):
    if uname not in users:
        logging.warning('Username not found on load.')
        return

    user = User()
    user.id = uname
    logging.info('User loaded.')
    return user


@login_manager.request_loader
def request_loader(request):
    uname = request.form.get('username')
    if uname not in users:
        logging.warning('Username not found on load.')
        return

    user = User()
    user.id = uname

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[uname]['password']

    return user
class ReusableForm(Form):
    words = TextField(validators=[validators.required()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None 
    if request.method == 'POST':
        if request.form['username'] in users.keys():
            logging.info('User tried to register as an existing user.')
            error = 'Username already exists. Try another.'
        else:
            users[request.form['username']] = hash(request.form['password'])
            print(users[request.form['username']])
            logging.info('New user registered: ' + str(users[request.form['username']]))
            return redirect(url_for('login'))
    if error != None:
        logging.warning('Registering returned an error: ' + error)
    return render_template('register.html', error=error)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form['username']
        try:
            if users[request.form['username']] != hash(request.form['password']):
                logging.warning('Invalid login occured for the following user: ' + str(users[request.form['username']]))
                error = 'Invalid Credentials. Please try again.'
            else:
                user = User()
                user.id = uname
                login_user(user)
                logging.info('User ' + user.id + ' logged in.')
                return redirect(url_for('hello'))
        except:
            logging.debug('Error on login. Probably user does not exist in dictionary.')
            pass
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    logout_user()
    logging.info('User logged out.')
    return 'Logged out'

@app.route("/", methods=['GET', 'POST'])
def hello():
    if current_user.is_authenticated:
        pass
    else:
        print("asssss")
        print(isLoggedIn)
        logging.debug("No user logged in. Redirecting to login.")
        return redirect(url_for('login'))
    form = ReusableForm(request.form)
    filename = "lexicon.txt"
    print(form.errors)
    if request.method == 'POST':
        words=request.form['words'].lower() #to match the case of the dictionary
        misspelledWords = []

        if form.validate():
            # Save the comment here.
            wordsList = words.split(' ')
            for w in range(len(wordsList)):
                wordsList[w] = re.sub(r'\W+', '', wordsList[w])
                dictionary = open(filename).readlines()
                dictionary = map(lambda x: x.strip(), dictionary)
                if wordsList[w] not in dictionary:
                    misspelledWords.append(wordsList[w])

            flash('The following words are misspelled: ' + str(misspelledWords))
        else:
            flash('Cannot leave the field blank. ')

    return render_template('hello.html', form=form)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'
if __name__ == "__main__":
    app.run()