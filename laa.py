# -*- coding: utf-8 -*-
"""
Created on Sat May  1 11:54:38 2021

@author: keybd
"""

import hdb
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import happy_utils as ht 

#utils

#전월 실업률 > 12개월 이동 평균 : 불황기

#전월 실업률 < 12개월 이동 평균 : 호황기

def get_unrate_status(conn, base_date):
    start_date =  base_date - timedelta(days=365*20) #get enough data
    #bdate_str = "{}-{}-01".format(base_date.year, base_date.month)
    valid, fdate, price_list = hdb.get_stock_data_from_db(conn, 'UNRATE', start_date, base_date)
    
    if len(fdate) < 12:
        return None
    
    total = 0.0
    add_cnt = 0
    for i in reversed(price_list):
        #print(i)
        total += i
        add_cnt += 1
        if add_cnt == 12:
            break;
    
    avg = total / 12
    if avg < price_list[-1]:
        st = "BAD"
    else:
        st = "GOOD"
    #print(f'latest_mon:{fdate[-1]} 12 months Average is : {avg:.2f} cnt: {add_cnt}, cur: {price_list[-1]:.2f} {st}')
    
    if st == "GOOD":
        return True
    else:
        return False
    
def get_snp_status(conn, base_date):
    #avg, curr_price, curr_date = get_moving_avg(conn, 'US500', base_date, 200)
    avg, curr_price, curr_date = get_moving_avg(conn, 'SPY', base_date, 200)
    if avg < 0:
        return None
    #print(f'{curr_price} avg {avg}')
    if curr_price > avg:
        return True
    else:
        return False

def get_moving_avg(conn, code, base_date, days=100):
    
    start_date =  base_date - timedelta(days=days+days/5*2+100) #get enough data
    valid, fdate, price_list = hdb.get_stock_data_from_db(conn, code, start_date, base_date)
    
    #print(start_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
    #print(base_date.strftime("%Y-%m-%d %H:%M:%S.%f"))
    
    if valid == False:
        print("getting stock data failed")
        return -1, -1, None
    
    cnt = len(fdate)
    
    #print(cnt)
    if cnt < days:
        print("getting stock data failed2")
        return -1, -1, None
    #print(f'{code}')

    
    total = 0.0
    add_cnt = 0
    for i in reversed(price_list):
        #print(i)
        total += i
        add_cnt += 1
        if add_cnt == days:
            break;
    
    avg = total / add_cnt
    #print(f'Average is : {avg:.2f} cnt: {add_cnt}')
    return avg, price_list[-1], fdate[-1]
        
   
def get_eco_status(conn, dd, log=False):
    un_status = get_unrate_status(conn, dd)
    snp_status = get_snp_status(conn, dd)
    if log:
        print(f'unemployeed rate: {un_status}  snp status: {snp_status}')
    if un_status == None or snp_status == None:
        print("Error........")
        return None
    if un_status == False and snp_status == False:
        #print(f'{ht.datetime_to_str(test_date)} ==> UNRATE:{un_status}  S&P:{snp_status}')
        return False
    else:
        return True        

    
if __name__ == '__main__':
    conn = hdb.connect_db("./stock_all.db")
    # start_date = '2006-12-01'
    # today = datetime.now()
    # test_date = ht.to_datetime(start_date)
    
    # r_avg = []
    # r_price = []
    # code = 'US500'
    # while today > test_date:
    #     avg, curr_price, curr_date = get_moving_avg(conn, code, test_date, 200)
    #     r_avg.append(avg)
    #     r_price.append(curr_price)
    #     if curr_price > avg:
    #         stat = "HIGH"
    #     else:
    #         stat = "LOW"
    #     print(f'{ht.datetime_to_str(test_date)} ==> {avg:.2f} today({curr_date}):{curr_price} => {stat}')
    #     test_date += timedelta(days=1)
    #     get_unrate_status(conn, test_date)
    #     #aaa
        
    # plt.plot(r_avg, c='r')
    # plt.plot(r_price, c='b')
    # plt.show()
    
    #start_date = '2021-05-11'
    #test_date = ht.to_datetime(start_date)
    
    
    start_date = '2006-12-01'
    today = datetime.now()
    test_date = ht.to_datetime(start_date)
    
    r_price = []
    r_no_stock = []
    while today > test_date:
        avg, curr_price, curr_date = get_moving_avg(conn, 'SPY', test_date, 200)
        r_price.append(curr_price)
        un_status = get_unrate_status(conn, test_date)
        snp_status = get_snp_status(conn, test_date)
        if un_status == None or snp_status == None:
            print("Error........")
            break
        if un_status == False and snp_status == False:
            print(f'{ht.datetime_to_str(test_date)} ==> UNRATE:{un_status}  S&P:{snp_status}')
            r_no_stock.append(100)
        else:
            r_no_stock.append(0)
        test_date += timedelta(days=1)
        
    plt.figure(figsize=(500,100))
    plt.plot(r_price, c='b')
    plt.plot(r_no_stock, c='r')
    plt.show()
 
    conn.close()
