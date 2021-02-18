import sqlite3
import datetime

conn = sqlite3.connect("tisb.db")
cursor = conn.cursor()

#function for checking whether or not that slot is filled. If not, it inserts it.



def book(x,booking):
    cursor = conn.execute("select name from tisb where datetime = '"+booking.get('bookdatetime')+"' and sport='"+booking.get('sport')+"'")
    row = cursor.fetchall()
    if len(row)<x:
        cursor=conn.execute("insert into tisb(name,email,datetime,sport)values \
            (?,?,?,?)", (booking.get('username'),booking.get('email'),booking.get('bookdatetime'),booking.get('sport')))
        conn.commit()
        print("y")
        return True
    else:
        print("n")
        return False



def showRemainingCourts(x,booking):
    cursor = conn.execute("select name from tisb where datetime = '"+booking.get('bookdatetime')+"'")
    row = cursor.fetchall()
    remaining=x-len(row)
    print(remaining)
    return remaining

def check(booking):
    cursor=conn.execute("select email from tisb where name ='" + booking.get('bookname')+"' and datetime ="+booking.datetime+"'")
    row=cursor.fetchall()
    if len(row) > 2:
        return False
    else:
        return True
