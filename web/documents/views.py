from debug import debug as sj_debug
# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db.utils import DatabaseError, IntegrityError
from datetime import datetime
import glob
import csv
from documents.models import Document, StockTick, StockInfo
from psycopg2 import IntegrityError
DATEFORMAT = "%Y%m%d"

def stockinfo(request, symbol, date):
    sj_debug() ############################## Breakpoint ##############################
    stockinfo = StockTick.objects.filter(symbol=symbol)
    print symbol
    return render_to_response("stockinfo.html", {'stockinfo':stockinfo[0]})


def updatedb(request):
    ptotal = 0
    for histfile in glob.glob("history/**/*.TXT"):
        with open(histfile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    stocktick = StockTick()
                    stocktick.symbol = row[0]
                    stocktick.date = datetime.strptime(row[1],DATEFORMAT)
                    stocktick.open = float(row[2])
                    stocktick.close = float(row[3])
                    stocktick.high =float( row[4])
                    stocktick.low = float(row[5])
                    stocktick.volume = float(row[5])
                    stocktick.save()
                    if ptotal%1000 ==0 :
                        print '.',
                    ptotal+=1
                except DatabaseError as e:
                    #print type(e)
                    pass

    print "Done loading %s stock ticks" % ptotal
    ptotal2 = 0

    stocks = {}
    symbol_map = 'ASXListedCompanies.csv'
    with open(symbol_map, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i==1:continue
            try:
                stock = StockInfo()
                stock.symbol = row[1].strip()
                stock.name = row[0].strip()
                stock.sector = row[2].strip()
                stock.week52low = 0
                stock.week52high = 0
                stock.save()
                ptotal2+=1
                stocks[row[1].strip()] = stock
            except Exception as e:
                print e

    print "Done loading %s stockinfo" % ptotal2

    ptotal3 = 0
    indices_file = 'ASXIndices.csv'
    with open(indices_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                index = stocks.get(row[1].strip(),StockInfo.objects.filter(symbol=row[1].strip()))
                index.isindex = True
                if not index.symbol:
                    index.symbol = row[1].strip()
                if not index.name:
                    index.name = row[0].strip()
                index.save()
                ptotal3+=1
            except Exception as e:
                print e

    print "Done loading %s indexinfo" % ptotal2

    return HttpResponse('<h1>Updated added %s stocks</h1>'% ptotal) 
