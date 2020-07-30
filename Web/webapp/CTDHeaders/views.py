from django.shortcuts import render
from django.http import HttpResponse

from Toolkits import cnv_tk
from Toolkits import db_tk
# Create your views here.

cast = cnv_tk.Cast()
database = '../CNV.db'
conn = db_tk.create_connection(database)
cnv_tk.FetchCastObject(cast, conn)

print("Fetch Complete")

def home(request):

    return render(request, 'CTDHeaders/home.html')

def map(request):
    return HttpResponse('<h1> CTD Map </h1>')

