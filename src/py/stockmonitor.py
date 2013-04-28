import os
import ystockquote as yq
from termcolor import colored
from table import pprint_table
from portfolios import portfolios
import argparse
import ConfigParser
import jabber
import logging

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def print_portfolios(args):
    header = []
    for h in ["SYM","PRICE","QTY", "VALUE", "COST PRICE", "COST", "CHANGE",
              "TOTAL_CHG","RETURN","% GAIN"]:
        header.append(colored(h,'magenta'))

    def colorize(val,comparator=lambda x:'red' if x<0 else 'green'):
        return colored(str(val),comparator(val))

    for name,portfolio in portfolios.items():
        myscrips = [
            header,]
        portfolio_mkt_val = 0
        portfolio_pur_val = 0
        portfolio_commision_cost = 0
        transaction_fee = 29
        print colored(name,'cyan')
        print "="*80
        for scrip in portfolio:
            script_details = yq.get_all(scrip['sym'])
            scrip_price = float(script_details['price'])
            portfolio_mkt_val+=scrip_price*scrip['qty']
            portfolio_pur_val+=scrip['value']*scrip['qty']
            portfolio_commision_cost += scrip['brokerage']
            cost = scrip['value']*scrip['qty']
            price = scrip_price*scrip['qty']
            total_change = (price)-(cost)
            returns = ((scrip_price*scrip['qty'])-(cost))-(scrip['brokerage']*2) 
            percentage_gain = (float(price-cost)/float(cost))*100.0
            myscrips.append([
                    colored(str(scrip['sym']),'white'),
                    colored(str(scrip_price),'white'),
                    colored(scrip['qty'],'white'),
                    colored(str(scrip_price*scrip['qty']),'white'),
                    colored(str(scrip['value']),'white'),
                    colored(cost,'white'),
                    colorize(scrip_price-scrip['value']),
                    colorize(total_change),
                    colorize(returns),
                    colorize('%.2f%%' %percentage_gain,lambda x:'red' if x.startswith('-') else 'green')
                    ]
                            )

        pprint_table(myscrips)
        print "Portfolio: %s (value) %s (cost)" % (portfolio_mkt_val+portfolio_commision_cost,portfolio_pur_val+portfolio_commision_cost)
        print "Mkt Gains: %s " % colorize(portfolio_mkt_val-portfolio_pur_val)
        print "Act Gains: %s " % colorize(portfolio_mkt_val-(portfolio_pur_val+portfolio_commision_cost))
        print "Total Commission:%s" % portfolio_commision_cost
    
def on_get_portfolio(message):
    return "get portfolio %s" % portfolio

def main(args, config):
    #print_portfolios(args)
    jabber_client = jabber.connect(config)
    jabber_client.add_handler("portfolio", on_get_portfolio)

if __name__ == '__main__':
    import daemon
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--launch', default=False, action="store_true",
                        help='show launcher')
    parser.add_argument('--notify', default='', help='show notification')
    parser.add_argument('--exit', default=False, action="store_true",
                        help='exit  daemon')
    parser.add_argument('--nodaemon', default=False, action="store_true",
                        help='dont daemonize')
    parser.add_argument('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    parser.add_argument('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)
    args = parser.parse_args()
    
    config = ConfigParser.RawConfigParser()
    home = os.getenv('USERPROFILE') or os.getenv('HOME')
    config_path = os.path.join(home, '.stockmonitor.cfg')
    print config_path
    config.read(config_path)

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.nodaemon:
        main(args, config)
    else:
        with daemon.DaemonContext():
            main(args, config)
