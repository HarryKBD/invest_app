import happy_utils as ht
import happy_server as hs
import hdb
import datetime
from datetime import datetime
import init_stock_db as indb
from pytz import timezone

def is_us_stock(code):
    if code.isnumeric():
        return False
    else:
        return True

def update_stock_db_today(conn, code):
    if is_us_stock(code):
        tz = timezone('US/Eastern')
        today = datetime.datetime.now(tz)
        #print(f'us time today: {ht.datetime_to_str(today)}')
    else: 
        today = datetime.datetime.now()
        #print(f'KOR time today: {ht.datetime_to_str(today)}')
    #today = ht.to_datetime('2021-08-12')
    l = hs.get_stock_data_from_server(code, today, today)
    if len(l) != 1:
        #print(f'code: {code} => there is no data for today. very strange')
        return None, ht.datetime_to_str(today)
    else:
        #print(f'{code} ==> {l[0].get_date()} value: {l[0].get_close()}')
        hdb.insert_stock_data(conn, l)

    return l[0].get_close(), ht.datetime_to_str(today)

def get_stock_trend(conn, code, from_date_str, to_date_str = None):
    today = datetime.datetime.now()
    #default
    if to_date_str == None: #get date from server
        l = hs.get_stock_data_from_server(code, today, today)
        if len(l) == 1:
            hdb.insert_stock_data(conn, l)

    end_date_str = to_date_str
    if to_date_str == None:
        end_date_str = ht.datetime_to_str(today)
       
    valid, fdate, price_list = hdb.get_stock_data_from_db(conn, code, ht.to_datetime(from_date_str), ht.to_datetime(end_date_str))
    latest_price = price_list[-1]
    highest = max(price_list)
    lowest = min(price_list)

    return highest, lowest, latest_price

def init_all_stock_data_by_days(conn, num_days = 30):
    from code_list import my_codes
    edate = datetime.datetime.now()
    sdate = edate - datetime.timedelta(days = num_days)
    edate_str = ht.datetime_to_str(edate)
    sdate_str = ht.datetime_to_str(sdate)
    print(f'({sdate_str} - {edate_str}) Preparing data base for the all codes')
    indb.prepare_initial_table(conn, my_codes, sdate, edate)

def init_all_stock_data(conn):
    from code_list import my_codes
    sdate = ht.to_datetime('2000-01-01')
    edate = datetime.datetime.now()
    indb.prepare_initial_table(conn, my_codes, sdate, edate)

def get_mdd_values(conn, code, start_date, end_date=None):
    sdate = ht.to_datetime(start_date)
    if end_date == None:
        edate = datetime.now()
    else:
        edate = ht.to_datetime(end_date)
    
    valid, dd, price = hdb.get_stock_data_from_db(conn, code, sdate, edate)
    print(f'{code} => len {len(dd)}')
    if valid == False:
        return None
    last_peak_date = '0000-00-00'
    all_max_mdd_date = '0000-00-00'
    all_max_mdd = 0
    peak = -100
    this_max_mdd = 0
    this_max_mdd_date = '0000-00-00'
    for d, p in zip(dd, price):
        if d == '2016-02-27':
            continue
        if p > peak:
            peak = p
            last_peak_date = d
            this_max_mdd = 0
            #print(f'{d} ==> {p: .3f} NEW Peak')

        cur_down = (peak - p)/peak * 100.0

        if cur_down > this_max_mdd:
            this_max_mdd = cur_down
            this_max_mdd_date = d
            if this_max_mdd > all_max_mdd:
                all_max_mdd = this_max_mdd
                all_max_mdd_date = d
    print(f'{code}  {d} ==> {p: .3f} cur_down: {cur_down: .3f} this_mdd: {this_max_mdd: .3f} ({this_max_mdd_date}) last_peak: {last_peak_date} all_max_mdd: {all_max_mdd: .2f} ({all_max_mdd_date}) ')

    return cur_down, d, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date


def get_current_mdd(conn, code, start_date, end_date=None):
    cur_date, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date = get_mdd_values(conn, code, start_date, end_date)
    return cur_down, cur_date

def get_this_cycle_max_mdd(conn, code, start_date, end_date=None):
    cur_date, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date = get_mdd_values(conn, code, start_date, end_date)
    return this_max_mdd, this_max_mdd_date