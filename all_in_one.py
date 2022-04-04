import hdb
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
import stock_utils as su
import laa
import code_list
import json
import daily_update as du


cal = SouthKorea()
fund_stocks_all = []

class Logger:
    def __init__(self, fname):
        now = datetime.now()
        self.log_file = hdb.MY_HOME + fname + '_log_' + now.strftime("%m%d") + '.txt'
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
        
    def set_level(self, level):
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

def show_market_trend(conn):
    codes = code_list.ticker_code
    
    for c in codes:
        high, low, latest = su.get_stock_trend(conn, c, '2019-01-01')
        gap_from_high = (latest - high)/high * 100.0
        gap_from_low = (latest - low)/low * 100.0
        print(f'{c: <7} =>  High: {high: > 10.1f} ({gap_from_high: > 7.1f} %)     LOW: {low: > 7.1f} ({gap_from_low: > 7.1f} %), Cur: {latest: > 8.1f} ')
 

def create_server_response(type=None):

    resp_str = ( '{"mdd_stocks" : [ {"code" : "TQQQ", '
                             ' "update" : "2021-12-31", '
                             ' "price" : "33.23", '
                             ' "cur_down" : "32", '
                             ' "this_max_mdd_date" : "2021-11-01", '
                             ' "this_max_mdd" : "50.22" '
                             ' }, '
                             ' {"code" : "QQQ", '
                             ' "update" : "2021-12-31", '
                             ' "price" : "33.23", '
                             ' "cur_down" : "32", '
                             ' "this_max_mdd_date" : "2021-11-01", '
                             ' "this_max_mdd" : "50.22" '
                             '} ], '
           ' "laa": { "labor" : "True", "Spy" : "False" }, ' 
           ' "asset_alloc_funds" : [ {"fund_name":"Samsung_Pention_1", "fund_meta":"AssetAllocationSelfFund", "total_price":"55969815.0","cur_price":"54469070.0", "profit_rate":"-2.7",'
                                      ' "stocks": '
                                        ' [ {"name":"KODEXUSS&P500_H","code":"219480","cnt":"728", "cur_price":"21005.00","buy_price":"23080.00","ideal_ratio":"30.00", "cur_ratio":"28.07","profit_rate":"-8.99"}, '
                                        ' {"name":"KBSTARUSlongbonds_H","code":"267440","cnt":"713", "cur_price":"11250.00","buy_price":"11770.00","ideal_ratio":"15.00", "cur_ratio":"14.73","profit_rate":"-4.42"}, '
                                        ' {"name":"KODEXUSUltra30y_H","code":"304660","cnt":"1769","cur_price":"11845.00","buy_price":"12660.00","ideal_ratio":"40.00","cur_ratio":"38.47","profit_rate":"-6.44"} '
                                        ' ]} ]'
           ' } ')

    conn = hdb.connect_db("stock_all.db")

    codes = code_list.ticker_code
    start_date = '2015-01-01'

    resp = json.loads(resp_str)

#gather mdd stock status
    mdd_list = []
    for c in codes:
        cur_date, price, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, \
        all_max_mdd_date, last_peak, last_peak_date = su.get_mdd_values(conn, c, start_date)

        str = (f' "code":"{c}", "update":"{cur_date}", "price":"{price: .2f}", "cur_down":"{cur_down: .2f}",'
               f' "this_max_mdd_date":"{this_max_mdd_date}", "this_max_mdd":"{this_max_mdd: .2f}",' 
               f' "all_max_mdd_date":"{all_max_mdd_date}", "all_max_mdd":"{all_max_mdd: .2f}",' 
               f' "last_peak_date":"{last_peak_date}", "last_peak":"{last_peak: .2f}"')
        str = '{ ' + str + '}'
        mdd_list.append(str)
        #print(str)

    resp["mdd_stocks"] = mdd_list

#gather laa status
    now = datetime.now()
    un_status = laa.get_unrate_status(conn, now)
    snp_status = laa.get_snp_status(conn, now)
    un_status_str = f'{un_status}'
    snp_status_str = f'{snp_status}'

    resp["laa"]["labor"] = un_status_str
    resp["laa"]["Spy"] = snp_status_str

    asset_list = su.get_asset_alloc_status(conn)

    resp["asset_alloc_funds"] = asset_list

    str = json.dumps(resp)

    import re
    str = re.sub(r"\\","", str);
    str = re.sub(" ", "", str);
    #str = str.replace('["', '[');
    #str = str.replace('"]', ']');
    str = str.replace('}"', '}');
    str = str.replace('"{', '{');

    print(str)
    conn.close()
    return str


def show_mdd_status(conn):
    codes = code_list.ticker_code
    for c in codes:
        su.get_current_mdd(conn, c, '2015-01-01')

if __name__ == "__main__":
    conn = hdb.connect_db("stock_all.db")
    fund_stocks = []
    fund_list = ['HighPerf_LowVal', 'SuperQuant', 'NewMagic_Small20']
    print("Connected to db")

    while True:
        line = input('Prompt ("quit" to quit): ')
        if line == 'quit' or line == 'q':
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
        if line == '6':
            show_market_trend(conn)
            continue
        if line == '7':
            show_mdd_status(conn)
        if line  == '100':
            print("Updating all stock db for a year")
            su.init_all_stock_data_by_days(conn, 40000)
            continue
        if line == '101':
            print("Updating all database")
            su.init_all_stock_data(conn)
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
