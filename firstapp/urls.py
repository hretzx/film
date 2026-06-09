from django.contrib import admin 
from django.urls import path
from . import views 

urlpatterns=[
    path('',views.home,name="home-page"),
    path('myhtml',views.home),
    path('go',views.user),
    path('results',views.results),
    path('admin/',admin.site.urls)
]