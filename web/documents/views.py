# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from datetime import datetime
from documents.models import Document

def week52loosers(request):
    
