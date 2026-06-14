from django.shortcuts import render
from django.http import HttpResponse
import bcrypt
import mysql.connector as m
import config as cf

mydb=m.connect(host=cf.DB_HOST,user=cf.DB_USER,password=cf.DB_PASSWORD)
cursor=mydb.cursor()
cursor.execute("use movies")

def login(request):
    if request.method!="POST":
        return render(request,'login.html')
    user=request.POST.get('user')
    password=request.POST.get('password')
    cursor.execute(""" select uid,password from users where username=%s""",(user,))
    data=cursor.fetchone()
    if data is None:
        return HttpResponse("User is not registered!")
    uid=data[0]
    passw=data[1]
    if bcrypt.checkpw(password.encode('utf-8'),passw.encode('utf-8')):
        request.session["uid"]=uid
        request.session["username"]=user
        return HttpResponse("You're logged in successfully! <a href="/"> Go back to home page </a>")
    else:
        return HttpResponse("Wrong password!")


def register(request):
    if request.method!="POST":
        return render(request,'register.html')
    user=request.POST.get('user')
    email=request.POST.get('email')
    password=request.POST.get('password')
    plain_password=password.encode('utf-8')
    salt=bcrypt.gensalt(rounds=12)
    hashed_password=bcrypt.hashpw(plain_password,salt).decode('utf-8')
    query="""insert into users(username,email,password) values(%s,%s,%s)"""
    cursor.execute(query,(user,email,hashed_password))
    mydb.commit()
    return HttpResponse("Congrats, you've registered successfully! <a href='/'>Go to home page</a>")