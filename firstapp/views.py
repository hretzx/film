from django.http import HttpResponse 
from django.shortcuts import render
from myproject import config
import mysql.connector as m

mydb=m.connect(host=config.DB_HOST,user=config.DB_USER,password=config.DB_PASSWORD)

cursor=mydb.cursor()

cursor.execute("Create database if not exists pythondb")
cursor.execute("use pythondb")
cursor.execute(""" 
create table if not exists demo(
               id INT PRIMARY KEY AUTO_INCREMENT,
               name VARCHAR(20),
               age INT
               )
""")


mydb.commit()
print("Success")

def home(request):
    return render(request,"myhtml.html")

def user(request):
    name=request.POST.get('name')
    age=request.POST.get('age')
    query=""" 
insert into demo(name,age) values(%s,%s)         
"""
    cursor.execute(query,(name,age))
    
    mydb.commit()
    return HttpResponse("<p> Success! </p> <a href='/results'>view results</a>")

def results(request):
    cursor.execute("SELECT* from demo")
    data=cursor.fetchall()
    return render(request,"results.html",{"data":data})