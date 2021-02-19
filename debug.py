import sqlite3

conn = sqlite3.connect("site.db")
cursor = conn.cursor()

booking={
    "bookdatetime":"20-05-2003-07",
    "username":"naman",
    "sport":"badminton"
    }

def book(number_of_courts_available, booking):
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
        return False
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
        return False

def showRemainingCourts(booking):
    number_of_courts_available = (
        Sport.query.filter_by(
            sport_name=booking.get("sport")).first().number_of_courts
    )
    cursor = conn.execute(
        "select name from tisb where datetime = ?;", (booking.get(
            "bookdatetime"))
    )
    row = cursor.fetchall()
    remaining = number_of_courts_available - len(row)
    return remaining
    
    

def str2datetime(string):
    datet = datetime.strptime(string, "%d-%m-%Y-%h")
    return datet
    
def seeall(booking):
    cursor = conn.execute(
        "select name,datetime from tisb where sport = ?;", (
            booking.get("sport"),)
    )

    row = cursor.fetchall()

    newli = []
    for i in row:
        a = list(i)
        a[2] = str2datetime(a[2])
        newli.append(a)

    return newli
    
def avail(booking):
    number_of_courts_available = 1
    cursor = conn.execute(
        "select datetime from tisb where sport =?;", (booking.get("sport"),))
    row = cursor.fetchall()
    times = []
    for i in row:
        bookingTime = booking.get("bookdatetime")
        if i[0][:10] == bookingTime[:10]:
            times.append(i[0][11:])
    li = ["07", "08", "09", "10", "11", "12", "13",
        "14", "15", "16", "17", "18", "19", "20", ]
    availSlots = []
    for i in li:
        if times.count(i) < number_of_courts_available:
            availSlots.append(i)
    return availSlots

def delete(bookid):
    cursor=conn.execute("delete from tisb where id =?;",(str(bookid)))
    conn.commit()
    return "deleted"
