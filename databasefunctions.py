import sqlite3
import datetime

conn = sqlite3.connect("tisb.db")
cursor = conn.cursor()

#function for checking whether or not that slot is filled. If not, it inserts it.
def book(x,booking):
    cursor = conn.execute("select name from tisb where time = '"+booking.bookday+"' and time ='"+booking.booktime+"' and sport='"+booking.sport+"'")
    
    row = cursor.fetchall()
    if len(row)<x:
        cursor=conn.execute("insert into tisb(name,email,day,time,sport)values \
            (?,?,?,?,?)", (booking.username,booking.email,booking.bookday,booking.booktime,booking.sport))

        return True
    else:
        return False



def showRemainingCourts(x,booking):
    cursor = conn.execute("select name from tisb where day = '"+booking.bookday+"' and time ='"+booking.booktime+"'")
    row = cursor.fetchall()
    remaining=x-len(row)
    return remaining

def display(booking):
    cursor=conn.execute("select name,email,day,time,sport from tisb where sport='"+booking.sport+"' order by day asc, time asc")
    row=cursor.fetchall()
    return row
