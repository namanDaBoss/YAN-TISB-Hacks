import sqlite3

conn = sqlite3.connect("site.db")
cursor = conn.cursor()


def book(number_of_courts_available, booking):
    cursor = conn.execute(
        "select name from tisb where datetime = ? and sport=?;",
        (booking.get("bookdatetime"), booking.get("sport")),
    )
    row = cursor.fetchall()
    if len(row) < number_of_courts_available:
        cursor = conn.execute(
            "insert into tisb(name,datetime,sport)values \
            (?,?,?,?)",
            (booking.get("username"), booking.get(
                "bookdatetime"), booking.get("sport")),
        )
        conn.commit()
        return True
    else:
        return False
