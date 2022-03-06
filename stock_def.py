# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:58:29 2021

@author: keybd
"""
from unicodedata import category
from happy_utils import FORMAT_DATE
from datetime import datetime
import happy_utils as ht

class StockPrice:
    def __init__(self, code, date, openp = 0.0, highp = 0.0, lowp = 0.0, closep=0.0, volume = 0, change=0.0):
        self.code = code
        self.date = date
        self.closep = closep
        self.openp = openp
        self.highp = highp
        self.lowp = lowp
        self.change = change
        self.volume = volume

    def to_price_text(self):
        return "{0: <6}: {1} {2: <10.0f} {3: <5.2f}".format(
                self.code, self.date.strftime(FORMAT_DATE), self.closep, self.change*100)
    def to_full_text(self):
        return "{} {} {:.1f} {:.1f} {:.1f} {:.1f} {} {:.1f}".format(
                self.code, self.date.strftime(FORMAT_DATE), 
                self.openp, self.highp, self.lowp, self.closep, self.volume, self.change)
    def get_code(self):
        return self.code
    def get_date(self):
        return self.date.strftime(FORMAT_DATE)
    def get_open(self):
        return self.openp
    def get_high(self):
        return self.highp
    def get_low(self):
        return self.lowp
    def get_close(self):
        return self.closep
    def get_volume(self):
        return self.volume
    def get_change(self):
        return self.change


class fund_stock:
    def __init__(self, code, added_date, buy_price, buy_cnt, fund_name):
        self.code = code
        self.added_date = added_date
        self.buy_price = buy_price
        self.buy_cnt = buy_cnt
        self.fund_name = fund_name
        self.cur_price = 0
        self.name = "TBD" 

    def set_current_price(self, p):
        self.cur_price = p
    
    def get_invested_value(self):
        return self.buy_price * self.buy_cnt

    def get_current_value(self):
        return self.cur_price * self.buy_cnt

    def get_fund_name(self):
        return self.fund_name

    def set_name(self, n):
        self.name = n

    def to_string(self):
        str1 = "{0: <6} {5: <15} {1: <11} {2: <7.0f} {3: <4} {4: <12} ".format(self.code, self.added_date, self.buy_price, self.buy_cnt, self.fund_name, self.name)
        if self.cur_price > 0:
            earn_rate = (self.cur_price - self.buy_price)/self.buy_price * 100.0
            str2 = " (today: {0: <7.0f} => {1: <3.2f})".format(self.cur_price, earn_rate)
            str1 += str2
        return str1

    def print_status(self):
        s = self.to_string()
        print(s)
    

class StockTrackingResult:
    def __init__(self, code, category, added_date, base_price, origin, wanted, cnt, avg_price, name, max_date, max_price, todayp, today_rate):
        self.code = code
        self.category = category
        self.added_date = added_date
        self.base_price = base_price
        self.origin = origin
        self.wanted = wanted
        self.cnt = cnt
        self.avg_price = avg_price
        self.name = name
        self.max_date = max_date
        self.max_price = max_price
        self.todayp = todayp
        self.today_rate = today_rate
        
        self.base_rate = (self.todayp - self.base_price)/self.base_price * 100.0
        self.rate_max = (self.todayp - self.max_price)/self.max_price * 100.0
            
    def get_print_string(self):
    
        if self.cnt > 0:
            profit_rate = (self.todayp - self.avg_price)/self.avg_price*100.0

        str1 = "{7: <1} {11: <1} {0: <7} {1: <6} {2: <13} {3: <7.0f} {4: >4.1f} MAX:({9: <8}, {8: >4.0f} {10: >6.0f})=> BS [{5: <7.0f} {6: >4.0f}] ".format(
                self.category[:6], self.code, self.name, self.todayp, self.today_rate, self.base_price, self.base_rate, self.origin[0], self.rate_max, self.max_date[2:], self.max_price, self.wanted)

        str2 = "{0: <22} {1: <5}".format(" "*22, self.added_date[2:7], self.origin)
        if self.cnt > 0:
            str2 = "[{0: >7.0f} {1: <5.1f} ({2: >4})] {3: <5} ".format(self.avg_price, profit_rate, str(self.cnt), self.added_date[2:7], self.origin)

        return (str1 + str2)

class AssetAllocItem:
    def __init__(self):
        pass

    def set_asset_data(self, fund, code, name_eng, name_kor, price, count, ideal_ratio, category, last_update=None):
        self.fund_name = fund
        self.stock_code = code
        self.stock_name_eng = name_eng
        self.stock_name_kor = name_kor
        self.avg_price = price
        self.count = count
        self.ideal_ratio = ideal_ratio
        self.category = category
        if last_update == None:
            today = datetime.now()
            self.last_update = ht.datetime_to_str(today)
        else:
            self.last_update = last_update

    def set_asset_data_by_series(self, pd_stock):
        self.fund_name = pd_stock['fund_name']
        self.stock_code = pd_stock['stock_code']
        self.stock_name_eng = pd_stock['stock_name_eng']
        self.stock_name_kor = pd_stock['stock_name_kor']
        self.avg_price = float(pd_stock['avg_price'])
        self.count = int(pd_stock['count'])
        self.ideal_ratio = pd_stock['ideal_ratio']
        self.category = pd_stock['category']
        self.last_update = pd_stock['last_updated']

    def get_fund_name(self):
        return self.fund_name
    
    def get_code(self):
        return self.stock_code
    
    def get_name(self):
        return self.stock_name_eng
    
    def get_name_kor(self):
        return self.stock_name_kor
    
    def get_count(self):
        return self.count
    
    def get_last_update_date(self):
        return self.last_update

    def get_ideal_ratio(self):
        return self.ideal_ratio

    def get_category(self):
        return self.category
    
    def get_avg_price(self):
        return self.avg_price

    def to_string(self):
        str = f'FUND: {self.fund_name} => {self.stock_name_eng} {self.stock_name_kor} {self.stock_code} \
               {self.avg_price: .1f} {self.count} {self.ideal_ratio: .1f} {self.category} {self.last_update}'
        return str