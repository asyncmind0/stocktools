from django.shortcuts import render_to_response
from django.http import HttpResponse
from datetime import datetime
from documents.models import Document

def current_datetime(request):
    now = datetime.now()
    return render_to_response('current_datetime.html', {'current_date': now})

def index(request):
    now = datetime.now()
    documents = Document.objects.all()
    return render_to_response('index.html', {'current_date': now, 'documents':documents})
