from flask import Flask, render_template, flash, redirect, url_for
from forms import RegistrationForm, LoginForm
from config import SECRET_KEY

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

@app.route("/")
def hello():
    return render_template('base.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('publicindex.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)\

@app.route('/login')
def login():
    form = RegistrationForm()
    return render_template('login.html', title='Login', form=form)



if __name__ == '__main__':
    app.run(debug=True)

