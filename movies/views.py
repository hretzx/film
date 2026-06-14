from django.shortcuts import render,redirect
from django.http import HttpResponse,request
import mysql.connector as m
import config 

mydb=m.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD)
cursor=mydb.cursor()

cursor.execute("create database if not exists movies")
cursor.execute("use movies")
cursor.execute(""" 
create table if not exists movie(
               id INT PRIMARY KEY AUTO_INCREMENT,
               title VARCHAR(20),
               actors JSON,
               director VARCHAR(20),
               rating INT,
               duration INT,
               description VARCHAR(1000),
               crew JSON,
               genre JSON,
               langauges JSON
               )
""")

mydb.commit()
print("Success from movies db!")

def home(request):
    if not request.session.get("uid"):
        return redirect("/users/login/")
    cursor.execute("select * from movie")
    data=cursor.fetchall()
    return render(request,'home.html',{"moviedata":data})

def movie(request,id):
    cursor.execute("select * from movie where id=%s",(id,))
    moviee=cursor.fetchone()
    return render(request,'detail.html',{"movie":moviee})