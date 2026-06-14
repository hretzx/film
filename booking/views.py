from django.shortcuts import render
import mysql.connector as m
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

def book(request,id):
    cursor.execute(""" select status from seats where seat_id=%s""",(id,))
    ava=cursor.fetchone()
    if(ava[0] != 'available'):
        return HttpResponse("<p> Sorry this seat is not available </p>")
    else:
        cursor.execute(""" select seat_no, seat_type, price from seats where seat_id=%s""",(id,))
        data=cursor.fetchone()

        return render(request,'payment.html',{"seat_id": id,"seat_no":data[0], "seat_type":data[1],"price":data[2]})
    

def payment(request,id):
    cname=request.POST["cname"]
    uid=request.session["uid"]
    cursor.execute(""" select price from seats where seat_id=%s""",(id,))
    price=cursor.fetchone()
    cursor.execute(""" insert into payment(seat_id,cname,amt,payment_status,uid) values(%s,%s,%s,%s,%s)
    """,(id,cname,price[0],'success',uid))
    cursor.execute(""" update seats set status='booked' where seat_id=%s """,(id,))
    db.commit()
    return render(request,'success.html')