import hdb
import sys
import math
import argparse
from datetime import datetime
from datetime import date
import matplotlib.pyplot as plt
import FinanceDataReader as fdr
from datetime import datetime
from datetime import timedelta
from workalendar.asia import SouthKorea
from datetime import date
import numpy as np
import hdb
from stock_def import StockPrice
from stock_def import fund_stock
import happy_utils as ht
from happy_utils import FORMAT_DATE
import laa

MY_HOME='./'

cal = SouthKorea()
fund_stocks_all = []


class Logger:
    def __init__(self, fname):
        now = datetime.now()
        self.log_file = MY_HOME + fname + '_log_' + now.strftime("%m%d") + '.txt'
        self.log_level = 5
        self.fd_opened = False
        
    def enable(self):
        self.fd = open(self.log_file, "a")
        self.fd_opened = True
        
    def w(self, msg, cprint = False, level=1):
        if self.log_level > level:
            self.fd.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "  :  " + msg + "\n")
        if cprint:
            print(msg)
        
    def set_level(level):
        self.log_level = level
        
    def disable(self):
        if self.fd_opened:
            self.fd_opened = False
            self.fd.close()


#global log
log = Logger("flow")
log.enable()    


def is_working_day(t):
    return cal.is_working_day(date(t.year, t.month, t.day))

def get_stock_data_from_server(code, s_datetime, e_datetime):
    price_days = []
    col_closed = 'Close'
    sdate_str = s_datetime.strftime(FORMAT_DATE)
    edate_str = e_datetime.strftime(FORMAT_DATE)
    #print("Connecting server to get data code: {}  from: {}  to: {} ".format(code, sdate_str, edate_str))
    while True:
        df = fdr.DataReader(code, sdate_str, edate_str)
        if len(df) == 0:
            #print("No more data for code : " + code)
            break
        #print(df.head())
        openp = df['Open']
        highp = df['High']
        lowp = df['Low']
        closep = df[col_closed]
        vol = df['Volume']
        change = df['Change']

        idx = df.index
        i = 0
        for c in closep:
            last_date =  idx[i].to_pydatetime()
            s = StockPrice(code, last_date, float(openp[i]), float(highp[i]), 
                    float(lowp[i]),  float(c), int(vol[i]), float(change[i]))
            price_days.append(s)
            #print(s.to_text())
            i += 1
        
        if ht.same_date(e_datetime, last_date):
            break;
        last_date += timedelta(days=1)
        sdate_str = "{}-{}-{}".format(last_date.year, last_date.month, last_date.day)
        #sdate_str = "{}-{}-{}".format(last_date.year, last_date.month+1, last_date.day)

    return price_days



#show menu
"""
1. show all funds
2. show magic funds
3. show low funds
4. show quant funds
5. show LAA status
6. show exchange rate
7. update stock database for 1 year
"""

def show_menu():
    print('1. show all funds    2. show magic funds')
    print('3. show low funds    4. show quant funds')
    print('5. show LAA status   6. show exchange rate')
    print('7. update stock database for 1 year')

def create_stock_status(conn, code, buy_date, buy_price, buy_cnt, fund_name, today = None, eng_name=True):
    t = datetime.now()
    if today != None:
        t = today
        
    if not is_working_day(t):
        log.w("Today {} is not a working day. pass".format(t.strftime(FORMAT_DATE)))
        return None, 'HOLIDAY'
    
    #first update latest price in the db
    log.w("Getting today's data from server and insert into database. today is : " + t.strftime(FORMAT_DATE))
    l = get_stock_data_from_server(code, t, t)
    if len(l) != 1:
        log.w("There is no data for today..very strange....")
        return None, 'NO_DATA_FROM_SERVER'

    todayp = l[0].get_close()

    stock = fund_stock(code, buy_date, buy_price, buy_cnt, fund_name)
    stock.set_current_price(todayp)

    kor, eng = hdb.get_stock_names(conn, code)
    if eng != None:
        if eng_name == True:
            name = eng[0:13]
        else:
            name = kor[0:13]
    else:
        name = "UNKNOWN"
        
    stock.set_name(name)

    return stock


    return r, "OK"
    


def print_fund_status(stocks, fund_name):
    total_invested = 0
    total_value = 0
    print("FUND_NAME -----------------------------  " + fund_name + "  ---------------------------------------")
    for s in stocks:
        if fund_name == 'all' or s.get_fund_name() == fund_name:
            s.print_status()
            total_invested += s.get_invested_value()
            total_value += s.get_current_value()

    earn = total_value - total_invested
    rate = earn / total_invested * 100.0
    print("-" * 100)

    print(f"Invested: {total_invested}    Value: {total_value}   => Earn: {earn}   {rate: < 3.2f}")

    print("-" * 100)
    print("")


def prepare_fund_data(conn):
    fund_items_raw = hdb.get_fund_items(conn)

    fund_stocks = []
    total_cnt = len(fund_items_raw)
    cur = 0
    print_p = 10
    for raw in fund_items_raw:
        st = create_stock_status(conn, raw[0], raw[1], float(raw[2]), int(raw[3]), raw[4], today = None, eng_name=True)
        #st.print_status()
        fund_stocks.append(st)
        cur += 1
        p = cur / total_cnt * 100.0
        if p > print_p:
            print(f'Getting data....... {p: <3.2f} %')
            print_p += 10
    return fund_stocks

def show_laa_status(conn, dd):
    un_status = laa.get_unrate_status(conn, dd)
    snp_status = laa.get_snp_status(conn, dd)
    print(f'{ht.datetime_to_str(dd)} ==> UNRATE:{un_status}  S&P:{snp_status}')
    if un_status == None or snp_status == None:
        print("Error........")
        return None, None
    return un_status, snp_status

def get_fund_stocks(conn):
    global fund_stocks_all
    if len(fund_stocks_all) <= 0:
        fund_stocks_all = prepare_fund_data(conn)
    return fund_stocks_all

 
if __name__ == "__main__":
    conn = hdb.connect_db("stock_all.db")
    fund_stocks = []
    fund_list = ['HighPerf_LowVal', 'SuperQuant', 'NewMagic_Small20']

    while True:
        line = input('Prompt ("quit" to quit): ')
        if line == 'quit':
            break
        if line == 'h' or line == 'help':
            show_menu()
            continue

        if line == '1':
            print_fund_status(get_fund_stocks(conn), 'all')
            continue
        if line == '2':
            print_fund_status(get_fund_stocks(conn), fund_list[2])
            continue
        if line == '3':
            print_fund_status(get_fund_stocks(conn), fund_list[0])
            continue
        if line == '4':
            print_fund_status(get_fund_stocks(conn), fund_list[1])
            continue
        if line == '5':
            #show_laa_status(conn, ht.datetime_to_str(datetime.now()))
            show_laa_status(conn, datetime.now())
            continue

    conn.close()

#show menu
"""
1. show all funds
2. show magic funds
3. show low funds
4. show quant funds
5. show LAA status
6. show exchange rate
7. update all stock database 20 years
8. update all stock database by days before. arg : [days_before_to_get_update]
0. show US Stocks

What to update
1. init_fund_data
2. update prices of sotcks interested. (QQQ, RPAR whatever... for LAA/FUND... TBD)
3. update market indicator (LABOR)
4. 

"""
