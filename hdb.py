# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 11:00:40 2021

@author: keybd
"""
import matplotlib.pyplot as plt
import sqlite3
import csv
from datetime import datetime
from stock_def import AssetAllocItem

FORMAT_DATE = '%Y-%m-%d'
MY_HOME='/home/pi/invest_app/'
#MY_HOME='./'

def connect_db(db_name):
    conn = sqlite3.connect(MY_HOME + db_name)
    return conn


def get_stock_data_from_db(conn, code, s_datetime=None, e_datetime=None):
    c = conn.cursor()
    
    
    if s_datetime != None and e_datetime != None:
        #for row in c.execute('select * from stocks order by code, sdate'):
        #for row in c.execute('select * from trade_history order by op_time'):
        query = "select sdate, close from stocks where code = '{}' and sdate >= '{}' and sdate <= '{}' order by sdate".format(
                code, s_datetime.strftime(FORMAT_DATE), e_datetime.strftime(FORMAT_DATE))
    else:
        query = "select sdate, close from stocks where code = '{}' order by sdate".format(code)
    #print(query)
    cnt = 0
    full_date = []
    y = []
    for row in c.execute(query):
        full_date.append(row[0])
        y.append(float(row[1]))
        cnt += 1

    if cnt == 0:
        return False, full_date, y
    else:
        return True, full_date, y



def log_stock_trading(conn, code, op, price, vol, log_date = None):
    if log_date:
        now = log_date
    else:
        now = datetime.now()
    op_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    print("ACTION: {} code: {}  optime: {} price: {:.1f}".format(op, code, op_time, price))
    query = (
            "insert or ignore into trade_history(code, op_time, operation, volume, price) " + 
            "values('{}','{}','{}',{},{:.2f})"
            ).format(code, op_time, op, str(vol), price);
    try:
        c = conn.cursor()
        #print(query)
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True




def get_closed_price(code, dd):
    colname = 'Close'
    df = fdr.DataReader(code, dd, dd)
    print(df.head())
    print("-"*100)
    print(len(df))
    print("-"*100)
    print(float(df[colname][0]))
    print("-"*100)
    print(type(df[colname]))
    print("-"*100)
    if len(df) == 1:
        return float(df[colname])
    else:
        return -1.0

def get_current_price(code):
    now = get_today()
    d = now.strftime(FORMAT_DATE)
    print("Today: " + d)
    return get_closed_price(code, d)

def get_latest_price_from_db(conn, code):
    c = conn.cursor()
    query = "select close, sdate from stocks where code='{}' order by sdate desc LIMIT 1".format(code)

    cnt = 0
    price = 0
    sdate = None
    for row in c.execute(query):
        price = float(row[0])
        sdate = row[1]
        cnt += 1

    if cnt == 0:
        return False, None, None
    else:
        return True, price, sdate

def get_stock_names(conn, code):
    query = "select name_kor, name_eng from stock_basic_info where code = '{}'".format(code)
    c = conn.cursor()
    for row in c.execute(query):
        return row[0], row[1]
    
    return None, None


def get_all_stocks_code(conn, market):
    
    code_list = []
    if market != 'all':
        return code_list
    
    query = "select code from stock_basic_info"
    c = conn.cursor()
    
    for row in c.execute(query):
        code_list.append(row[0])
    
    return code_list


def get_stock_code_list_interested(conn):
    code_list = []

    query = "select code from target_list"
    c = conn.cursor()
    
    for row in c.execute(query):
        code_list.append(row[0])
    
    return code_list

def get_stock_info_interested(conn, code):
    query = "select category, added_date, base_price, origin, wanted from target_list where code = '{}'".format(code)
    c = conn.cursor()
    
    for row in c.execute(query):
        return row[0], row[1], row[2], row[3], row[4]
    
    return None, None, None, None, None, None
    
def get_latest_transaction(conn, code):
    query = "select code, max(op_time), operation from trade_history where code = '{}'".format(code)
    
    #print(query)
    c = conn.cursor()
    #result = 
    #print("History returns {}" + str(result.rowcount))

    for row in c.execute(query):
        return row[1], row[2]
    now = datetime.now()
    return now.strftime(FORMAT_DATE), 'SELL'
    

def get_own_stock_info(conn, code):
    query = "select cnt, avg_price from current_stock where code = '{}'".format(code)
    #print(query)
    c = conn.cursor()
    
    for row in c.execute(query):
        return row[0], row[1]
    
    return 0, 0.0
    
def clean_history_table(conn):
    query = "delete from trade_history"
    c = conn.cursor()
    c.execute(query)

def clean_all_stock_price_table(conn):
    query = "delete from stocks"
    c = conn.cursor()
    c.execute(query)


   
def insert_stock_data(conn, s_list):
    try:
        c = conn.cursor()
        for s in s_list:
            query = (
                    "insert or replace into stocks(code, sdate, open, high, low, close, volume, change) "
                    + "values('{}', '{}', {:.1f}, {:.1f}, {:.1f}, {:.1f}, {}, 0.0)"
                    ).format(s.get_code(), s.get_date(), s.get_open(), s.get_high(),
                            s.get_low(), s.get_close(), s.get_volume())
            #print(query)
            c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)
#c.execute("insert into stocks(code, sdate, closep) values(068270, '2021-01-12', 123.456)")
#c.execute("insert into stocks(code, sdate, closep) values(068270, '2021-01-13', 123.456)")
#c.execute("insert into stocks(code, sdate, closep) values(068270, '1999-01-13', 123.456)")
#conn.commit()

def insert_current_stock(conn, code, avg_price, cnt):
    try:
        c = conn.cursor()
        query = (
                 "insert or replace into current_stock(code, cnt, avg_price) "
               + "values('{}', {}, {:.1f})"
               ).format(code, str(cnt), avg_price)
        print(query)
        c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)


def insert_target_list(conn, category, code, base_price, added, origin, wanted='2'):
    try:
        c = conn.cursor()
        query = (
                 "insert or replace into target_list(category, code, added_date, base_price, origin, wanted) "
               + "values('{}', '{}', '{}', {:.1f}, '{}', '{}')"
               ).format(category, code, added, base_price, origin, wanted)
        print(query)
        c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)
    

def insert_stock_in_fund(conn, code, buy_date, buy_price, buy_cnt, fund_name):
    try:
        c = conn.cursor()
        query = (
                 "insert or replace into fund(code, added_date, buy_price, scnt, fund_name) "
               + "values('{}', '{}', '{:.1f}', {}, '{}')"
               ).format(code, buy_date, buy_price, buy_cnt, fund_name)
        print(query)
        c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)

def insert_stock_basic_info(conn, rdr):
    try:
        c = conn.cursor()
        for line in rdr:
            code = line[1].replace("'", "")
            name_kor = line[3].replace("'", "")
            name_eng = line[4].replace("'", "")
            market = line[6].replace("'", "")
            
            query = (
                    "insert or replace into stock_basic_info(code, name_kor, name_eng, market_type) "
                    + "values('{}', '{}', '{}', '{}' )"
                    ).format(code, name_kor, name_eng, market)
            #print(query)
            c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)

def init_stock_basic_info_table(conn, csv_file):
    create_stock_basic_info_table(conn)
 
    f = open(csv_file,'r')
    rdr = csv.reader(f)
 
    insert_stock_basic_info(conn, rdr)
     
    f.close()   


def create_stock_basic_info_table(conn):
    query = """CREATE TABLE IF NOT EXISTS stock_basic_info(
                code TEXT NOT NULL,
                name_kor TEXT NOT NULL, 
                name_eng TEXT NOT NULL,
                market_type TEXT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def create_fund_table(conn):
    query = """CREATE TABLE IF NOT EXISTS fund(
                code TEXT PRIMARY KEY NOT NULL,
                added_date DATE NOT NULL, 
                buy_price FLOAT NOT NULL,
                scnt INT NOT NULL,
                fund_name TEXT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def drop_asset_allocation_stock_table(conn):
    query = "DROP TABLE IF EXISTS asset_alloc_stock;"
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True


def create_asset_allocation_stock_table(conn):
    drop_asset_allocation_stock_table(conn)
    query = """CREATE TABLE IF NOT EXISTS asset_alloc_stock(
                fund_name TEXT NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name_eng TEXT NOT NULL,
                stock_name_kor TEXT NOT NULL,
                avg_price FLOAT NOT NULL,
                count INT NOT NULL,
                ideal_ratio FLOAT NOT NULL,
                category INT NOT NULL,
                last_updated DATE NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def insert_asset_alloc_stock_data(conn, s_list):
    try:
        c = conn.cursor()
        for s in s_list:
            query = (
                    "insert or replace into asset_alloc_stock( "
                    + "fund_name, stock_code, stock_name_eng, stock_name_kor, avg_price, count, ideal_ratio, category, last_updated) "
                    + "values('{}', '{}', '{}', '{}', {:.1f}, {}, {:.1f}, {}, {})"
                    ).format(s.get_fund_name(), s.get_code(), s.get_name(), s.get_name_kor(), s.get_avg_price(),
                             s.get_count(), s.get_ideal_ratio(), s.get_category(), s.get_last_update_date())
            c.execute(query)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(e)

import copy

def get_asset_alloc_data(conn):
    query = (
            "select fund_name, stock_code, stock_name_eng, stock_name_kor, avg_price, count, ideal_ratio, category, last_updated "
            + "from asset_alloc_stock where fund_name in (select DISTINCT(fund_name) from asset_alloc_stock)"
            )

    c = conn.cursor()
    
    last_fund_name = "NONE"
    item_list = []
    asset_fund_data = {}
    for row in c.execute(query):
        fund_name = row[0]
        item = AssetAllocItem()
        item.set_asset_data(row[0], row[1], row[2], row[3], float(row[4]), int(row[5]), float(row[6]), int(row[7]), row[8])
        if fund_name != last_fund_name: #append
            #"select fund_name, stock_code, stock_name_eng, stock_name_kor, avg_price, count, ideal_ratio, category, last_updated "
            if len(item_list) > 0:
                asset_fund_data[last_fund_name] = copy.deepcopy(item_list)
            item_list.clear()
            last_fund_name = fund_name
        item_list.append(item)

    if len(item_list) > 0:
        asset_fund_data[last_fund_name] = copy.deepcopy(item_list)
    return asset_fund_data
 

def get_fund_items(conn, fund_name='all'):
    stock_list = []

    query = "select code, added_date, buy_price, scnt, fund_name from fund"
    if fund_name != 'all':
        query = query + " where fund_name = '{}'".format(fund_name)

    c = conn.cursor()
    
    for row in c.execute(query):
        tmpl = [row[0], row[1], row[2], row[3], row[4]]
        stock_list.append(tuple(tmpl))
    
    return stock_list

def create_target_list_table(conn):
    query = """CREATE TABLE IF NOT EXISTS target_list(
                category TEXT NOT NULL,            
                code TEXT PRIMARY KEY NOT NULL,
                added_date DATE NOT NULL, 
                base_price FLOAT NOT NULL,
                origin TEXT NOT NULL,
                wanted TEXT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True


def create_trade_history_table(conn):
    query = """CREATE TABLE IF NOT EXISTS trade_history(
                code TEXT NOT NULL,
                op_time DATETIME NOT NULL,
                operation TEXT NOT NULL,
                volume INT NOT NULL,
                price FLOAT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def create_current_stock_table(conn):
    query = """CREATE TABLE IF NOT EXISTS current_stock(
                code TEXT PRIMARY KEY NOT NULL,
                cnt INT NOT NULL,
                avg_price FLOAT NOT NULL
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
        conn.commit()
    except Error as e:
        print(e)
        return False
    return True

def create_stock_price_table(conn):
    query = """CREATE TABLE IF NOT EXISTS stocks(
                code text NOT NULL,
                sdate date NOT NULL,
                open FLOAT NOT NULL,
                high FLOAT NOT NULL,
                low FLOAT NOT NULL,
                close FLOAT NOT NULL,
                volume INT NOT NULL,
                change FLOAT NOT NULL,
                PRIMARY KEY (code, sdate)
                );"""
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)
        return False
    return True


def create_all_tables(conn):
    create_current_stock_table(conn)
    create_stock_basic_info_table(conn)
    create_trade_history_table(conn)
    create_stock_price_table(conn)
    create_target_list_table(conn)
    create_fund_table(conn)
    create_asset_allocation_stock_table(conn)
