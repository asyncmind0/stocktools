# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from datetime import datetime
from documents.models import Document, Stocks
DATEFORMAT = "%Y%m%d"

def updatedb(request):
    ptotal = 0
    for histfile in glob.glob("**/*.TXT"):
        with open(histfile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
            stocktick = StockTick()
            stocktick.symbol = row[0]
            stocktick.date = datetime.strptime(row[1],DATEFORMAT)
            stocktick.open = float(row[2])
            stocktick.close = float(row[3])
            stocktick.high =float( row[4])
            stocktick.low = float(row[5])
            stocktick.volume = float(row[5])
            stocktick.save()
            ptotal+=1

    stocks = {}
    symbol_map = 'ASXListedCompanies.csv'
    with open(symbol_map, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i==1:continue
            stock = StockInfo()
            stock.symbol = row[1].strip()
            stock.name = row[0].strip()
            stock.sector = row[2].strip()
            stock.save()
            stocks[row[1] = stock


    indices_file = 'ASXIndices.csv'
    with open(indices_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            index = stocks.get(row[1].strip(),StockInfo())
            index.isindex = True
            if not index.symbol:
                index.symbol = row[1].strip()
            if not index.name:
                index.name = row[0].strip()
            index.save()
   return HttpResponse('<h1>Updated added %s stocks</h1>'% ptotal) 
