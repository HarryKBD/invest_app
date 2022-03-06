# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 18:19:45 2021

@author: keybd
"""
FORMAT_DATE = '%Y-%m-%d'

import datetime
import hdb
from workalendar.asia import SouthKorea


class Logger:
    def __init__(self, fname):
        now = datetime.datetime.now()
        self.log_file = hdb.MY_HOME + fname + '_log_' + now.strftime("%m%d") + '.txt'
        self.log_level = 5
        self.fd_opened = False
        print(self.log_file)
        
    def enable(self):
        self.fd = open(self.log_file, "a")
        self.fd_opened = True
        print('enable: ' + self.log_file)
        
    def w(self, msg, cprint = True, level=1):
        if self.log_level > level:
            self.fd.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "  :  " + msg + "\n")
        if cprint:
            print(msg)
        
    def set_level(self, level):
        self.log_level = level
        
    def disable(self):
        if self.fd_opened:
            self.fd_opened = False
            self.fd.close()

def is_same_month(d1, d2):
    tokens = d1.split("-")
    mon1 = int(tokens[1])

    tokens = d2.split("-")
    mon2 = int(tokens[1])

    if mon1 == mon2:
        return True
    else:
        return False

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
