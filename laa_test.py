# -*- coding: utf-8 -*-
"""
Created on Sat May 15 15:46:35 2021

@author: keybd
"""


# import FinanceDataReader as fdr

# unrate = fdr.DataReader('UNRATE', '2020-07-01', '2020-07-01', data_source='fred') 


# list_unrate = unrate['UNRATE']
# idx = unrate.index
# i = 0

# for un in list_unrate:
#     last_date =  idx[i].to_pydatetime()
#     print(f'{last_date} => {un}')
#     i += 1
    
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 16:07:24 2021

@author: keybd
"""
from datetime import datetime
import sys
import math
import hdb
import happy_utils as ht
import laa

MY_HOME='./'
cash_left = 0


class Stock:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.cnt = 0
        self.history = []
        self.avg_price = 0.0

    def buy(self, price, cnt):
        now = datetime.now()
        cur_value = self.avg_price * self.cnt
        add_val = price * cnt
        self.cnt += cnt
        self.avg_price = (cur_value + add_val) / self.cnt
        htext = "{}: buy:  price: {}  cnt: {}  => current: avg {:.1f}  cnt: {}".format(
            now.strftime("%Y-%m-%d %H:%M:%S.%f"), str(price), str(cnt), self.avg_price, str(self.cnt))
        #print(htext)
        self.history.append(htext)
        
    def sell(self, cnt):
        now = datetime.now()
        self.cnt -= cnt
        if self.cnt < 0:
            print("Error count cannot be minus value")
        if self.cnt <= 0:
            self.avg_price = 0
            self.cnt = 0
        htext = "{}: sell:  cnt: {}  => current: avg {:.1f}  cnt: {}".format(
            now.strftime("%Y-%m-%d %H:%M:%S.%f"), str(cnt), self.avg_price, str(self.cnt))
        #print(htext)
        self.history.append(htext)
        
    def adjust(self, budget, curr_price):
        val = self.get_value(curr_price)
        if val > budget: #sell some
            diff = val - budget
            to_sell = math.floor(diff/(curr_price*0.99))
            if to_sell > self.cnt:
                print(f"Error......current: {self.cnt} can't sell {to_sell}  {price}  {budget}")
                return -1
            self.sell(to_sell)
            #print("Adjusting to {:.1f}, sell cnt: {}  sell_value: {}. Now: {}".format(budget, str(to_sell), str(to_sell*curr_price), self.to_str()))
            return diff
        else:           #buy some
            diff = budget - val
            to_buy = math.floor(diff/(curr_price*1.01))
            self.buy(curr_price, to_buy)
            #print("Adjusting to {:.1f}, buy cnt: {}  buy_value: {}. Now: {}".format(budget, str(to_buy), str(to_buy*curr_price), self.to_str()))
            return diff * -1
        
    def get_value(self, curr_price):
        #print(f'get_value {curr_price}, cnt: {self.cnt}')
        return curr_price * self.cnt

    def get_history(self):
        return self.history
    
    def to_str(self):
        result = "code: {} avg_price: {:.1f} cnt: {}".format(self.code, self.avg_price, self.cnt)
        return result        
        
      


    
class BalancedAccount:
    #port = {'VT': 35.0, 'DBC':5.0, 'IAU':5.0, 'TLT':20.0, 'LTPZ':20.0, 'VCLT':7.5, 'EMLC':7.5}
    #port = {stock('VT'):ratio}
    def __init__(self, invest, portpolio):
        self.initial_invest = invest
        self.portpolio = portpolio
        self.stocks = {}
        self.cash = 0
        if self.check_valid_portpolio(portpolio) != True:
            print(f"Portpolio is not valid. pls check")
            sys.exit()
        self.create_stock_list()
           
   
    def create_stock_list(self):
        #generate portpolio
        self.stocks.clear()
        codes = self.portpolio.keys()
        for c in codes:
            stock = Stock(c, c)
            self.stocks[c] = stock    
 
    
    def replace_portpolio(self, new_portpolio, price_dict):
        self.sell_all_stocks(price_dict)
        if self.check_valid_portpolio(new_portpolio) != True:
            print(f"Portpolio is not valid. pls check")
            sys.exit()
        self.portpolio = new_portpolio
        self.create_stock_list()
        self.rebalance(price_dict, self.cash)
        self.cash = 0

    def sell_all_stocks(self, price_dict):  #private
        stocks = self.stocks.keys()
        for c in stocks:
            stock = self.stocks[c]
            if c not in price_dict:
                print(f"code {c} not exists in the price dict")
                sys.exit()

            cur_price = price_dict[c]
            self.cash += stock.get_value(cur_price)
        
        #print(f'sell_all_done cash: {self.cash}')
        self.stocks.clear()
       
    def check_valid_portpolio(self, portpolio):
        vals = port.values()
        sums = 0
        for v in vals:
            sums += v
        if sums != 100:
            print(f"SUM: {sums}")
            return False
        else:
            return True
    
    
    def init_account(self, price_dict):
        self.rebalance(price_dict,self.initial_invest)
        
    def rebalance(self, price_dict, budget = 0):
        #print(f'start rebalance: budget: {budget}')
        codes = self.stocks.keys()
        if budget == 0:
            budget = self.get_total_value(price_dict)
        for c in codes:
            stock = self.stocks[c]
            percent = self.portpolio[c]
            price = price_dict[c]
            allocated = math.floor(budget * percent / 100.0)
            #print(f'code: {c} allocated: {allocated} price: {price}')
            stock.adjust(allocated, price)
    
    def get_total_value(self, price_dict):
        vsum = 0
        codes = self.stocks.keys()
        for c in codes:
            vsum += self.get_stock_value(c, price_dict[c])
        return vsum
    
    def get_stock_value(self, code, price):
        stock = self.stocks[code]
        return stock.get_value(price)
        
    def show_items(self):
        codes = self.stocks.keys()
        for c in codes:
            print(self.stocks[c].to_str())
    
    def print_stat(self, price_dict):
        total_value = self.get_total_value(price_dict)
        codes = self.stocks.keys()
        for c in codes:
            value = self.get_stock_value(c, price_dict[c])
            percent = value/total_value*100.0
            r = "{} => {:.1f}  {:.1f}% ideal({:.1f}%)".format(self.stocks[c].to_str(), value, percent, self.portpolio[c])
            print(r)


def exit_prog(conn, msg):
    print(msg)
    conn.close()
    sys.exit()
    
def get_eco_status(conn, dd, log=False):
    un_status = laa.get_unrate_status(conn, dd)
    snp_status = laa.get_snp_status(conn, dd)
    if log:
        print(f'unemployeed rate: {un_status}  snp status: {snp_status}')
    if un_status == None or snp_status == None:
        print("Error........")
        exit_prog(conn, "eco_status")
    if un_status == False and snp_status == False:
        #print(f'{ht.datetime_to_str(test_date)} ==> UNRATE:{un_status}  S&P:{snp_status}')
        return False
    else:
        return True
        
if __name__ == '__main__':
    conn = hdb.connect_db("./stock_all.db")
        

    #SHY or QQQ
    port = {'OP1': 25.0, 'OP2': 25.0, 'OP3': 25.0, 'OP4': 25.0}

    #active_portpolio = {'IWD' : 25.0, 'GLD': 25.0, 'IEF': 25.0, 'QQQ': 25.0}
    #passive_portpolio = {'IWD' : 25.0, 'GLD': 25.0, 'IEF': 25.0, 'SHY': 25.0}

    active_portpolio = {'SSO' : 25.0, 'UGL': 25.0, 'UBT': 25.0, 'TQQQ': 25.0}
    passive_portpolio = {'SSO' : 25.0, 'UGL': 25.0, 'UBT': 25.0, 'SHY': 25.0}


    cur_price_list = {}

    slist = active_portpolio.keys()
    for c in slist:
        if c not in cur_price_list.keys():
            cur_price_list[c] = 0.0
    slist = passive_portpolio.keys()
    for c in slist:
        if c not in cur_price_list.keys():
            cur_price_list[c] = 0.0

    print(cur_price_list)

    start_date = '2016-12-01'
    end_date = '2020-04-30'
    
    today = datetime.now()
    sdate = ht.to_datetime(start_date)
    edate = ht.to_datetime(end_date)
    
    datapot = {}
    for c in cur_price_list.keys():
        valid, dd, price = hdb.get_stock_data_from_db(conn, c, sdate, edate)
        print(f'{c} => len {len(dd)}')
        if valid == False:
            print(c)
            exit_prog(conn, "code not found in the db error")
        datapot[c] = price
    
    cnt = len(dd)
    for v in datapot.values():
        if len(v) != cnt:
            exit_prog(conn, "Count error")

    init_invest = 100000

    #init the first pricelist
    for c in datapot.keys():
        price_list = datapot[c]
        cur_price_list[c] = price_list[0]
    
    #init the first
    last_eco_status = get_eco_status(conn, ht.to_datetime(dd[0]))
    if last_eco_status:
        cur_port = active_portpolio
    else:
        cur_port = passive_portpolio

    account = BalancedAccount(init_invest, cur_port)
    account.init_account(cur_price_list)
    print("Starting.....")
    #account.print_stat(cur_price_list)
    cur_year = ht.get_year(dd[0])
    year_start_val = account.get_total_value(cur_price_list)
    
    idx = 1
    aged = 1
    for td in dd[1:]:
        #update price list
        for c in datapot.keys():
            price_list = datapot[c]
            cur_price_list[c] = price_list[idx]
 
        y = ht.get_year(td)
        if y != cur_year:
            account.print_stat(cur_price_list)
            y_val = account.get_total_value(cur_price_list)
            earn = y_val - year_start_val
            print(f'{cur_year} :  start: {year_start_val:.1f} -> end: {y_val:.1f}  earn: {earn:.1f} ==> {earn/year_start_val*100:.1f}')
            print(f'before rebal {account.get_total_value(cur_price_list)}')
            account.rebalance(cur_price_list)
            print(f'After rebal {account.get_total_value(cur_price_list)}')
            account.print_stat(cur_price_list)
            year_start_val = y_val
            cur_year = y
        td_eco = get_eco_status(conn, ht.to_datetime(td))
        if td_eco != last_eco_status: #portpolio change
            print(f'{td} Changing portpolio today eco status {td_eco}')
            if td_eco:
                cur_port = active_portpolio
            else:
                cur_port = passive_portpolio
            #account.print_stat(cur_price_list)
            account.replace_portpolio(cur_port, cur_price_list)
            last_eco_status = td_eco
            aged = 0
        else:
            if aged > 120:
                #print(f'{td} Time pass : Reblance portpolio today eco status {td_eco}')
                
                #account.rebalance(cur_price_list)
                aged = 0


        idx += 1
        aged += 1


    account.print_stat(cur_price_list)
    total = account.get_total_value(cur_price_list)
    earn = total - init_invest
    
    print(f'start: {init_invest:.1f} -> end: {total:.1f}  earn: {earn:.1f} ==> {earn/init_invest*100:.1f}')
    
    
    print(get_eco_status(conn, ht.to_datetime('2021-05-23'), True))
    conn.close()
    