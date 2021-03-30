from flask import Flask, redirect, render_template, request, session, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime
from db_functions import appropiate_datetime_format, book, userDetails, seeall, avail, str2datetime
from models import db, User, Sport


app = Flask(__name__)
app.secret_key = "somesecretkeythatonlyishouldknow"
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def is_admin():
    return "username" in session and session["username"] == "000"


class MyModelView(ModelView):
    def is_accessible(self):
        return is_admin()


admin = Admin(app, name="Sports Booking", template_mode="bootstrap3")
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Sport, db.session))




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


def today():
    return datetime.date.today()


def week_later():
    today = datetime.date.today()
    return today + datetime.timedelta(days=7)


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
    if request.method == "POST" and not is_admin() and logged_in():

        date = request.form["date"]
        time = request.form["time"]
        sport_from_form = request.form["sport"]

        datetime_to_func = appropiate_datetime_format(date, time)

        if Sport.query.filter_by(sport_name=sport_from_form).first() is not None:
            booking = {
                "username": session["username"],
                "bookdatetime": datetime_to_func,
                "sport": sport_from_form
            }
            session["booking"] = booking
            result = book(booking, number_of_courts_available = Sport.query.filter_by(
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

    if is_admin():
        return redirect("/admin")

    if logged_in():
        return render_template("booking.html", min_date=today(), max_date=week_later(),
                               sports=Sport.query.all())

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
    app.run(debug=True, port = 3300)
