#!/usr/bin/env python2
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    if 'loadcsv' in sys.argv:
        from cwbstatement import get_transactions
        from expenses.models import Transaction
        transactions = get_transactions()
        for transaction in transactions:
            tr = Transaction()
            tr.label = transaction['label']
            tr.credit = transaction['credit']
            tr.debit = transaction['debit']
            tr.date = transaction['date']
            tr.save()
    else:
        execute_from_command_line(sys.argv)
