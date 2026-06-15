from django.contrib import admin
from django.urls import path

from . import views

urlpatterns=[
    path('admin/',admin.site.urls),
    path('shows/<int:id>/', views.shows),
    path('showseats/<int:id>/', views.showseats),
    path('bookseat/',views.book),
    path('payment/', views.payment)
]