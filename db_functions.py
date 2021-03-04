import sqlite3
import datetime


def today():
    return datetime.date.today()


def week_later():
    today = datetime.date.today()
    return today + datetime.timedelta(days=7)

def str2datetime(string):
    return datetime.strptime(string, "%d-%m-%Y-%h")

def book(booking, number_of_courts_available):
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


def userDetails(username):
    conn = sqlite3.connect("site.db")
    cursor = conn.cursor()
    cursor = conn.execute(
        "select * from tisb where name = ?", (username, ))
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
            elif int(time) == 12:
                time = time + " " + "PM"
            else:
                time = str(int(time) - 12) + " " + "PM"
            i[2] = date
            i.insert(3, time)
            newli.append(i)

    return newli


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
            elif int(time) == 12:
                time = time + " " + "PM"
            else:
                time = str(int(time) - 12) + " " + "PM"
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
    availSlots = [i for i in li if times.count(i) < number_of_courts_available]
    newAvailSlots = []
    for i in availSlots:
        if int(i) <= 12:
          newAvailSlots.append(i + " AM")
        else:
          newAvailSlots.append(str(int(i) - 12) + " PM")
    return newAvailSlots