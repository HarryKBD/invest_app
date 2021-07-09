# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 18:19:45 2021

@author: keybd
"""
FORMAT_DATE = '%Y-%m-%d'

from datetime import datetime
from datetime import timedelta
from happy_utils import FORMAT_DATE
import FinanceDataReader as fdr


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
    return datetime(int(tokens[0]), int(tokens[1]), int(tokens[2]))

def datetime_to_str(d):
    return d.strftime(FORMAT_DATE)

def get_fred_data_from_server(code, s_datetime, e_datetime):
    price_days = []
    
    sdate_str = s_datetime.strftime(FORMAT_DATE)
    edate_str = e_datetime.strftime(FORMAT_DATE)
    print("Connecting server to get data code: {}  from: {}  to: {} ".format(code, sdate_str, edate_str))
    ret = []
    while True:
        df = fdr.DataReader(code, sdate_str, edate_str, data_source='fred')
        print(len(df))
        if len(df) == 0:
            #print("No more data for code : " + code)
            break
        data_list = df[code]

        idx = df.index
        i = 0
        for value in data_list:
            last_date =  idx[i].to_pydatetime()
            print(f'{last_date} => {value}')
            ret.append((last_date, value))
            i += 1
        
        break

    return ret


def is_working_day(t):
    return cal.is_working_day(date(t.year, t.month, t.day))

#-------------------------
#https://financedata.github.io/posts/finance-data-reader-users-guide.html





if __name__ == '__main__':
    start_date = '2006-12-01'
    end_date = '2011-12-01'
    get_fred_data_from_server('UNRATE', to_datetime(start_date), to_datetime(end_date))