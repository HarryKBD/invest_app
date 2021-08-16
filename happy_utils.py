# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 18:19:45 2021

@author: keybd
"""
FORMAT_DATE = '%Y-%m-%d'

import datetime
from happy_utils import FORMAT_DATE
from workalendar.asia import SouthKorea

def get_year(dd):
    tokens =  dd.split("-")
    return tokens[0]

def same_date(a, b):
    if a.year == b.year and a.month == b.month and a.day == b.day:
        return True
    else:
        return False

def to_datetime(strdate):
    tokens =  strdate.split("-")
    return datetime.datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

def datetime_to_str(d):
    return d.strftime(FORMAT_DATE)

def is_working_day(t):
    cal = SouthKorea()
    #dd = datetime.date(t.ye)
    return cal.is_working_day(datetime.date(t.year, t.month, t.day))

#-------------------------
#https://financedata.github.io/posts/finance-data-reader-users-guide.html





if __name__ == '__main__':
    start_date = '2006-12-01'
    end_date = '2011-12-01'