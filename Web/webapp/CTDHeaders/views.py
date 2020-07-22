from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.



def home(request):
    return render(request, 'CTDHeaders/home.html')

def map(request):
    return HttpResponse('<h1> CTD Map </h1>')

