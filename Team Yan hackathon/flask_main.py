from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'


app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f'<User: {self.username}>'


class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_courts = db.Column(db.Integer)
    sport_name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f'<Sport: {self.sport_name}>'

class MyModelView(ModelView):
    
admin = Admin(app, name='Sports Booking', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Sport, db.session))

def is_admin():
    if "username" in session:
        if session["username"] == "000":
            return True
        return False
@app.route('/')
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' not in session:
        if request.method == 'POST':
            session.pop('username', None)
            username = str(request.form['username'])
            password = str(request.form['password'])
            user_queried = User.query.filter_by(username=username).first()

            if user_queried is not None:
                if password == user_queried.password:
                    session['username'] = user_queried.name
                    return redirect(url_for('home'))
        return render_template('login.html')
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    if 'username' in session:
        session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
