import sqlite3
from datetime import datetime,date,timedelta

conn = sqlite3.connect("tisb.db")
cursor = conn.cursor()

#function for checking whether or not that slot is filled. If not, it inserts it.
#booking= {
 #   'username':'Naman',
  #  'email':'email2namanjain@gmail.com',
   # 'bookdatetime':'16-05-2003-09395',
    #'sport': 'badminton'
    #}
#class booking():
 #   now=datetime.now()
  #  username='Arjun'
   # email='agtherock13@gmail.com'
    #bookdatetime=now.strftime("%d-%m-%Y")
    #sport='badminton'
    


def book(x,booking):
    cursor = conn.execute("select name from tisb where datetime = '"+booking.bookdatetime+"' and sport='"+booking.sport+"'")
    row = cursor.fetchall()
    if len(row)<x:
        cursor=conn.execute("insert into tisb(name,email,datetime,sport)values \
            (?,?,?,?)", (booking.username,booking.email,booking.bookdatetime,booking.sport))
        conn.commit()
        return True
    else:
        return False



def showRemainingCourts(x,booking):
    cursor = conn.execute("select name from tisb where datetime = '"+booking.bookdatetime+"'")
    row = cursor.fetchall()
    remaining=x-len(row)
    return remaining

def check(booking):
    if len(booking.bookdatetime)>10:
    
        cursor=conn.execute("select email from tisb where name ='" + booking.username+"' and datetime like '"+booking.bookdatetime[:10]+"%' and sport='"+booking.sport+"'")
        
    else:
        
        cursor=conn.execute("select email from tisb where name ='" + booking.username+"' and datetime ='"+booking.bookdatetime+"' and sport='"+booking.sport+"'")
    row=cursor.fetchall()
    if len(row) >= 2:
        return False
    else:
        return True


def str2datetime(string):
    datet = datetime.strptime(string,"%d-%m-%Y")
    return datet

def seeall(booking):
    cursor=conn.execute("select name,email,datetime from tisb where sport = '"+booking.sport+"'")

    row=cursor.fetchall()

    newli=[]
    for i in row:
        a=list(i)
        sdate=a[2]
        ddate=str2datetime(sdate)
        a.remove(sdate)
        a.insert(2,ddate)
        newli.append(a)


    return newli

def today():
    today=date.today()
    return today
def week():
    today=date.today()
    week_ago = today + timedelta(days=7)
    return week_ago


