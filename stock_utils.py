import happy_utils as ht
import happy_server as hs
import hdb
import datetime
import init_stock_db as indb
from pytz import timezone

def is_us_stock(code):
    if code.isnumeric():
        return False
    else:
        return True

def update_stock_db_today(conn, code):
    today = datetime.datetime.now()
    #test_date = '2022-03-10'
    #today = ht.to_datetime(test_date)
    l = hs.get_stock_data_from_server(code, today, today)

    if is_us_stock(code):
        tz = timezone('US/Eastern')
        today = datetime.datetime.now(tz)
        #today = ht.to_datetime(test_date)
        print(f'us time today: {ht.datetime_to_str(today)}')
    else:
        print(f'KOR time today: {ht.datetime_to_str(today)}')
 
    today_str = ht.datetime_to_str(today)

    if len(l) > 0:
        for s in l:
            if s.get_date() == today_str:
                print(f"Got the today's data {code} ==> {s.get_date()} value: {s.get_close()}")
                hdb.insert_stock_data(conn, l)
                return s.get_close(), ht.datetime_to_str(today)

    return None, ht.datetime_to_str(today)

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
        edate = datetime.datetime.now()
    else:
        edate = ht.to_datetime(end_date)
    
    valid, dd, price = hdb.get_stock_data_from_db(conn, code, sdate, edate)
    print(f'{code} => len {len(dd)} {start_date} - {ht.datetime_to_str(edate)}')
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

    return d, p, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date, peak, last_peak_date

import json

def to_asset_alloc_fund_json(conn, fund_name, item_list):

    resp_str = ( '{   "fund_name":"Samsung Stock IRP1", '
                    ' "fund_meta":"Write your additional strings", '
                    ' "total_price":"1000000", '
                    ' "cur_price":"1500000", '
                    ' "profit_rate":"50", '
                    ' "stocks":[ '
                            ' {"name":"Tiger Nasdaq 100", "code":"293474", "cnt":"283", '
                            ' "cur_price":"4000", "buy_price":"3000", "ideal_ratio":"20", '
                            ' "cur_ratio":"25", "profit_rate":"30"}, '
                            ' {"name":"Tiger S&P 100", "code":"332343", "cnt":"283", '
                            ' "cur_price":"4000", "buy_price":"3000", "ideal_ratio":"20", '
                            ' "cur_ratio":"25", "profit_rate":"30"} '
                            ']'

                 '} '
                 )
    resp = json.loads(resp_str)

    resp["fund_name"] = fund_name
    resp["fund_meta"] = "Asset Allocation Self Fund"

    total_percent = 0.0
    total_amount = 0.0
    current_total_amount = 0
    for s in item_list:
        total_percent += s.get_ideal_ratio()
        total_amount += s.get_count() * s.get_avg_price()
        valid, price, sdate = hdb.get_latest_price_from_db(conn, s.get_code())
        if valid:
            current_total_amount += price * s.get_count()
    
    if total_percent != 100.0:
        print(f'Fund: {fund_name} => Strange total percent is not 100 but {total_percent: .2f}')
    resp["total_price"] = f'{total_amount: .1f}'
    
    stock_list = []
    for s in item_list:
        code = s.get_code()
        valid, price, sdate = hdb.get_latest_price_from_db(conn, code)
        item_str = None
        if valid:
            if s.get_count() == 0:
                item_str = (f' "name":"{s.get_name()}", "code":"{s.get_code()}", "cnt":"{s.get_count()}", "cur_price":"{price: .2f}",'
                f' "buy_price":"{s.get_avg_price(): .2f}", "ideal_ratio":"{s.get_ideal_ratio(): .2f}",' 
                f' "cur_ratio":"0.0", "profit_rate":"0.0"') 
            else:
                cur_ratio = (s.get_count() * price)/current_total_amount * 100.0
                profit_rate = (price - s.get_avg_price())/s.get_avg_price() * 100.0
                item_str = (f' "name":"{s.get_name()}", "code":"{s.get_code()}", "cnt":"{s.get_count()}", "cur_price":"{price: .2f}",'
                f' "buy_price":"{s.get_avg_price(): .2f}", "ideal_ratio":"{s.get_ideal_ratio(): .2f}",' 
                f' "cur_ratio":"{cur_ratio: .2f}", "profit_rate":"{profit_rate: .2f}"') 
            item_str = '{ ' + item_str + '}'
            stock_list.append(item_str)

    if total_amount > 0:
        total_profit = (current_total_amount - total_amount)/total_amount * 100.0
        resp["profit_rate"] = f'{total_profit: .1f}'
    else:
        resp["profit_rate"] = '0.0'
    resp["cur_price"] = f'{current_total_amount: .1f}'
    resp["stocks"] = stock_list

    str_out = json.dumps(resp)
    import re
    str_out = re.sub(r"\\","", str_out);
    str_out = re.sub(" ", "", str_out);
    #str_out = str_out.replace('["', '[');
    #str_out = str_out.replace('"]', ']');
    str_out = str_out.replace('}"', '}');
    str_out = str_out.replace('"{', '{');
    #print(str_out)

    return str_out

def get_asset_alloc_status(conn):
    fund_data = hdb.get_asset_alloc_data(conn)

    asset_list = []
    for fund_name in fund_data.keys():
        item_list = fund_data[fund_name]
        print(f'---------------- {fund_name} --------------------')
        for s in item_list:
            print(s.to_string())
        print('-'*50)
        str_out = to_asset_alloc_fund_json(conn, fund_name, item_list)
        asset_list.append(str_out)

    return asset_list


def get_current_mdd(conn, code, start_date, end_date=None):
    cur_date, price, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date = get_mdd_values(conn, code, start_date, end_date)
    return cur_down, cur_date

def get_this_cycle_max_mdd(conn, code, start_date, end_date=None):
    cur_date, price, cur_down, this_max_mdd, this_max_mdd_date, all_max_mdd, all_max_mdd_date = get_mdd_values(conn, code, start_date, end_date)
    return this_max_mdd, this_max_mdd_date
