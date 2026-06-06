from django.http import HttpResponse 
from django.shortcuts import render

def home(request):
    return HttpResponse('<h2> Welcome to the page </h2>')
