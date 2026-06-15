from django.shortcuts import render, redirect
import mysql.connector as m
from django.http import HttpResponse
import config

db=m.connect(host=config.DB_HOST,user=config.DB_USER, password=config.DB_PASSWORD)

cursor=db.cursor()
cursor.execute("USE movies")

# showDetails / seats / payment tables — referenced by the booking routes but never created
cursor.execute("""
CREATE TABLE IF NOT EXISTS showDetails(
    show_id   INT PRIMARY KEY AUTO_INCREMENT,
    movie_id  INT,
    screen    VARCHAR(50),
    format    VARCHAR(50),
    show_time VARCHAR(50)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS seats(
    seat_id INT PRIMARY KEY AUTO_INCREMENT,
    show_id INT,
    seat_no VARCHAR(10),
    price   INT,
    status  VARCHAR(20) DEFAULT 'available'
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS payment(
    pid            INT PRIMARY KEY AUTO_INCREMENT,
    seat_id        INT,
    cname          VARCHAR(100),
    amt            INT,
    payment_status VARCHAR(20),
    uid            INT
)
""")
db.commit()


# Predefined shows that every film gets, each seeded with a seat map.
PREDEFINED_SHOWS = [
    ("Screen 1", "Standard Theatre",  "Today • 10:30 AM",   250),
    ("Screen 1", "Standard Theatre",  "Today • 2:00 PM",    250),
    ("Screen 2", "Digital 4K Cinema", "Today • 5:30 PM",    300),
    ("IMAX",     "IMAX Laser 70mm",   "Tomorrow • 6:45 PM", 500),
]
SEAT_ROWS = ["A", "B", "C", "D", "E"]
SEATS_PER_ROW = 8
# Dummy pre-booked seats so every fresh show map shows a realistic available/booked mix.
PREBOOKED_SEATS = {"A3", "A7", "B2", "B8", "C5", "D1", "D7", "E6"}


def _ensure_shows(movie_id):
    """Seed the predefined shows + seat configuration for a movie the first time it's viewed."""
    cursor.execute("select count(*) from showDetails where movie_id=%s", (movie_id,))
    if cursor.fetchone()[0] > 0:
        return
    for screen, fmt, show_time, price in PREDEFINED_SHOWS:
        cursor.execute(
            "insert into showDetails(movie_id,screen,format,show_time) values(%s,%s,%s,%s)",
            (movie_id, screen, fmt, show_time),
        )
        show_id = cursor.lastrowid
        for row in SEAT_ROWS:
            for n in range(1, SEATS_PER_ROW + 1):
                seat_no = "%s%d" % (row, n)
                status = "booked" if seat_no in PREBOOKED_SEATS else "available"
                cursor.execute(
                    "insert into seats(show_id,seat_no,price,status) values(%s,%s,%s,%s)",
                    (show_id, seat_no, price, status),
                )
    db.commit()


def _show_summary(seat_id):
    """Resolve a seat -> its show -> the movie, for booking summaries."""
    cursor.execute("select show_id from seats where seat_id=%s", (seat_id,))
    row = cursor.fetchone()
    if row is None:
        return {}
    show_id = row[0]
    cursor.execute("select screen,format,show_time,movie_id from showDetails where show_id=%s", (show_id,))
    show = cursor.fetchone()
    if show is None:
        return {}
    screen, fmt, show_time, movie_id = show
    cursor.execute("select title from movie where id=%s", (movie_id,))
    title_row = cursor.fetchone()
    title = title_row[0] if title_row else ""
    return {"title": title, "screen": screen, "format": fmt, "show_time": show_time}


def shows(request,id):
    _ensure_shows(id)
    cursor.execute("""select * from showDetails where movie_id=%s""",(id,))
    shows=cursor.fetchall()
    cursor.execute("select id,title,poster_url from movie where id=%s",(id,))
    movie=cursor.fetchone()
    return render(request,'shows.html',{"shows":shows,"movie":movie})

def showseats(request,id):
    cursor.execute("""select * from seats where show_id=%s order by seat_no""",(id,))
    seats=cursor.fetchall()
    return render(request,'seats.html', {"seats":seats,"show_id":id})

def book(request):
    seat_ids=request.POST.getlist("seat_ids")
    if len(seat_ids)==0:
        return HttpResponse("<p>Please select at least one seat</p>")
    total=0
    seat_numbers=[]
    for id in seat_ids:
        cursor.execute(""" select status from seats where seat_id=%s""",(id,))
        ava=cursor.fetchone()
        if(ava[0] != 'available'):
            return HttpResponse("<p> Sorry this seat is not available </p>")
        cursor.execute(""" select seat_no, price from seats where seat_id=%s""",(id,))
        data=cursor.fetchone()
        seat_numbers.append(data[0])
        total+=data[1]
    summary=_show_summary(seat_ids[0])
    return render(request,'payment.html',{
        "seat_ids": ",".join(seat_ids),
        "seat_numbers": seat_numbers,
        "total": total,
        "show": summary,
    })

def payment(request):
    if not request.session.get("uid"):
        return redirect("/users/login/")
    cname=request.POST["cname"]
    uid=request.session["uid"]
    seat_ids=request.POST["seat_ids"].split(",")
    total=0
    seat_string=""
    for id in seat_ids:
        cursor.execute(""" select price from seats where seat_id=%s""",(id,))
        price=cursor.fetchone()
        total+=price[0]
        cursor.execute(""" select seat_no from seats where seat_id=%s""",(id,))
        seat_no=cursor.fetchone()[0]
        if seat_string=="":
            seat_string=seat_no
        else:
            seat_string=seat_string+", "+seat_no
        cursor.execute(""" insert into payment(seat_id,cname,amt,payment_status,uid) values(%s,%s,%s,%s,%s)""",(id,cname,price[0],'success',uid))
        cursor.execute(""" update seats set status='booked' where seat_id=%s """,(id,))
    db.commit()
    summary=_show_summary(seat_ids[0])
    return render(request,'success.html',{"cname": cname,"total": total,"seat_string": seat_string,"show": summary})
