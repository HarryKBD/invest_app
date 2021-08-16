import happy_utils as ht
import happy_server as hs
import hdb
import datetime
import init_stock_db as indb

def update_stock_db_today(conn, code):
    today = datetime.datetime.now()
    if ht.is_working_day(today):
        l = hs.get_stock_data_from_server(code, today, today)
        if len(l) != 1:
            print(f'code: {code} => there is no data for today. very strange')
            return None
        else:
            hdb.insert_stock_data(conn, l)
    else:
        print(f'code: {code} => today is not a working day')
        return None

    return l[0].get_close()

def get_stock_trend(conn, code, from_date_str, to_date_str = None):
    today = datetime.datetime.now()
    #default
    if to_date_str == None and ht.is_working_day(today): #get date from server
        l = hs.get_stock_data_from_server(code, today, today)
        if len(l) != 1:
            print("there is no data for today. very strange")
        else:
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