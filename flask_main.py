from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime
import sqlite3


app = Flask(__name__)
app.secret_key = "somesecretkeythatonlyishouldknow"
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
db = SQLAlchemy(app)




def appropiate_datetime_format(date, time):
    date = date.split("-")
    time = time.split(":")[0]
    appropiate_datetime_format = date[2] + \
        "-" + date[1] + "-" + date[0] + "-" + time
    return appropiate_datetime_format


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<User: {self.username}>"


class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    number_of_courts = db.Column(db.Integer)
    sport_name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f"<Sport: {self.sport_name}>"


def is_admin():
    if "username" in session:
        if session["username"] == "000":
            return True
    return False


class MyModelView(ModelView):
    def is_accessible(self):
        return is_admin()


admin = Admin(app, name="Sports Booking", template_mode="bootstrap4")
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Sport, db.session))


def str2datetime(string):
    datet = datetime.strptime(string, "%d-%m-%Y-%h")
    return datet








@app.route("/")
@app.route("/home")
def home():
    if logged_in():
        if is_admin():
            return render_template("admin_index.html")
        else:
            return render_template(
                "index.html", button_content="Booking", button_url=url_for("book_slot")
            )
    return render_template(
        "index.html", button_content="Login", button_url=url_for("login")
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if not logged_in():
        if request.method == "POST":
            session.pop("username", None)
            username = str(request.form["username"])
            password = str(request.form["password"])
            user_queried = User.query.filter_by(username=username).first()

            if user_queried is not None:
                if password == user_queried.password:
                    session["username"] = user_queried.username
                    return redirect(url_for("home"))

        return render_template("login.html")
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    if logged_in():
        session.clear()
    return redirect(url_for("login"))


def logged_in():
    if "username" in session:
        return True
    return False


def today():
    today = datetime.date.today()
    return today


def week_later():
    today = datetime.date.today()
    week_later = today + datetime.timedelta(days=7)
    return week_later


@app.route("/book-slots", methods=["GET", "POST"])
def book_slot():
    if request.method == "POST" and not is_admin() and logged_in():

        date = request.form["date"]
        time = request.form["time"]
        sport_from_form = request.form["sport"]

        datetime_to_func = appropiate_datetime_format(date, time)

        if Sport.query.filter_by(sport_name=sport_from_form).first() is not None:
            number_of_courts_available = 2
            booking_thing = {
                "username": "Samrath",
                "bookdatetime": "21-02-2021-10",
                "sport": "Tennis"
            }
            with sqlite3.connect("site.db") as conn:
                cur = conn.cursor()
                cursor = conn.execute(
                    "select name from tisb where datetime = ? and sport=?;",
                    (booking_thing.get("bookdatetime"), booking_thing.get("sport")),
                )
                row = cursor.fetchall()
                if len(row) < number_of_courts_available:
                    cursor = conn.execute(
                        "insert into tisb(name,datetime,sport)values \
                        (?,?,?)",
                        (booking_thing.get("username"), booking_thing.get(
                            "bookdatetime"), booking_thing.get("sport")),
                    )
                    conn.commit()
            return datetime_to_func + " " + sport_from_form

    if is_admin():
        return redirect("/admin")

    if logged_in():
        return render_template("booking.html", min_date=today(), max_date=week_later())

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
