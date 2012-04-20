# Create your views here.
import os
import re

from base import render_to_response, render_json, render_to_string, Jinja2ResponseMixin,\
        JSONResponseMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from settings import DEBUG
from django.http import QueryDict
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
from django import forms
from django.views.generic import ListView
from datetime import datetime
from documents.models import Document

from django.views.generic import TemplateView

from zmqrpc.client import ZMQRPC
import urllib2
import json
from dateutil.parser import parse as dateparse
from alphapagination import NamePaginator

DATEFORMAT = "%Y%m%d"
TIMEFORMAT = "%Y%m%d"
YAHOO_API="http://query.yahooapis.com/v1/public/yql?q=%s&format=json"
GOOGLE_API="http://finance.google.com/finance/info?client=ig&q=%s"

rpc = ZMQRPC("tcp://127.0.0.1:5000",timeout=50000)
#results = rpc.exec_tool('tools','ClientTools','week52diff',high_low='low')
#print results
print "Server is %s" % rpc.get_status()
servers = rpc.__serverstatus__()


class IndexView(ListView, Jinja2ResponseMixin):
    template_name = "index.html"

class JSONView(TemplateView, JSONResponseMixin):
    pass


def current_datetime(request):
    now = datetime.now()
    return render_to_response(request,'current_datetime.html', {'current_date': now})

def index(request):
    now = datetime.now()
    return render_to_response(request,'index.html', {'current_date': now, })
def _paginate(request,items, on):
    paginator = NamePaginator(items,on=on)
    page = 1
    try:
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    try:
        page = paginator.page(page)
    except (InvalidPage):
        page = paginator.page(paginator.num_pages)
    return page
def get_symbols(request):
    now = datetime.now()
    symbols = rpc.exec_tool('tools.ClientTools.all_symbols_names_sectors')
    page = _paginate(request,symbols, 0)
    return render_to_response(request,'symbols.html', {'current_date': now, 'page':page})
def get_sectors(request):
    now = datetime.now()
    sectors = rpc.exec_tool('tools.ClientTools.get_sectors')
    return render_to_response(request,'sectors.html', {'current_date': now, 'sectors':sectors})
def get_info(request, symbol):
    info = rpc.exec_tool('tools.ClientTools.get_info',symbol)
    prices = rpc.date_range(symbol,columns=['close'])
    startdate = datetime.strptime(prices[0][1],'%Y%m%d')
    enddate = datetime.strptime(prices[-1][1],'%Y%m%d')
    return render_to_response(request,'info.html', {'startdate': startdate,
        'enddate':enddate,'prices':prices, 'symbol':symbol, 'info':info})
def get_loosers52(request):
    loosers = rpc.exec_tool('tools.ClientTools.week52diff','low')
    page = _paginate(request,loosers,0)
    return render_to_response(request,'stocklisting.html', dict(page=page))
