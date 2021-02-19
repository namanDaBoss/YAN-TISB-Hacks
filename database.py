import sqlite3
from datetime import datetime, date, timedelta

conn = sqlite3.connect("tisb.db")
cursor = conn.cursor()


"""
class booking:
    bookdatetime -> time of the booking, string
    sport -> the sport for the booking, string
    email -> email of the person who booked the slot, string
    username -> the username of the person who booked the slot, string
"""
def book(number_of_courts, booking):#to book a slot
    cursor = conn.execute("select name from tisb where datetime = '" +
                          booking.bookdatetime+"' and sport='"+booking.sport+"'")
    row = cursor.fetchall()
    if len(row) < number_of_courts:#if there are available courts
        cursor = conn.execute(
            "insert into tisb(name,email,datetime,sport)values(?,?,?,?)",
            (booking.username, booking.email, booking.bookdatetime, booking.sport))
        conn.commit()#adding the users
        return True
    else:
        return False


def showRemainingCourts(number_of_courts, booking):
    cursor = conn.execute(
        "select name from tisb where datetime = '"+booking.bookdatetime+"'")
    row = cursor.fetchall()
    remaining = number_of_courts-len(row)
    return remaining


def check(booking):
    if len(booking.bookdatetime) > 10:

        cursor = conn.execute("select email from tisb where name ='" + booking.username +
                              "' and datetime like '"+booking.bookdatetime[:10]+"%' and sport='"+booking.sport+"'")

    else:

        cursor = conn.execute("select email from tisb where name ='" + booking.username +
                              "' and datetime ='"+booking.bookdatetime+"' and sport='"+booking.sport+"'")
    row = cursor.fetchall()
    if len(row) >= 2:
        return False
    else:
        return True


def str2datetime(datetime_in_str):
    datetime_as_datetime = datetime.strptime(datetime_in_str, "%d-%m-%Y-%h")
    return datetime_as_datetime


def seeall(booking):
    cursor = conn.execute(
        "select name,email,datetime from tisb where sport = '"+booking.sport+"'")
    result = cursor.fetchall()

    result_with_datetime = []
    for i in result:# This for loop changes the str datetime to a datetime object
        a = list(i)
        a[2] = str2datetime(a[2])
        result_with_datetime.append(a)

    return result_with_datetime


def today():
    today = date.today()
    return today


def week():
    today = date.today()
    week_ago = today + timedelta(days=7)
    return week_ago


def avail(booking, x):
    cursor = conn.execute(
        "select datetime from tisb where sport ='"+booking.sport+"'")
    row = cursor.fetchall()
    times = []
    for i in row:
        if i[0][:10] == booking.bookdatetime[:10]:
            times.append(i[0][11:])
    li = ['07', '08', '09', '10', '11', '12', '13',
          '14', '15', '16', '17', '18', '19', '20']
    availSlots = []
    for i in li:
        if times.count(i) < x:
            availSlots.append(i)
    return availSlots