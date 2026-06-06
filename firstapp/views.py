from django.http import HttpResponse 
from django.shortcuts import render

import sqlite3 as m 

mydb=m.connect(database="pythondb1",check_same_thread=False)

cursor=mydb.cursor()

cursor.execute("""
create table if not exists movies(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(30),
               duration INTEGER,
                director VARCHAR(20),
                actors TEXT
               )
""")

mydb.commit()

cursor.execute("SELECT COUNT(*) FROM movies")

if cursor.fetchone()[0]==0:

    cursor.execute("""
    insert into movies(name,duration,director,actors) values("Home alone",120,"Idk","Idk1,Idk2,Idk3")
               """)

    mydb.commit()

cursor.execute("SELECT * FROM movies")
print(cursor.fetchall())

def home(request):
  #  return HttpResponse('<h2> Welcome to the page </h2>')
    cursor.execute("SELECT * from movies")
    movie=cursor.fetchall()
    return render(request,'myhtml.html',{"movie":movie})

