from django.shortcuts import render, redirect
from django.http import HttpResponse
import mysql.connector as m
import config

mydb = m.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD)
cursor = mydb.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS movies")
cursor.execute("USE movies")
cursor.execute("""
CREATE TABLE IF NOT EXISTS movie(
    id          INT PRIMARY KEY AUTO_INCREMENT,
    title       VARCHAR(100),
    actors      JSON,
    director    VARCHAR(100),
    rating      INT,
    duration    INT,
    description VARCHAR(1000),
    crew        JSON,
    genre       JSON,
    langauges   JSON,
    poster_url  VARCHAR(1000)
)
""")

mydb.commit()
print("Success from movies db!")


def home(request):
    if not request.session.get("uid"):
        return redirect("/users/login/")
    cursor.execute("SELECT * FROM movie")
    data = cursor.fetchall()
    return render(request, 'home.html', {"moviedata": data})


def movie(request, id):
    cursor.execute("SELECT * FROM movie WHERE id=%s", (id,))
    moviee = cursor.fetchone()
    return render(request, 'detail.html', {"movie": moviee})