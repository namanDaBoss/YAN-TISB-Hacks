from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime
import sqlite3
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = "somesecretkeythatonlyishouldknow"
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'samrath1324@gmail.com'
app.config['MAIL_PASSWORD'] = 'merinolam'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
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


def book(booking):
    number_of_courts_available = (Sport.query.filter_by(
        sport_name=booking.get("sport")).first().number_of_courts)
    conn = sqlite3.connect("site.db")
    cursor = conn.cursor()
    if len(booking.get("bookdatetime")) > 10:
        timeOfBook = booking.get("bookdatetime")
        cursor = conn.execute(
            "select name from tisb where name =? and datetime like ? and sport=?;",
            (booking.get("username"),
             timeOfBook[:10] + "%", booking.get("sport")),
        )
    else:
        cursor = conn.execute(
            "select name from tisb where name =? and datetime =? and sport=?;",
            (booking.get("username"), booking.get(
                "bookdatetime"), booking.get("sport")),
        )

    booksInDay = cursor.fetchall()
    if len(booksInDay) >= 2:
        return "False"
    cursor = conn.execute(
        "select name from tisb where datetime = ? and sport=?;",
        (booking.get("bookdatetime"), booking.get("sport")),
    )
    row = cursor.fetchall()
    if len(row) < number_of_courts_available:
        cursor = conn.execute(
            "insert into tisb(name,datetime,sport)values \
            (?,?,?)",
            (booking.get("username"), booking.get(
                "bookdatetime"), booking.get("sport")),
        )
        conn.commit()
        return True
    else:
        session["can_book"] = True
        return False


def seeall():
    conn = sqlite3.connect("site.db")
    cursor = conn.cursor()
    cursor = conn.execute(
        "select * from tisb")
    result = cursor.fetchall()
    today = datetime.datetime.now()
    newli = []
    for i in result:
        date = i[2]
        date = datetime.datetime.strptime(date, "%d-%m-%Y-%H")
        if date >= today:
            date = datetime.datetime.strftime(date, "%d-%m-%Y-%H")
            time = date[11:]
            date = date[:10]
            i = list(i)
            if int(time) < 12:
                time = time + " " + "AM"
            else:
                time = time + " " + "PM"
            i[2] = date
            i.insert(3, time)
            newli.append(i)

    return newli



def avail(booking):
    conn = sqlite3.connect("site.db")
    cursor = conn.cursor()
    number_of_courts_available = 1
    cursor = conn.execute(
        "select datetime from tisb where sport = ?;", (booking.get("sport"),))

    result = cursor.fetchall()
    times = []
    for i in result:
        bookingTime = booking.get("bookdatetime")
        if i[0][:10] == bookingTime[:10]:
            times.append(i[0][11:])
    li = ["07", "08", "09", "10", "11", "12", "13",
          "14", "15", "16", "17", "18", "19", "20", ]
    availSlots = []
    for i in li:
        if times.count(i) < number_of_courts_available:
            availSlots.append(i)
    newAvailSlots = []
    for i in availSlots:
        if int(i) <= 12:
          newAvailSlots.append(i + " AM")
        else:
          newAvailSlots.append(str(int(i) - 12) + " PM")
    return newAvailSlots


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


@app.route("/empty-slots")
def empty_slots232324():
    return redirect(url_for("home"))


@app.route("/empty-slots/<string:sport>")
def empty_slots(sport=""):
    availableSlots = avail(session["booking"])
    session["redirect_from_empty_slots"] = True
    return render_template("available_slots.html", availSlots=availableSlots, sport=session["booking"].get("sport"))


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
            result = book(booking)
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

@app.route("/seeall-admin")
def seeall_admin():
    if is_admin():
        return render_template("all_bookings_admin.html" ,allBookings = seeall())
    else:
        return redirect(url_for("home"))
if __name__ == "__main__":
    app.run(debug=True)
