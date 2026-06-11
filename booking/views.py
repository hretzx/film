from django.shortcuts import render
import mysql.connector as m
import config

db=m.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD
)

cursor=db.cursor()

cursor.execute("USE movies")


def shows(request,id):

    cursor.execute("""
        SELECT *
        FROM showDetails
        WHERE movie_id=%s
    """,(id,))

    shows=cursor.fetchall()

    return render(
        request,
        'shows.html',
        {"shows":shows}
    )

def showseats(request,id):

    cursor.execute("""
        SELECT *
        FROM seats
        WHERE show_id=%s
    """,(id,))

    seats=cursor.fetchall()
    print("SEATS =", seats)
    return render(
        request,
        'seats.html',
        {"seats":seats}
    )