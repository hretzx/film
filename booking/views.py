from django.shortcuts import render
import mysql.connector as m
from django.http import HttpResponse
import config

db=m.connect(host=config.DB_HOST,user=config.DB_USER, password=config.DB_PASSWORD)

cursor=db.cursor()
cursor.execute("USE movies")

def shows(request,id):
    cursor.execute("""select * from showDetails where movie_id=%s""",(id,))
    shows=cursor.fetchall()
    return render(request,'shows.html',{"shows":shows})

def showseats(request,id):
    cursor.execute("""select * from seats where show_id=%s""",(id,))
    seats=cursor.fetchall()
    return render(request,'seats.html', {"seats":seats})

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
    return render(request,'payment.html',{"seat_ids": ",".join(seat_ids),"seat_numbers": seat_numbers,"total": total})

def payment(request):
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
    cursor.execute(""" select * from payment where uid=%s order by pid desc""",(uid,))
    data=cursor.fetchall()
    return render(request,'success.html',{"cname": cname,"total": total,"seat_string": seat_string})