from operator import index
from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'


app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f'<User: {self.username}>'


@app.route('/')
@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if "Admin_logged_in" in session:
        return "<h1>ADMIN</h1>"
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' not in session:
        if request.method == 'POST':
            session.pop('user_id', None)
            username = str(request.form['username'])
            password = str(request.form['password'])
            if username == "Admin" and password == "QswhHJ21334Gk23j23h1G4HJ4KJHv2kj34v4k2233":
                session["Admin_logged_in"] = True
                return redirect(url_for('admin'))
            user_queried = User.query.filter_by(username=username).first()

            if user_queried is not None:
                if password == user_queried.password:
                    session['user_id'] = user_queried.id
                    return redirect(url_for('home'))
        return render_template('login.html')
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    if 'user_id' in session:
        session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)