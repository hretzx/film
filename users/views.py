from django.shortcuts import render, redirect
from django.http import HttpResponse
import bcrypt
import mysql.connector as m
import config as cf

mydb=m.connect(host=cf.DB_HOST,user=cf.DB_USER,password=cf.DB_PASSWORD)
cursor=mydb.cursor()
cursor.execute("use movies")

# users table — referenced by login/register/history but was never created
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    uid      INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE,
    email    VARCHAR(150),
    password VARCHAR(255)
)
""")
mydb.commit()

def login(request):
    if request.method!="POST":
        return render(request,'login.html')
    user=request.POST.get('username')
    password=request.POST.get('password')
    cursor.execute(""" select uid,password from users where username=%s""",(user,))
    data=cursor.fetchone()
    if data is None:
        return HttpResponse("User is not registered! <a href='/users/register/'>Register here</a>")
    uid=data[0]
    passw=data[1]
    if bcrypt.checkpw(password.encode('utf-8'),passw.encode('utf-8')):
        request.session["uid"]=uid
        request.session["username"]=user
        return redirect("/")
    else:
        return HttpResponse("Wrong password! <a href='/users/login/'>Try again</a>")


def register(request):
    if request.method!="POST":
        return render(request,'register.html')
    user=request.POST.get('username')
    email=request.POST.get('email')
    password=request.POST.get('password')
    plain_password=password.encode('utf-8')
    salt=bcrypt.gensalt(rounds=12)
    hashed_password=bcrypt.hashpw(plain_password,salt).decode('utf-8')
    query="""insert into users(username,email,password) values(%s,%s,%s)"""
    try:
        cursor.execute(query,(user,email,hashed_password))
        mydb.commit()
    except m.errors.IntegrityError:
        return HttpResponse("That username is already taken! <a href='/users/register/'>Try another</a>")
    return redirect("/users/login/")

def logout(request):
    request.session.flush()
    return redirect("/users/login/")

def history(request):
    if not request.session.get("uid"):
        return redirect("/users/login/")
    uid=request.session["uid"]
    # Join payment -> seats -> showDetails -> movie so each booking shows its film + seat.
    cursor.execute("""
        select p.pid, m.title, s.seat_no, p.amt, p.payment_status, m.poster_url
        from payment p
        join seats s        on p.seat_id = s.seat_id
        join showDetails sd on s.show_id = sd.show_id
        join movie m        on sd.movie_id = m.id
        where p.uid=%s
        order by p.pid desc
    """,(uid,))
    rows=cursor.fetchall()
    data=[{
        "ref": r[0],
        "title": r[1],
        "seat": r[2],
        "amt": r[3],
        "status": r[4],
        "poster": r[5],
    } for r in rows]
    total_spent=sum(r[3] for r in rows)
    return render(request,'history.html',{
        "data":data,
        "total_spent":total_spent,
        "count":len(data),
    })
