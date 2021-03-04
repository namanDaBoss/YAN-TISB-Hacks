from flask import Flask, redirect, render_template, request, session, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from db_functions import book, userDetails, seeall, avail, str2datetime, today, week_later,\
    appropiate_datetime_format
from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, PasswordField, SelectField, validators
from wtforms.fields.html5 import DateField, TimeField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.secret_key = "somesecretkeythatonlyishouldknow"
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)

db = SQLAlchemy(app)


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
    return "username" in session and session["username"] == "000"


class MyModelView(ModelView):
    def is_accessible(self):
        return is_admin()


admin = Admin(app, name="Sports Booking", template_mode="bootstrap3")
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Sport, db.session))


class LoginForm(FlaskForm):
    username = TextField([validators.DataRequired()],
                         render_kw={"placeholder": "Username"})
    password = PasswordField([validators.DataRequired()], render_kw={
                             "placeholder": "Password"})


class BookingForm(FlaskForm):
    date = DateField('Date:', format='%d-%m-%Y', validators=[validators.DataRequired()],
                     render_kw={"min": today(), "max": week_later()})
    time = TimeField('Time:', validators=[validators.DataRequired()],
                     format='%T:%H:%M', render_kw={"step": "3600", "min": "07:00", "max": "20:00"})
    sport = SelectField(
        "Sport:", choices=[i.sport_name for i in Sport.query.all()])
    submit = SubmitField('Submit')


@app.route("/")
@app.route("/home")
def home():
    if is_admin():
        return render_template("admin_index.html")
    if logged_in():
        return render_template("index.html", button_content="Booking", button_url=url_for("book_slot"))
    return render_template("index.html", button_content="Login", button_url=url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if logged_in():
        return redirect(url_for("home"))
    if request.method == "POST":
        session.pop("username", None)
        username = str(request.form["username"])
        password = str(request.form["password"])
        user_queried = User.query.filter_by(username=username).first()

        if user_queried is not None and password == user_queried.password:
            session["username"] = user_queried.username
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    if logged_in():
        session.clear()
    return redirect(url_for("login"))


def logged_in():
    return "username" in session


@app.route("/empty-slots")
def empty_slots232324():
    return redirect(url_for("home"))


@app.route("/empty-slots/<string:sport>")
def empty_slots(sport=""):
    availableSlots = avail(session["booking"])
    session["redirect_from_empty_slots"] = True
    return render_template("available_slots.html", availSlots=availableSlots,
                           sport=session["booking"].get("sport"))


@app.route("/book-slots", methods=["GET", "POST"])
def book_slot():
    form = BookingForm()
    if is_admin():
        return redirect("/admin")
    if not logged_in():
        return redirect(url_for("login"))
    if request.method == 'POST' and form.is_submitted():
        date = request.form["date"]
        time = request.form["time"]
        sport_from_form = request.form["sport"]
        datetime_object = appropiate_datetime_format(date, time)

        if Sport.query.filter_by(sport_name=sport_from_form).first() is not None:
            booking = {
                "username": session["username"],
                "bookdatetime": datetime_object,
                "sport": sport_from_form
            }
            session["booking"] = booking
            result = book(booking, number_of_courts_available=Sport.query.filter_by(
                sport_name=booking.get("sport")).first().number_of_courts)
            if result == True:
                return render_template("one_message.html", message="Booking successful!",
                                       message2="You can now book another slot or logout.",
                                       home_and_login=True)
            elif result == False:
                empty_slots_page = "/empty-slots/" + booking.get("sport")
                return redirect(empty_slots_page)
            else:
                return render_template("too_many_bookings.html")

    return redirect(url_for("login"))


@app.route("/seeall-admin/")
def seeall_admin():
    if is_admin():
        return render_template("all_bookings_admin.html", allBookings=seeall())
    else:
        return redirect(url_for("home"))


@app.route("/seeall-user/")
def seeall_user():
    if logged_in():
        return render_template("all_data_user.html", allBookings=userDetails(session["username"]))
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=3300)
