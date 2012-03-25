# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db.utils import DatabaseError, IntegrityError
from datetime import datetime
import glob
import csv
import sys
from documents.models import Document, StockTick, StockInfo
from psycopg2 import IntegrityError
from django.db import transaction
DATEFORMAT = "%Y%m%d"

def stockinfo(request, symbol, date):
    stockinfo = StockTick.objects.filter(symbol=symbol)
    print symbol
    return render_to_response("stockinfo.html", {'stockinfo':stockinfo[0]})


@transaction.commit_manually
def updatedb(request):
    ptotal2 = 0

    stocks = {}
    symbol_map = 'ASXListedCompanies.csv'
    with open(symbol_map, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i==1:continue
            sid = transaction.savepoint()
            try:
                stock = StockInfo()
                stock.symbol = row[1].strip()
                stock.name = row[0].strip()
                stock.sector = row[2].strip()
                stock.week52low = 0
                stock.week52high = 0
                stock.save()
                transaction.savepoint_commit(sid)
                ptotal2+=1
                stocks[row[1].strip()] = stock
            except Exception as e:
                transaction.savepoint_rollback(sid)
                if not e.message.startswith('duplicate'):
                    print e
            else:
                transaction.commit()

    print "Done loading %s stockinfo" % ptotal2

    ptotal3 = 0
    indices_file = 'ASXIndices.csv'
    with open(indices_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            sid = transaction.savepoint()
            try:
                index = stocks.get(row[1].strip(),None)
                if not index:
                    index = StockInfo.objects.filter(symbol=row[1].strip())
                    if not index:
                        index = StockInfo()
                    else :
                        index = index[0]
                index.isindex = True
                if not index.symbol:
                    index.symbol = row[1].strip()
                if not index.name:
                    index.name = row[0].strip()
                index.week52high = 0
                index.week52low = 0
                index.save()
                transaction.savepoint_commit(sid)
                ptotal3+=1
            except Exception as e:
                transaction.savepoint_rollback(sid)
                print e
            else:
                transaction.commit()

    print "Done loading %s indexinfo" % ptotal3
    def get_num_lines():
        total_linenum = 0
        for histfile in glob.glob("history/**/*.TXT"):
            with open(histfile) as f:
                for l in f:
                    total_linenum+= 1
        return total_linenum
    print("Calculating data size")
    numlines = get_num_lines()
    print("Number of etries: %s"%numlines)
    ptotal = 0
    try:
        for histfile in glob.glob("history/**/*.TXT"):
            with open(histfile, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    sid = transaction.savepoint()
                    try:
                        ptotal+=1
                        if ptotal%100 ==0 :
                            sys.stdout.write( '\r')
                            sys.stdout.write( str(ptotal))
                            sys.stdout.flush()
                        stocktick = StockTick()
                        stocktick.symbol = row[0]
                        stocktick.date = datetime.strptime(row[1],DATEFORMAT)
                        stocktick.open = float(row[2])
                        stocktick.close = float(row[3])
                        stocktick.high =float( row[4])
                        stocktick.low = float(row[5])
                        stocktick.volume = float(row[5])
                        stocktick.save()
                        transaction.savepoint_commit(sid)
                    except DatabaseError as e:
                        transaction.savepoint_rollback(sid)
                        if not e.message.startswith('duplicate'):
                            print e
                        pass
                    if ptotal%1000 ==0 :
                        transaction.commit()
    except Exception as e:
        print e
    transaction.commit()

    print "Done loading %s stock ticks" % ptotal

    return HttpResponse('<h1>Updated added %s stocks</h1>'% ptotal) 
