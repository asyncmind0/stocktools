import csv, sys
from datetime import datetime
import re


def total_matches(pattern):
    total = 0
    for i,label in enumerate(labels):
        if re.match(pattern, label,re.I):
            total+=float(debits[i])
    return total

def plot_expenses():
    import matplotlib as mpl
    import pylab as pl
    from pylab import plot, show, ylim, yticks, connect
    import matplotlib.dates
    from pylab import get_current_fig_manager as gcfm
    import wx
    mpl.use('WXAgg')
    mpl.interactive(False)
    fig = pl.figure()
    ax = fig.gca()

    tooltip = wx.ToolTip(tip='tip with a long %s line and a newline\n'
    % (' '*100))
    # create a long tooltip with newline to get around wx bug where
    #newlines aren't recognized on subsequent self.tooltip.SetTip() calls
    tooltip.Enable(False) # leave disabled for now
    tooltip.SetDelay(0) # set popup delay in ms
    gcfm().canvas.SetToolTip(tooltip) # connect the tooltip to the canvas

    # Plotting stuff here ...
    ax.plot_date(dates, credits, 'b.-', picker=5, markersize=5)

    # Set major x ticks on Mondays.
    ax.xaxis.set_minor_locator(
        matplotlib.dates.WeekdayLocator(byweekday=matplotlib.dates.MO)
    )
    ax.xaxis.set_major_locator(
        matplotlib.dates.DayLocator(bymonthday=15)
    )
    ax.xaxis.set_major_formatter(
        matplotlib.dates.DateFormatter('%a %d\n%b %Y')
    )


    def onmotion( event):
        """Called during mouse motion over figure"""
        if event.xdata != None and event.ydata != None: # mouse is inside the axes
            tip='x=%f\ny=%f' % (event.xdata, event.ydata)
            tooltip.SetTip(tip) # update the tooltip
            tooltip.Enable(True) # make sure it's enabled
        else: # mouse is outside the axes
            tooltip.Enable(False) # disable the tooltip

    #connect('motion_notify_event', onmotion)
    def pick_event(event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        for i in ind:
            print labels[i], credits[i]
            tip='x=%s\ny=%s' % (labels[i], credits[i])
            tooltip.SetTip(tip) # update the tooltip
            tooltip.Enable(True) # make sure it's enabled
        #print 'onpick points:', zip(xdata[ind], ydata[ind])

    #connect('pick_event', af)
    connect('pick_event', pick_event)
    #pylab.annotate(labels[2],xy=(dates[2],credits[2]), visible=True, contains=af)
    pl.show()

special_cases= {'.*PAYPAL.*':'Paypal',
        '.*COMMSEC.*':'CommSec',
        '^DR.*':'Doctors',
        '^wdl.*':'Withdrawals'}

def get_transactions_by_payees(transactions):
    similar = {}
    items = []
    for transaction in transactions:
        key = None
        for case in special_cases:
            if re.match(case, transaction['label'],re.I):
                key = special_cases[case]
        if not key:
            key = transaction['label'].split(' ')[0]
        #if key == 'Transfer':
        #    continue
        item = {}
        similar.setdefault(key,item)
        similar[key].setdefault('key',key)
        similar[key].setdefault('items',[])
        similar[key].setdefault('total',0.0)
        similar[key]['items'].append(transaction)
        similar[key]['total']+=transaction['debit']
    items = similar.values()
    items.sort(key=lambda x:x['total'])
    return items, similar

def match_strings(str1,str2):
    ziped = zip(str1,str2)
    mat = [ p[0] if p[0] == p[1] else '' for p in ziped]
    return ''.join(mat).strip()

def get_keys(transactions):
    keys = []
    for transaction in transactions:
        if transaction['label'] not in keys:
            pass


def get_expenses():
    eatouts = [ "SUMO.*","GUZMAN.*", "OPORTO.*", "CAFE.*", "FRATELLI.*", "MAX BREN.*", "the village.*"]
    eatouts_total = 0
    for eats in eatouts:
        total = total_matches(eats)
        print "%s:%s" % (eats,total)
        eatouts_total+= total
    print eatouts_total

def get_transactions(filename = 'cwbstatement.csv'):
    transactions = []
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try :
            for row in reader:
                transaction = {}
                transaction['date'] = datetime.strptime(row[0],'%d/%m/%Y')
                transaction['debit'] = float(row[1])
                transaction['credit'] = float(row[3])
                transaction['label'] = row[2]
                transactions.append(transaction)
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
    return transactions

if __name__ == '__main__':
    transactions = get_transactions()
    print_payees(transactions)
